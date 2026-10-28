"""
DNSE LightSpeed — wss://ws-openapi.dnse.com.vn/v1/stream?encoding=json|msgpack
Reference: docs/dnse/brief/DOCUMENT.md

Faithful to the docs:
  * welcome {action, session_id, timestamp, message} on connect
  * auth {action:auth, api_key, signature, timestamp, nonce}; the server RECOMPUTES
    HMAC-SHA256(api_secret, "{api_key}:{timestamp}:{nonce}"), enforces the +/-5 min
    window, rejects a nonce reused within 10 min, and AUTH_TIMEOUT after 30 s.
    Failure = {action:error, code:AUTH_FAILED, message} then close.
  * auth_success carries rate_limit {messages_per_second, subscriptions_max}
  * subscribe {channels:[{name, symbols}]} -> {action:subscribed}
  * server ping every 3 min (timestamp in ms), pong deadline 60 s, close 1008;
    a client ping gets a pong whose timestamp is in SECONDS
  * 8-hour limit: connection_expired {code:MAX_DURATION_EXCEEDED} then close 1008
  * a consumer whose queue overflows is closed with 1013 (backpressure)
  * payload shapes per section 6, including the documented inconsistencies:
    {Seconds,Nanos} on most channels, transactTime {Seconds,Nanos} on market_index,
    a string time on estimated_market_index and session, transactTime "HHMMSSmmm"
    on foreign, epoch-second integer on OHLC, futures OHLC under the symbolType
    (VN30F1M) with "volume" as a STRING, fluctuationLowerLimitIssueCount null

INVENTED where the docs are silent:
  * `T` on data messages (11.1) — absent by default, SIM_DNSE_SEND_T=1 adds the
    channel function name; estimated_market_index carries `action` as the docs warn
  * error codes NOT_AUTHENTICATED / SUBSCRIPTION_LIMIT_EXCEEDED / BAD_CHANNEL;
    subscriptions counted per channel (11.6 leaves it open)
  * expected_price stays silent (the simulator never runs ATO/ATC auctions);
    OHLC resolutions other than "1" are accepted but silent
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timezone

import msgpack
from aiohttp import WSCloseCode, web

from .config import SimConfig
from .hub import Client, Registry, Stats, ws_loop
from .market import (VN_TZ, Bar, Event, Foreign, IndexValue, MarketEngine, Quote, Session,
                     SymbolState, Trade)
from .universe import DNSE_MARKET_ID, HOSE

log = logging.getLogger(__name__)

SOURCE, FEED = "dnse", "dnse.market"
CHANNEL_FUNCS = ("tick", "tick_extra", "top_price", "expected_price", "security_definition",
                 "ohlc", "ohlc_closed", "market_index", "estimated_market_index", "foreign",
                 "session")
FUTURE_TYPE = {0: "VN30F1M", 1: "VN30F2M", 2: "VN30F1Q"}


def _ts(ts_ns: int) -> dict:
    return {"Seconds": ts_ns // 1_000_000_000, "Nanos": ts_ns % 1_000_000_000}


class DnseServer:
    def __init__(self, cfg: SimConfig, market: MarketEngine, stats: Stats, reg: Registry) -> None:
        self.cfg, self.market, self.stats, self.reg = cfg, market, stats, reg
        self._nonces: dict[str, float] = {}
        self._session_seq = int(time.time() * 1e6)
        futures = [s for s in market.states.values() if s.inst.kind == "future"]
        self._symbol_type = {s.inst.symbol: FUTURE_TYPE.get(i, s.inst.symbol)
                             for i, s in enumerate(futures)}
        market.listen(self.on_event)

    # -------------------------------------------------------------- encoding
    def _send(self, c: Client, obj: dict, wire: str | None = None) -> None:
        if c.encoding == "msgpack":
            c.send(msgpack.packb(obj, use_bin_type=True), wire)
        else:
            c.send(json.dumps(obj, separators=(",", ":")), wire)

    def _decode(self, c: Client, text: str) -> dict | None:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    # ------------------------------------------------------------- WebSocket
    async def stream(self, req: web.Request) -> web.StreamResponse:
        encoding = req.query.get("encoding", "json")
        if encoding not in ("json", "msgpack"):
            return web.json_response({"code": "BAD_ENCODING"}, status=400)
        ws = web.WebSocketResponse(autoping=False, heartbeat=None)
        await ws.prepare(req)
        c = Client(SOURCE, FEED, ws, self.stats, self.cfg.send_queue_max)
        c.encoding = encoding
        c.subs = {}
        c.pending_ping = None            # ms timestamp of an unanswered server ping
        self._session_seq += 1
        self._send(c, {"action": "welcome", "session_id": f"conn_{self._session_seq}",
                       "timestamp": int(time.time()),
                       "message": "Please authenticate within 30 seconds"})
        self.reg.add(c)
        self.stats.event(SOURCE, "connections")
        tasks = [asyncio.create_task(self._auth_deadline(c)),
                 asyncio.create_task(self._pinger(c)),
                 asyncio.create_task(self._lifetime(c))]
        try:
            await ws_loop(ws, lambda text: self._on_text(c, text))
        finally:
            for t in tasks:
                t.cancel()
            self.reg.remove(c)
            await c.finished()
        return ws

    async def _auth_deadline(self, c: Client) -> None:
        await asyncio.sleep(self.cfg.dnse_auth_deadline_s)
        if not c.authed:
            self._send(c, {"action": "error", "code": "AUTH_TIMEOUT",
                           "message": "authentication timeout"})
            await asyncio.sleep(0.05)
            await c.close(WSCloseCode.POLICY_VIOLATION, "auth timeout")

    async def _pinger(self, c: Client) -> None:
        while True:
            await asyncio.sleep(self.cfg.dnse_ping_s)
            ts = int(time.time() * 1000)
            c.pending_ping = ts
            self._send(c, {"action": "ping", "timestamp": ts})
            await asyncio.sleep(self.cfg.dnse_pong_deadline_s)
            if c.pending_ping == ts:
                await c.close(WSCloseCode.POLICY_VIOLATION, "pong timeout")
                return

    async def _lifetime(self, c: Client) -> None:
        await asyncio.sleep(self.cfg.dnse_max_conn_s)
        self._send(c, {"action": "connection_expired", "code": "MAX_DURATION_EXCEEDED",
                       "message": "Connection expired after 8 hours. Please reconnect."})
        await asyncio.sleep(0.05)
        await c.close(WSCloseCode.POLICY_VIOLATION, "max duration")

    def _verify(self, msg: dict) -> str | None:
        """None when the auth message is valid, else the reason."""
        now = time.time()
        if msg.get("api_key") != self.cfg.dnse_api_key:
            return "invalid api_key"
        ts = msg.get("timestamp")
        if not isinstance(ts, int) or abs(now - ts) > 300:
            return "timestamp outside valid window"
        nonce = str(msg.get("nonce", ""))
        self._nonces = {n: t for n, t in self._nonces.items() if now - t < 600}
        if not nonce or nonce in self._nonces:
            return "nonce already used"
        expect = hmac.new(self.cfg.dnse_api_secret.encode(),
                          f"{msg['api_key']}:{ts}:{nonce}".encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expect, str(msg.get("signature", ""))):
            return "invalid signature"
        self._nonces[nonce] = now
        return None

    async def _on_text(self, c: Client, text: str) -> None:
        msg = self._decode(c, text)
        if not isinstance(msg, dict):
            return
        action = msg.get("action")
        if action == "pong":
            c.pending_ping = None
            return
        if action == "ping":
            self._send(c, {"action": "pong", "timestamp": int(time.time())})
            return
        if action == "auth":
            reason = self._verify(msg)
            if reason:
                self.stats.event(SOURCE, "auth_rejected")
                self._send(c, {"action": "error", "code": "AUTH_FAILED",
                               "message": f"authentication failed: {reason}"})
                await asyncio.sleep(0.05)
                return await c.close(WSCloseCode.POLICY_VIOLATION, "auth failed")
            c.authed = True
            self._send(c, {"action": "auth_success", "user_id": msg["api_key"],
                           "capabilities": {"batch_delivery": False},
                           "rate_limit": {"messages_per_second": 100,
                                          "subscriptions_max": self.cfg.dnse_subscriptions_max}})
            return
        if not c.authed:
            self._send(c, {"action": "error", "code": "NOT_AUTHENTICATED",
                           "message": "authenticate before subscribing"})
            return
        if action == "subscribe":
            self._subscribe(c, msg.get("channels") or [])
        elif action == "unsubscribe":
            for ch in msg.get("channels") or []:
                c.subs.pop(ch.get("name"), None)
            self._send(c, {"action": "unsubscribed"})

    # -------------------------------------------------------- subscriptions
    def _subscribe(self, c: Client, channels: list[dict]) -> None:
        added = []
        for ch in channels:
            name = str(ch.get("name", ""))
            parts = name.split(".")
            if len(parts) < 3 or parts[0] not in CHANNEL_FUNCS or parts[-1] != c.encoding:
                self._send(c, {"action": "error", "code": "BAD_CHANNEL",
                               "message": f"unknown channel {name}"})
                continue
            syms = [s for s in ch.get("symbols") or []]
            if any(s != s.upper() for s in syms):
                self._send(c, {"action": "error", "code": "BAD_CHANNEL",
                               "message": "symbols must be UPPERCASE"})
                continue
            c.subs[name] = (parts[0], parts[1:-1], set(syms) or None)
            added.append(name)
        if len(c.subs) > self.cfg.dnse_subscriptions_max:
            self._send(c, {"action": "error", "code": "SUBSCRIPTION_LIMIT_EXCEEDED",
                           "message": f"max {self.cfg.dnse_subscriptions_max} subscriptions"})
        self._send(c, {"action": "subscribed"})
        for name in added:
            func, scope, syms = c.subs[name]
            if func == "security_definition":
                for st in self.market.states.values():
                    if syms is None or st.inst.symbol in syms:
                        self._send(c, self._data("security_definition", self._secdef(st)),
                                   self._wire("security_definition"))
            elif func == "session":
                ph = self.market.phase
                self._send(c, self._data("session", self._session(
                    Session(HOSE, ph[0], ph[1], ph[2], time.time_ns()), scope)), self._wire("session"))

    def _targets(self, func: str, key: str | None, symbol: str | None):
        for c in self.reg.of(SOURCE):
            if not c.authed:
                continue
            for f, scope, syms in c.subs.values():
                if f != func:
                    continue
                if key is not None and key not in scope:
                    continue
                if symbol is not None and syms is not None and symbol not in syms:
                    continue
                yield c
                break

    def _data(self, func: str, body: dict) -> dict:
        if self.cfg.dnse_send_t:
            body = {"T": func, **body}
        return body

    def _wire(self, func: str) -> str:
        """What ingestion will tag the frame with: `T`, or 'unknown' when absent."""
        return func if self.cfg.dnse_send_t else "unknown"

    def _fan(self, func: str, key: str | None, symbol: str | None, body: dict) -> None:
        msg = self._data(func, body)
        for c in self._targets(func, key, symbol):
            self._send(c, msg, self._wire(func))

    # ---------------------------------------------------------------- shapes
    @staticmethod
    def _px(st: SymbolState, v: float) -> float:
        """Equities in THOUSAND VND as numbers (24.35); futures in index points."""
        return round(v, 1) if st.inst.kind == "future" else round(v / 1000, 2)

    def _head(self, st: SymbolState) -> dict:
        return {"marketId": DNSE_MARKET_ID[st.inst.exchange], "boardId": "G1",
                "isin": st.inst.isin, "symbol": st.inst.symbol}

    def _secdef(self, st: SymbolState) -> dict:
        fut = st.inst.kind == "future"
        return {**self._head(st),
                "productGrpId": "FIO" if fut else DNSE_MARKET_ID[st.inst.exchange],
                "securityGroupId": "FU" if fut else "EW" if st.inst.kind == "cw" else "ST",
                "basicPrice": self._px(st, st.ref), "ceilingPrice": self._px(st, st.ceiling),
                "floorPrice": self._px(st, st.floor),
                **({"openInterestQuantity": 24473} if fut else {}),
                "securityStatus": "NO_HALT", "symbolAdminStatusCode": "NRM",
                "symbolTradingMethodStatusCode": "NRM", "symbolTradingSanctionStatusCode": "NRM",
                "listingDate": 20260223, "time": _ts(time.time_ns())}

    def _session(self, e: Session, scope) -> dict:
        return {"marketId": "DVX" if e.exchange == "DERIVATIVES" else "STO", "boardId": "G1",
                "eventId": e.event_id, "tradingSessionId": e.session_id,
                "tscProdGrpId": scope[0] if scope else "STO",
                "time": datetime.fromtimestamp(e.ts_ns / 1e9, timezone.utc)
                        .strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"}

    def on_event(self, e: Event) -> None:
        if isinstance(e, Trade):
            st = e.st
            fut = st.inst.kind == "future"
            body = {**self._head(st), "matchPrice": self._px(st, e.price),
                    # documented: integer on equities, float on futures
                    "matchQtty": float(e.qty) if fut else e.qty,
                    "totalVolumeTraded": st.vol,
                    "grossTradeAmount": round(st.value / 1e9, 5),
                    "highestPrice": self._px(st, st.high), "lowestPrice": self._px(st, st.low),
                    "openPrice": self._px(st, st.open),
                    "tradingSessionId": self.market.phase[1], "time": _ts(e.ts_ns)}
            self._fan("tick", "G1", st.inst.symbol, body)
            self._fan("tick_extra", "G1", st.inst.symbol,
                      {**body, "side": "BUY" if e.side == "B" else "SELL",
                       "avgPrice": self._px(st, st.avg)})
        elif isinstance(e, Quote):
            st = e.st
            n = 10 if st.inst.exchange in ("HNX", "UPCOM") else 3
            self._fan("top_price", "G1", st.inst.symbol, {
                **self._head(st),
                "bid": [{"price": self._px(st, p), "quantity": float(q)} for p, q in st.bids[:n]],
                "offer": [{"price": self._px(st, p), "quantity": float(q)} for p, q in st.asks[:n]],
                "totalOfferQtty": float(sum(q for _, q in st.asks)),
                "totalBidQtty": float(sum(q for _, q in st.bids)),
                "time": _ts(e.ts_ns)})
        elif isinstance(e, Foreign):
            st = e.st
            utc = datetime.fromtimestamp(e.ts_ns / 1e9, timezone.utc)
            self._fan("foreign", "G1", st.inst.symbol, {
                "marketId": DNSE_MARKET_ID[st.inst.exchange], "boardId": "G1",
                "tradingSessionId": self.market.phase[1], "symbol": st.inst.symbol,
                "transactTime": utc.strftime("%H%M%S") + f"{utc.microsecond // 1000:03d}",
                "foreignInvestorTypeCode": "10",
                "sellVolume": st.foreign_sell, "sellTradedAmount": int(st.foreign_sell_val),
                "buyVolume": st.foreign_buy, "buyTradedAmount": int(st.foreign_buy_val),
                "totalSellVolume": st.foreign_sell, "totalSellTradedAmount": int(st.foreign_sell_val),
                "totalBuyVolume": st.foreign_buy, "totalBuyTradedAmount": int(st.foreign_buy_val),
                "foreignerOrderLimitQuantity": st.room_total,
                "foreignerBuyPossibleQuantity": st.room_left})
        elif isinstance(e, Bar):
            st = e.st
            fut = st.inst.kind == "future"
            sym = self._symbol_type[st.inst.symbol] if fut else st.inst.symbol
            body = {"time": e.start_s, "open": self._px(st, e.o), "high": self._px(st, e.h),
                    "low": self._px(st, e.l), "close": self._px(st, e.c),
                    "volume": str(e.v) if fut else e.v, "symbol": sym, "resolution": "1",
                    "lastUpdated": int(time.time()), "type": "DERIVATIVE" if fut else "STOCK"}
            self._fan("ohlc_closed" if e.closed else "ohlc", "1", sym, body)
        elif isinstance(e, IndexValue):
            turnover_bn = round(e.turnover / 1e9, 8)
            self._fan("market_index", e.name, None, {
                "indexName": e.name, "valueIndexes": e.value, "priorValueIndexes": e.prior,
                "changedValue": round(e.value - e.prior, 2),
                "changedRatio": round((e.value - e.prior) / e.prior * 100, 2),
                "highestValueIndexes": e.high, "lowestValueIndexes": e.low,
                "fluctuationUpIssueCount": e.advances, "fluctuationDownIssueCount": e.declines,
                "fluctuationSteadinessIssueCount": e.unchanged,
                "fluctuationUpperLimitIssueCount": e.ceiling,
                # The documentation's own example has null here.
                "fluctuationLowerLimitIssueCount": e.floor or None,
                "grossTradeAmount": turnover_bn, "totalVolumeTraded": e.volume,
                "currencyCode": "VND", "indexTypeCode": e.type_code, "marketIndexClass": 1,
                "marketId": "STX" if e.name.startswith("HNX") else "UPX" if e.name == "UPCOM" else "STO",
                "tradingSessionId": self.market.phase[1], "transactTime": _ts(e.ts_ns)})
            if e.name == "VN30":
                vn = datetime.fromtimestamp(e.ts_ns / 1e9, VN_TZ)
                self._fan("estimated_market_index", "VN30", None, {
                    # The docs warn this data message carries `action` as well as `T`.
                    "action": "estimated_market_index",
                    "indexName": "VN30", "valueIndexes": e.value,
                    "changedValue": round(e.value - e.prior, 2),
                    "changedRatio": round((e.value - e.prior) / e.prior * 100, 2),
                    "fluctuationUpIssueCount": e.advances, "fluctuationDownIssueCount": e.declines,
                    "fluctuationSteadinessIssueCount": e.unchanged,
                    "grossTradeAmount": round(turnover_bn, 2), "totalVolumeTraded": e.volume,
                    "time": vn.strftime("%Y-%m-%d %H:%M:%S.") + f"{vn.microsecond // 1000:03d}"})
        elif isinstance(e, Session):
            for c in self.reg.of(SOURCE):
                for f, scope, _ in list(c.subs.values()):
                    if f == "session" and c.authed:
                        self._send(c, self._data("session", self._session(e, scope)),
                                   self._wire("session"))
                        break

    def app(self) -> web.Application:
        app = web.Application()
        app.router.add_get("/v1/stream", self.stream)
        return app
