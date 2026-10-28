"""
SSI FastConnect configuration — WebSocket market data.

Reference: docs/ssi/brief/DOCUMENT.md
Everything here belongs to SSI. Never promote anything from this file into
base.py, even if DNSE/TCBS have a field that looks the same.

THREE DOCUMENTED AMBIGUITIES are exposed as tunables rather than hardcoded
(see DOCUMENT.md section 10), because only a real connection can settle them:
  1. 10.1  the endpoint has two conflicting values   -> stream_url
  2. 10.2  expiresAt is seconds in one doc, ms in another -> expires_at_unit
  3. 10.6  does market-data streaming require OTP?   -> require_otp
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .base import InfraSettings, BackoffSettings, env_bool, env_csv, env_int, env_str

# The six topic groups of the DATA channel (DOCUMENT.md section 5.1)
DATA_TOPICS = ("trade", "quote", "room", "put", "oddlot", "market")

# Valid intervals. The market-data page states explicitly "there is no 3m",
# while the heartbeat page shows tick|1m|3m and the SDK exposes
# Timeframe.MINUTE_3 (section 10.4). We follow the market-data page — more
# specific and more recent — but surface the list here so it is easy to change
# once verified against the live feed.
VALID_INTERVALS = ("tick", "1m", "5m")


@dataclass(frozen=True)
class SSIConfig:
    """A single WebSocket connection, DATA channel."""

    enabled: bool = field(default_factory=lambda: env_bool("SSI_ENABLED", True))
    infra: InfraSettings = field(default_factory=InfraSettings)

    # -- Endpoint ----------------------------------------------------------
    api_url: str = field(
        default_factory=lambda: env_str("SSI_API_URL", "https://api.ssi.com.vn")
    )
    # Section 10.1: the API spec says `wss://stream.ssi.com.vn` while every SDK
    # (Python/Node/Go/C#) defaults to `wss://stream.ssi.com.vn/ws/v3`. We default
    # to the SDK value because that is code which actually runs, but BOTH must be
    # tried against the live endpoint.
    stream_url: str = field(
        default_factory=lambda: env_str("SSI_STREAM_URL", "wss://stream.ssi.com.vn/ws/v3")
    )

    # -- Credentials -------------------------------------------------------
    # SSI: apiKey + apiSecret -> accessToken + refreshToken.
    # Completely unlike DNSE (the secret is an HMAC key that never leaves the
    # process) and TCBS (no refresh token at all). That is precisely why
    # credentials do not live in base.py.
    api_key: str = field(default_factory=lambda: env_str("SSI_API_KEY"))
    api_secret: str = field(default_factory=lambda: env_str("SSI_API_SECRET"))

    # Section 10.6: the tutorial says market data does NOT need OTP, while the
    # SDK page describes the `Stream` class as "requires OTP". If the latter is
    # true, a 24/7 collector cannot run unattended. Default follows the API spec
    # (`otp` is optional, only needed for trading rights) — flip to true if the
    # live endpoint disagrees.
    require_otp: bool = field(default_factory=lambda: env_bool("SSI_REQUIRE_OTP", False))
    otp: str = field(default_factory=lambda: env_str("SSI_OTP"))

    # Section 10.2: the guide prints 1779806203 (10 digits = seconds), the API
    # spec prints 1772075293023 (13 digits = milliseconds). "auto" infers from
    # magnitude.
    expires_at_unit: str = field(
        default_factory=lambda: env_str("SSI_EXPIRES_AT_UNIT", "auto")  # auto | s | ms
    )
    # Refresh this many seconds before expiry; do not wait for a 401004.
    token_refresh_lead_s: int = field(
        default_factory=lambda: env_int("SSI_TOKEN_REFRESH_LEAD_S", 300)
    )

    # Section 10.3: the docs never say HOW the token reaches the socket — they
    # only show a `{client_id, api_key, api_secret, access_token}` blob without
    # saying where it goes. All three possibilities are implemented and selected
    # by environment variable so they can be tried without touching code:
    #   query  : ?access_token=<token>   (default — matches how the SDK builds its URL)
    #   header : Authorization: Bearer <token>
    #   frame  : send an auth JSON as the first message and await the reply
    auth_mode: str = field(default_factory=lambda: env_str("SSI_AUTH_MODE", "query"))
    auth_query_param: str = field(
        default_factory=lambda: env_str("SSI_AUTH_QUERY_PARAM", "access_token")
    )

    # -- Subscriptions -----------------------------------------------------
    # Topics look like `<prefix>.<scope>@<interval>`, where scope is a symbol,
    # several symbols joined by '-', a basket name (vn30), an exchange (hose),
    # or '*' for everything within the key's permissions.
    topics: tuple[str, ...] = field(
        default_factory=lambda: tuple(env_csv("SSI_TOPICS")) or (
            "trade.*@tick",
            "quote.*@tick",
            "room.*@tick",
            "put.*@tick",
            "oddlot.*@tick",
            "market.*",          # the `market` topic has NO interval
        )
    )

    # -- Heartbeat ---------------------------------------------------------
    # The server sends PING {method,channel:HEARTBEAT,time} and the client must
    # answer PONG. The docs give NEITHER the server's ping period NOR the reply
    # deadline, so the client also pings on its own schedule to be safe.
    client_ping_interval_s: float = field(
        default_factory=lambda: env_int("SSI_PING_INTERVAL_S", 30)
    )

    # -- Connection --------------------------------------------------------
    connect_timeout_s: int = field(
        default_factory=lambda: env_int("SSI_CONNECT_TIMEOUT_S", 15)
    )
    backoff: BackoffSettings = field(
        default_factory=lambda: BackoffSettings(initial_ms=1_000, max_ms=30_000)
    )

    # -- Kafka destination -------------------------------------------------
    # One Kafka topic for the whole DATA channel; the `market_event` header
    # distinguishes the payload kind, and the payload stays byte-for-byte.
    kafka_topic: str = field(
        default_factory=lambda: env_str("SSI_KAFKA_TOPIC", "ssi.data.raw.market")
    )

    # ------------------------------------------------------------------
    def validate(self) -> None:
        if not self.enabled:
            return
        self.infra.validate()
        self.backoff.validate()

        if not self.api_key or not self.api_secret:
            raise ValueError("Missing SSI_API_KEY / SSI_API_SECRET")
        if self.require_otp and not self.otp:
            raise ValueError("SSI_REQUIRE_OTP=1 but SSI_OTP is missing")
        if self.auth_mode not in ("query", "header", "frame"):
            raise ValueError(
                f"SSI_AUTH_MODE must be query|header|frame, got {self.auth_mode!r}"
            )
        if self.expires_at_unit not in ("auto", "s", "ms"):
            raise ValueError(
                f"SSI_EXPIRES_AT_UNIT must be auto|s|ms, got {self.expires_at_unit!r}"
            )
        if not self.topics:
            raise ValueError("SSI_TOPICS is empty — nothing to receive")

        for t in self.topics:
            prefix = t.split(".", 1)[0]
            if prefix not in DATA_TOPICS:
                raise ValueError(
                    f"Invalid SSI topic {t!r}: prefix must be one of {DATA_TOPICS}"
                )
            if "@" in t:
                interval = t.rsplit("@", 1)[1]
                if interval not in VALID_INTERVALS:
                    raise ValueError(
                        f"SSI topic {t!r}: interval {interval!r} not in {VALID_INTERVALS}"
                    )
                if prefix == "market":
                    raise ValueError(f"The `market` topic takes no interval, got {t!r}")

    def __str__(self) -> str:
        return (
            f"SSIConfig(enabled={self.enabled}, stream={self.stream_url}, "
            f"key={'<set>' if self.api_key else '<missing>'}, "
            f"require_otp={self.require_otp}, topics={len(self.topics)}, "
            f"kafka_topic={self.kafka_topic})"
        )
