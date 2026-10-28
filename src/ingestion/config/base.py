"""
Shared infrastructure configuration — the parts WE own.

BOUNDARY (read this before adding a field here):
    Only things that change when WE decide they change belong in this file:
    Kafka, telemetry, runtime, reconnect policy.

    Everything owned by a broker — URLs, credentials, API versions, message
    grammar, server-imposed timeouts, symbol universes — lives entirely in
    ssi.py / dnse.py / tcbs.py, even when the three look superficially alike.

    Rationale: the two groups change at completely different rates. Brokers
    change their API without asking us (SSI is already on /api/v3, meaning v1
    and v2 came and went; DNSE has a documented breaking-change policy; the
    TCBS docs are v1.0.0, published 2026-07-31). Mixing them with our own
    infrastructure means one broker's policy change drags the other two along.

WIRING: composition, not inheritance.
    Each broker config HOLDS a KafkaSettings/TelemetrySettings rather than
    inheriting from one. All three brokers publish to the SAME Redpanda
    cluster, so that cluster is global configuration — inheritance would
    create three copies of one thing. Overriding still works exactly the same:
    pass a different InfraSettings.

All settings are frozen dataclasses read from environment variables, with no
third-party dependency — the same approach examples/ used successfully.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from os import getenv
from pathlib import Path

# ---------------------------------------------------------------------------
# Environment helpers
# ---------------------------------------------------------------------------


def env_str(name: str, default: str = "") -> str:
    raw = getenv(name)
    return default if raw is None or raw == "" else raw


def env_int(name: str, default: int) -> int:
    raw = getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def env_float(name: str, default: float) -> float:
    raw = getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def env_bool(name: str, default: bool = False) -> bool:
    raw = getenv(name)
    if raw is None or raw == "":
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def env_csv(name: str, default: str = "") -> list[str]:
    return [s.strip() for s in env_str(name, default).split(",") if s.strip()]


def read_symbol_file(path: str) -> list[str]:
    """
    Read a symbol universe from a file, one symbol per line. Quoted lines are
    accepted; blank lines and '#' comments are skipped.

    A 1600+ symbol universe does not belong in an environment variable — the
    config only points at the source.
    """
    p = Path(path)
    if not p.exists():
        return []
    out: list[str] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        if line:
            out.append(line)
    return out


# ---------------------------------------------------------------------------
# Kafka
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KafkaSettings:
    """
    Target Kafka/Redpanda cluster. Defaults point at the local dev cluster from
    environment/dev/kafka (3 brokers, ports 19092/19093/19094 seen from the host).
    """

    bootstrap_servers: str = field(
        default_factory=lambda: env_str(
            "KAFKA_BOOTSTRAP_SERVERS", "localhost:19092,localhost:19093,localhost:19094"
        )
    )
    security_protocol: str = field(
        default_factory=lambda: env_str("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT")
    )
    sasl_mechanism: str = field(
        default_factory=lambda: env_str("KAFKA_SASL_MECHANISM", "PLAIN")
    )
    sasl_username: str = field(default_factory=lambda: env_str("KAFKA_SASL_USERNAME"))
    sasl_password: str = field(default_factory=lambda: env_str("KAFKA_SASL_PASSWORD"))

    # acks=all + idempotence: no loss and no duplicates on retry. Ack latency
    # stays off the hot path because sends are pipelined.
    acks: str = field(default_factory=lambda: env_str("KAFKA_ACKS", "all"))
    linger_ms: int = field(default_factory=lambda: env_int("KAFKA_LINGER_MS", 5))
    compression: str = field(default_factory=lambda: env_str("KAFKA_COMPRESSION", "zstd"))
    request_timeout_ms: int = field(
        default_factory=lambda: env_int("KAFKA_REQUEST_TIMEOUT_MS", 30_000)
    )
    retry_backoff_ms: int = field(
        default_factory=lambda: env_int("KAFKA_RETRY_BACKOFF_MS", 100)
    )
    flush_timeout_s: float = field(
        default_factory=lambda: env_float("KAFKA_FLUSH_TIMEOUT_S", 15.0)
    )

    @property
    def enable_idempotence(self) -> bool:
        return self.acks == "all"

    def client_kwargs(self) -> dict:
        """Security kwargs for AIOKafkaProducer matching security_protocol."""
        kwargs: dict = {"security_protocol": self.security_protocol}
        if "SASL" in self.security_protocol:
            kwargs.update(
                sasl_mechanism=self.sasl_mechanism,
                sasl_plain_username=self.sasl_username,
                sasl_plain_password=self.sasl_password,
            )
        if "SSL" in self.security_protocol:
            import ssl

            kwargs["ssl_context"] = ssl.create_default_context()
        return kwargs

    def validate(self) -> None:
        if not self.bootstrap_servers:
            raise ValueError("KAFKA_BOOTSTRAP_SERVERS is empty")
        if self.acks not in ("0", "1", "all"):
            raise ValueError(f"KAFKA_ACKS must be '0', '1' or 'all', got {self.acks!r}")
        if "SASL" in self.security_protocol and not self.sasl_username:
            raise ValueError("security_protocol requests SASL but KAFKA_SASL_USERNAME is missing")


# ---------------------------------------------------------------------------
# Telemetry
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TelemetrySettings:
    """
    OpenTelemetry. An empty endpoint disables telemetry entirely (no worker
    thread is started).

    queue_max is a safety fence: telemetry is best-effort, so a full queue
    DROPS metrics rather than ever slowing down or blocking the datafeed.
    """

    otlp_endpoint: str = field(
        default_factory=lambda: env_str("OTEL_EXPORTER_OTLP_ENDPOINT")
    )
    export_interval_ms: int = field(
        default_factory=lambda: env_int("OTEL_METRIC_EXPORT_INTERVAL_MS", 10_000)
    )
    queue_max: int = field(
        default_factory=lambda: env_int("OTEL_METRIC_QUEUE_MAX", 10_000)
    )
    service_namespace: str = field(
        default_factory=lambda: env_str("OTEL_SERVICE_NAMESPACE", "vnmd")
    )

    @property
    def enabled(self) -> bool:
        return bool(self.otlp_endpoint.strip())


# ---------------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RuntimeSettings:
    """Operational basics: service identity, environment, logging."""

    service_name: str = field(
        default_factory=lambda: env_str("SERVICE_NAME", "vnmd-ingestion")
    )
    environment: str = field(
        default_factory=lambda: env_str("DEVELOPMENT_ENVIRONMENT", env_str("RUN_ENV", "dev"))
    )
    log_level: str = field(default_factory=lambda: env_str("LOG_LEVEL", "INFO"))

    # Log every N frames so we can see a feed is alive without drowning in logs.
    log_every_n_frames: int = field(
        default_factory=lambda: env_int("LOG_EVERY_N_FRAMES", 1000)
    )
    # Per-sample latency logging — debug only; written through a queue so the
    # event loop never blocks on it.
    log_latency_samples: bool = field(
        default_factory=lambda: env_bool("LOG_LATENCY_SAMPLES", False)
    )


# ---------------------------------------------------------------------------
# Reconnect
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BackoffSettings:
    """
    Reconnect backoff parameters. This is OUR policy, so it belongs in base —
    the algorithm is identical everywhere (exponential + jitter, capped), only
    the constants differ, so each broker overrides the numbers its vendor
    recommends:
        TCBS : min(2^n, 30) seconds, at most 10 attempts
        DNSE : 1 -> 2 -> 4 -> ... -> 60 seconds

    Deliberately holds values only. The delay formula lives in core/, not here.
    """

    initial_ms: int = 1_000
    max_ms: int = 30_000
    multiplier: float = 2.0
    jitter: float = 0.2          # +/-20%, so a fleet does not reconnect in lockstep
    max_attempts: int = 0        # 0 = retry forever

    def validate(self) -> None:
        if self.initial_ms <= 0 or self.max_ms < self.initial_ms:
            raise ValueError("backoff: require 0 < initial_ms <= max_ms")
        if not 0.0 <= self.jitter < 1.0:
            raise ValueError("backoff: jitter must be within [0, 1)")


# ---------------------------------------------------------------------------
# Infrastructure bundle
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class InfraSettings:
    """
    Bundles the shared infrastructure so a broker config carries ONE `infra`
    field instead of four. A broker that needs different infrastructure is
    simply handed a different InfraSettings.
    """

    kafka: KafkaSettings = field(default_factory=KafkaSettings)
    telemetry: TelemetrySettings = field(default_factory=TelemetrySettings)
    runtime: RuntimeSettings = field(default_factory=RuntimeSettings)

    def validate(self) -> None:
        self.kafka.validate()
