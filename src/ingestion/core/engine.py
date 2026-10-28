"""
WsEngine — THE INVARIANT ENGINE.

This file must NOT know that SSI/DNSE/TCBS exist. It only knows `FeedSpec`.
Adding a fourth broker must not change a single line here — that is the test of
whether the design is right.

Fixed lifecycle:
    connect -> handshake -> subscribe -> [heartbeat || pump] -> close -> backoff -> repeat

Decisions worth noting:
  * Timestamps are captured ONCE per message, BEFORE parsing: `recv_ns`
    (monotonic, for measuring durations) and `recv_ts_ns` (epoch, the event-time
    label). Capturing after parsing would fold parse time into latency.
  * Backoff restarts from the base delay after a SUCCESSFUL handshake. Repeated
    network failures keep doubling; a session that connected then dropped retries
    quickly.
  * AuthError is not retried blindly — wrong credentials stay wrong however many
    times you try, and hammering the broker risks an IP ban. Wait much longer and
    complain loudly.
  * `max_session_lifetime_s` lets us renew before the server cuts us off (DNSE
    hard-cuts at 8 hours).
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Awaitable, Callable

from ..config.base import BackoffSettings
from .backoff import delay_seconds, exhausted
from .connection import WebSocketConn, open_connection
from .frame import Frame
from .spec import AuthError, FeedSpec, ProtocolError
from .telemetry import Telemetry

log = logging.getLogger(__name__)

# frame, recv_ns, recv_ts_ns -> None
OnFrame = Callable[[Frame, int, int], Awaitable[None]]

# Bad credentials warrant a much longer wait than a network blip.
_AUTH_ERROR_DELAY_S = 60.0


@dataclass
class FeedStats:
    frames: int = 0
    messages: int = 0
    reconnects: int = 0
    malformed: int = 0
    first_frame_logged: bool = False
    # State read by the health check. `connected` flips on AFTER the handshake,
    # not after the socket opens — a socket that opens but fails auth is dead.
    connected: bool = False
    last_message_ns: int = 0


class WsEngine:
    def __init__(
        self,
        spec: FeedSpec,
        on_frame: OnFrame,
        *,
        backoff: BackoffSettings,
        connect_timeout_s: float,
        telemetry: Telemetry,
        log_every_n_frames: int = 1000,
    ) -> None:
        self._spec = spec
        self._on_frame = on_frame
        self._backoff = backoff
        self._connect_timeout_s = connect_timeout_s
        self._t = telemetry
        self._log_every = max(1, log_every_n_frames)
        self._stopping = False
        self.stats = FeedStats()
        self._session_authed = False
        self._log = log.getChild(spec.name)

    @property
    def name(self) -> str:
        return self._spec.name

    def stop(self) -> None:
        self._stopping = True

    # ------------------------------------------------------------------
    async def run_forever(self) -> None:
        self._log.info("Starting feed", extra={"feed": self._spec.name,
                                               "url": self._spec.url})
        attempt = 0
        while not self._stopping:
            # Set by _run_session the moment the handshake succeeds. NOT taken from
            # its return value: almost every session ends by raising (the server
            # closes, the network drops), which would skip the assignment and make
            # every reconnect look like a failure — backoff never resetting, and a
            # max_attempts budget (TCBS: 10) used up by ordinary disconnects.
            self._session_authed = False
            reason = "session_ended"
            try:
                await self._run_session()
            except asyncio.CancelledError:
                self._log.info("Feed cancelled", extra={"feed": self._spec.name})
                raise
            except AuthError as exc:
                reason = "auth_failed"
                self._log.error("Authentication failed — NOT retrying fast: %s", exc,
                                extra={"feed": self._spec.name})
            except ProtocolError as exc:
                reason = "protocol_error"
                self._log.error("Protocol error: %s", exc, extra={"feed": self._spec.name})
            except Exception as exc:
                self._log.error("Session ended: %r", exc, extra={"feed": self._spec.name})

            if self._stopping:
                break

            attempt = 1 if self._session_authed else attempt + 1
            self.stats.reconnects += 1
            self._t.reconnect(self._spec.name, reason)

            if exhausted(self._backoff, attempt):
                self._log.error("Retry budget exhausted (%d) — stopping feed",
                                self._backoff.max_attempts, extra={"feed": self._spec.name})
                break

            delay = (_AUTH_ERROR_DELAY_S if reason == "auth_failed"
                     else delay_seconds(self._backoff, attempt))
            self._log.info("Reconnecting in %.1fs (attempt %d)", delay, attempt,
                           extra={"feed": self._spec.name, "reason": reason})
            await asyncio.sleep(delay)

    # ------------------------------------------------------------------
    async def _run_session(self) -> bool:
        """Returns True once the handshake succeeded (used to reset backoff)."""
        authed = False
        # Optional hook run BEFORE opening the socket: for brokers that need the
        # token present at HTTP upgrade time (SSI with auth_mode=query/header).
        # Called on EVERY attempt, so a token that expired mid-session is
        # refreshed on reconnect.
        prepare = getattr(self._spec, "prepare", None)
        if prepare is not None:
            await prepare()

        async with open_connection(
            self._spec.url,
            connect_timeout_s=self._connect_timeout_s,
            **self._spec.connect_kwargs(),
        ) as ws:
            conn = WebSocketConn(ws)
            self._log.info("Connected", extra={"feed": self._spec.name})

            session = await self._spec.handshake(conn)
            authed = True
            self._session_authed = True
            self.stats.connected = True
            self._log.info("Handshake OK", extra={
                "feed": self._spec.name,
                "session_id": session.session_id,
                "server_heartbeat_timeout_s": session.heartbeat_timeout_s,
                "limits": session.limits or None,
            })
            self._guard_heartbeat(session.heartbeat_timeout_s)

            for msg in self._spec.subscribe_frames():
                await conn.send(msg)
                self._log.info("Subscription sent", extra={
                    "feed": self._spec.name,
                    "frame": (msg[:160] if isinstance(msg, str) else f"<{len(msg)} bytes>"),
                })

            tasks = [asyncio.create_task(self._pump(conn), name=f"{self._spec.name}.pump")]
            hb = self._spec.heartbeat_frame()
            if hb is not None:
                tasks.append(asyncio.create_task(
                    self._heartbeat(conn, hb), name=f"{self._spec.name}.hb"))
            lifetime = self._spec.max_session_lifetime_s()
            if lifetime:
                tasks.append(asyncio.create_task(
                    self._session_timer(lifetime), name=f"{self._spec.name}.ttl"))

            try:
                # Whichever task finishes first tears the session down and it is
                # rebuilt — simple, and always returns to a clean state.
                done, pending = await asyncio.wait(
                    tasks, return_when=asyncio.FIRST_COMPLETED)
                for t in pending:
                    t.cancel()
                await asyncio.gather(*pending, return_exceptions=True)
                for t in done:
                    exc = t.exception()
                    if exc is not None:
                        raise exc
            finally:
                self.stats.connected = False
                for t in tasks:
                    t.cancel()
        return authed

    def _guard_heartbeat(self, server_timeout_s: float | None) -> None:
        """The server announces its timeout; complain if our ping rate is too sparse."""
        if not server_timeout_s:
            return
        interval = self._spec.heartbeat_interval_s()
        if interval * 2 >= server_timeout_s:
            self._log.warning(
                "Heartbeat every %.1fs is too sparse for the server-announced %.1fs timeout",
                interval, server_timeout_s, extra={"feed": self._spec.name})

    async def _heartbeat(self, conn, frame: str | bytes) -> None:
        interval = self._spec.heartbeat_interval_s()
        while not self._stopping:
            await asyncio.sleep(interval)
            await conn.send(frame)

    async def _session_timer(self, lifetime_s: float) -> None:
        await asyncio.sleep(lifetime_s)
        self._log.info("Renewing connection ahead of the session lifetime limit",
                       extra={"feed": self._spec.name, "lifetime_s": lifetime_s})

    async def _pump(self, conn) -> None:
        spec, stats = self._spec, self.stats
        async for raw in conn:
            # Capture time BEFORE any processing.
            recv_ns = time.monotonic_ns()
            recv_ts_ns = time.time_ns()
            stats.messages += 1
            stats.last_message_ns = recv_ns
            self._t.ws_message(spec.name, recv_ns)

            handled = spec.on_message(raw)

            if handled.malformed:
                stats.malformed += 1
                self._t.malformed(spec.name)
                self._log.warning("Unrecognised message: %s",
                                  str(raw)[:200], extra={"feed": spec.name})

            for reply in handled.replies:
                await conn.send(reply)

            for frame in handled.frames:
                stats.frames += 1
                self._t.data_frame(spec.name, frame.wire_code, len(frame.payload), recv_ns)
                if not stats.first_frame_logged:
                    stats.first_frame_logged = True
                    self._log.info(">>> First frame", extra={
                        "feed": spec.name, "wire_code": frame.wire_code,
                        "key": frame.key, "bytes": len(frame.payload)})
                elif stats.frames % self._log_every == 0:
                    self._log.info("Feed running", extra={
                        "feed": spec.name, "frames": stats.frames,
                        "last_wire_code": frame.wire_code})
                await self._on_frame(frame, recv_ns, recv_ts_ns)
