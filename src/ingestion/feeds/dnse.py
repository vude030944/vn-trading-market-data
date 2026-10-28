"""
DNSE LightSpeed feed — wss://ws-openapi.dnse.com.vn/v1/stream

Three specifics handled here:

  1. SIGNATURE-BASED AUTH; THE SECRET IS NEVER SENT.
     signature = HMAC-SHA256(key=api_secret, msg="{api_key}:{timestamp}:{nonce}")
     `api_secret` never leaves the process. Every reconnect MUST mint a fresh
     timestamp and nonce (a nonce reused within 10 minutes is rejected).

  2. A CONNECTION LIVES ONLY 8 HOURS. We renew BEFORE the limit rather than
     waiting to be cut off — see `max_session_lifetime_s`.

  3. APPLICATION-LEVEL PING/PONG. The server pings every 3 minutes and expects a
     pong within 60s; we echo `timestamp` back so it can measure round-trip.
     We also ping every 25s in case NAT or a mobile network eats the server ping.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from typing import Any, Iterable

from ..config.dnse import CHANNEL_TEMPLATES, DNSEConfig
from ..core.connection import Conn
from ..core.frame import Frame, Handled, SessionInfo
from ..core.spec import AuthError, FeedSpec, ProtocolError

log = logging.getLogger(__name__)

# Only these actions are control messages. The docs warn explicitly: do NOT infer
# "has an action field => control", because some data messages
# (estimated_market_index) carry BOTH `action` and `T`.
CONTROL_ACTIONS = frozenset(
    {"welcome", "auth_success", "subscribed", "unsubscribed",
     "ping", "pong", "connection_expired", "error"}
)

_HANDSHAKE_TIMEOUT_S = 20.0


class DNSESpec:
    source = "dnse"
    name = "dnse.market"

    def __init__(self, cfg: DNSEConfig) -> None:
        self._cfg = cfg
        sep = "&" if "?" in cfg.stream_url else "?"
        self.url = f"{cfg.stream_url}{sep}encoding={cfg.encoding}"
        self._binary = cfg.encoding == "msgpack"
        self._unpack = self._make_unpacker() if self._binary else None

    @staticmethod
    def _make_unpacker():
        try:
            import msgpack
        except ImportError as exc:                      # pragma: no cover
            raise RuntimeError("DNSE_ENCODING=msgpack requires the `msgpack` package") from exc
        return lambda b: msgpack.unpackb(b, raw=False)

    def connect_kwargs(self) -> dict:
        return {}

    # -- handshake -------------------------------------------------------
    def _auth_message(self) -> str:
        ts = int(time.time())
        nonce = str(int(time.time() * 1_000_000))     # microseconds -> always unique
        msg = f"{self._cfg.api_key}:{ts}:{nonce}"
        sig = hmac.new(
            self._cfg.api_secret.encode("utf-8"), msg.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return json.dumps({
            "action": "auth", "api_key": self._cfg.api_key,
            "signature": sig, "timestamp": ts, "nonce": nonce,
        })

    async def handshake(self, conn: Conn) -> SessionInfo:
        session = SessionInfo()

        # 1. welcome (carries session_id and the "authenticate within 30 seconds" note)
        welcome = self._decode(await conn.recv(timeout=_HANDSHAKE_TIMEOUT_S))
        if welcome.get("action") != "welcome":
            raise ProtocolError(f"Expected 'welcome', received: {str(welcome)[:200]}")
        session.session_id = welcome.get("session_id")

        # 2. auth
        await conn.send(self._auth_message())
        while True:
            msg = self._decode(await conn.recv(timeout=_HANDSHAKE_TIMEOUT_S))
            action = msg.get("action")
            if action == "auth_success":
                # The REAL per-tier limits — always use these rather than trusting
                # the 100 printed in the documentation.
                session.limits = dict(msg.get("rate_limit") or {})
                self._check_subscription_budget(session.limits)
                return session
            if action == "error":
                raise AuthError(f"{msg.get('code')}: {msg.get('message')}")
            if action in ("ping",):
                await conn.send(self._pong(msg))
                continue
            log.debug("Ignoring frame during auth: %s", str(msg)[:160])

    def _check_subscription_budget(self, limits: dict) -> None:
        cap = limits.get("subscriptions_max") or self._cfg.default_max_subscriptions
        want = len(list(self._channels()))
        if cap and want > cap:
            log.error(
                "Subscription count exceeds the server limit — raise DNSE_SHARD_COUNT",
                extra={"requested": want, "subscriptions_max": cap,
                       "shard": f"{self._cfg.shard_index}/{self._cfg.shard_count}"},
            )

    def max_session_lifetime_s(self) -> float | None:
        c = self._cfg
        return max(60.0, c.connection_max_lifetime_s - c.connection_renew_lead_s)

    # -- heartbeat -------------------------------------------------------
    def heartbeat_frame(self) -> str:
        return json.dumps({"action": "ping", "timestamp": int(time.time() * 1000)})

    def heartbeat_interval_s(self) -> float:
        return self._cfg.client_ping_interval_s

    @staticmethod
    def _pong(ping_msg: dict) -> str:
        # Echo the timestamp back so the server can measure latency; omitting it
        # still keeps the link alive, it just loses the measurement.
        return json.dumps({"action": "pong", "timestamp": ping_msg.get("timestamp")})

    # -- subscribe -------------------------------------------------------
    def _channels(self) -> Iterable[dict[str, Any]]:
        """Build the channel list from templates; each channel is one subscription."""
        c = self._cfg
        symbols = list(c.shard_symbols)
        for name in c.channels:
            tpl = CHANNEL_TEMPLATES[name]
            if "{resolution}" in tpl:
                for res in c.resolutions:
                    yield {"name": tpl.format(resolution=res, encoding=c.encoding),
                           "symbols": symbols}
            elif "{market_index}" in tpl:
                for idx in c.market_indices:
                    yield {"name": tpl.format(market_index=idx, encoding=c.encoding),
                           "symbols": []}
            elif "{product_group_id}" in tpl:
                yield {"name": tpl.format(product_group_id=c.product_group_id,
                                          board_id=c.board_id, encoding=c.encoding),
                       "symbols": []}
            else:
                yield {"name": tpl.format(board_id=c.board_id, encoding=c.encoding),
                       "symbols": symbols}

    def subscribe_frames(self) -> Iterable[str]:
        channels = list(self._channels())
        if not channels:
            return []
        return [json.dumps({"action": "subscribe", "channels": channels})]

    # -- inbound data ----------------------------------------------------
    def _decode(self, raw: str | bytes) -> dict:
        if self._binary and isinstance(raw, (bytes, bytearray)):
            return self._unpack(raw)            # type: ignore[misc]
        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode("utf-8", "replace")
        return json.loads(raw)

    def on_message(self, raw: str | bytes) -> Handled:
        try:
            msg = self._decode(raw)
        except Exception:
            return Handled(malformed=True)
        if not isinstance(msg, dict):
            return Handled(malformed=True)

        action = msg.get("action")
        if action in CONTROL_ACTIONS:
            if action == "ping":
                return Handled(replies=(self._pong(msg),))
            if action == "error":
                log.error("DNSE reported an error", extra={"code": msg.get("code"),
                                                          "message": msg.get("message")})
            elif action == "connection_expired":
                # Normal, not an error: the 8-hour limit. The engine reconnects.
                log.info("DNSE signalled connection expiry — will reconnect",
                         extra={"code": msg.get("code")})
            return Handled()

        # Data. `T` is the field the docs say to classify by, yet NO sample payload
        # in the documentation contains it -> its value set is unknown. When T is
        # absent we tag 'unknown' and STILL FORWARD, never discarding data we do
        # not yet understand.
        wire = str(msg.get("T") or "unknown")
        key = msg.get("symbol") or msg.get("indexName")
        return Handled(
            frames=(
                Frame(
                    topic=self._cfg.kafka_topic,
                    key=str(key) if key else None,
                    wire_code=wire,
                    # Keep the original bytes: msgpack stays bytes, json stays text.
                    payload=raw if isinstance(raw, (bytes, str)) else str(raw),
                ),
            )
        )


def build_specs(cfg: DNSEConfig) -> list[FeedSpec]:
    return [DNSESpec(cfg)] if cfg.enabled else []
