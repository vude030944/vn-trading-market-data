"""Fakes for testing specs WITHOUT a real server — this is why Conn is a Protocol."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


class FakeConn:
    """
    A fake Conn: `recv()` returns scripted messages in order, `send()` records
    everything so it can be asserted on.
    """

    def __init__(self, incoming: list[str | bytes] | None = None) -> None:
        self.incoming = list(incoming or [])
        self.sent: list[str | bytes] = []
        self.closed = False

    async def send(self, data: str | bytes) -> None:
        self.sent.append(data)

    async def recv(self, timeout: float | None = None) -> str | bytes:
        if not self.incoming:
            raise asyncio.TimeoutError("FakeConn ran out of messages")
        return self.incoming.pop(0)

    def __aiter__(self):
        async def gen():
            for m in list(self.incoming):
                yield m
        return gen()

    async def close(self, code: int = 1000, reason: str = "") -> None:
        self.closed = True


@pytest.fixture
def fake_conn():
    return FakeConn


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Every test starts from a clean environment so config picks up no stray vars."""
    for k in list(os.environ):
        if k.split("_")[0] in ("SSI", "DNSE", "TCBS", "KAFKA", "OTEL", "LOG", "RUN", "SERVICE"):
            monkeypatch.delenv(k, raising=False)
