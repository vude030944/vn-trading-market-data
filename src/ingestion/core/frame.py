"""Types crossing the engine <-> sink boundary. Deliberately minimal."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Frame:
    """
    One data message, unwrapped from its protocol envelope but otherwise UNTOUCHED.

    `payload` is kept byte-for-byte exactly as the broker sent it. Turning it
    into typed columns is the transformation layer's job (the Flink job), not
    ingestion's. A wrong parser is fixed by replaying from Kafka; nothing is lost.
    """

    topic: str                  # destination Kafka topic
    key: str | None             # partition key -> preserves per-symbol ordering
    wire_code: str              # 's|6', 'C001', 'trade_tick', 'tick_extra.G1'...
    payload: str | bytes        # verbatim


@dataclass(frozen=True, slots=True)
class Handled:
    """
    The result of processing ONE raw message.

    Separating `replies` from `frames` is the key point: some protocols require
    an immediate answer on the read path (DNSE sends `ping`, the client must
    `pong`), and that must not leak into the data path.
    """

    frames: tuple[Frame, ...] = ()
    replies: tuple[str | bytes, ...] = ()
    malformed: bool = False          # counted for alerting, never swallowed


@dataclass(slots=True)
class SessionInfo:
    """
    Values the server announces during the handshake. ALWAYS prefer these over
    configuration.

    Why this exists: the TCBS docs state the ouranos timeout is 15s but live
    probing observed `d|33|30`; DNSE returns a per-tier `rate_limit` inside
    `auth_success`. Hardcoding the documented numbers is asking for trouble.
    """

    session_id: str | None = None
    heartbeat_timeout_s: float | None = None
    limits: dict = field(default_factory=dict)
