"""
TCBS iFlash — REST token + the thesis (normal / derivative) and ouranos sockets.
Reference: docs/tcbs/brief/DOCUMENT.md, plus the production audit in
examples/xno-data-transformation/src/test/python/out/ (field_union.json,
distinct_report.json), which wins where the two disagree.

Faithful to the docs:
  * POST /gaia/v1/oauth2/openapi/token {apiKey, otp} -> {"token"}; 8-hour JWT, no refresh
  * auth `d|a|||<base64(token)>` -> `d|33|<timeout>` + `d|0|{"success":true,"error":null}`;
    bad token -> `d|0|{"success":false,"error":{"code":"211110","message":"Invalid JWT"}}`
  * subscribing before auth is rejected (connection closed)
  * thesis: d|s|tk|<codes>|<symbols>, d|s|ro|<codes>|<floors>, d|s|si|rt|<indices>,
    d|s|pt|ptm+ptb+pts|<floors>, d|u|... unsubscribe, d|r|tk||<symbols> -> s|38;
    every subscribe acknowledged with d|34|1; `tmh` backfills the day's matches (s|22)
  * ouranos: d|st|<codes>|<tickers>, d|ut|...; frames CODE|SYMBOL|{json}
  * heartbeat: client `d|p|||` (thesis) / `d|po` (ouranos) every 2 s; silence longer
    than the announced timeout -> close 1000. An RFC 6455 ping -> close 1002 (the
    docs' "number-one hard-to-debug failure")
  * cash prices/quantities are STRINGS, derivatives are NUMBERS

Faithful to the production audit (not in the docs):
  * covered warrants: s|18 tm, s|28 bi, s|29 op, s|30 fe, s|32 mp
  * futures foreign s|25; 10-level depth s|42, unlocked only by the `dtn` code
  * futures 21/23/24/25/27 broadcast on BOTH sockets, byte-identical, the normal
    socket ~1 ms earlier (SIM_TCBS_FUTURES_ON_BOTH)
  * ouranos announces d|33|30 (docs say 15) and pings the client with d|pi ~10 s
  * s|4 prices and s|5 high/low/open as strings (docs say numbers); C001 carries
    `highLight` and no `prevChange`

INVENTED: the s|38 snapshot body (undocumented — fields of s|4/s|5/s|6/s|1/s|2
merged), the s|42 `action` value ("U"), the s|8 `session` value ("5").
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import random
import time
from datetime import datetime

from aiohttp import WSCloseCode, web

from .config import SimConfig
from .hub import Client, Registry, Stats, ws_loop
from .market import (VN_TZ, Event, Foreign, IndexValue, MarketEngine, PutThrough, Quote,
                     SupplyDemand, SymbolState, Trade)
from .tokens import VALID, SignedTokens
from .universe import TCBS_PT_FLOOR

log = logging.getLogger(__name__)

SOURCE = "tcbs"
FEEDS = {"normal": "tcbs.stock", "derivative": "tcbs.derivative", "ouranos": "tcbs.ouranos"}

# channel code -> wire id, per instrument family and socket
CASH = {"bi": "1", "op": "2", "fe": "3", "bp": "4", "mp": "5", "tm": "6", "tmh": "22"}
CW = {"tm": "18", "bi": "28", "op": "29", "fe": "30", "mp": "32", "bp": "4"}
FUT = {"tm": "21", "bi": "23", "op": "24", "fe": "25", "mp": "27", "dtn": "42"}
FUT_BOTH = {"21", "23", "24", "25", "27"}      # also broadcast on the normal socket


def _j(obj: dict) -> str:
    return json.dumps(obj, separators=(",", ":"))


def _s(v: float) -> str:
    """TCBS cash numbers: integral VND as a string."""
    return str(int(round(v)))


class TcbsServer:
    def __init__(self, cfg: SimConfig, market: MarketEngine, stats: Stats, reg: Registry) -> None:
        self.cfg, self.market, self.stats, self.reg = cfg, market, stats, reg
        self.tokens = SignedTokens(cfg.token_secret, "eyJ")
        self.rng = random.Random(cfg.seed + 1)
        market.listen(self.on_event)

    # ------------------------------------------------------------------ REST
    async def token(self, req: web.Request) -> web.Response:
        body = await req.json()
        if body.get("apiKey") != self.cfg.tcbs_api_key or body.get("otp") != self.cfg.tcbs_otp:
            self.stats.event(SOURCE, "auth_rejected")
            return web.json_response({"code": "401", "message": "Invalid apiKey or otp"},
                                     status=401)
        tok, _ = self.tokens.issue(self.cfg.tcbs_token_ttl_s)
        self.stats.event(SOURCE, "token_issued")
        return web.json_response({"token": tok})

    # ------------------------------------------------------------- WebSocket
    def _handler(self, kind: str):
        async def handle(req: web.Request) -> web.StreamResponse:
            ws = web.WebSocketResponse(autoping=False, heartbeat=None)
            await ws.prepare(req)
            c = Client(SOURCE, FEEDS[kind], ws, self.stats, self.cfg.send_queue_max)
            c.kind = kind
            c.timeout = (self.cfg.tcbs_ouranos_timeout_s if kind == "ouranos"
                         else self.cfg.tcbs_thesis_timeout_s)
            c.sym_codes, c.floor_codes = {}, {}
            c.indices, c.pt_floors = set(), set()
            self.reg.add(c)
            self.stats.event(SOURCE, f"connections_{kind}")
            tasks = [asyncio.create_task(self._watchdog(c))]
            if kind == "ouranos":
                tasks.append(asyncio.create_task(self._server_ping(c)))
            try:
                await ws_loop(ws, lambda text: self._on_text(c, text),
                              on_rfc_ping=lambda: self._rfc_ping(c))
            finally:
                for t in tasks:
                    t.cancel()
                self.reg.remove(c)
                await c.finished()
            return ws
        return handle

    async def _rfc_ping(self, c: Client) -> None:
        self.stats.event(SOURCE, "rfc_ping_rejected")
        await c.close(WSCloseCode.PROTOCOL_ERROR, "RFC 6455 ping not allowed — use text heartbeat")

    async def _watchdog(self, c: Client) -> None:
        while True:
            await asyncio.sleep(1)
            if time.monotonic() - c.last_heartbeat > c.timeout:
                self.stats.event(SOURCE, "heartbeat_timeout")
                await c.close(WSCloseCode.OK, "heartbeat timeout")
                return

    async def _server_ping(self, c: Client) -> None:
        while True:
            await asyncio.sleep(self.cfg.tcbs_ouranos_server_ping_s)
            c.send("d|pi")

    async def _on_text(self, c: Client, text: str) -> None:
        if text.startswith("d|p"):                  # d|p||| (thesis) / d|po (ouranos)
            c.last_heartbeat = time.monotonic()
            if c.kind != "ouranos":
                c.send("d|p|||")
            return
        if text.startswith("d|a|||"):
            try:
                tok = base64.b64decode(text[6:]).decode("utf-8")
            except Exception:
                tok = ""
            if tok != self.cfg.tcbs_static_token and self.tokens.check(tok) != VALID:
                self.stats.event(SOURCE, "auth_rejected")
                c.send('d|0|{"success":false,"error":{"code":"211110","message":"Invalid JWT"}}')
                await asyncio.sleep(0.05)
                return await c.close(WSCloseCode.POLICY_VIOLATION, "invalid JWT")
            c.authed = True
            c.last_heartbeat = time.monotonic()
            c.send(f"d|33|{c.timeout}")
            c.send('d|0|{"success":true,"error":null}')
            return
        if not c.authed:
            self.stats.event(SOURCE, "subscribe_before_auth")
            return await c.close(WSCloseCode.POLICY_VIOLATION, "subscribe before auth")

        parts = text.split("|")
        if c.kind == "ouranos" and len(parts) >= 4 and parts[1] in ("st", "ut"):
            codes = set(parts[2].split("+"))
            for t in filter(None, parts[3].split(",")):
                if parts[1] == "st":
                    c.sym_codes.setdefault(t.upper(), set()).update(codes)
                else:
                    c.sym_codes.get(t.upper(), set()).difference_update(codes)
            c.send("d|34|1")
        elif c.kind != "ouranos" and len(parts) >= 5 and parts[1] in ("s", "u", "r"):
            self._thesis_command(c, parts[1], parts[2], parts[3], parts[4])

    def _thesis_command(self, c: Client, verb: str, obj: str, props: str, items: str) -> None:
        targets = [x.strip() for x in items.split(",") if x.strip()]
        codes = set(filter(None, props.split("+")))
        if verb == "r":                             # one-shot snapshot -> s|38
            for sym in targets:
                st = self.market.states.get(sym.upper())
                if st is not None:
                    self._out(c, "38", self._snapshot(st))
            return
        if obj == "tk":
            book = c.sym_codes
        elif obj == "ro":
            book = c.floor_codes
        elif obj == "si":
            (c.indices.update if verb == "s" else c.indices.difference_update)(targets)
            c.send("d|34|1")
            return
        elif obj == "pt":
            (c.pt_floors.update if verb == "s" else c.pt_floors.difference_update)(targets)
            c.send("d|34|1")
            return
        else:
            return
        for t in targets:
            key = t.upper() if obj == "tk" else t
            if verb == "s":
                book.setdefault(key, set()).update(codes)
            else:
                book.get(key, set()).difference_update(codes)
        c.send("d|34|1")
        if verb == "s":
            self._on_subscribe(c, obj, targets, codes)

    def _on_subscribe(self, c: Client, obj: str, targets: list[str], codes: set[str]) -> None:
        """Start-of-day prices (bp) and the `tmh` backfill, as a real board shows on open."""
        for st in self.market.states.values():
            hit = (st.inst.symbol in {t.upper() for t in targets}) if obj == "tk" \
                else st.inst.tcbs_floor in targets
            if not hit:
                continue
            fam = self._family(c, st)
            if fam is None:
                continue
            if "bp" in codes and "bp" in fam:
                self._out(c, fam["bp"], {"symbol": st.inst.symbol, "ceilPrice": _s(st.ceiling),
                                         "floorPrice": _s(st.floor), "refPrice": _s(st.ref)})
            if "tmh" in codes and "tmh" in fam:
                for hms, px, qty, chg in list(st.history):
                    self._out(c, "22", {"symbol": st.inst.symbol, "time": hms,
                                        "matchPrice": _s(px), "matchQtty": str(qty),
                                        "change": float(chg)})

    # ------------------------------------------------------------ routing
    def _family(self, c: Client, st: SymbolState) -> dict | None:
        """The code->wire table this socket uses for this instrument, or None."""
        kind = st.inst.kind
        if c.kind == "derivative":
            return FUT if kind == "future" else None
        if kind == "future":
            if not self.cfg.tcbs_futures_on_both:
                return None
            return {k: v for k, v in FUT.items() if v in FUT_BOTH}
        return CW if kind == "cw" else CASH

    def _wants(self, c: Client, st: SymbolState, code: str) -> bool:
        return (code in c.sym_codes.get(st.inst.symbol, ())
                or code in c.floor_codes.get(st.inst.tcbs_floor, ()))

    def _out(self, c: Client, wire: str, body: dict) -> None:
        c.send(f"s|{wire}|{_j(body)}", f"s|{wire}")

    def _fan(self, st: SymbolState, code: str, build) -> None:
        """Send one channel of one instrument to every interested thesis socket."""
        frame = None
        for c in self.reg.of(SOURCE):
            if not c.authed or c.kind == "ouranos":
                continue
            fam = self._family(c, st)
            if fam is None or code not in fam or not self._wants(c, st, code):
                continue
            wire = fam[code]
            if frame is None:
                frame = f"s|{wire}|{_j(build())}"
            if c.kind == "derivative" and wire in FUT_BOTH and self.cfg.tcbs_futures_on_both:
                c.send_later(0.001, frame, f"s|{wire}")     # the normal socket wins by ~1 ms
            else:
                c.send(frame, f"s|{wire}")

    def _ouranos(self, code: str, sym: str, body: dict) -> None:
        frame = None
        for c in self.reg.of(SOURCE):
            if c.authed and c.kind == "ouranos" and code in c.sym_codes.get(sym, ()):
                frame = frame or f"{code}|{sym}|{_j(body)}"
                c.send(frame, code)

    # ------------------------------------------------------------- shapes
    def _snapshot(self, st: SymbolState) -> dict:
        b = {"symbol": st.inst.symbol, "ceilPrice": _s(st.ceiling), "floorPrice": _s(st.floor),
             "refPrice": _s(st.ref), "matchPrice": _s(st.price), "totalVolume": str(st.vol)}
        for i in range(3):
            b[f"bidPrice0{i + 1}"], b[f"bidQtty0{i + 1}"] = _s(st.bids[i][0]), str(int(st.bids[i][1]))
            b[f"offerPrice0{i + 1}"], b[f"offerQtty0{i + 1}"] = _s(st.asks[i][0]), str(int(st.asks[i][1]))
        return b

    def _top3(self, st: SymbolState, side: str) -> dict:
        levels = st.bids if side == "bid" else st.asks
        name, qn = ("bidPrice", "bidQtty") if side == "bid" else ("offerPrice", "offerQtty")
        body: dict = {"symbol": st.inst.symbol}
        fut = st.inst.kind == "future"
        for i, (p, q) in enumerate(levels[:3]):
            # "Field null does not appear in JSON": a thin book drops its outer levels.
            if q <= 0 or (i == 2 and self.rng.random() < 0.03):
                continue
            body[f"{name}0{i + 1}"] = p if fut else _s(p)
            body[f"{qn}0{i + 1}"] = float(q) if fut else str(int(q))
        return body

    def on_event(self, e: Event) -> None:
        if isinstance(e, Trade):
            self._trade(e)
        elif isinstance(e, Quote):
            st = e.st
            if any(i < 3 for i in e.changed):
                self._fan(st, "bi", lambda: self._top3(st, "bid"))
                self._fan(st, "op", lambda: self._top3(st, "ask"))
            if st.inst.kind == "future":
                cum_b = cum_a = 0.0
                for i in range(10):
                    cum_b += st.bids[i][1]
                    cum_a += st.asks[i][1]
                    if i in e.changed:
                        self._fan(st, "dtn", lambda i=i, cb=cum_b, ca=cum_a: {
                            "symbol": st.inst.symbol, "top": i + 1, "action": "U",
                            "bidPrice": st.bids[i][0], "bidQty": float(st.bids[i][1]),
                            "bidMatchedQty": 0.0, "bidCumulativeQty": cb,
                            "offerPrice": st.asks[i][0], "offerQty": float(st.asks[i][1]),
                            "offerMatchedQty": 0.0, "offerCumulativeQty": ca})
        elif isinstance(e, Foreign):
            st = e.st
            self._fan(st, "fe", lambda: {"symbol": st.inst.symbol,
                                         "buyForeignQtty": str(st.foreign_buy),
                                         "sellForeignQtty": str(st.foreign_sell),
                                         "room": str(st.room_left)})
        elif isinstance(e, IndexValue):
            body = {"indexNumber": e.number, "index": e.value,
                    "change": round(e.value - e.prior, 2),
                    "changePercent": round((e.value - e.prior) / e.prior * 100, 2),
                    "volume": float(e.volume), "value": float(e.turnover),
                    "increase": e.advances, "decrease": e.declines, "notChange": e.unchanged,
                    "session": "5", "ceilIncrease": e.ceiling, "floorDecrease": e.floor}
            for c in self.reg.of(SOURCE):
                if c.authed and c.kind == "normal" and str(e.number) in c.indices:
                    self._out(c, "8", body)
        elif isinstance(e, PutThrough):
            st = e.st
            floor = TCBS_PT_FLOOR.get(st.inst.exchange)
            body = {"symbol": st.inst.symbol, "price": float(e.price), "vol": float(e.vol),
                    "val": float(e.price * e.vol),
                    "time": datetime.fromtimestamp(e.ts_ns / 1e9, VN_TZ).strftime("%H:%M:%S"),
                    "color": 4, "accumulatedValue": float(st.pt_acc_value)}
            for c in self.reg.of(SOURCE):
                if c.authed and c.kind == "normal" and floor in c.pt_floors:
                    self._out(c, "17", body)
        elif isinstance(e, SupplyDemand):
            st = e.st
            code = "C002S60" if e.frame_s == self.cfg.sd_short_s else "C002S900"
            total = st.buy_up_acc + st.sell_down_acc
            self._ouranos(code, st.inst.symbol, {
                "symbol": st.inst.symbol, "timeSec": str(e.time_s),
                "totalBUVol": float(e.buy_up), "totalBUVolAcc": float(st.buy_up_acc),
                "totalSDVol": float(e.sell_down), "totalSDVolAcc": float(st.sell_down_acc),
                "bsAccRatio": round(st.buy_up_acc / total, 7) if total else 0.0,
                "unitTimeFrame": "60" if code == "C002S60" else "900"})

    def _trade(self, e: Trade) -> None:
        st = e.st
        sym, kind = st.inst.symbol, st.inst.kind
        if kind == "future":
            self._fan(st, "tm", lambda: {"symbol": sym, "matchPrice": e.price,
                                         "matchQtty": float(e.qty), "change": st.change,
                                         "changePercent": round(st.change_pct, 2),
                                         "totalVolume": float(st.vol)})
        else:
            body = {"symbol": sym, "matchPrice": _s(e.price), "matchQtty": str(e.qty),
                    "change": float(st.change), "changePercent": st.change_pct,
                    "totalVolume": str(st.vol), "totalValue": _s(st.value)}
            if kind == "cw":
                body.update(bep=float(round(e.price * 1.05)), tradingVolRatio=1.0)
            self._fan(st, "tm", lambda: body)
            self._fan(st, "tmh", lambda: {"symbol": sym, "time": st.history[-1][0],
                                          "matchPrice": _s(e.price), "matchQtty": str(e.qty),
                                          "change": float(st.change)})
        # Session stats (s|5 / s|32 / s|27): only when the day's range moves, or rarely.
        if e.price in (st.high, st.low) or self.rng.random() < 0.02:
            if kind == "future":
                self._fan(st, "mp", lambda: {"symbol": sym, "high": st.high, "low": st.low,
                                             "avg": st.avg, "open": st.open})
            else:
                body = {"symbol": sym, "high": _s(st.high), "low": _s(st.low),
                        "avg": float(st.avg), "open": _s(st.open)}
                if kind == "cw":
                    body.update(highestFromListing=_s(st.ceiling), lowestFromListing=_s(st.floor))
                self._fan(st, "mp", lambda: body)
        # Foreign flow for futures (s|25, numbers) and warrants (s|30, strings, foreignNet).
        if kind == "future" and self.rng.random() < 0.01:
            self._fan(st, "fe", lambda: {"symbol": sym, "buyForeignQtty": float(e.qty),
                                         "sellForeignQtty": 0.0})
        elif kind == "cw" and self.rng.random() < 0.07:
            self._fan(st, "fe", lambda: {"symbol": sym, "buyForeignQtty": str(e.qty),
                                         "foreignNet": str(e.qty), "sellForeignQtty": "0"})
        if kind != "future":
            self._ouranos("C001", sym, {
                "symbol": sym, "closePrice": float(e.price), "closeVol": float(e.qty),
                "change": float(st.change), "reference": float(st.ref),
                "totalTrading": float(st.vol), "totalTradingValue": float(st.value),
                "timeSec": str(e.ts_ns // 1_000_000_000),
                "action": "BU" if e.side == "B" else "SD", "unitTimeFrame": "60",
                "tradingValue": float(e.price * e.qty), "buyUpAcc": float(st.buy_up_acc),
                "sellDownAcc": float(st.sell_down_acc), "bidPrice": float(st.bids[0][0]),
                "bidVol": float(st.bids[0][1]), "askPrice": float(st.asks[0][0]),
                "askVol": float(st.asks[0][1]), "highLight": e.qty >= 10_000})

    def app(self) -> web.Application:
        app = web.Application()
        app.router.add_post("/gaia/v1/oauth2/openapi/token", self.token)
        app.router.add_get("/ws/thesis/v1/stream/normal", self._handler("normal"))
        app.router.add_get("/ws/thesis/v1/stream/derivative", self._handler("derivative"))
        app.router.add_get("/ws/ouranos/v1/stream", self._handler("ouranos"))
        return app
