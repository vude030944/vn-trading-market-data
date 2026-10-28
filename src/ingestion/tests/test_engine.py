"""
Engine tests — proving the engine knows NOTHING about any specific broker.

The spec here is entirely invented. If the engine runs against it, adding a
fourth broker will not require touching the engine.
"""

from __future__ import annotations

import asyncio
from typing import Iterable

import pytest

from ingestion.config.base import BackoffSettings, RuntimeSettings, TelemetrySettings
from ingestion.core.engine import WsEngine
from ingestion.core.frame import Frame, Handled, SessionInfo
from ingestion.core.spec import FeedSpec
from ingestion.core.telemetry import Telemetry


def _noop_telemetry() -> Telemetry:
    # An empty otlp_endpoint makes Telemetry a no-op: no thread, no exporter.
    return Telemetry(TelemetrySettings(otlp_endpoint=""), RuntimeSettings(), ())


class FakeSpec:
    """An imaginary broker speaking the protocol 'X:<key>:<payload>'."""

    source = "fake"
    name = "fake.feed"
    url = "wss://example.invalid/stream"

    def __init__(self) -> None:
        self.handshaked = 0
        self.subscribed = 0

    def connect_kwargs(self) -> dict:
        return {}

    async def handshake(self, conn) -> SessionInfo:
        self.handshaked += 1
        return SessionInfo(session_id="s1", heartbeat_timeout_s=30)

    def subscribe_frames(self) -> Iterable[str]:
        self.subscribed += 1
        return ["SUB"]

    def heartbeat_frame(self):
        return None                 # heartbeat disabled to keep the test simple

    def heartbeat_interval_s(self) -> float:
        return 1.0

    def max_session_lifetime_s(self):
        return None

    def on_message(self, raw):
        if not isinstance(raw, str) or not raw.startswith("X:"):
            return Handled(malformed=True)
        _, key, payload = raw.split(":", 2)
        return Handled(frames=(Frame(topic="t", key=key, wire_code="x", payload=payload),))


def test_fake_spec_satisfies_protocol():
    assert isinstance(FakeSpec(), FeedSpec)


async def test_engine_runs_a_complete_session(monkeypatch):
    """connect -> handshake -> subscribe -> pump -> the sink receives the frames."""
    from ingestion.core import engine as engine_mod

    messages = ["X:ACB:{'p':1}", "unintelligible-garbage", "X:HPG:{'p':2}"]

    class FakeWs:
        def __aiter__(self):
            async def gen():
                for m in messages:
                    yield m
            return gen()
        async def send(self, data): ...
        async def close(self, *a, **k): ...

    class FakeCtx:
        async def __aenter__(self): return FakeWs()
        async def __aexit__(self, *exc): return False

    monkeypatch.setattr(engine_mod, "open_connection", lambda *a, **k: FakeCtx())

    got: list[Frame] = []
    async def sink(frame, recv_ns, recv_ts_ns):
        assert recv_ts_ns > 0 and recv_ns > 0     # timestamps captured before parsing
        got.append(frame)

    spec = FakeSpec()
    eng = WsEngine(spec, sink, backoff=BackoffSettings(initial_ms=1, max_ms=1),
                   connect_timeout_s=1, telemetry=_noop_telemetry())

    task = asyncio.create_task(eng.run_forever())
    await asyncio.sleep(0.15)
    eng.stop()
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)

    assert spec.handshaked >= 1 and spec.subscribed >= 1
    assert [f.key for f in got][:2] == ["ACB", "HPG"]
    assert eng.stats.malformed >= 1        # garbage is COUNTED, never swallowed


async def test_engine_counts_reconnects_when_session_drops(monkeypatch):
    from ingestion.core import engine as engine_mod

    class BoomCtx:
        async def __aenter__(self): raise ConnectionError("broker refused")
        async def __aexit__(self, *exc): return False

    monkeypatch.setattr(engine_mod, "open_connection", lambda *a, **k: BoomCtx())

    async def sink(*a): ...
    eng = WsEngine(FakeSpec(), sink, backoff=BackoffSettings(initial_ms=1, max_ms=2),
                   connect_timeout_s=1, telemetry=_noop_telemetry())

    task = asyncio.create_task(eng.run_forever())
    await asyncio.sleep(0.1)
    eng.stop()
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)
    assert eng.stats.reconnects >= 2       # it retries instead of dying outright


async def test_engine_stops_when_retry_budget_is_exhausted(monkeypatch):
    from ingestion.core import engine as engine_mod

    class BoomCtx:
        async def __aenter__(self): raise ConnectionError("down")
        async def __aexit__(self, *exc): return False

    monkeypatch.setattr(engine_mod, "open_connection", lambda *a, **k: BoomCtx())

    async def sink(*a): ...
    eng = WsEngine(FakeSpec(), sink,
                   backoff=BackoffSettings(initial_ms=1, max_ms=1, max_attempts=3),
                   connect_timeout_s=1, telemetry=_noop_telemetry())
    await asyncio.wait_for(eng.run_forever(), timeout=5)   # must exit ON ITS OWN
    assert eng.stats.reconnects == 3


# =========================================================================
# Health
# =========================================================================


def test_health_is_ok_outside_trading_hours(tmp_path):
    """
    The crux: at 3pm there is not a single tick, yet the feeds are perfectly
    connected. Health must follow CONNECTION STATE, not data flow.
    """
    from ingestion.core import health

    f = tmp_path / "h.json"
    health.write(f, "tcbs", {"tcbs.stock": {"connected": True, "frames": 0}})
    ok, reason = health.check(f)
    assert ok, reason


def test_health_reports_a_disconnected_feed(tmp_path):
    from ingestion.core import health

    f = tmp_path / "h.json"
    health.write(f, "tcbs", {
        "tcbs.stock": {"connected": True, "frames": 10},
        "tcbs.ouranos": {"connected": False, "frames": 0},
    })
    ok, reason = health.check(f)
    assert not ok and "tcbs.ouranos" in reason


def test_health_reports_stale_file(tmp_path, monkeypatch):
    import time as _t

    from ingestion.core import health

    f = tmp_path / "h.json"
    health.write(f, "ssi", {"ssi.market": {"connected": True}})
    monkeypatch.setattr(_t, "time", lambda: _t.__dict__["time"] and 0)  # noqa
    monkeypatch.setattr(health.time, "time", lambda: 10**10)
    ok, reason = health.check(f)
    assert not ok and "stuck" in reason


def test_health_missing_file(tmp_path):
    from ingestion.core import health

    ok, reason = health.check(tmp_path / "khong-co.json")
    assert not ok and "missing file" in reason
