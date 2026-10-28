"""Shared across every TCBS feed: the `d|a|||` handshake and control frames."""

from __future__ import annotations

import base64
import json
import logging

from ...core.connection import Conn
from ...core.frame import SessionInfo
from ...core.spec import AuthError, ProtocolError
from . import framing

log = logging.getLogger(__name__)

_AUTH_TIMEOUT_S = 10.0


async def handshake_pipe(conn: Conn, token: str, feed_name: str) -> SessionInfo:
    """
    Handshake for the thesis and ouranos feeds.

    The token must be base64-encoded DIRECTLY, not wrapped in JSON (unlike
    /ws/aither and /ws/nesoi). The docs stress: wait for
    `d|0|{"success":true}` before sending any subscription.

    We also capture `d|33|N` to learn the REAL timeout the server announces —
    the docs say ouranos is 15 but live probing observed 30.
    """
    b64 = base64.b64encode(token.encode("utf-8")).decode("ascii")
    await conn.send(framing.AUTH_FRAME.format(b64_token=b64))

    session = SessionInfo()
    while True:
        raw = await conn.recv(timeout=_AUTH_TIMEOUT_S)
        if not isinstance(raw, str):
            continue

        timeout = framing.parse_config_timeout(raw)
        if timeout is not None:
            session.heartbeat_timeout_s = timeout
            continue

        if raw.startswith(framing.AUTH_RESPONSE_PREFIX):
            body = raw[len(framing.AUTH_RESPONSE_PREFIX) :]
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError as exc:
                raise ProtocolError(f"Auth response is not JSON: {body[:200]}") from exc
            if parsed.get("success"):
                return session
            raise AuthError(f"TCBS rejected authentication: {parsed.get('error')}")

        log.debug("Ignoring pre-auth frame: %s", raw[:120], extra={"feed": feed_name})
