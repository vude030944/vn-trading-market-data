"""
Stateless signed tokens, like the brokers' real JWTs: a simulator restart does not
forget them (a real broker restart does not log every client out).

    <prefix><base64url(generation.expiry.nonce)>.<hmac>

`revoke_all()` bumps the generation, so every token issued before it is rejected
as INVALID — the way to exercise a client's "token refused, get a new one" path.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import time

VALID, INVALID, EXPIRED = "valid", "invalid", "expired"


class SignedTokens:
    def __init__(self, secret: str, prefix: str) -> None:
        self._key = secret.encode()
        self._prefix = prefix
        self.generation = 0

    def _sig(self, body: str) -> str:
        return hmac.new(self._key, (self._prefix + body).encode(), hashlib.sha256).hexdigest()[:32]

    def issue(self, ttl_s: float) -> tuple[str, float]:
        expiry = time.time() + ttl_s
        raw = f"{self.generation}.{int(expiry)}.{secrets.token_hex(8)}"
        body = base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")
        return f"{self._prefix}{body}.{self._sig(body)}", expiry

    def check(self, token: str | None) -> str:
        if not token or not token.startswith(self._prefix) or "." not in token:
            return INVALID
        body, _, sig = token[len(self._prefix):].rpartition(".")
        if not hmac.compare_digest(sig, self._sig(body)):
            return INVALID
        try:
            gen, expiry, _ = base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)).decode().split(".")
        except Exception:
            return INVALID
        if int(gen) != self.generation:
            return INVALID
        return EXPIRED if int(expiry) < time.time() else VALID

    def revoke_all(self) -> None:
        self.generation += 1
