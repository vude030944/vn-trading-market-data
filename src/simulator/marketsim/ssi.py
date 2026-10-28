"""
SSI FastConnect — REST token endpoints + the DATA WebSocket channel.
Reference: docs/ssi/brief/DOCUMENT.md

Faithful to the docs:
  * POST /api/v3/auth/token {apiKey, apiSecret[, otp]} -> {tokenType, accessToken,
    refreshToken, expiresAt, refreshExpiresAt}; /api/v3/auth/refresh {refreshToken}
  * Stream served on BOTH documented endpoints, `/` and `/ws/v3` (10.1)
  * {"method":"SUBSCRIBE|UNSUBSCRIBE|LIST_SUBSCRIPTION|PING|PONG", "channel", "topics"}
  * Topic grammar <prefix>.<scope>[@tick|1m|5m]; scope = * | SYM | SYM-SYM | vn30 | hose...
  * Data {"channel":"DATA","topic":...,"data":{abbreviated fields, numbers as STRINGS}}
  * Server PING {"method":"PING","channel":"HEARTBEAT","time":"dd-mm-yyyy hh-mm-ss"};
    a client that stops answering PONG is closed
  * market topic: two shapes — start-of-day (s,b,t,ce,fl,ref) and session flag (b,t,f)

INVENTED where the docs are silent (10.3, 10.7):
  * how the token reaches the socket: query `access_token`, `Authorization: Bearer`,
    or a first frame {"method":"AUTH","access_token":...} — SIM_SSI_AUTH_MODE picks
    one, `any` accepts all three
  * the reply to a frame auth: {"method":"AUTH","status":"success","connectionId":...}
  * the PONG deadline (SIM_SSI_PONG_DEADLINE_S); errors on the socket as
    {"method":...,"status":"error","code":<REST error code>,"message":...}
"""

from __future__ import annotations

import asyncio
import json
import logging
import secrets
import time
from datetime import datetime

from aiohttp import WSCloseCode, web

from .config import SimConfig
from .hub import Client, Registry, Stats, ws_loop
from .tokens import EXPIRED, VALID, SignedTokens
from .market import (VN_TZ, Bar, Event, Foreign, MarketEngine, Oddlot, PutThrough, Quote,
                     Session, Trade)
from .universe import VN30

log = logging.getLogger(__name__)

SOURCE, FEED = "ssi", "ssi.market"
PREFIXES = ("trade", "quote", "room", "put", "oddlot", "market")


def _t(ts_ns: int) -> str:
    return datetime.fromtimestamp(ts_ns / 1e9, VN_TZ).strftime("%Y/%m/%d %H:%M:%S")


def _k(vnd: float) -> str:
    """SSI quotes equities in THOUSAND VND, as a string: 45500 -> "45.50"."""
    return f"{vnd / 1000:.2f}"


class SsiServer:
    def __init__(self, cfg: SimConfig, market: MarketEngine, stats: Stats, reg: Registry) -> None:
        self.cfg, self.market, self.stats, self.reg = cfg, market, stats, reg
        self.tokens = SignedTokens(cfg.token_secret, "ssi-")
        self.refresh = SignedTokens(cfg.token_secret, "ssir-")
        self._agg5: dict[str, list] = {}            # symbol -> 5-minute bar being built
        market.listen(self.on_event)

    # ------------------------------------------------------------------ REST
    def _issue(self) -> dict:
        access, exp = self.tokens.issue(self.cfg.ssi_token_ttl_s)
        refresh, rexp = self.refresh.issue(7 * 86400)
        scale = 1000 if self.cfg.ssi_expires_unit == "ms" else 1
        return {"tokenType": "Bearer", "accessToken": access, "refreshToken": refresh,
                "expiresAt": int(exp * scale), "refreshExpiresAt": int(rexp * scale)}

    async def token(self, req: web.Request) -> web.Response:
        body = await req.json()
        if not body.get("apiKey"):
            return web.json_response({"code": 400, "msg": "apiKey is required"}, status=400)
        if body.get("apiKey") != self.cfg.ssi_api_key or body.get("apiSecret") != self.cfg.ssi_api_secret:
            self.stats.event(SOURCE, "auth_rejected")
            return web.json_response({"code": 401105, "msg": "Invalid API Key or Secret"}, status=401)
        self.stats.event(SOURCE, "token_issued")
        return web.json_response(self._issue())

    async def do_refresh(self, req: web.Request) -> web.Response:
        body = await req.json()
        rt = body.get("refreshToken", "")
        if self.refresh.check(rt) != VALID:
            return web.json_response({"code": 401103, "msg": "Refresh Token Revoked or Expired"},
                                     status=401)
        self.stats.event(SOURCE, "token_refreshed")
        return web.json_response(self._issue())

    def _check(self, token: str | None) -> int | None:
        """None = valid, else the documented 401xxx code."""
        if not token:
            return 401002
        state = self.tokens.check(token)
        if state == VALID:
            return None
        return 401004 if state == EXPIRED else 401003

    # ------------------------------------------------------------- WebSocket
    async def stream(self, req: web.Request) -> web.StreamResponse:
        mode = self.cfg.ssi_auth_mode
        token = None
        if mode in ("any", "query"):
            token = req.query.get("access_token")
        if not token and mode in ("any", "header"):
            h = req.headers.get("Authorization", "")
            token = h[7:] if h.startswith("Bearer ") else None
        if token or mode in ("query", "header"):
            code = self._check(token)
            if code is not None:
                self.stats.event(SOURCE, f"upgrade_rejected_{code}")
                return web.json_response({"code": code, "msg": "unauthorized"}, status=401)

        ws = web.WebSocketResponse(autoping=False, heartbeat=None)
        await ws.prepare(req)
        c = Client(SOURCE, FEED, ws, self.stats, self.cfg.send_queue_max)
        c.authed = token is not None
        c.subs = {}
        c.last_pong = time.monotonic()
        self.reg.add(c)
        self.stats.event(SOURCE, "connections")
        pinger = asyncio.create_task(self._pinger(c))
        try:
            await ws_loop(ws, lambda text: self._on_text(c, text))
        finally:
            pinger.cancel()
            self.reg.remove(c)
            await c.finished()
        return ws

    async def _pinger(self, c: Client) -> None:
        while True:
            await asyncio.sleep(self.cfg.ssi_ping_s)
            if time.monotonic() - c.last_pong > self.cfg.ssi_ping_s + self.cfg.ssi_pong_deadline_s:
                await c.close(WSCloseCode.POLICY_VIOLATION, "heartbeat timeout")
                return
            c.send(json.dumps({"method": "PING", "channel": "HEARTBEAT",
                               "time": datetime.now(VN_TZ).strftime("%d-%m-%Y %H-%M-%S")}))

    def _err(self, c: Client, method: str, code: int, message: str) -> None:
        c.send(json.dumps({"method": method, "status": "error", "code": code, "message": message}))

    async def _on_text(self, c: Client, text: str) -> None:
        try:
            msg = json.loads(text)
        except json.JSONDecodeError:
            return self._err(c, "", 400, "message is not JSON")
        method = msg.get("method")
        if method == "PONG":
            c.last_pong = time.monotonic()
            return
        if method == "PING":
            c.last_pong = time.monotonic()
            c.send(json.dumps({"method": "PONG", "channel": "HEARTBEAT", "time": msg.get("time")}))
            return
        if method == "AUTH":
            if self.cfg.ssi_auth_mode not in ("any", "frame"):
                return self._err(c, "AUTH", 400, "frame auth not enabled")
            code = self._check(msg.get("access_token"))
            if code is not None:
                c.send(json.dumps({"method": "AUTH", "status": "error", "code": code}))
                return await c.close(WSCloseCode.POLICY_VIOLATION, "auth failed")
            c.authed = True
            c.send(json.dumps({"method": "AUTH", "status": "success",
                               "connectionId": "ssi-" + secrets.token_hex(6)}))
            return
        if not c.authed:
            return self._err(c, method or "", 401002, "Access Token Missing")
        if method == "SUBSCRIBE" and msg.get("channel") == "DATA":
            for t in msg.get("topics", []):
                self._subscribe(c, t)
        elif method == "UNSUBSCRIBE":
            for t in msg.get("topics", []):
                c.subs.pop(t, None)
        elif method == "LIST_SUBSCRIPTION":
            c.send(json.dumps({"trading": "", "data": ";".join(c.subs)}))

    # -------------------------------------------------------- subscriptions
    def _scope(self, scope: str) -> set[str] | None:
        """None = everything; else the set of symbols the scope resolves to."""
        s = scope.lower()
        if s == "*":
            return None
        if s == "vn30":
            return set(VN30)
        if s in ("hose", "hnx", "upcom"):
            return {st.inst.symbol for st in self.market.states.values()
                    if st.inst.exchange.lower() == s and st.inst.kind != "future"}
        return {x.upper() for x in scope.split("-") if x}

    def _subscribe(self, c: Client, topic: str) -> None:
        head, _, interval = topic.partition("@")
        prefix, _, scope = head.partition(".")
        if prefix not in PREFIXES or (interval and interval not in ("tick", "1m", "5m")):
            return self._err(c, "SUBSCRIBE", 400, f"invalid topic {topic}")
        c.subs[topic] = (prefix, interval or ("" if prefix == "market" else "tick"),
                         self._scope(scope or "*"))
        if prefix == "market":
            self._start_of_day(c, c.subs[topic][2])

    def _wants(self, c: Client, prefix: str, interval: str, symbol: str | None) -> bool:
        for p, iv, syms in c.subs.values():
            if p == prefix and iv == interval and (syms is None or symbol is None or symbol in syms):
                return True
        return False

    def _start_of_day(self, c: Client, syms: set[str] | None) -> None:
        now_ns = time.time_ns()
        day = datetime.fromtimestamp(now_ns / 1e9, VN_TZ).strftime("%Y/%m/%d")
        for st in self.market.states.values():
            if st.inst.kind == "future" or (syms is not None and st.inst.symbol not in syms):
                continue
            self._data(c, f"market.{st.inst.symbol}", "market", {
                "s": st.inst.symbol, "b": st.inst.exchange, "t": day,
                "ce": _k(st.ceiling), "fl": _k(st.floor), "ref": _k(st.ref)})
        flag = self.market.phase[0]
        for board in ("HOSE", "HNX", "UPCOM", "DERIVATIVES"):
            self._data(c, f"market.{board}", "market",
                       {"b": board, "t": _t(now_ns), "f": flag})

    # ----------------------------------------------------------------- data
    def _data(self, c: Client, topic: str, wire: str, data: dict) -> None:
        c.send(json.dumps({"channel": "DATA", "topic": topic, "data": data},
                          separators=(",", ":")), wire)

    def _fan(self, prefix: str, interval: str, symbol: str | None, topic: str, wire: str,
             data: dict) -> None:
        for c in self.reg.of(SOURCE):
            if c.authed and self._wants(c, prefix, interval, symbol):
                self._data(c, topic, wire, data)

    @staticmethod
    def _book(levels, n: int = 5) -> list[list[str]]:
        return [[_k(p), str(int(q))] for p, q in levels[:n] if q > 0]

    def on_event(self, e: Event) -> None:
        st = getattr(e, "st", None)
        if st is not None and st.inst.kind == "future":
            return                       # the DATA channel here carries equities only
        sym = st.inst.symbol if st is not None else None
        if isinstance(e, Trade):
            self._fan("trade", "tick", sym, f"trade.{sym}", "trade_tick", {
                "s": sym, "t": _t(e.ts_ns), "p": _k(e.price), "q": str(e.qty),
                "a": _k(st.avg), "si": e.side, "o": _k(st.open), "h": _k(st.high),
                "l": _k(st.low), "v": str(st.vol)})
        elif isinstance(e, Quote):
            self._fan("quote", "tick", sym, f"quote.{sym}", "quote_tick", {
                "s": sym, "t": _t(e.ts_ns), "bids": self._book(st.bids), "asks": self._book(st.asks)})
        elif isinstance(e, Foreign):
            self._fan("room", "tick", sym, f"room.{sym}", "room_tick", {
                "s": sym, "t": _t(e.ts_ns), "tr": str(st.room_total), "cr": str(st.room_left),
                "bq": str(st.foreign_buy), "bv": str(int(st.foreign_buy_val)),
                "sq": str(st.foreign_sell), "sv": str(int(st.foreign_sell_val))})
        elif isinstance(e, PutThrough):
            self._fan("put", "tick", sym, f"put.{sym}", "put_tick", {
                "s": sym, "t": _t(e.ts_ns), "p": _k(e.price), "q": str(e.vol),
                "tq": str(st.pt_vol), "tv": str(int(st.pt_acc_value))})
        elif isinstance(e, Oddlot):
            self._fan("oddlot", "tick", sym, f"oddlot.{sym}", "oddlot_tick", {
                "s": sym, "t": _t(e.ts_ns), "p": _k(e.price), "q": str(e.qty),
                "bids": [[_k(st.bids[0][0]), str(e.qty)]], "asks": [[_k(st.asks[0][0]), "50"]]})
        elif isinstance(e, Bar) and e.closed:
            self._bar(sym, "1m", e.start_s, e.o, e.h, e.l, e.c, e.v)
            a = self._agg5.get(sym)
            start5 = e.start_s // 300 * 300
            if a is None or a[0] != start5:
                a = self._agg5[sym] = [start5, e.o, e.h, e.l, e.c, 0]
            a[2], a[3], a[4], a[5] = max(a[2], e.h), min(a[3], e.l), e.c, a[5] + e.v
            if e.start_s + 60 >= start5 + 300:
                self._bar(sym, "5m", *a)
        elif isinstance(e, Session):
            self._fan("market", "", None, f"market.{e.exchange}", "market",
                      {"b": e.exchange, "t": _t(e.ts_ns), "f": e.flag})

    def _bar(self, sym, res, start_s, o, h, l, c, v) -> None:
        self._fan("trade", res, sym, f"trade.{sym}@{res}", f"trade_{res}", {
            "s": sym, "t": _t(start_s * 1_000_000_000), "open": _k(o), "high": _k(h),
            "low": _k(l), "close": _k(c), "volume": str(v)})

    # ----------------------------------------------------------------- app
    def app(self) -> web.Application:
        app = web.Application()
        app.router.add_post("/api/v3/auth/token", self.token)
        app.router.add_post("/api/v3/auth/refresh", self.do_refresh)
        app.router.add_get("/ws/v3", self.stream)
        app.router.add_get("/", self.stream)
        return app
