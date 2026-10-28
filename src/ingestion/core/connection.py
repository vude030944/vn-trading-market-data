"""
A thin adapter over the websockets library.

It exists for two reasons:
  1. FeedSpec only needs `send`/`recv` — it should not depend on one library's
     API. Testing a spec against a fake Conn then needs no real server.
  2. To force auto-ping OFF in exactly one place. All three brokers use
     application-level heartbeats; TCBS states outright that an RFC 6455 ping
     frame makes the server return 1002 Protocol Error and disconnect — their
     documented number-one hard-to-debug failure.
"""

from __future__ import annotations

import asyncio
from typing import Protocol

from websockets.asyncio.client import ClientConnection, connect as ws_connect


class Conn(Protocol):
    """The minimal surface a FeedSpec is allowed to use."""

    async def send(self, data: str | bytes) -> None: ...
    async def recv(self, timeout: float | None = None) -> str | bytes: ...


class WebSocketConn:
    def __init__(self, ws: ClientConnection) -> None:
        self._ws = ws

    async def send(self, data: str | bytes) -> None:
        await self._ws.send(data)

    async def recv(self, timeout: float | None = None) -> str | bytes:
        if timeout is None:
            return await self._ws.recv()
        return await asyncio.wait_for(self._ws.recv(), timeout=timeout)

    def __aiter__(self):
        return self._ws.__aiter__()

    async def close(self, code: int = 1000, reason: str = "") -> None:
        await self._ws.close(code, reason)


def open_connection(url: str, *, connect_timeout_s: float, **extra):
    """
    Open a connection with auto-ping already disabled.

    `ping_interval=None` applies to every broker — none of the three uses
    protocol-level ping frames; all of them heartbeat with text/binary messages.
    """
    return ws_connect(
        url,
        open_timeout=connect_timeout_s,
        close_timeout=5,
        ping_interval=None,
        ping_timeout=None,
        max_queue=256,
        **extra,
    )
