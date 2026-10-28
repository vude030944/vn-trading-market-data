"""
TCBS ouranos feed — /ws/ouranos/v1/stream.

The ONLY TCBS source with a real exchange timestamp (`timeSec`, epoch seconds)
and the aggressor side (`action` BU/SD). The thesis feeds have no equivalent,
which makes this feed valuable for order-flow analysis.

Three differences from thesis: the `d|po` heartbeat, the `d|st` subscribe
grammar, and data frames shaped `CODE|SYMBOL|{json}` — the symbol sits in the
envelope, so the partition key needs no payload inspection.
"""

from __future__ import annotations

from typing import Iterable

from ...config.tcbs import OuranosFeedSettings, TCBSConfig
from ...core.connection import Conn
from ...core.frame import Frame, Handled, SessionInfo
from . import framing
from .base import handshake_pipe
from .token import TokenProvider


class OuranosSpec:
    source = "tcbs"
    name = "tcbs.ouranos"

    def __init__(self, cfg: TCBSConfig, feed: OuranosFeedSettings, tokens: TokenProvider) -> None:
        self.url = cfg.url_of(feed)
        self._feed = feed
        self._tokens = tokens

    def connect_kwargs(self) -> dict:
        return {}

    async def handshake(self, conn: Conn) -> SessionInfo:
        return await handshake_pipe(conn, await self._tokens.get(), self.name)

    def max_session_lifetime_s(self) -> float | None:
        return None

    def heartbeat_frame(self) -> str:
        return self._feed.heartbeat_frame          # d|po, DIFFERENT from thesis
    def heartbeat_interval_s(self) -> float:
        return self._feed.heartbeat_interval_s

    def subscribe_frames(self) -> Iterable[str]:
        """
        d|st|<code1+code2+...>|<ticker1,ticker2,...>

        Chunk the symbol list: the per-frame limit is UNDOCUMENTED, so chunking
        keeps any universe size subscribable.
        """
        codes = "+".join(self._feed.codes)
        chunk = max(1, self._feed.subscribe_chunk)
        t = self._feed.tickers
        return [
            f"d|st|{codes}|" + ",".join(t[i : i + chunk]) for i in range(0, len(t), chunk)
        ]

    def on_message(self, raw: str | bytes) -> Handled:
        if not isinstance(raw, str) or not raw:
            return Handled()

        # `d|pi` is a server-initiated ping (~10s) — NOT documented, found by
        # live probing. Without filtering it, a warning is logged every 10s.
        if raw.startswith((framing.OURANOS_SERVER_PING, "d|33|", "d|34|", "d|p")):
            return Handled()

        parsed = framing.parse_ouranos_frame(raw)
        if parsed is None:
            return Handled(malformed=True)

        return Handled(
            frames=(
                Frame(
                    topic=self._feed.kafka_topic,
                    key=parsed.symbol or None,
                    wire_code=parsed.code,
                    payload=parsed.json_body,
                ),
            )
        )
