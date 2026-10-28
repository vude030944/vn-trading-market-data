"""Simulator settings — environment variables only, all with working defaults."""

from __future__ import annotations

from dataclasses import dataclass, field
from os import getenv


def _str(name: str, default: str) -> str:
    v = getenv(name)
    return default if v is None or v == "" else v


def _int(name: str, default: int) -> int:
    return int(_str(name, str(default)))


def _float(name: str, default: float) -> float:
    return float(_str(name, str(default)))


def _bool(name: str, default: bool) -> bool:
    return _str(name, "1" if default else "0").lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class SimConfig:
    host: str = field(default_factory=lambda: _str("SIM_HOST", "0.0.0.0"))
    ssi_port: int = field(default_factory=lambda: _int("SIM_SSI_PORT", 8001))
    dnse_port: int = field(default_factory=lambda: _int("SIM_DNSE_PORT", 8002))
    tcbs_port: int = field(default_factory=lambda: _int("SIM_TCBS_PORT", 8003))
    stats_port: int = field(default_factory=lambda: _int("SIM_STATS_PORT", 8080))

    # -- market --------------------------------------------------------------
    seed: int = field(default_factory=lambda: _int("SIM_SEED", 7))
    # Matched trades per second across the whole universe. Each trade also moves
    # the book, so total frames/s across the three brokers is roughly 10-20x this.
    trades_per_sec: float = field(default_factory=lambda: _float("SIM_TRADES_PER_SEC", 40))
    # 1 = only produce data inside the real HOSE sessions (Asia/Ho_Chi_Minh);
    # 0 = the market never closes, so a test can run at any hour.
    market_hours: bool = field(default_factory=lambda: _bool("SIM_MARKET_HOURS", False))
    index_interval_s: float = field(default_factory=lambda: _float("SIM_INDEX_INTERVAL_S", 5))
    sd_short_s: int = field(default_factory=lambda: _int("SIM_SD_SHORT_S", 60))
    sd_long_s: int = field(default_factory=lambda: _int("SIM_SD_LONG_S", 900))

    # -- SSI -----------------------------------------------------------------
    ssi_api_key: str = field(default_factory=lambda: _str("SIM_SSI_API_KEY", "sim-ssi-key"))
    ssi_api_secret: str = field(default_factory=lambda: _str("SIM_SSI_API_SECRET", "sim-ssi-secret"))
    # How the stream accepts the token: any | query | header | frame (DOCUMENT.md 10.3).
    ssi_auth_mode: str = field(default_factory=lambda: _str("SIM_SSI_AUTH_MODE", "any"))
    ssi_token_ttl_s: int = field(default_factory=lambda: _int("SIM_SSI_TOKEN_TTL_S", 3600))
    ssi_expires_unit: str = field(default_factory=lambda: _str("SIM_SSI_EXPIRES_UNIT", "ms"))
    ssi_ping_s: float = field(default_factory=lambda: _float("SIM_SSI_PING_S", 30))
    ssi_pong_deadline_s: float = field(default_factory=lambda: _float("SIM_SSI_PONG_DEADLINE_S", 60))

    # -- DNSE ----------------------------------------------------------------
    dnse_api_key: str = field(default_factory=lambda: _str("SIM_DNSE_API_KEY", "sim-dnse-key"))
    dnse_api_secret: str = field(default_factory=lambda: _str("SIM_DNSE_API_SECRET", "sim-dnse-secret"))
    dnse_ping_s: float = field(default_factory=lambda: _float("SIM_DNSE_PING_S", 180))
    dnse_pong_deadline_s: float = field(default_factory=lambda: _float("SIM_DNSE_PONG_DEADLINE_S", 60))
    dnse_auth_deadline_s: float = field(default_factory=lambda: _float("SIM_DNSE_AUTH_DEADLINE_S", 30))
    dnse_max_conn_s: float = field(default_factory=lambda: _float("SIM_DNSE_MAX_CONN_S", 8 * 3600))
    dnse_subscriptions_max: int = field(default_factory=lambda: _int("SIM_DNSE_SUBSCRIPTIONS_MAX", 100))
    # The docs say data is classified by `T` but no sample carries it (11.1).
    # 0 reproduces the samples; 1 adds an INVENTED T = channel function name.
    dnse_send_t: bool = field(default_factory=lambda: _bool("SIM_DNSE_SEND_T", False))

    # -- TCBS ----------------------------------------------------------------
    tcbs_api_key: str = field(default_factory=lambda: _str("SIM_TCBS_API_KEY", "sim-tcbs-key"))
    tcbs_otp: str = field(default_factory=lambda: _str("SIM_TCBS_OTP", "111111"))
    # A fixed token that is always accepted, for TCBS_TOKEN-style provisioning.
    tcbs_static_token: str = field(default_factory=lambda: _str("SIM_TCBS_STATIC_TOKEN", "sim-tcbs-jwt"))
    tcbs_token_ttl_s: int = field(default_factory=lambda: _int("SIM_TCBS_TOKEN_TTL_S", 8 * 3600))
    tcbs_thesis_timeout_s: int = field(default_factory=lambda: _int("SIM_TCBS_THESIS_TIMEOUT_S", 15))
    # The docs say 15; live probing in examples/ observed 30 (DOCUMENT.md 11.4).
    tcbs_ouranos_timeout_s: int = field(default_factory=lambda: _int("SIM_TCBS_OURANOS_TIMEOUT_S", 30))
    tcbs_ouranos_server_ping_s: float = field(default_factory=lambda: _float("SIM_TCBS_OURANOS_PING_S", 10))
    # The audit found futures frames 21/23/24/25/27 on BOTH sockets, the normal
    # one ~1 ms earlier (DOCUMENT.md 11.2).
    tcbs_futures_on_both: bool = field(default_factory=lambda: _bool("SIM_TCBS_FUTURES_ON_BOTH", True))

    # -- chaos -----------------------------------------------------------------
    # Every N seconds drop one random client connection per broker (0 = never),
    # to exercise reconnect + resubscribe end to end.
    chaos_drop_every_s: float = field(default_factory=lambda: _float("SIM_CHAOS_DROP_EVERY_S", 0))
    # Per-connection send queue. DNSE closes a slow consumer with 1013.
    send_queue_max: int = field(default_factory=lambda: _int("SIM_SEND_QUEUE_MAX", 20000))

    # Signs SSI/TCBS tokens, so they stay valid across a simulator restart.
    token_secret: str = field(default_factory=lambda: _str("SIM_TOKEN_SECRET", "marketsim-dev-secret"))

    log_level: str = field(default_factory=lambda: _str("LOG_LEVEL", "INFO"))
