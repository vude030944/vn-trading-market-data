"""
FeedSpec — the ONE contract between the engine and the brokers.

It was derived from exactly three real cases (SSI / DNSE / TCBS), not from
theorising about "what a WebSocket connection is in general". Keeping it THIN
is deliberate: every method added here is a constraint imposed on all three
brokers, and when one vendor changes policy the interface grows optional
methods — the classic sign of rot. A broker that diverges too far should get
its own path rather than widen this contract.

Five things the engine must do uniformly, and no more:
    1. open a connection      -> url + connect_kwargs
    2. reach a ready state    -> handshake
    3. subscribe              -> subscribe_frames
    4. keep the link alive    -> heartbeat
    5. understand a message   -> on_message
"""

from __future__ import annotations

from typing import Iterable, Protocol, runtime_checkable

from .connection import Conn
from .frame import Handled, SessionInfo


class AuthError(RuntimeError):
    """Handshake failed on credentials — do NOT retry blindly, fix the cause."""


class ProtocolError(RuntimeError):
    """The server said something off-protocol — retryable."""


@runtime_checkable
class FeedSpec(Protocol):
    """One feed = one WebSocket connection = one independent task in the engine."""

    # Identifier used in logs and metrics, shaped '<broker>.<feed>', e.g. 'tcbs.ouranos'.
    name: str
    source: str          # 'ssi' | 'dnse' | 'tcbs' — low-cardinality metric label
    url: str

    def connect_kwargs(self) -> dict:
        """Extra arguments for the connect call (subprotocols, headers...)."""
        ...

    async def handshake(self, conn: Conn) -> SessionInfo:
        """
        Drive the connection to a state where subscriptions are accepted.

        Free to perform any request/response dance — this is where the three
        brokers differ most, and where credentials are used. The engine never
        sees a credential.

        Raise AuthError for bad credentials, ProtocolError for an odd server.
        """
        ...

    def subscribe_frames(self) -> Iterable[str | bytes]:
        """Subscription messages, sent in order once the handshake completes."""
        ...

    def heartbeat_frame(self) -> str | bytes | None:
        """What to send periodically; None if the broker needs no client ping."""
        ...

    def heartbeat_interval_s(self) -> float:
        ...

    def on_message(self, raw: str | bytes) -> Handled:
        """
        Classify and unwrap. MUST NOT raise on an unknown message — set
        `malformed=True` so the engine can count it, and still forward unknown
        data ("better to over-collect than to lose a frame").
        """
        ...

    def max_session_lifetime_s(self) -> float | None:
        """
        Proactively close and reopen after this many seconds; None = unlimited.
        Exists because DNSE hard-cuts a connection at 8 hours — renewing ahead
        of the limit loses no ticks, letting the server cut does.
        """
        ...
