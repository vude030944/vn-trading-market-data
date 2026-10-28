"""
TCBS token source — SHARED by all three feeds.

This is where the TCBS "one token" constraint becomes code: a single
`TokenProvider` instance held by all three specs. That constraint is precisely
why TCBS must be ONE service rather than three.

The token lives 8 hours and there is NO refresh token — minting a new one
requires an OTP from the TCInvest app. So the provider does two things only:
hold the token, and SHOUT before it expires so an operator can supply a new one.
"""

from __future__ import annotations

import asyncio
import logging
import time

import httpx

from ...config.tcbs import TCBSConfig
from ...core.spec import AuthError

log = logging.getLogger(__name__)

_TOKEN_PATH = "/gaia/v1/oauth2/openapi/token"


class TokenProvider:
    def __init__(self, cfg: TCBSConfig) -> None:
        self._cfg = cfg
        self._token: str = cfg.token
        self._issued_at: float = time.time() if cfg.token else 0.0
        self._warned = False
        # The three feeds start together and all find no token. Without this lock
        # each would exchange the SAME one-time OTP — the later ones fail.
        self._lock = asyncio.Lock()

    @property
    def expires_at(self) -> float:
        return self._issued_at + self._cfg.token_ttl_s

    def seconds_left(self) -> float:
        return self.expires_at - time.time() if self._token else 0.0

    async def get(self) -> str:
        """The current token; mints one if absent and apiKey + OTP are available."""
        if not self._token:
            async with self._lock:
                if not self._token:
                    await self._issue()
        self._warn_if_expiring()
        return self._token

    def _warn_if_expiring(self) -> None:
        left = self.seconds_left()
        if left <= 0:
            raise AuthError(
                "TCBS token has expired and there is no refresh token — a new OTP "
                "from the TCInvest app is required, then reload via TCBS_TOKEN"
            )
        if left <= self._cfg.token_refresh_lead_s and not self._warned:
            self._warned = True
            log.warning(
                "TCBS token expiring soon — MANUAL ACTION REQUIRED (no refresh token)",
                extra={"seconds_left": int(left)},
            )

    async def _issue(self) -> None:
        if not (self._cfg.api_key and self._cfg.otp):
            raise AuthError("No TCBS_TOKEN and not enough TCBS_API_KEY + TCBS_OTP")
        url = self._cfg.rest_url.rstrip("/") + _TOKEN_PATH
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    url,
                    json={"apiKey": self._cfg.api_key, "otp": self._cfg.otp},
                    headers={"Content-Type": "application/json"},
                )
        except httpx.HTTPError as exc:
            raise AuthError(f"Request to {url} failed: {exc!r}") from exc

        if resp.status_code != 200:
            raise AuthError(f"TCBS token request returned HTTP {resp.status_code}: {resp.text[:200]}")
        token = resp.json().get("token")
        if not token:
            raise AuthError(f"TCBS token response has no 'token' field: {resp.text[:200]}")

        self._token = token
        self._issued_at = time.time()
        self._warned = False
        log.info("Obtained TCBS token", extra={"ttl_s": self._cfg.token_ttl_s})
