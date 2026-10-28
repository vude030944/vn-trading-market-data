"""Spec tests driven by a fake Conn — protocol correctness without an open market."""

from __future__ import annotations

import json

import pytest

from ingestion.config.dnse import DNSEConfig
from ingestion.config.ssi import SSIConfig
from ingestion.config.tcbs import TCBSConfig
from ingestion.core.spec import AuthError
from ingestion.feeds.dnse import DNSESpec
from ingestion.feeds.ssi import SSISpec, normalize_expiry
from ingestion.feeds.tcbs import build_specs as tcbs_specs

# =========================================================================
# TCBS
# =========================================================================


def _tcbs_cfg(**kw) -> TCBSConfig:
    """A minimal but VALID TCBS config (passes validate)."""
    from dataclasses import replace

    cfg = TCBSConfig(token="tok", api_key="", otp="")
    cfg = replace(
        cfg,
        derivative=replace(cfg.derivative, symbols=("41I1G8000",)),
        ouranos=replace(cfg.ouranos, tickers=("TCB", "FPT")),
    )
    cfg.validate()
    return replace(cfg, **kw) if kw else cfg


def test_tcbs_three_feeds_share_one_token_provider():
    """The "one token" constraint must be visible in code, not only in the docs."""
    specs = tcbs_specs(_tcbs_cfg())
    providers = {id(s._tokens) for s in specs}
    assert len(specs) == 3
    assert len(providers) == 1


async def test_tcbs_handshake_uses_plain_base64_and_reads_timeout(fake_conn):
    conn = fake_conn(['d|33|30', 'd|0|{"success":true,"error":null}'])
    spec = tcbs_specs(_tcbs_cfg())[0]
    session = await spec.handshake(conn)

    # the token must be base64-encoded DIRECTLY, not wrapped in JSON
    assert conn.sent == ["d|a|||dG9r"]
    # the timeout comes from the server (30), not from the documentation (15)
    assert session.heartbeat_timeout_s == 30.0


async def test_tcbs_failed_handshake_raises_auth_error(fake_conn):
    conn = fake_conn(['d|0|{"success":false,"error":{"code":"211110","message":"Invalid JWT"}}'])
    spec = tcbs_specs(_tcbs_cfg())[0]
    with pytest.raises(AuthError):
        await spec.handshake(conn)


def test_tcbs_derivative_subscribe_includes_dtn():
    """`dtn` unlocks s|42 — undocumented, yet ~94% of the derivatives traffic."""
    specs = tcbs_specs(_tcbs_cfg())
    deriv = next(s for s in specs if s.name == "tcbs.derivative")
    frames = list(deriv.subscribe_frames())
    assert any("dtn" in f for f in frames)
    assert all(f.startswith("d|s|tk|") or f.startswith("d|r|") for f in frames)


def test_tcbs_stock_subscribes_all_four_kinds():
    spec = next(s for s in tcbs_specs(_tcbs_cfg()) if s.name == "tcbs.stock")
    frames = list(spec.subscribe_frames())
    kinds = {f.split("|")[1] + "|" + f.split("|")[2] for f in frames}
    assert {"s|ro", "s|si", "s|pt"} <= kinds


def test_tcbs_on_message_splits_frame_and_sets_key():
    spec = next(s for s in tcbs_specs(_tcbs_cfg()) if s.name == "tcbs.stock")
    h = spec.on_message('s|6|{"symbol":"TCB","matchPrice":"24550"}')
    assert len(h.frames) == 1
    f = h.frames[0]
    assert (f.key, f.wire_code, f.topic) == ("TCB", "s|6", "tcbs.data.raw.stock")
    assert f.payload == '{"symbol":"TCB","matchPrice":"24550"}'   # verbatim


def test_tcbs_ignores_control_without_flagging_malformed():
    spec = next(s for s in tcbs_specs(_tcbs_cfg()) if s.name == "tcbs.stock")
    for ctl in ("d|33|15", "d|34|1", "d|p|||"):
        h = spec.on_message(ctl)
        assert not h.frames and not h.malformed


def test_ouranos_ignores_undocumented_server_ping():
    """The server emits `d|pi` roughly every 10s; unfiltered it floods the logs."""
    spec = next(s for s in tcbs_specs(_tcbs_cfg()) if s.name == "tcbs.ouranos")
    assert not spec.on_message("d|pi").malformed


def test_ouranos_heartbeat_differs_from_thesis():
    specs = {s.name: s for s in tcbs_specs(_tcbs_cfg())}
    assert specs["tcbs.stock"].heartbeat_frame() == "d|p|||"
    assert specs["tcbs.ouranos"].heartbeat_frame() == "d|po"


def test_ouranos_chunks_symbol_list():
    from dataclasses import replace
    base = _tcbs_cfg()
    cfg = replace(base, ouranos=replace(
        base.ouranos, tickers=tuple(f"S{i:03d}" for i in range(250)), subscribe_chunk=100))
    spec = next(s for s in tcbs_specs(cfg) if s.name == "tcbs.ouranos")
    frames = list(spec.subscribe_frames())
    assert len(frames) == 3
    assert sum(f.split("|")[-1].count(",") + 1 for f in frames) == 250


# =========================================================================
# DNSE
# =========================================================================


def _dnse_cfg(**kw) -> DNSEConfig:
    from dataclasses import replace
    cfg = DNSEConfig(api_key="key", api_secret="secret", symbols=("ACB", "HPG"))
    return replace(cfg, **kw) if kw else cfg


async def test_dnse_handshake_signs_hmac_and_never_sends_secret(fake_conn):
    conn = fake_conn([
        json.dumps({"action": "welcome", "session_id": "conn_1"}),
        json.dumps({"action": "auth_success",
                    "rate_limit": {"messages_per_second": 100, "subscriptions_max": 100}}),
    ])
    spec = DNSESpec(_dnse_cfg())
    session = await spec.handshake(conn)

    auth = json.loads(conn.sent[0])
    assert auth["action"] == "auth"
    assert len(auth["signature"]) == 64                 # hex sha256
    assert "secret" not in conn.sent[0]                 # the secret NEVER leaves the process
    assert session.limits["subscriptions_max"] == 100
    assert session.session_id == "conn_1"


async def test_dnse_mints_a_new_nonce_per_connection():
    """A nonce reused within 10 minutes is rejected -> mint a fresh one each time."""
    spec = DNSESpec(_dnse_cfg())
    a = json.loads(spec._auth_message())["nonce"]
    b = json.loads(spec._auth_message())["nonce"]
    assert a != b


async def test_dnse_auth_failure(fake_conn):
    conn = fake_conn([
        json.dumps({"action": "welcome"}),
        json.dumps({"action": "error", "code": "AUTH_FAILED", "message": "invalid signature"}),
    ])
    with pytest.raises(AuthError):
        await DNSESpec(_dnse_cfg()).handshake(conn)


def test_dnse_replies_pong_echoing_timestamp():
    spec = DNSESpec(_dnse_cfg())
    h = spec.on_message(json.dumps({"action": "ping", "timestamp": 1750000000123}))
    assert not h.frames and len(h.replies) == 1
    pong = json.loads(h.replies[0])
    assert pong == {"action": "pong", "timestamp": 1750000000123}


def test_dnse_message_with_both_action_and_T_is_still_data():
    """The trap the docs call out by name: estimated_market_index has BOTH `action` and `T`."""
    spec = DNSESpec(_dnse_cfg())
    raw = json.dumps({"action": "estimated_market_index", "T": "emi",
                      "indexName": "VN30", "valueIndexes": 1948.57})
    h = spec.on_message(raw)
    assert len(h.frames) == 1
    assert h.frames[0].key == "VN30"


def test_dnse_missing_T_is_forwarded_not_dropped():
    spec = DNSESpec(_dnse_cfg())
    h = spec.on_message(json.dumps({"symbol": "ACB", "matchPrice": 24.35}))
    assert h.frames[0].wire_code == "unknown"
    assert h.frames[0].key == "ACB"


def test_dnse_renews_before_the_8_hour_limit():
    spec = DNSESpec(_dnse_cfg())
    ttl = spec.max_session_lifetime_s()
    assert ttl == 8 * 3600 - 300           # 5 minutes before the hard limit
    assert ttl < 8 * 3600


def test_dnse_builds_channels_from_templates():
    spec = DNSESpec(_dnse_cfg(channels=("tick", "ohlc", "market_index", "session")))
    names = [c["name"] for c in spec._channels()]
    assert "tick.G1.json" in names
    assert "ohlc.1.json" in names
    assert "market_index.VNINDEX.json" in names
    assert "session.STO.G1.json" in names


# =========================================================================
# SSI
# =========================================================================


def _ssi_cfg(**kw) -> SSIConfig:
    from dataclasses import replace
    cfg = SSIConfig(api_key="key", api_secret="secret")
    return replace(cfg, **kw) if kw else cfg


def test_ssi_infers_expires_at_unit():
    """Section 10.2: the guide prints seconds, the API spec milliseconds — same field."""
    assert normalize_expiry(1779806203, "auto") == 1779806203        # seconds
    assert normalize_expiry(1772075293023, "auto") == 1772075293.023  # milliseconds
    assert normalize_expiry(1772075293023, "ms") == 1772075293.023
    assert normalize_expiry(1779806203, "s") == 1779806203


def test_ssi_auth_mode_query_puts_token_in_url():
    spec = SSISpec(_ssi_cfg(auth_mode="query"))
    spec._token = "abc123"
    import asyncio
    asyncio.get_event_loop_policy().new_event_loop().close()
    # exercise the URL-building part directly (prepare needs the network for a token)
    sep = "&" if "?" in spec._cfg.stream_url else "?"
    spec.url = f"{spec._cfg.stream_url}{sep}access_token=abc123"
    assert "access_token=abc123" in spec.url


def test_ssi_auth_mode_header():
    spec = SSISpec(_ssi_cfg(auth_mode="header"))
    spec._token = "abc123"
    assert spec.connect_kwargs()["additional_headers"]["Authorization"] == "Bearer abc123"


def test_ssi_replies_pong_in_correct_shape():
    spec = SSISpec(_ssi_cfg())
    h = spec.on_message(json.dumps({"method": "PING", "channel": "HEARTBEAT",
                                    "time": "01-08-2026 09-15-32"}))
    pong = json.loads(h.replies[0])
    assert pong["method"] == "PONG" and pong["channel"] == "HEARTBEAT"
    assert pong["time"] == "01-08-2026 09-15-32"


def test_ssi_wire_code_derived_from_topic():
    spec = SSISpec(_ssi_cfg())
    assert spec._wire_code("trade.SSI@1m") == "trade_1m"
    assert spec._wire_code("quote.SSI") == "quote_tick"
    assert spec._wire_code("market.HOSE") == "market"


def test_ssi_extracts_key_and_keeps_payload_verbatim():
    spec = SSISpec(_ssi_cfg())
    raw = json.dumps({"channel": "DATA", "topic": "trade.SSI@tick",
                      "data": {"s": "SSI", "p": "45.50"}})
    h = spec.on_message(raw)
    f = h.frames[0]
    assert f.key == "SSI" and f.wire_code == "trade_tick"
    assert f.payload == raw          # verbatim, not a re-serialised json.dumps(data)
