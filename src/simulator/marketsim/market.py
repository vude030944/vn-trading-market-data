"""
One market, three brokers.

The engine owns the truth — prices, books, day statistics — and publishes events.
Each broker server listens and re-encodes those events in its own dialect. So the
same HPG trade reaches SSI, DNSE and TCBS clients, each with that broker's units,
types and timestamp conventions, which is what makes cross-source comparison in
ClickHouse meaningful.

Listeners run synchronously inside the engine loop and must only format and
enqueue; they may read state but never block.
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from .config import SimConfig
from .universe import INDICES, Instrument, build_universe

log = logging.getLogger(__name__)

VN_TZ = timezone(timedelta(hours=7))
LEVELS = 10


def vn_now() -> datetime:
    return datetime.now(VN_TZ)


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------


@dataclass
class SymbolState:
    inst: Instrument
    price: float
    floor: float
    ceiling: float
    open: float | None = None
    high: float | None = None
    low: float | None = None
    vol: int = 0
    value: float = 0.0
    last_qty: int = 0
    last_side: str = ""
    bids: list[list[float]] = field(default_factory=list)   # [[price, qty], ...] best first
    asks: list[list[float]] = field(default_factory=list)
    foreign_buy: int = 0
    foreign_sell: int = 0
    foreign_buy_val: float = 0.0
    foreign_sell_val: float = 0.0
    room_total: int = 0
    room_left: int = 0
    buy_up_acc: int = 0
    sell_down_acc: int = 0
    pt_acc_value: float = 0.0
    pt_vol: int = 0
    # minute bar: [start_epoch_s, open, high, low, close, volume]
    bar: list[Any] | None = None
    # supply/demand windows: {frame_s: [buy_up, sell_down]}
    sd_window: dict[int, list[int]] = field(default_factory=dict)
    # recent matches for TCBS `tmh` backfill: (hh:mm:ss, price, qty, change)
    history: deque = field(default_factory=lambda: deque(maxlen=300))

    @property
    def ref(self) -> float:
        return self.inst.ref_price

    @property
    def change(self) -> float:
        return round(self.price - self.ref, 2)

    @property
    def change_pct(self) -> float:
        return round((self.price - self.ref) / self.ref * 100, 4)

    @property
    def avg(self) -> float:
        return round(self.value / self.vol, 2) if self.vol else self.price


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------


@dataclass
class Trade:
    st: SymbolState
    price: float
    qty: int
    side: str        # B (buy-up, aggressor buys) | S (sell-down)
    ts_ns: int


@dataclass
class Quote:
    st: SymbolState
    ts_ns: int
    changed: tuple[int, ...]   # indexes (0-based) of levels that moved, for TCBS s|42


@dataclass
class Foreign:
    st: SymbolState
    ts_ns: int


@dataclass
class Bar:
    st: SymbolState
    start_s: int
    o: float
    h: float
    l: float
    c: float
    v: int
    closed: bool


@dataclass
class IndexValue:
    name: str
    number: int          # TCBS indexNumber
    type_code: str       # DNSE indexTypeCode
    value: float
    prior: float
    high: float
    low: float
    advances: int
    declines: int
    unchanged: int
    ceiling: int
    floor: int
    volume: int
    turnover: float      # VND
    ts_ns: int


@dataclass
class SupplyDemand:
    st: SymbolState
    frame_s: int
    buy_up: int
    sell_down: int
    time_s: int


@dataclass
class PutThrough:
    st: SymbolState
    price: float
    vol: int
    ts_ns: int


@dataclass
class Oddlot:
    st: SymbolState
    price: float
    qty: int
    ts_ns: int


@dataclass
class Session:
    exchange: str
    flag: str            # SSI-style: ATO | LO | INTERMISSION | ATC | CLOSED
    session_id: str      # DNSE tradingSessionId: 10 ATO, 40 continuous, 30 ATC, 99 closed
    event_id: str        # DNSE eventId
    ts_ns: int


Event = Trade | Quote | Foreign | Bar | IndexValue | SupplyDemand | PutThrough | Oddlot | Session
Listener = Callable[[Event], None]


# ---------------------------------------------------------------------------
# Session calendar (HOSE)
# ---------------------------------------------------------------------------

_PHASES = (  # (start hh:mm, flag, session_id, event_id)
    ("00:00", "CLOSED", "99", "AB2"),
    ("09:00", "ATO", "10", "AA1"),
    ("09:15", "LO", "40", "AB1"),
    ("11:30", "INTERMISSION", "99", "AW8"),
    ("13:00", "LO", "40", "AW9"),
    ("14:30", "ATC", "30", "BC1"),
    ("14:45", "CLOSED", "99", "AB2"),
)


def phase_at(now: datetime, market_hours: bool) -> tuple[str, str, str]:
    if not market_hours:
        return ("LO", "40", "AB1")
    if now.weekday() >= 5:
        return ("CLOSED", "99", "AB2")
    hm = now.strftime("%H:%M")
    cur = _PHASES[0]
    for p in _PHASES:
        if hm >= p[0]:
            cur = p
    return cur[1:]


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class MarketEngine:
    def __init__(self, cfg: SimConfig) -> None:
        self.cfg = cfg
        self.rng = random.Random(cfg.seed)
        self.states: dict[str, SymbolState] = {}
        for inst in build_universe():
            lo, hi = inst.band()
            st = SymbolState(inst, inst.ref_price, lo, hi)
            if inst.kind == "stock":
                st.room_total = int(inst.shares_out * 0.49)
                st.room_left = int(st.room_total * self.rng.uniform(0.2, 0.9))
            self._rebuild_book(st, range(LEVELS))
            self.states[inst.symbol] = st
        self._symbols = list(self.states)
        self._weights = [self.states[s].inst.weight for s in self._symbols]
        self._listeners: list[Listener] = []
        self._phase = phase_at(vn_now(), cfg.market_hours)
        # Set via POST /control/pause: no new events, so a test can wait for the
        # pipeline to drain and then compare counts exactly.
        self.paused = False
        self.index_prior = {n: v[3] for n, v in INDICES.items()}
        self._index_hilo: dict[str, list[float]] = {}

    # -- wiring --------------------------------------------------------------
    def listen(self, fn: Listener) -> None:
        self._listeners.append(fn)

    def _emit(self, evt: Event) -> None:
        for fn in self._listeners:
            try:
                fn(evt)
            except Exception:                 # a broken formatter must not stop the market
                log.exception("listener failed on %s", type(evt).__name__)

    @property
    def phase(self) -> tuple[str, str, str]:
        return self._phase

    def is_trading(self) -> bool:
        return self._phase[0] in ("ATO", "LO", "ATC")

    def by_exchange(self, pred: Callable[[Instrument], bool]) -> list[SymbolState]:
        return [s for s in self.states.values() if pred(s.inst)]

    # -- price mechanics -----------------------------------------------------
    def _snap(self, st: SymbolState, px: float) -> float:
        t = st.inst.tick_size(px)
        px = round(round(px / t) * t, 1)
        return min(max(px, st.floor), st.ceiling)

    def _rebuild_book(self, st: SymbolState, levels) -> None:
        t = st.inst.tick_size(st.price)
        lot = st.inst.lot()
        big = 40 if st.inst.kind == "future" else 300
        if not st.bids:
            st.bids = [[0.0, 0] for _ in range(LEVELS)]
            st.asks = [[0.0, 0] for _ in range(LEVELS)]
        for i in levels:
            bp = self._snap(st, st.price - t * (i + 1))
            ap = self._snap(st, st.price + t * (i + 1))
            st.bids[i] = [bp, lot * self.rng.randint(1, big)]
            st.asks[i] = [ap, lot * self.rng.randint(1, big)]

    def _trade(self, st: SymbolState, now_ns: int) -> None:
        t = st.inst.tick_size(st.price)
        # Random walk with mild mean reversion towards the reference price.
        drift = (st.ref - st.price) / st.ref * 0.5
        step = self.rng.choice((-2, -1, -1, 0, 0, 0, 1, 1, 2)) + (1 if self.rng.random() < drift else 0)
        prev = st.price
        st.price = self._snap(st, st.price + step * t)
        side = "B" if st.price > prev or (st.price == prev and self.rng.random() < 0.5) else "S"
        qty = st.inst.lot() * max(1, int(self.rng.expovariate(1 / (3 if st.inst.kind == "future" else 15))))
        st.open = st.open if st.open is not None else st.price
        st.high = max(st.high or st.price, st.price)
        st.low = min(st.low or st.price, st.price)
        st.vol += qty
        mult = 100_000 if st.inst.kind == "future" else 1   # VN30F multiplier: 100k VND/point
        st.value += st.price * qty * mult
        st.last_qty, st.last_side = qty, side
        if side == "B":
            st.buy_up_acc += qty
        else:
            st.sell_down_acc += qty
        for frame_s in (self.cfg.sd_short_s, self.cfg.sd_long_s):
            w = st.sd_window.setdefault(frame_s, [0, 0])
            w[0 if side == "B" else 1] += qty
        st.history.append((vn_now().strftime("%H:%M:%S"), st.price, qty, st.change))
        self._emit(Trade(st, st.price, qty, side, now_ns))

        # The book re-centres on the new price: every level moves.
        self._rebuild_book(st, range(LEVELS))
        self._emit(Quote(st, now_ns, tuple(range(LEVELS))))

        if st.inst.kind == "stock" and self.rng.random() < 0.15:
            fq = min(qty, st.room_left) if side == "B" else qty
            if side == "B":
                st.foreign_buy += fq
                st.foreign_buy_val += fq * st.price
                st.room_left -= fq
            else:
                st.foreign_sell += fq
                st.foreign_sell_val += fq * st.price
                st.room_left = min(st.room_total, st.room_left + fq)
            self._emit(Foreign(st, now_ns))

        self._update_bar(st, now_ns, qty)

        if st.inst.kind == "stock" and self.rng.random() < 0.03:
            self._emit(Oddlot(st, st.price, self.rng.randint(1, 99), now_ns))

    def _quote_only(self, st: SymbolState, now_ns: int) -> None:
        """Book changes without a trade — on futures this is most of the traffic."""
        n = self.rng.randint(1, 3)
        levels = tuple(sorted(self.rng.sample(range(LEVELS), n)))
        lot = st.inst.lot()
        big = 40 if st.inst.kind == "future" else 300
        for i in levels:
            st.bids[i][1] = lot * self.rng.randint(1, big)
            st.asks[i][1] = lot * self.rng.randint(1, big)
        self._emit(Quote(st, now_ns, levels))

    def _update_bar(self, st: SymbolState, now_ns: int, qty: int) -> None:
        minute = now_ns // 1_000_000_000 // 60 * 60
        if st.bar is not None and st.bar[0] != minute:
            b = st.bar
            self._emit(Bar(st, b[0], b[1], b[2], b[3], b[4], b[5], True))
            st.bar = None
        if st.bar is None:
            st.bar = [minute, st.price, st.price, st.price, st.price, 0]
        b = st.bar
        b[2], b[3], b[4], b[5] = max(b[2], st.price), min(b[3], st.price), st.price, b[5] + qty
        self._emit(Bar(st, b[0], b[1], b[2], b[3], b[4], b[5], False))

    # -- periodic ------------------------------------------------------------
    def _indices(self, now_ns: int) -> None:
        for name, (pred, number, code, base) in INDICES.items():
            members = self.by_exchange(pred)
            if not members:
                continue
            ret = sum(s.price / s.ref for s in members) / len(members)
            value = round(base * ret, 2)
            hl = self._index_hilo.setdefault(name, [value, value])
            hl[0], hl[1] = max(hl[0], value), min(hl[1], value)
            self._emit(IndexValue(
                name=name, number=number, type_code=code, value=value, prior=base,
                high=hl[0], low=hl[1],
                advances=sum(s.price > s.ref for s in members),
                declines=sum(s.price < s.ref for s in members),
                unchanged=sum(s.price == s.ref for s in members),
                ceiling=sum(s.price >= s.ceiling for s in members),
                floor=sum(s.price <= s.floor for s in members),
                volume=sum(s.vol for s in members),
                turnover=sum(s.value for s in members),
                ts_ns=now_ns))

    def _supply_demand(self, frame_s: int, now_ns: int) -> None:
        t = now_ns // 1_000_000_000 // frame_s * frame_s
        for st in self.states.values():
            w = st.sd_window.get(frame_s)
            if not w or w == [0, 0]:
                continue
            self._emit(SupplyDemand(st, frame_s, w[0], w[1], t))
            st.sd_window[frame_s] = [0, 0]

    # -- main loop -------------------------------------------------------------
    async def run(self) -> None:
        tick = 0.02
        last_index = last_short = last_long = time.monotonic()
        log.info("market engine running: %d instruments, %.0f trades/s, market_hours=%s",
                 len(self.states), self.cfg.trades_per_sec, self.cfg.market_hours)
        while True:
            await asyncio.sleep(tick)
            if self.paused:
                continue
            now_ns = time.time_ns()
            phase = phase_at(vn_now(), self.cfg.market_hours)
            if phase != self._phase:
                self._phase = phase
                for ex in ("HOSE", "HNX", "UPCOM", "DERIVATIVES"):
                    self._emit(Session(ex, phase[0], phase[1], phase[2], now_ns))
            if not self.is_trading():
                continue

            expected = self.cfg.trades_per_sec * tick
            n = int(expected) + (1 if self.rng.random() < expected % 1 else 0)
            for sym in self.rng.choices(self._symbols, self._weights, k=n):
                self._trade(self.states[sym], now_ns)
            q = int(expected * 2) + (1 if self.rng.random() < (expected * 2) % 1 else 0)
            for sym in self.rng.choices(self._symbols, self._weights, k=q):
                self._quote_only(self.states[sym], now_ns)
            if self.rng.random() < 0.05 * tick:
                st = self.states[self.rng.choice(self._symbols[:40])]
                vol = 10_000 * self.rng.randint(1, 50)
                st.pt_vol += vol
                st.pt_acc_value += vol * st.price
                self._emit(PutThrough(st, st.price, vol, now_ns))

            mono = time.monotonic()
            if mono - last_index >= self.cfg.index_interval_s:
                last_index = mono
                self._indices(now_ns)
            if mono - last_short >= self.cfg.sd_short_s:
                last_short = mono
                self._supply_demand(self.cfg.sd_short_s, now_ns)
            if mono - last_long >= self.cfg.sd_long_s:
                last_long = mono
                self._supply_demand(self.cfg.sd_long_s, now_ns)
