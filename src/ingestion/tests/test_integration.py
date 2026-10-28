"""
Integration tests — the REAL engine talking over a REAL socket to fake servers
that speak each broker's actual protocol.

No open market, no real credentials, no Kafka required. What gets verified here
is the part most easily got wrong and impossible to reason out: whether the bytes
actually put on the wire match the broker's grammar.

The fakes are NOT lenient: the DNSE server recomputes the HMAC itself and rejects
a bad signature, so this proves our signing algorithm is correct rather than
merely "it runs".
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
from dataclasses import replace

import pytest
from websockets.asyncio.server import serve

from ingestion.config.base import BackoffSettings, RuntimeSettings, TelemetrySettings
from ingestion.config.dnse import DNSEConfig
from ingestion.config.ssi import SSIConfig
from ingestion.config.tcbs import TCBSConfig
from ingestion.core.engine import WsEngine
from ingestion.core.frame import Frame
from ingestion.core.telemetry import Telemetry
from ingestion.feeds.dnse import DNSESpec
from ingestion.feeds.ssi import SSISpec
from ingestion.feeds.tcbs import build_specs as tcbs_specs

API_KEY, API_SECRET, TOKEN = "test-key", "test-secret", "test-token"


def _telemetry() -> Telemetry:
    return Telemetry(TelemetrySettings(otlp_endpoint=""), RuntimeSettings(), ())


async def _run_engine(spec, seconds: float = 1.2) -> tuple[list[Frame], WsEngine]:
    got: list[Frame] = []

    async def sink(frame, recv_ns, recv_ts_ns):
        assert recv_ns > 0 and recv_ts_ns > 0
        got.append(frame)

    eng = WsEngine(spec, sink, backoff=BackoffSettings(initial_ms=50, max_ms=100),
                   connect_timeout_s=5, telemetry=_telemetry())
    task = asyncio.create_task(eng.run_forever())
    await asyncio.sleep(seconds)
    eng.stop()
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)
    return got, eng


# =========================================================================
# TCBS — protocol pipe-delimited
# =========================================================================


class TcbsServer:
    """Simulates /ws/thesis/v1/stream/normal."""

    def __init__(self) -> None:
        self.received: list[str] = []
        self.authed = False

    async def handler(self, ws):
        async for raw in ws:
            self.received.append(raw)

            if raw.startswith("d|a|||"):
                token = base64.b64decode(raw[len("d|a|||"):]).decode()
                if token != TOKEN:
                    await ws.send('d|0|{"success":false,"error":{"code":"211110"}}')
                    return
                # Same order as the real thing: timeout config first, then auth response.
                await ws.send("d|33|30")
                await ws.send('d|0|{"success":true,"error":null}')
                self.authed = True
                continue

            if raw.startswith("d|s|") or raw.startswith("d|r|"):
                assert self.authed, "subscribed BEFORE auth completed — protocol violation"
                await ws.send("d|34|1")
                await ws.send('s|6|{"symbol":"TCB","matchPrice":"24550","matchQtty":"5000"}')
                await ws.send('s|1|{"symbol":"TCB","bidPrice01":"24500"}')
                await ws.send('s|8|{"indexNumber":5,"index":91.43}')
                continue

            if raw.startswith("d|p"):
                await ws.send("d|p|||")


async def test_tcbs_end_to_end_over_a_real_socket():
    server = TcbsServer()
    async with serve(server.handler, "127.0.0.1", 0) as ws_server:
        port = ws_server.sockets[0].getsockname()[1]

        cfg = TCBSConfig(token=TOKEN, api_key="", otp="",
                         base_ws_url=f"ws://127.0.0.1:{port}")
        cfg = replace(cfg,
                      derivative=replace(cfg.derivative, enabled=False),
                      ouranos=replace(cfg.ouranos, enabled=False),
                      stock=replace(cfg.stock, symbols=("TCB",)))
        spec = tcbs_specs(cfg)[0]

        frames, eng = await _run_engine(spec)

    # 1. Auth syntax: base64 DIRECTLY, not wrapped in JSON
    assert server.received[0].startswith("d|a|||")
    assert base64.b64decode(server.received[0][6:]).decode() == TOKEN

    # 2. All four subscribe kinds plus the snapshot
    subs = [r for r in server.received if r.startswith(("d|s|", "d|r|"))]
    kinds = {r.split("|")[1] + "|" + r.split("|")[2] for r in subs}
    assert {"s|ro", "s|si", "s|pt", "s|tk", "r|tk"} <= kinds

    # 3. Data frames are received and split correctly
    by_wire = {f.wire_code: f for f in frames}
    assert by_wire["s|6"].key == "TCB"
    assert by_wire["s|6"].payload == '{"symbol":"TCB","matchPrice":"24550","matchQtty":"5000"}'
    # s|8 only has indexNumber -> the key must be "5", never None
    assert by_wire["s|8"].key == "5"
    assert eng.stats.malformed == 0


async def test_tcbs_bad_token_raises_auth_error_and_backs_off():
    server = TcbsServer()
    async with serve(server.handler, "127.0.0.1", 0) as ws_server:
        port = ws_server.sockets[0].getsockname()[1]
        cfg = TCBSConfig(token="SAI-TOKEN", api_key="", otp="",
                         base_ws_url=f"ws://127.0.0.1:{port}")
        cfg = replace(cfg,
                      derivative=replace(cfg.derivative, enabled=False),
                      ouranos=replace(cfg.ouranos, enabled=False),
                      stock=replace(cfg.stock, symbols=("TCB",)))
        frames, eng = await _run_engine(tcbs_specs(cfg)[0], seconds=0.8)

    assert frames == []
    # AuthError -> a 60s wait before retrying, so exactly one attempt within 0.8s
    assert eng.stats.reconnects == 1


# =========================================================================
# DNSE — JSON + HMAC, the server VERIFIES the signature
# =========================================================================


class DnseServer:
    def __init__(self) -> None:
        self.received: list[dict] = []
        self.sig_ok: bool | None = None
        self.pong_ts: int | None = None

    async def handler(self, ws):
        await ws.send(json.dumps({"action": "welcome", "session_id": "conn_test",
                                  "timestamp": 1750000000}))
        async for raw in ws:
            msg = json.loads(raw)
            self.received.append(msg)

            if msg.get("action") == "auth":
                expect = hmac.new(
                    API_SECRET.encode(),
                    f"{msg['api_key']}:{msg['timestamp']}:{msg['nonce']}".encode(),
                    hashlib.sha256,
                ).hexdigest()
                self.sig_ok = hmac.compare_digest(expect, msg["signature"])
                if not self.sig_ok:
                    await ws.send(json.dumps({"action": "error", "code": "AUTH_FAILED"}))
                    return
                await ws.send(json.dumps({
                    "action": "auth_success", "user_id": msg["api_key"],
                    "rate_limit": {"messages_per_second": 100, "subscriptions_max": 100}}))
                continue

            if msg.get("action") == "subscribe":
                await ws.send(json.dumps({"action": "subscribed"}))
                await ws.send(json.dumps({
                    "T": "tick_extra", "symbol": "ACB", "matchPrice": 24.35,
                    "side": "SELL", "time": {"Seconds": 1779762571, "Nanos": 101000000}}))
                # The trap the docs name explicitly: BOTH action and T -> still data
                await ws.send(json.dumps({
                    "action": "estimated_market_index", "T": "emi",
                    "indexName": "VN30", "valueIndexes": 1948.57}))
                # Server ping -> the client must pong, echoing the timestamp
                await ws.send(json.dumps({"action": "ping", "timestamp": 1750000000123}))
                continue

            if msg.get("action") == "pong":
                self.pong_ts = msg.get("timestamp")


async def test_dnse_end_to_end_server_verifies_signature():
    server = DnseServer()
    async with serve(server.handler, "127.0.0.1", 0) as ws_server:
        port = ws_server.sockets[0].getsockname()[1]
        cfg = DNSEConfig(api_key=API_KEY, api_secret=API_SECRET,
                         symbols=("ACB", "HPG"),
                         stream_url=f"ws://127.0.0.1:{port}")
        frames, eng = await _run_engine(DNSESpec(cfg))

    # 1. The HMAC matches the broker's formula (the server recomputes it)
    assert server.sig_ok is True
    # 2. api_secret never reaches the wire
    assert all(API_SECRET not in json.dumps(m) for m in server.received)
    # 3. Pong replies echo the timestamp so the server can measure latency
    assert server.pong_ts == 1750000000123
    # 4. Both data shapes reach the sink, including the one carrying `action`
    keys = {f.key for f in frames}
    assert {"ACB", "VN30"} <= keys
    assert eng.stats.malformed == 0


async def test_dnse_wrong_secret_raises_auth_error():
    server = DnseServer()
    async with serve(server.handler, "127.0.0.1", 0) as ws_server:
        port = ws_server.sockets[0].getsockname()[1]
        cfg = DNSEConfig(api_key=API_KEY, api_secret="SAI-SECRET",
                         symbols=("ACB",), stream_url=f"ws://127.0.0.1:{port}")
        frames, eng = await _run_engine(DNSESpec(cfg), seconds=0.8)

    assert server.sig_ok is False
    assert frames == []


# =========================================================================
# SSI — JSON, auth via query parameter
# =========================================================================


class SsiServer:
    def __init__(self) -> None:
        self.path: str | None = None
        self.received: list[dict] = []
        self.got_pong = False

    async def handler(self, ws):
        self.path = ws.request.path
        async for raw in ws:
            msg = json.loads(raw)
            self.received.append(msg)

            if msg.get("method") == "SUBSCRIBE":
                await ws.send(json.dumps({
                    "channel": "DATA", "topic": "trade.SSI@tick",
                    "data": {"s": "SSI", "t": "2026/07/29 09:15:32", "p": "45.50",
                             "q": "1000", "si": "B"}}))
                await ws.send(json.dumps({
                    "channel": "DATA", "topic": "market.HOSE",
                    "data": {"b": "HOSE", "t": "2026/07/29 09:00:00", "f": "ATO"}}))
                # Server PING -> the client must PONG in the exact shape
                await ws.send(json.dumps({"method": "PING", "channel": "HEARTBEAT",
                                          "time": "29-07-2026 09-15-32"}))
                continue

            if msg.get("method") == "PONG":
                self.got_pong = True


async def test_ssi_end_to_end_auth_mode_query(monkeypatch):
    server = SsiServer()
    async with serve(server.handler, "127.0.0.1", 0) as ws_server:
        port = ws_server.sockets[0].getsockname()[1]
        cfg = SSIConfig(api_key=API_KEY, api_secret=API_SECRET,
                        stream_url=f"ws://127.0.0.1:{port}/stream",
                        auth_mode="query")
        spec = SSISpec(cfg)
        # Skip the REST token call — this test verifies the WebSocket side.
        async def fake_get():
            return "TOKEN-123"
        monkeypatch.setattr(spec._tokens, "get", fake_get)

        frames, eng = await _run_engine(spec)

    # 1. The token is attached to the query string when the socket opens
    assert "access_token=TOKEN-123" in (server.path or "")
    # 2. The subscription has the exact {method, channel, topics} shape
    sub = next(m for m in server.received if m.get("method") == "SUBSCRIBE")
    assert sub["channel"] == "DATA" and "trade.*@tick" in sub["topics"]
    # 3. A PONG is sent in response to the server's PING
    assert server.got_pong
    # 4. wire_code is derived from the topic and the key works for both payload shapes
    by_wire = {f.wire_code: f for f in frames}
    assert by_wire["trade_tick"].key == "SSI"
    assert by_wire["market"].key == "HOSE"
    assert eng.stats.malformed == 0
