"""
Runner — hosts N feeds inside ONE process.

Why "N feeds" and not "one feed":
    TCBS requires its three endpoints to share a single token, so they must live
    in the same process. SSI/DNSE only have one feed each, but they use the same
    runner so there is not a second code path to maintain.

BULKHEAD: every feed is its own task with its own engine. One feed dying (bad
credentials, a broker changing protocol) leaves the others running — which
matters for TCBS, where a broken ouranos feed must not take the cash price board
down with it.
"""

from __future__ import annotations

import asyncio
import logging
import signal

from ..config.base import BackoffSettings, InfraSettings
from . import health
from .engine import WsEngine
from .frame import Frame
from .publisher import KafkaPublisher
from .shutdown import drain
from .spec import FeedSpec
from .telemetry import FeedLabels, Telemetry

log = logging.getLogger(__name__)


class Runner:
    def __init__(
        self,
        specs: list[FeedSpec],
        infra: InfraSettings,
        *,
        backoff: BackoffSettings,
        connect_timeout_s: float,
        topics: dict[str, str],
    ) -> None:
        if not specs:
            raise ValueError("No feed is enabled")
        self._specs = specs
        self._infra = infra
        self._backoff = backoff
        self._connect_timeout_s = connect_timeout_s
        self._topics = topics
        self._stop = asyncio.Event()
        self._broker = specs[0].source

    async def run(self) -> None:
        rt = self._infra.runtime
        labels = tuple(
            FeedLabels(source=s.source, feed=s.name, topic=self._topics.get(s.name, ""))
            for s in self._specs
        )
        telemetry = Telemetry(self._infra.telemetry, rt, labels)
        publisher = KafkaPublisher(self._infra.kafka, telemetry)
        await publisher.start()

        engines = [
            WsEngine(
                spec,
                self._make_sink(publisher, spec),
                backoff=self._backoff,
                connect_timeout_s=self._connect_timeout_s,
                telemetry=telemetry,
                log_every_n_frames=rt.log_every_n_frames,
            )
            for spec in self._specs
        ]

        self._install_signal_handlers()
        tasks = [asyncio.create_task(e.run_forever(), name=f"feed.{e.name}") for e in engines]
        tasks.append(asyncio.create_task(self._health_loop(engines), name="health"))
        log.info("Started %d feed(s): %s", len(engines),
                 ", ".join(e.name for e in engines))

        # Stop on a signal OR when every feed has given up.
        stop_wait = asyncio.create_task(self._stop.wait(), name="stop-signal")
        await asyncio.wait([stop_wait, *tasks], return_when=asyncio.FIRST_COMPLETED)
        if not self._stop.is_set():
            log.error("All feeds stopped — exiting")
        stop_wait.cancel()

        for e in engines:
            e.stop()
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

        for e in engines:
            log.info("Feed summary", extra={
                "feed": e.name, "messages": e.stats.messages, "frames": e.stats.frames,
                "reconnects": e.stats.reconnects, "malformed": e.stats.malformed})

        await drain(publisher, self._infra.kafka.flush_timeout_s)
        telemetry.shutdown()

    async def _health_loop(self, engines: list[WsEngine], interval_s: float = 5.0) -> None:
        """Refresh the health file so Docker knows when to restart the container."""
        while True:
            health.write(
                health.DEFAULT_PATH,
                self._broker,
                {
                    e.name: {
                        "connected": e.stats.connected,
                        "frames": e.stats.frames,
                        "reconnects": e.stats.reconnects,
                    }
                    for e in engines
                },
            )
            await asyncio.sleep(interval_s)

    # ------------------------------------------------------------------
    def _make_sink(self, publisher: KafkaPublisher, spec: FeedSpec):
        """
        Closure binding a feed to the publisher.

        Deliberately `await` rather than `create_task`: awaiting creates natural
        backpressure — when the producer buffer fills, the socket read loop slows
        down. Using create_task would break PER-SYMBOL ORDERING, exactly the bug
        examples/ssi-data had.
        """
        source, feed = spec.source, spec.name

        async def sink(frame: Frame, recv_ns: int, recv_ts_ns: int) -> None:
            await publisher.publish(
                frame, source=source, feed=feed, recv_ns=recv_ns, recv_ts_ns=recv_ts_ns)

        return sink

    def _install_signal_handlers(self) -> None:
        loop = asyncio.get_running_loop()

        def on_signal(name: str) -> None:
            log.info("Received %s — starting graceful shutdown", name)
            self._stop.set()

        for sig in (signal.SIGTERM, signal.SIGINT):
            try:
                loop.add_signal_handler(sig, on_signal, sig.name)
            except NotImplementedError:      # Windows
                pass
