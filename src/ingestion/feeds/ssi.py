"""
SSI FastConnect feed — DATA channel.

HONEST WARNING: the SSI documentation does NOT specify how the token reaches the
WebSocket (DOCUMENT.md section 10.3). It only shows a
`{client_id, api_key, api_secret, access_token}` blob without saying where it
goes — query string? header? first frame?

Approach taken here: implement ALL THREE and select with `SSI_AUTH_MODE`. This
is deliberate — when something is unknown, parameterise the unknown instead of
guessing and burying the guess in code. Once verified against the live market,
changing one environment variable is enough; no code change, no rebuild.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Iterable
from urllib.parse import quote

import httpx

from ..config.ssi import SSIConfig
from ..core.connection import Conn
from ..core.frame import Frame, Handled, SessionInfo
from ..core.spec import AuthError, FeedSpec, ProtocolError

log = logging.getLogger(__name__)

_TOKEN_PATH = "/api/v3/auth/token"
_REFRESH_PATH = "/api/v3/auth/refresh"
_HANDSHAKE_TIMEOUT_S = 15.0


def normalize_expiry(value: float | int | None, unit: str) -> float | None:
    """
    Section 10.2: the guide prints `1779806203` (seconds) while the API spec
    prints `1772075293023` (milliseconds) — same field, two units. 'auto' infers
    from magnitude: 1e11 seconds is the year 5138, so anything larger must be ms.
    """
    if value is None:
        return None
    v = float(value)
    if unit == "s":
        return v
    if unit == "ms":
        return v / 1000.0
    return v / 1000.0 if v > 1e11 else v


class TokenManager:
    """Holds the access token and refreshes it BEFORE expiry."""

    def __init__(self, cfg: SSIConfig) -> None:
        self._cfg = cfg
        self._access: str = ""
        self._refresh: str = ""
        self._expires_at: float = 0.0

    def invalidate(self) -> None:
        """Forget the access token (the server rejected it); the refresh token stays."""
        self._access = ""

    def _needs_refresh(self) -> bool:
        return (not self._access
                or time.time() >= self._expires_at - self._cfg.token_refresh_lead_s)

    async def get(self) -> str:
        if self._needs_refresh():
            await (self._do_refresh() if self._refresh else self._issue())
        return self._access

    async def _post(self, path: str, body: dict) -> dict:
        url = self._cfg.api_url.rstrip("/") + path
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(url, json=body,
                                         headers={"Content-Type": "application/json"})
        except httpx.HTTPError as exc:
            raise AuthError(f"Request to {url} failed: {exc!r}") from exc
        if resp.status_code != 200:
            raise AuthError(f"{path} returned HTTP {resp.status_code}: {resp.text[:200]}")
        return resp.json()

    def _absorb(self, data: dict) -> None:
        self._access = data.get("accessToken", "")
        self._refresh = data.get("refreshToken", "") or self._refresh
        if not self._access:
            raise AuthError(f"Response has no accessToken: {str(data)[:200]}")
        exp = normalize_expiry(data.get("expiresAt"), self._cfg.expires_at_unit)
        # With no expiresAt, assume a short life — safer than using a dead token.
        self._expires_at = exp if exp else time.time() + 3600

    async def _issue(self) -> None:
        body = {"apiKey": self._cfg.api_key, "apiSecret": self._cfg.api_secret}
        if self._cfg.require_otp and self._cfg.otp:
            body["otp"] = self._cfg.otp
        self._absorb(await self._post(_TOKEN_PATH, body))
        log.info("Obtained SSI access token",
                 extra={"expires_in_s": int(self._expires_at - time.time())})

    async def _do_refresh(self) -> None:
        try:
            self._absorb(await self._post(_REFRESH_PATH, {"refreshToken": self._refresh}))
            log.info("Refreshed SSI token")
        except AuthError as exc:
            log.warning("Refresh failed (%s) — minting a brand new token", exc)
            self._refresh = ""
            await self._issue()


class SSISpec:
    source = "ssi"
    name = "ssi.market"

    def __init__(self, cfg: SSIConfig) -> None:
        self._cfg = cfg
        self._tokens = TokenManager(cfg)
        self._token: str = ""
        self.url = cfg.stream_url          # may be rewritten in prepare()
        # True while the current token has not yet carried a connection through
        # its handshake. If the next attempt finds it still True, the server most
        # likely refused the token (401003 Invalid / 401004 Expired at the upgrade
        # — the docs say "get a new token"), so it is dropped instead of reused forever.
        self._token_unproven = False

    # -- connection ------------------------------------------------------
    async def prepare(self) -> None:
        """
        Fetch the token BEFORE opening the socket — required for auth_mode
        query/header because the token must be present at the HTTP upgrade.
        """
        if self._token_unproven:
            self._tokens.invalidate()
        self._token_unproven = True
        self._token = await self._tokens.get()
        if self._cfg.auth_mode == "query":
            sep = "&" if "?" in self._cfg.stream_url else "?"
            self.url = (f"{self._cfg.stream_url}{sep}"
                        f"{self._cfg.auth_query_param}={quote(self._token)}")

    def connect_kwargs(self) -> dict:
        if self._cfg.auth_mode == "header" and self._token:
            return {"additional_headers": {"Authorization": f"Bearer {self._token}"}}
        return {}

    async def handshake(self, conn: Conn) -> SessionInfo:
        if self._cfg.auth_mode != "frame":
            # query/header: the token travelled with the upgrade, no handshake step —
            # the socket being open means it was accepted.
            self._token_unproven = False
            return SessionInfo()

        await conn.send(json.dumps({
            "method": "AUTH", "channel": "DATA", "access_token": self._token,
        }))
        raw = await conn.recv(timeout=_HANDSHAKE_TIMEOUT_S)
        try:
            msg = json.loads(raw if isinstance(raw, str) else raw.decode("utf-8"))
        except Exception as exc:
            raise ProtocolError(f"Auth response is not JSON: {str(raw)[:200]}") from exc
        if str(msg.get("status", "")).lower() in ("error", "fail", "false"):
            raise AuthError(f"SSI rejected authentication: {str(msg)[:200]}")
        self._token_unproven = False
        return SessionInfo(session_id=msg.get("connectionId"))

    def max_session_lifetime_s(self) -> float | None:
        return None

    # -- heartbeat -------------------------------------------------------
    def heartbeat_frame(self) -> str:
        return json.dumps({"method": "PING", "channel": "HEARTBEAT",
                           "time": time.strftime("%d-%m-%Y %H-%M-%S")})

    def heartbeat_interval_s(self) -> float:
        return self._cfg.client_ping_interval_s

    # -- subscribe -------------------------------------------------------
    def subscribe_frames(self) -> Iterable[str]:
        return [json.dumps({"method": "SUBSCRIBE", "channel": "DATA",
                            "topics": list(self._cfg.topics)})]

    # -- inbound data ----------------------------------------------------
    @staticmethod
    def _wire_code(topic: str) -> str:
        """`trade.SSI@1m` -> `trade_1m`; `market.HOSE` -> `market`."""
        if topic.startswith("market."):
            return "market"
        head, _, interval = topic.partition("@")
        prefix = head.split(".", 1)[0]
        return f"{prefix}_{interval or 'tick'}"

    def on_message(self, raw: str | bytes) -> Handled:
        try:
            msg = json.loads(raw if isinstance(raw, str) else raw.decode("utf-8"))
        except Exception:
            return Handled(malformed=True)
        if not isinstance(msg, dict):
            return Handled(malformed=True)

        channel = msg.get("channel")
        if channel == "HEARTBEAT" or msg.get("method") in ("PING", "PONG"):
            if msg.get("method") == "PING":
                # The server demands a correctly shaped PONG; not answering closes the link.
                return Handled(replies=(json.dumps({
                    "method": "PONG", "channel": "HEARTBEAT", "time": msg.get("time"),
                }),))
            return Handled()

        topic = msg.get("topic")
        if not topic:
            return Handled(malformed=True)

        data = msg.get("data")
        key = None
        if isinstance(data, dict):
            key = data.get("s") or data.get("market") or data.get("b")

        # Forward the ORIGINAL message verbatim rather than json.dumps(data), so the
        # exact received bytes stay replayable and comparable later.
        payload = raw if isinstance(raw, (str, bytes)) else json.dumps(msg)
        return Handled(
            frames=(
                Frame(topic=self._cfg.kafka_topic, key=str(key) if key else None,
                      wire_code=self._wire_code(str(topic)), payload=payload),
            )
        )


def build_specs(cfg: SSIConfig) -> list[FeedSpec]:
    return [SSISpec(cfg)] if cfg.enabled else []
