"""
TCBS iFlash Open API configuration — WebSocket market data.

Reference: docs/tcbs/brief/DOCUMENT.md

WHY THIS FILE IS NESTED WHILE SSI/DNSE ARE FLAT:
    TCBS does not have "a connection" — it has FIVE physical endpoints, each a
    different dialect: different URL, different auth syntax, different heartbeat
    frame, different timeout (15s / 15s / 7s / 45s) and a different data format.
    Forcing them into a flat class like SSIConfig would mean inventing fields
    such as `heartbeat_frame_2`, so each feed gets its own dataclass here.

    This is exactly why the natural unit of configuration is (broker, feed)
    rather than (broker) — but only TCBS needs it, so SSI/DNSE do not carry it.

OPERATIONAL WARNING:
    The JWT lives for 8 hours and there is NO refresh token; a new one requires
    an OTP from the TCInvest app. This is the harshest constraint of the three
    brokers for a 24/7 service — see `token_ttl_s` / `token_refresh_lead_s`.
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

# ---------------------------------------------------------------------------
# Feeds
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FeedSettings:
    """
    What every TCBS WebSocket connection has in common.

    `heartbeat_timeout_s` is only a DEFAULT. The server announces the real
    threshold at runtime (`d|33|N` for thesis/ouranos, `pingTimeout|N` for
    aither/nesoi), and the real value has already disagreed with the docs: the
    documentation says ouranos is 15, live probing showed 30. Code must always
    prefer what the server sends.
    """

    enabled: bool
    path: str                    # appended to base_ws_url
    heartbeat_frame: str
    heartbeat_interval_s: float = 2.0     # all five feeds use 2 seconds
    heartbeat_timeout_s: int = 15         # default, overridden at runtime
    kafka_topic: str = ""


@dataclass(frozen=True)
class ThesisFeedSettings(FeedSettings):
    """Price board — endpoint /ws/thesis/v1/stream/{normal,derivative}."""

    # Channel codes sent inside `d|s|tk|<codes>|<symbols>`.
    #   bi=s|1  op=s|2  fe=s|3  bp=s|4  mp=s|5  tm=s|6  tmh=s|22
    channel_codes: tuple[str, ...] = ("bp", "bi", "tm", "mp", "op", "fe")

    # Subscribing by exchange / index / put-through (cash feed only).
    floors: tuple[str, ...] = ()
    indices: tuple[str, ...] = ()
    pt_floors: tuple[str, ...] = ()
    symbols: tuple[str, ...] = ()

    # Snapshot request `d|r|tk||<symbols>` returns s|38.
    # TCBS is the ONLY one of the three brokers offering this; worth issuing
    # immediately after every (re)connect.
    snapshot_on_connect: bool = True


@dataclass(frozen=True)
class OuranosFeedSettings(FeedSettings):
    """
    Price history and supply/demand — endpoint /ws/ouranos/v1/stream.

    The ONLY TCBS source carrying a real exchange timestamp (`timeSec`, epoch
    seconds) and the aggressor side (`action` BU/SD). The thesis feeds carry
    nothing comparable.
    """

    codes: tuple[str, ...] = ("C001", "C002S60", "C002S900")
    tickers: tuple[str, ...] = ()
    # The per-frame symbol limit is UNDOCUMENTED, so chunk conservatively and
    # any universe size will subscribe successfully — same approach as examples/.
    subscribe_chunk: int = 100


# ---------------------------------------------------------------------------
# Broker
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TCBSConfig:
    enabled: bool = field(default_factory=lambda: env_bool("TCBS_ENABLED", True))
    infra: InfraSettings = field(default_factory=InfraSettings)

    # -- Endpoints ---------------------------------------------------------
    rest_url: str = field(
        default_factory=lambda: env_str("TCBS_REST_URL", "https://openapi.tcbs.com.vn")
    )
    base_ws_url: str = field(
        default_factory=lambda: env_str("TCBS_WS_URL", "wss://openapi.tcbs.com.vn")
    )

    # -- Credentials -------------------------------------------------------
    # apiKey (created in TCInvest) + otp -> JWT via POST /gaia/v1/oauth2/openapi/token
    api_key: str = field(default_factory=lambda: env_str("TCBS_API_KEY"))
    otp: str = field(default_factory=lambda: env_str("TCBS_OTP"))
    # Allows injecting a pre-obtained token for a manual token-provisioning flow.
    token: str = field(default_factory=lambda: env_str("TCBS_TOKEN"))

    token_ttl_s: int = field(
        default_factory=lambda: env_int("TCBS_TOKEN_TTL_S", 8 * 3600)
    )
    # There is NO refresh token: once expired a fresh OTP is required. Warn early
    # so an operator can supply a new token instead of the feed dying mid-session.
    token_refresh_lead_s: int = field(
        default_factory=lambda: env_int("TCBS_TOKEN_REFRESH_LEAD_S", 1800)
    )

    # -- Feed: cash price board -------------------------------------------
    stock: ThesisFeedSettings = field(
        default_factory=lambda: ThesisFeedSettings(
            enabled=env_bool("TCBS_STOCK_ENABLED", True),
            path="/ws/thesis/v1/stream/normal",
            heartbeat_frame="d|p|||",
            heartbeat_timeout_s=env_int("TCBS_STOCK_HB_TIMEOUT_S", 15),
            kafka_topic=env_str("TCBS_STOCK_KAFKA_TOPIC", "tcbs.data.raw.stock"),
            channel_codes=tuple(
                env_csv("TCBS_STOCK_CHANNELS", "bp,bi,tm,mp,op,fe")
            ),
            floors=tuple(env_csv("TCBS_FLOORS", "1,2,3,4,5,7,8,9")),
            indices=tuple(env_csv("TCBS_INDICES", "1,2,3,4,5,7,8,9")),
            pt_floors=tuple(env_csv("TCBS_PT_FLOORS", "1,2,3")),
            symbols=tuple(
                read_symbol_file(env_str("TCBS_SYMBOLS_FILE"))
                if env_str("TCBS_SYMBOLS_FILE")
                else env_csv("TCBS_SYMBOLS")
            ),
        )
    )

    # -- Feed: derivatives price board ------------------------------------
    # `dtn` is NOT in the documentation, but an audit of 6.1M messages in
    # examples/ showed it unlocks channel s|42 — the 10-level depth book, which
    # is ~94% of the futures topic's traffic. Dropping this code loses the single
    # largest data channel TCBS offers.
    derivative: ThesisFeedSettings = field(
        default_factory=lambda: ThesisFeedSettings(
            enabled=env_bool("TCBS_DERIVATIVE_ENABLED", True),
            path="/ws/thesis/v1/stream/derivative",
            heartbeat_frame="d|p|||",
            heartbeat_timeout_s=env_int("TCBS_DERIV_HB_TIMEOUT_S", 15),
            kafka_topic=env_str("TCBS_DERIV_KAFKA_TOPIC", "tcbs.data.raw.future"),
            channel_codes=tuple(
                env_csv("TCBS_DERIV_CHANNELS", "bp,bi,tm,mp,op,fe,dtn")
            ),
            symbols=tuple(env_csv("TCBS_FUTURES_SYMBOLS")),
        )
    )

    # -- Feed: ouranos -----------------------------------------------------
    ouranos: OuranosFeedSettings = field(
        default_factory=lambda: OuranosFeedSettings(
            enabled=env_bool("TCBS_OURANOS_ENABLED", True),
            path="/ws/ouranos/v1/stream",
            heartbeat_frame="d|po",          # DIFFERENT from the thesis feeds
            heartbeat_timeout_s=env_int("TCBS_OURANOS_HB_TIMEOUT_S", 15),
            kafka_topic=env_str("TCBS_OURANOS_KAFKA_TOPIC", "tcbs.data.raw.ouranos"),
            codes=tuple(env_csv("TCBS_OURANOS_CODES", "C001,C002S60,C002S900")),
            tickers=tuple(
                read_symbol_file(env_str("TCBS_OURANOS_SYMBOLS_FILE"))
                if env_str("TCBS_OURANOS_SYMBOLS_FILE")
                else env_csv("TCBS_OURANOS_TICKERS")
            ),
            subscribe_chunk=env_int("TCBS_OURANOS_SUB_CHUNK", 100),
        )
    )

    # -- Feed: private order streams (disabled by default) ----------------
    # /ws/aither (cash, 7s timeout) and /ws/nesoi (derivatives, 45s timeout).
    # Not market data; the auth syntax also differs entirely:
    # authenticate|base64({"jwt":token}).
    private_stock: FeedSettings = field(
        default_factory=lambda: FeedSettings(
            enabled=env_bool("TCBS_PRIVATE_STOCK_ENABLED", False),
            path="/ws/aither",
            heartbeat_frame="ping|1",
            heartbeat_timeout_s=env_int("TCBS_AITHER_HB_TIMEOUT_S", 7),
            kafka_topic=env_str("TCBS_AITHER_KAFKA_TOPIC", "tcbs.data.raw.stock_order"),
        )
    )
    private_derivative: FeedSettings = field(
        default_factory=lambda: FeedSettings(
            enabled=env_bool("TCBS_PRIVATE_DERIV_ENABLED", False),
            path="/ws/nesoi",
            heartbeat_frame="ping|1",
            heartbeat_timeout_s=env_int("TCBS_NESOI_HB_TIMEOUT_S", 45),
            kafka_topic=env_str("TCBS_NESOI_KAFKA_TOPIC", "tcbs.data.raw.deriv_order"),
        )
    )

    # -- Connection --------------------------------------------------------
    connect_timeout_s: int = field(
        default_factory=lambda: env_int("TCBS_CONNECT_TIMEOUT_S", 15)
    )
    # TCBS recommends min(2^n, 30) seconds, at most 10 attempts.
    backoff: BackoffSettings = field(
        default_factory=lambda: BackoffSettings(
            initial_ms=1_000, max_ms=30_000, max_attempts=10
        )
    )

    # ------------------------------------------------------------------
    @property
    def feeds(self) -> tuple[FeedSettings, ...]:
        """Every enabled feed, in declaration order."""
        candidates = (
            self.stock,
            self.derivative,
            self.ouranos,
            self.private_stock,
            self.private_derivative,
        )
        return tuple(f for f in candidates if f.enabled)

    def url_of(self, feed: FeedSettings) -> str:
        return self.base_ws_url.rstrip("/") + feed.path

    # ------------------------------------------------------------------
    def validate(self) -> None:
        if not self.enabled:
            return
        self.infra.validate()
        self.backoff.validate()

        if not self.token and not (self.api_key and self.otp):
            raise ValueError(
                "TCBS needs TCBS_TOKEN, or TCBS_API_KEY + TCBS_OTP to mint one"
            )
        if self.token_refresh_lead_s >= self.token_ttl_s:
            raise ValueError("token_refresh_lead_s must be less than token_ttl_s")

        active = self.feeds
        if not active:
            raise ValueError("No TCBS feed is enabled — nothing to receive")

        for f in active:
            if not f.kafka_topic:
                raise ValueError(f"Feed {f.path} has no kafka_topic")
            if f.heartbeat_interval_s <= 0:
                raise ValueError(f"Feed {f.path}: heartbeat_interval_s must be > 0")
            # Pinging less often than the timeout is suicide, especially on
            # /ws/aither which only tolerates 7 seconds.
            if f.heartbeat_interval_s * 2 >= f.heartbeat_timeout_s:
                raise ValueError(
                    f"Feed {f.path}: a heartbeat every {f.heartbeat_interval_s}s is too "
                    f"sparse for a {f.heartbeat_timeout_s}s timeout"
                )

        if self.stock.enabled and not (
            self.stock.floors or self.stock.indices
            or self.stock.symbols or self.stock.pt_floors
        ):
            raise ValueError("Stock feed enabled but no floors/indices/symbols/pt_floors")
        if self.derivative.enabled and not self.derivative.symbols:
            raise ValueError("Derivative feed enabled but TCBS_FUTURES_SYMBOLS is missing")
        if self.ouranos.enabled and not (self.ouranos.tickers and self.ouranos.codes):
            raise ValueError("Ouranos feed enabled but tickers or codes are missing")

    def __str__(self) -> str:
        feeds = ", ".join(f.path.rsplit("/", 1)[-1] for f in self.feeds)
        return (
            f"TCBSConfig(enabled={self.enabled}, ws={self.base_ws_url}, "
            f"token={'<set>' if self.token else '<via OTP>'}, "
            f"feeds=[{feeds}])"
        )
