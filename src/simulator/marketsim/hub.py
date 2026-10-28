"""
Client connections and delivery statistics.

Every data frame is counted under the SAME key ingestion later puts on the Kafka
record — (source, feed, wire_code) — so an end-to-end check can compare "sent by
the broker" with "landed in vnmd.raw" one row at a time (see scripts/e2e_check.py).
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
from collections import defaultdict
from typing import Callable

from aiohttp import WSCloseCode, web

log = logging.getLogger(__name__)


class Stats:
    def __init__(self) -> None:
        self.started = time.time()
        # source -> feed -> wire_code -> frames delivered
        self.frames: dict[str, dict[str, dict[str, int]]] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(int)))
        self.events: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def frame(self, source: str, feed: str, wire: str, n: int = 1) -> None:
        self.frames[source][feed][wire] += n

    def event(self, source: str, name: str) -> None:
        self.events[source][name] += 1

    def as_dict(self, clients: dict[str, set]) -> dict:
        return {
            "started": self.started,
            "uptime_s": round(time.time() - self.started, 1),
            "connections_open": {b: len(c) for b, c in clients.items()},
            "events": {b: dict(e) for b, e in self.events.items()},
            "frames": {s: {f: dict(w) for f, w in feeds.items()} for s, feeds in self.frames.items()},
            "frames_total": {s: sum(sum(w.values()) for w in feeds.values())
                             for s, feeds in self.frames.items()},
        }


class Client:
    """
    One accepted WebSocket. Producers call send() (never blocks); a writer task
    drains the queue. A full queue means the consumer is too slow — the
    `on_overflow` policy decides (DNSE documents close code 1013 for exactly this).
    """

    def __init__(self, source: str, feed: str, ws: web.WebSocketResponse, stats: Stats,
                 queue_max: int, overflow_code: int = WSCloseCode.TRY_AGAIN_LATER) -> None:
        self.source = source
        self.feed = feed
        self.ws = ws
        self.stats = stats
        self.opened = time.monotonic()
        self.authed = False
        self.last_heartbeat = time.monotonic()
        self.subs: dict = {}
        self._q: asyncio.Queue = asyncio.Queue(maxsize=queue_max)
        self._overflow_code = overflow_code
        self._closing = False
        self._writer = asyncio.create_task(self._drain())

    def send(self, data: str | bytes, wire: str | None = None) -> None:
        """Queue a frame. `wire` set = a data frame, counted in the stats once written."""
        if self._closing:
            return
        try:
            self._q.put_nowait((data, wire))
        except asyncio.QueueFull:
            self.stats.event(self.source, "close_slow_consumer")
            asyncio.ensure_future(self.close(self._overflow_code, "client too slow"))

    def send_later(self, delay_s: float, data: str | bytes, wire: str | None = None) -> None:
        asyncio.get_running_loop().call_later(delay_s, self.send, data, wire)

    async def _drain(self) -> None:
        # Counted BEFORE the await: aiohttp hands the bytes to the transport
        # synchronously and only then awaits the drain, so a writer cancelled
        # mid-send (a close racing it) has usually delivered the frame already.
        # Only an outright send failure takes the count back.
        while True:
            try:
                data, wire = await self._q.get()
            except asyncio.CancelledError:
                return
            if wire is not None:
                self.stats.frame(self.source, self.feed, wire)
            try:
                if isinstance(data, bytes):
                    await self.ws.send_bytes(data)
                else:
                    await self.ws.send_str(data)
            except asyncio.CancelledError:
                return
            except (ConnectionResetError, RuntimeError):
                if wire is not None:
                    self.stats.frame(self.source, self.feed, wire, -1)
                return

    async def close(self, code: int = WSCloseCode.OK, message: str = "") -> None:
        if self._closing:
            return
        self._closing = True
        self.stats.event(self.source, f"close_{int(code)}")
        log.info("closing %s client: %s %s", self.feed, int(code), message)
        try:
            await self.ws.close(code=code, message=message.encode())
        finally:
            self._writer.cancel()

    async def finished(self) -> None:
        self._closing = True
        self._writer.cancel()


class Registry:
    """Live clients per broker — for fan-out and for chaos."""

    def __init__(self) -> None:
        self.clients: dict[str, set[Client]] = defaultdict(set)

    def add(self, c: Client) -> None:
        self.clients[c.source].add(c)

    def remove(self, c: Client) -> None:
        self.clients[c.source].discard(c)

    def of(self, source: str) -> list[Client]:
        return list(self.clients[source])

    async def chaos(self, every_s: float, rng: random.Random) -> None:
        """Drop one random connection per broker every `every_s` seconds."""
        while True:
            await asyncio.sleep(every_s)
            for source, cs in list(self.clients.items()):
                if cs:
                    victim = rng.choice(list(cs))
                    victim.stats.event(source, "chaos_drop")
                    await victim.close(WSCloseCode.SERVICE_RESTART, "chaos: simulated restart")


async def ws_loop(ws: web.WebSocketResponse, on_text: Callable, on_rfc_ping: Callable | None = None):
    """Read loop shared by the three servers. Text frames go to `on_text`."""
    from aiohttp import WSMsgType

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            await on_text(msg.data)
        elif msg.type == WSMsgType.BINARY:
            await on_text(msg.data.decode("utf-8", "replace"))
        elif msg.type == WSMsgType.PING:
            if on_rfc_ping is not None:
                await on_rfc_ping()
            else:
                await ws.pong(msg.data)
        elif msg.type in (WSMsgType.CLOSE, WSMsgType.CLOSING, WSMsgType.CLOSED, WSMsgType.ERROR):
            break
