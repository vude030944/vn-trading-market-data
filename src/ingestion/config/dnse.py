"""
DNSE LightSpeed configuration — WebSocket market data.

Reference: docs/dnse/brief/DOCUMENT.md

Two DNSE constraints shape the architecture directly, so they appear here as
explicit parameters instead of being buried in code:
  * A connection lives for AT MOST 8 HOURS (section 5.2) -> reconnecting is the
    normal path, not an exception branch. We renew ahead of the hard limit.
  * A `nonce` may not be reused within 10 minutes and `timestamp` must be within
    +/-5 minutes of server time (section 3.2) -> the host clock must be on NTP.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .base import (
    InfraSettings,
    BackoffSettings,
    env_bool,
    env_csv,
    env_int,
    env_str,
    read_symbol_file,
)

# Market-data channels (DOCUMENT.md section 6.1). Channel names follow
# `<function>.<scope>.<encoding>` where the scope varies by kind — board_id,
# resolution or market_index — hence templates rather than a flat list.
CHANNEL_TEMPLATES = {
    "tick": "tick.{board_id}.{encoding}",
    "tick_extra": "tick_extra.{board_id}.{encoding}",
    "top_price": "top_price.{board_id}.{encoding}",
    "expected_price": "expected_price.{board_id}.{encoding}",
    "security_definition": "security_definition.{board_id}.{encoding}",
    "ohlc": "ohlc.{resolution}.{encoding}",
    "ohlc_closed": "ohlc_closed.{resolution}.{encoding}",
    "market_index": "market_index.{market_index}.{encoding}",
    "estimated_market_index": "estimated_market_index.{market_index}.{encoding}",
    "foreign": "foreign.{board_id}.{encoding}",
    "session": "session.{product_group_id}.{board_id}.{encoding}",
}

VALID_ENCODINGS = ("json", "msgpack")
VALID_RESOLUTIONS = ("1", "3", "5", "15", "30", "1H", "1D", "1W")


@dataclass(frozen=True)
class DNSEConfig:
    enabled: bool = field(default_factory=lambda: env_bool("DNSE_ENABLED", True))
    infra: InfraSettings = field(default_factory=InfraSettings)

    # -- Endpoint ----------------------------------------------------------
    rest_url: str = field(
        default_factory=lambda: env_str("DNSE_REST_URL", "https://openapi.dnse.com.vn")
    )
    stream_url: str = field(
        default_factory=lambda: env_str(
            "DNSE_STREAM_URL", "wss://ws-openapi.dnse.com.vn/v1/stream"
        )
    )
    # Date-based REST version. Omitting it makes the server fall back to
    # 2026-05-07; the docs recommend pinning it explicitly so a breaking-change
    # release cannot drag us along.
    api_version: str = field(
        default_factory=lambda: env_str("DNSE_API_VERSION", "2026-05-07")
    )

    # -- Credentials -------------------------------------------------------
    # For DNSE the api_secret is an HMAC KEY — it must never travel over the wire.
    # signature = HMAC-SHA256(key=api_secret, msg="{api_key}:{timestamp}:{nonce}").
    api_key: str = field(default_factory=lambda: env_str("DNSE_API_KEY"))
    api_secret: str = field(default_factory=lambda: env_str("DNSE_API_SECRET"))

    # Server-imposed constraints (section 3.2). They live here as check values,
    # not as knobs to "loosen until it works": a skewed clock is fixed with NTP,
    # not by widening this window.
    auth_timestamp_skew_s: int = field(
        default_factory=lambda: env_int("DNSE_AUTH_SKEW_S", 300)      # +/-5 minutes
    )
    nonce_ttl_s: int = field(
        default_factory=lambda: env_int("DNSE_NONCE_TTL_S", 600)      # 10 minutes
    )
    auth_deadline_s: int = field(
        default_factory=lambda: env_int("DNSE_AUTH_DEADLINE_S", 30)   # must auth within 30s
    )

    # -- 8-hour connection lifetime ---------------------------------------
    connection_max_lifetime_s: int = field(
        default_factory=lambda: env_int("DNSE_CONN_MAX_LIFETIME_S", 8 * 3600)
    )
    # Open the replacement connection this many seconds before the hard limit,
    # then close the old one, so no tick is lost at the handover.
    connection_renew_lead_s: int = field(
        default_factory=lambda: env_int("DNSE_CONN_RENEW_LEAD_S", 300)
    )

    # -- Encoding and heartbeat -------------------------------------------
    encoding: str = field(default_factory=lambda: env_str("DNSE_ENCODING", "json"))
    # The server pings every 3 minutes and expects a pong within 60s. The docs
    # recommend the client ALSO ping every 25s (the SDK default) in case NAT or
    # a mobile network swallows the server's ping.
    client_ping_interval_s: float = field(
        default_factory=lambda: env_int("DNSE_PING_INTERVAL_S", 25)
    )
    pong_deadline_s: int = field(
        default_factory=lambda: env_int("DNSE_PONG_DEADLINE_S", 60)
    )

    # -- Server-published limits ------------------------------------------
    # `auth_success` returns rate_limit {messages_per_second, subscriptions_max}.
    # This is only a DEFAULT for sanity checks; the real value must be read from
    # the response at runtime because it depends on the key's tier.
    default_max_subscriptions: int = field(
        default_factory=lambda: env_int("DNSE_MAX_SUBSCRIPTIONS", 100)
    )

    # -- Subscriptions -----------------------------------------------------
    channels: tuple[str, ...] = field(
        default_factory=lambda: tuple(env_csv("DNSE_CHANNELS"))
        or ("tick_extra", "top_price", "foreign", "session")
    )
    board_id: str = field(default_factory=lambda: env_str("DNSE_BOARD_ID", "G1"))
    product_group_id: str = field(
        default_factory=lambda: env_str("DNSE_PRODUCT_GROUP_ID", "STO")
    )
    resolutions: tuple[str, ...] = field(
        default_factory=lambda: tuple(env_csv("DNSE_RESOLUTIONS", "1"))
    )
    market_indices: tuple[str, ...] = field(
        default_factory=lambda: tuple(env_csv("DNSE_MARKET_INDICES", "VNINDEX,VN30"))
    )

    # Symbol universe: file first, environment variable as fallback. DNSE
    # requires UPPERCASE symbols.
    symbols_file: str = field(default_factory=lambda: env_str("DNSE_SYMBOLS_FILE"))
    symbols: tuple[str, ...] = field(
        default_factory=lambda: tuple(
            read_symbol_file(env_str("DNSE_SYMBOLS_FILE"))
            if env_str("DNSE_SYMBOLS_FILE")
            else env_csv("DNSE_SYMBOLS")
        )
    )

    # -- Horizontal scaling ------------------------------------------------
    # The server currently reports subscriptions_max = 100. Once the universe
    # exceeds that, run N replicas of the same image, each taking one slice:
    #     DNSE_SHARD_COUNT=3  DNSE_SHARD_INDEX=0|1|2
    # Sharding uses a stable hash of the symbol, so adding or removing symbols
    # does not reshuffle everything, and a symbol always lands on the same replica.
    shard_index: int = field(default_factory=lambda: env_int("DNSE_SHARD_INDEX", 0))
    shard_count: int = field(default_factory=lambda: env_int("DNSE_SHARD_COUNT", 1))

    # -- Connection --------------------------------------------------------
    connect_timeout_s: int = field(
        default_factory=lambda: env_int("DNSE_CONNECT_TIMEOUT_S", 15)
    )
    # DNSE recommends a 60s cap (TCBS says 30s) -> overridden here.
    backoff: BackoffSettings = field(
        default_factory=lambda: BackoffSettings(initial_ms=1_000, max_ms=60_000)
    )

    # -- Kafka destination -------------------------------------------------
    kafka_topic: str = field(
        default_factory=lambda: env_str("DNSE_KAFKA_TOPIC", "dnse.data.raw.market")
    )

    # ------------------------------------------------------------------
    @property
    def shard_symbols(self) -> tuple[str, ...]:
        """The slice of the universe that belongs to this replica."""
        if self.shard_count <= 1:
            return self.symbols
        from zlib import crc32

        return tuple(
            s for s in self.symbols
            if crc32(s.encode("ascii")) % self.shard_count == self.shard_index
        )

    def validate(self) -> None:
        if not self.enabled:
            return
        self.infra.validate()
        self.backoff.validate()

        if not self.api_key or not self.api_secret:
            raise ValueError("Missing DNSE_API_KEY / DNSE_API_SECRET")
        if self.encoding not in VALID_ENCODINGS:
            raise ValueError(
                f"DNSE_ENCODING must be one of {VALID_ENCODINGS}, got {self.encoding!r}"
            )
        if not self.channels:
            raise ValueError("DNSE_CHANNELS is empty — nothing to receive")

        unknown = [c for c in self.channels if c not in CHANNEL_TEMPLATES]
        if unknown:
            raise ValueError(f"Unrecognised DNSE channels: {unknown}")

        bad_res = [r for r in self.resolutions if r not in VALID_RESOLUTIONS]
        if bad_res:
            raise ValueError(f"Invalid resolutions: {bad_res}")

        if any(s != s.upper() for s in self.symbols):
            raise ValueError("DNSE symbols must be UPPERCASE")

        if self.connection_renew_lead_s >= self.connection_max_lifetime_s:
            raise ValueError("connection_renew_lead_s must be less than connection_max_lifetime_s")

        if self.shard_count < 1:
            raise ValueError("DNSE_SHARD_COUNT must be >= 1")
        if not 0 <= self.shard_index < self.shard_count:
            raise ValueError(
                f"DNSE_SHARD_INDEX must be within [0, {self.shard_count}), got {self.shard_index}"
            )

    def __str__(self) -> str:
        src = f"file={self.symbols_file}" if self.symbols_file else "env"
        return (
            f"DNSEConfig(enabled={self.enabled}, stream={self.stream_url}, "
            f"encoding={self.encoding}, version={self.api_version}, "
            f"channels={list(self.channels)}, "
            f"symbols={len(self.shard_symbols)}/{len(self.symbols)}({src}), "
            f"shard={self.shard_index}/{self.shard_count}, "
            f"kafka_topic={self.kafka_topic})"
        )
