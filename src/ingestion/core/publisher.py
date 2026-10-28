"""
Publishes raw frames to Kafka.

Three required properties:
  * The payload is NOT transformed — Kafka is a pipe; the Flink job parses.
  * Pipelined: `send()` returns as soon as the message is buffered; the broker
    ack is handled in a callback. The socket read loop never waits on an ack.
  * acks=all + idempotence: no loss, no duplicates on retry.

Metadata travels out-of-band rather than being injected into the payload:
    key                = symbol      -> Kafka guarantees per-symbol ordering
    header source      = ssi|dnse|tcbs
    header feed        = feed name
    header wire_code   = the broker's own channel code
    header recv_ts_ns  = epoch nanoseconds WHEN WE RECEIVED IT (event-time label)
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass

from aiokafka import AIOKafkaProducer

from ..config.base import KafkaSettings
from .frame import Frame
from .telemetry import Telemetry

log = logging.getLogger(__name__)

_ERROR_LOG_INTERVAL_S = 5.0


@dataclass
class PublisherStats:
    sent: int = 0
    errors: int = 0


class KafkaPublisher:
    def __init__(self, settings: KafkaSettings, telemetry: Telemetry) -> None:
        self._s = settings
        self._t = telemetry
        self._producer: AIOKafkaProducer | None = None
        self._started = False
        self._lock = asyncio.Lock()
        self.stats = PublisherStats()
        self._last_error_log = 0.0
        self._suppressed = 0

    async def start(self) -> None:
        async with self._lock:
            if self._started:
                return
            acks = "all" if self._s.acks == "all" else int(self._s.acks)
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self._s.bootstrap_servers,
                # value may be str (JSON/pipe protocols) or bytes (DNSE msgpack)
                value_serializer=lambda v: v.encode("utf-8") if isinstance(v, str) else v,
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks=acks,
                enable_idempotence=self._s.enable_idempotence,
                linger_ms=self._s.linger_ms,
                compression_type=self._s.compression,
                request_timeout_ms=self._s.request_timeout_ms,
                retry_backoff_ms=self._s.retry_backoff_ms,
                **self._s.client_kwargs(),
            )
            await self._producer.start()
            self._started = True
            log.info(
                "KafkaPublisher ready",
                extra={"bootstrap": self._s.bootstrap_servers, "acks": str(acks),
                       "idempotence": self._s.enable_idempotence},
            )

    async def publish(
        self, frame: Frame, *, source: str, feed: str, recv_ns: int, recv_ts_ns: int
    ) -> None:
        if self._producer is None:
            self.stats.errors += 1
            self._t.kafka_error(feed, frame.topic, "producer_not_started")
            self._log_ratelimited("publish called before producer start — dropping message")
            return

        headers = [
            ("source", source.encode("ascii")),
            ("feed", feed.encode("ascii")),
            ("wire_code", frame.wire_code.encode("utf-8")),
            ("recv_ts_ns", str(recv_ts_ns).encode("ascii")),
        ]
        try:
            fut = await self._producer.send(
                topic=frame.topic, value=frame.payload, key=frame.key, headers=headers
            )
        except Exception as exc:
            self.stats.errors += 1
            self._t.kafka_error(feed, frame.topic, "send_error")
            self._log_ratelimited(f"Kafka send failed topic={frame.topic}: {exc!r}")
            return

        fut.add_done_callback(
            lambda f: self._on_delivery(f, feed=feed, frame=frame, recv_ns=recv_ns)
        )

    def _on_delivery(self, fut: asyncio.Future, *, feed: str, frame: Frame, recv_ns: int) -> None:
        if fut.cancelled():
            self.stats.errors += 1
            self._t.kafka_error(feed, frame.topic, "delivery_cancelled")
            return
        exc = fut.exception()
        if exc is not None:
            self.stats.errors += 1
            self._t.kafka_error(feed, frame.topic, "delivery_error")
            self._log_ratelimited(f"Kafka delivery failed topic={frame.topic}: {exc!r}")
            return
        self.stats.sent += 1
        # Latency measured with a monotonic clock -> immune to NTP adjustments.
        self._t.published(feed, frame.topic, frame.wire_code,
                          (time.monotonic_ns() - recv_ns) / 1e6)

    def _log_ratelimited(self, msg: str) -> None:
        """A Kafka outage produces one error per in-flight message — compress them."""
        now = time.monotonic()
        if now - self._last_error_log >= _ERROR_LOG_INTERVAL_S:
            if self._suppressed:
                msg += f" (+{self._suppressed} similar errors suppressed)"
            self._suppressed = 0
            self._last_error_log = now
            log.error(msg)
        else:
            self._suppressed += 1

    async def flush(self) -> None:
        if self._producer is not None:
            await self._producer.flush()

    async def stop(self) -> None:
        async with self._lock:
            if not self._started:
                return
            log.info("Stopping KafkaPublisher",
                     extra={"sent": self.stats.sent, "errors": self.stats.errors})
            if self._producer is not None:
                await self._producer.stop()   # flushes remaining batches
                self._producer = None
            self._started = False
