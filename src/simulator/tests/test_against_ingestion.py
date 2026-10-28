"""
The production ingestion client (src/ingestion) against the simulator.

If these pass, the simulator speaks each broker's protocol well enough for the
real code to authenticate, subscribe, stay alive and receive every channel — and
the frames it receives are exactly the ones the simulator counted as delivered.
"""

from __future__ import annotations

import asyncio
import json
from collections import Counter
from dataclasses import replace

import pytest
import websockets

from ingestion.config.base import BackoffSettings, RuntimeSettings, TelemetrySettings
from ingestion.config.dnse import DNSEConfig
from ingestion.config.ssi import SSIConfig
from ingestion.config.tcbs import TCBSConfig
from ingestion.core.engine import WsEngine
from ingestion.core.telemetry import Telemetry
from ingestion.feeds.dnse import DNSESpec
from ingestion.feeds.ssi import SSISpec
from ingestion.feeds.tcbs import build_specs as tcbs_specs


async def run_specs(specs, seconds: float = 3.0):
    got: dict[str, list] = {s.name: [] for s in specs}
    engines = []
    for spec in specs:
        async def sink(frame, recv_ns, recv_ts_ns, name=spec.name):
            got[name].append(frame)
        engines.append(WsEngine(spec, sink, backoff=BackoffSettings(initial_ms=50, max_ms=100),
                                connect_timeout_s=5,
                                telemetry=Telemetry(TelemetrySettings(otlp_endpoint=""),
                                                    RuntimeSettings(), ())))
    tasks = [asyncio.create_task(e.run_forever()) for e in engines]
    await asyncio.sleep(seconds)
    for e in engines:
        e.stop()
    for t in tasks:
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    return got, engines


def delivered(sim, source: str, feed: str) -> Counter:
    return Counter(dict(sim.stats.frames[source][feed]))


def received(frames) -> Counter:
    return Counter(f.wire_code for f in frames)


def assert_matches_delivery(sim, source, feed, frames):
    """Every frame ingestion got was counted by the simulator, and (almost) vice versa."""
    sent, got = delivered(sim, source, feed), received(frames)
    for wire, n in got.items():
        assert n <= sent[wire], f"{wire}: received {n} > delivered {sent[wire]}"
    # Frames written in the last instant before the engine stopped may be unread.
    assert sum(got.values()) >= 0.95 * sum(sent.values())


# =========================================================================== SSI


@pytest.mark.parametrize("auth_mode", ["query", "header", "frame"])
async def test_ssi_all_auth_modes_and_topics(sim, auth_mode):
    base = f"127.0.0.1:{sim.ports['ssi']}"
    cfg = SSIConfig(api_key=sim.cfg.ssi_api_key, api_secret=sim.cfg.ssi_api_secret,
                    api_url=f"http://{base}", stream_url=f"ws://{base}/ws/v3",
                    auth_mode=auth_mode,
                    topics=("trade.*@tick", "quote.*@tick", "room.*@tick", "put.*@tick",
                            "oddlot.*@tick", "market.*", "trade.vn30@1m"))
    got, (eng,) = await run_specs([SSISpec(cfg)])
    frames = got["ssi.market"]

    assert eng.stats.reconnects == 0 and eng.stats.malformed == 0
    wires = received(frames)
    assert {"trade_tick", "quote_tick", "room_tick", "market"} <= set(wires)
    trade = json.loads(next(f.payload for f in frames if f.wire_code == "trade_tick"))
    assert trade["channel"] == "DATA" and isinstance(trade["data"]["p"], str)
    # The REST token flow ran for real (no monkeypatching).
    assert sim.stats.events["ssi"]["token_issued"] >= 1
    assert_matches_delivery(sim, "ssi", "ssi.market", frames)


async def test_ssi_recovers_when_its_token_is_revoked(sim):
    """401003 at the upgrade must lead to a NEW token, not the same one forever."""
    import aiohttp

    base = f"127.0.0.1:{sim.ports['ssi']}"
    cfg = SSIConfig(api_key=sim.cfg.ssi_api_key, api_secret=sim.cfg.ssi_api_secret,
                    api_url=f"http://{base}", stream_url=f"ws://{base}/ws/v3")

    async def revoke_then_drop():
        await asyncio.sleep(1.0)
        async with aiohttp.ClientSession() as s:
            await s.post(f"http://127.0.0.1:{sim.ports['stats']}/control/revoke-tokens")
        for c in sim.reg.of("ssi"):
            await c.close(1012, "restart")
    chaos = asyncio.create_task(revoke_then_drop())
    got, (eng,) = await run_specs([SSISpec(cfg)], seconds=4.0)
    await chaos

    assert sim.stats.events["ssi"]["upgrade_rejected_401003"] >= 1
    assert sim.stats.events["ssi"]["token_issued"] >= 2
    assert sim.stats.events["ssi"]["connections"] >= 2      # it got back in
    late = [f for f in got["ssi.market"] if f.wire_code == "trade_tick"]
    assert late, "data must flow again after the new token"


async def test_ssi_bad_secret_is_refused(sim):
    base = f"127.0.0.1:{sim.ports['ssi']}"
    cfg = SSIConfig(api_key=sim.cfg.ssi_api_key, api_secret="wrong",
                    api_url=f"http://{base}", stream_url=f"ws://{base}/ws/v3")
    got, (eng,) = await run_specs([SSISpec(cfg)], seconds=1.0)
    assert got["ssi.market"] == [] and not eng.stats.connected
    assert sim.stats.events["ssi"]["auth_rejected"] >= 1


# ========================================================================== DNSE


@pytest.mark.parametrize("encoding", ["json", "msgpack"])
async def test_dnse_hmac_channels_and_encodings(sim, encoding):
    syms = tuple(s for s in sim.market.states if sim.market.states[s].inst.kind != "cw")
    cfg = DNSEConfig(api_key=sim.cfg.dnse_api_key, api_secret=sim.cfg.dnse_api_secret,
                     stream_url=f"ws://127.0.0.1:{sim.ports['dnse']}/v1/stream",
                     encoding=encoding, symbols=syms,
                     channels=("tick_extra", "top_price", "foreign", "session",
                               "market_index", "estimated_market_index", "ohlc",
                               "security_definition"),
                     market_indices=("VNINDEX", "VN30"))
    got, (eng,) = await run_specs([DNSESpec(cfg)])
    frames = got["dnse.market"]

    assert eng.stats.reconnects == 0 and eng.stats.malformed == 0
    decode = (lambda p: json.loads(p)) if encoding == "json" else \
        (lambda p: __import__("msgpack").unpackb(p, raw=False))
    bodies = [decode(f.payload) for f in frames]
    assert any("matchPrice" in b and "side" in b for b in bodies)            # tick_extra
    assert any("bid" in b and "offer" in b for b in bodies)                  # top_price
    assert any("valueIndexes" in b and "transactTime" in b for b in bodies)  # market_index
    assert any(b.get("action") == "estimated_market_index" for b in bodies)  # the docs' trap
    assert any("ceilingPrice" in b for b in bodies)                          # security_definition
    tick = next(b for b in bodies if "matchPrice" in b)
    assert set(tick["time"]) == {"Seconds", "Nanos"}
    assert_matches_delivery(sim, "dnse", "dnse.market", frames)


async def test_dnse_wrong_secret_gets_auth_failed(sim):
    cfg = DNSEConfig(api_key=sim.cfg.dnse_api_key, api_secret="wrong", symbols=("HPG",),
                     stream_url=f"ws://127.0.0.1:{sim.ports['dnse']}/v1/stream")
    got, (eng,) = await run_specs([DNSESpec(cfg)], seconds=1.0)
    assert got["dnse.market"] == [] and not eng.stats.connected
    assert sim.stats.events["dnse"]["auth_rejected"] >= 1


async def test_dnse_reused_nonce_is_rejected(sim):
    import hashlib, hmac, time
    url = f"ws://127.0.0.1:{sim.ports['dnse']}/v1/stream?encoding=json"
    ts, nonce = int(time.time()), "123456789"
    sig = hmac.new(sim.cfg.dnse_api_secret.encode(),
                   f"{sim.cfg.dnse_api_key}:{ts}:{nonce}".encode(), hashlib.sha256).hexdigest()
    auth = json.dumps({"action": "auth", "api_key": sim.cfg.dnse_api_key,
                       "signature": sig, "timestamp": ts, "nonce": nonce})
    replies = []
    for _ in range(2):
        async with websockets.connect(url, ping_interval=None) as ws:
            await ws.recv()                                   # welcome
            await ws.send(auth)
            replies.append(json.loads(await ws.recv()))
    assert replies[0]["action"] == "auth_success"
    assert replies[1] == {"action": "error", "code": "AUTH_FAILED",
                          "message": "authentication failed: nonce already used"}


# ========================================================================== TCBS


def tcbs_config(sim, **kw) -> TCBSConfig:
    cfg = TCBSConfig(token="", api_key=sim.cfg.tcbs_api_key, otp=sim.cfg.tcbs_otp,
                     rest_url=f"http://127.0.0.1:{sim.ports['tcbs']}",
                     base_ws_url=f"ws://127.0.0.1:{sim.ports['tcbs']}", **kw)
    return replace(cfg,
                   stock=replace(cfg.stock, symbols=("TCB", "HPG", "FPT"),
                                 channel_codes=("bp", "bi", "tm", "mp", "op", "fe", "tmh")),
                   derivative=replace(cfg.derivative, symbols=("41I1G8000",)),
                   ouranos=replace(cfg.ouranos, tickers=("TCB", "HPG", "FPT", "SSI", "VNM")))


async def test_tcbs_three_feeds_with_one_token(sim):
    got, engines = await run_specs(tcbs_specs(tcbs_config(sim)))
    for e in engines:
        assert e.stats.reconnects == 0 and e.stats.malformed == 0, e.name

    stock, deriv, our = (received(got[n]) for n in ("tcbs.stock", "tcbs.derivative", "tcbs.ouranos"))
    # Cash board over floors: equities, covered warrants, the index and put-throughs.
    assert {"s|1", "s|2", "s|6", "s|4", "s|8", "s|18", "s|28", "s|29"} <= set(stock)
    # Production quirk: the futures family ALSO arrives on the cash socket (floor 8).
    assert {"s|21", "s|23", "s|24"} <= set(stock)
    # s|42 exists only on the derivative socket, and only because of `dtn`.
    assert "s|42" in deriv and "s|42" not in stock
    assert {"C001", "C002S60"} <= set(our)
    # One token for all three sockets, minted once over REST.
    assert sim.stats.events["tcbs"]["token_issued"] == 1

    s6 = json.loads(next(f.payload for f in got["tcbs.stock"] if f.wire_code == "s|6"))
    s21 = json.loads(next(f.payload for f in got["tcbs.derivative"] if f.wire_code == "s|21"))
    assert isinstance(s6["matchPrice"], str) and isinstance(s21["matchPrice"], float)
    for name in ("tcbs.stock", "tcbs.derivative", "tcbs.ouranos"):
        assert_matches_delivery(sim, "tcbs", name, got[name])


async def test_tcbs_futures_copies_are_byte_identical(sim):
    got, _ = await run_specs(tcbs_specs(tcbs_config(sim)))
    on_stock = {f.payload for f in got["tcbs.stock"] if f.wire_code == "s|21"}
    on_deriv = {f.payload for f in got["tcbs.derivative"] if f.wire_code == "s|21"}
    assert on_stock & on_deriv, "the same s|21 frame should arrive on both sockets"


async def test_ordinary_disconnects_do_not_use_up_the_retry_budget(sim):
    """
    A session that authenticated and then dropped must reset the backoff. TCBS
    allows only 10 attempts; if ordinary drops counted, a feed would die for good
    after its tenth routine disconnect of the day.
    """
    cfg = tcbs_config(sim)
    cfg = replace(cfg, derivative=replace(cfg.derivative, enabled=False),
                  ouranos=replace(cfg.ouranos, enabled=False),
                  backoff=BackoffSettings(initial_ms=50, max_ms=100, max_attempts=3))
    spec = tcbs_specs(cfg)[0]
    got: list = []

    async def sink(frame, *_):
        got.append(frame)
    eng = WsEngine(spec, sink, backoff=cfg.backoff, connect_timeout_s=5,
                   telemetry=Telemetry(TelemetrySettings(otlp_endpoint=""), RuntimeSettings(), ()))
    task = asyncio.create_task(eng.run_forever())
    for _ in range(5):                       # more drops than the budget allows
        await asyncio.sleep(0.6)
        for c in sim.reg.of("tcbs"):
            await c.close(1012, "restart")
    await asyncio.sleep(0.6)
    alive = not task.done()
    n_before = len(got)
    await asyncio.sleep(0.5)
    eng.stop()
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)

    assert eng.stats.reconnects >= 5
    assert alive, "the feed gave up although every session had authenticated"
    assert len(got) > n_before, "data must still be flowing after the drops"


async def test_tcbs_rfc_ping_is_a_protocol_error(sim):
    url = f"ws://127.0.0.1:{sim.ports['tcbs']}/ws/thesis/v1/stream/normal"
    async with websockets.connect(url, ping_interval=None) as ws:
        await ws.ping()
        with pytest.raises(websockets.ConnectionClosed) as exc:
            await asyncio.wait_for(ws.recv(), 3)
    assert exc.value.rcvd.code == 1002


async def test_tcbs_subscribe_before_auth_is_rejected(sim):
    url = f"ws://127.0.0.1:{sim.ports['tcbs']}/ws/thesis/v1/stream/normal"
    async with websockets.connect(url, ping_interval=None) as ws:
        await ws.send("d|s|tk|tm|TCB")
        with pytest.raises(websockets.ConnectionClosed) as exc:
            await asyncio.wait_for(ws.recv(), 3)
    assert exc.value.rcvd.code == 1008


async def test_tcbs_silence_past_the_timeout_closes(sim):
    sim_cfg = sim.cfg
    url = f"ws://127.0.0.1:{sim.ports['tcbs']}/ws/thesis/v1/stream/normal"
    import base64
    async with websockets.connect(url, ping_interval=None) as ws:
        await ws.send("d|a|||" + base64.b64encode(sim_cfg.tcbs_static_token.encode()).decode())
        assert await ws.recv() == f"d|33|{sim_cfg.tcbs_thesis_timeout_s}"
        assert json.loads((await ws.recv())[4:]) == {"success": True, "error": None}
        # No heartbeat at all -> the server hangs up with 1000 after the timeout.
        with pytest.raises(websockets.ConnectionClosed) as exc:
            while True:
                await asyncio.wait_for(ws.recv(), sim_cfg.tcbs_thesis_timeout_s + 3)
    assert exc.value.rcvd.code == 1000
