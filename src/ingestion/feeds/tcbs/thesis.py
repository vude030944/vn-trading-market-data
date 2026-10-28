"""
TCBS price-board feed — /ws/thesis/v1/stream/{normal,derivative}.

The two endpoints SHARE the subscribe grammar but use DIFFERENT channel IDs and
different data types (cash returns strings for price/quantity, derivatives return
numbers). Ingestion does not parse payloads so that difference is harmless here —
it is documented so the transformation layer does not reuse one parser for both.
"""

from __future__ import annotations

from typing import Iterable

from ...config.tcbs import TCBSConfig, ThesisFeedSettings
from ...core.connection import Conn
from ...core.frame import Frame, Handled, SessionInfo
from . import framing
from .base import handshake_pipe
from .token import TokenProvider


class ThesisSpec:
    source = "tcbs"

    def __init__(
        self, cfg: TCBSConfig, feed: ThesisFeedSettings, mode: str, tokens: TokenProvider
    ) -> None:
        assert mode in ("stock", "derivative")
        self.name = f"tcbs.{mode}"
        self.url = cfg.url_of(feed)
        self._cfg = cfg
        self._feed = feed
        self._mode = mode
        self._tokens = tokens

    # -- connection ------------------------------------------------------
    def connect_kwargs(self) -> dict:
        return {}

    async def handshake(self, conn: Conn) -> SessionInfo:
        return await handshake_pipe(conn, await self._tokens.get(), self.name)

    def max_session_lifetime_s(self) -> float | None:
        return None      # TCBS does not time-limit connections the way DNSE does

    # -- heartbeat -------------------------------------------------------
    def heartbeat_frame(self) -> str:
        return self._feed.heartbeat_frame          # d|p|||

    def heartbeat_interval_s(self) -> float:
        return self._feed.heartbeat_interval_s     # 2s

    # -- subscribe -------------------------------------------------------
    def subscribe_frames(self) -> Iterable[str]:
        codes = "+".join(self._feed.channel_codes)
        f = self._feed
        out: list[str] = []

        if self._mode == "derivative":
            if f.symbols:
                # `dtn` inside channel_codes is what unlocks s|42 (10-level depth book).
                out.append(f"d|s|tk|{codes}|" + ",".join(f.symbols))
        else:
            if f.floors:
                out.append(f"d|s|ro|{codes}|" + ",".join(f.floors))
            if f.indices:
                out.append(f"d|s|si|rt|" + ",".join(f.indices))
            if f.pt_floors:
                out.append("d|s|pt|ptm+ptb+pts|" + ",".join(f.pt_floors))
            if f.symbols:
                out.append(f"d|s|tk|{codes}|" + ",".join(f.symbols))

        # One-shot snapshot to resynchronise state right after a (re)connect —
        # a mechanism only TCBS offers. The server replies on s|38.
        if f.snapshot_on_connect and f.symbols:
            out.append("d|r|tk||" + ",".join(f.symbols))
        return out

    # -- inbound data ----------------------------------------------------
    def on_message(self, raw: str | bytes) -> Handled:
        if not isinstance(raw, str) or not raw:
            return Handled()

        # Control: timeout config, subscription ack, server pong.
        if raw.startswith(("d|33|", "d|34|", "d|p")):
            return Handled()

        frames: list[Frame] = []
        for piece in framing.split_frames(raw):
            parsed = framing.parse_thesis_frame(piece)
            if parsed is None:
                continue
            frames.append(
                Frame(
                    topic=self._feed.kafka_topic,
                    key=framing.extract_key(parsed.json_body),
                    wire_code=f"s|{parsed.wire_code}",
                    payload=parsed.json_body,
                )
            )
        # Unrecognised -> report malformed so the engine counts it, never swallow it.
        return Handled(frames=tuple(frames), malformed=not frames)
