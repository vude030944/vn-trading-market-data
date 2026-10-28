"""
OpenTelemetry metrics that must NEVER block the datafeed.

Three rules, all learned from examples/:
  1. The event loop only does `put_nowait` into a bounded queue. A full queue
     DROPS the metric — losing a number beats losing a tick.
  2. Counter/histogram updates and export happen on a separate thread.
  3. Labels stay LOW cardinality: source/feed/wire_code/status only, never a
     symbol or an order_id.
"""

from __future__ import annotations

import logging
import queue
import threading
import time
from dataclasses import dataclass
from typing import Any, Iterable

from ..config.base import RuntimeSettings, TelemetrySettings

log = logging.getLogger(__name__)

_MS_BUCKETS = [1, 2, 5, 10, 20, 50, 100, 250, 500, 1000, 2000, 5000]
_BYTE_BUCKETS = [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]


@dataclass(frozen=True)
class FeedLabels:
    source: str
    feed: str
    topic: str


class Telemetry:
    """A complete no-op when no OTLP endpoint is configured."""

    def __init__(
        self,
        settings: TelemetrySettings,
        runtime: RuntimeSettings,
        feeds: tuple[FeedLabels, ...],
    ) -> None:
        self._enabled = settings.enabled
        self._feeds = feeds
        self._queue: queue.Queue[dict[str, Any]] | None = None
        self._thread: threading.Thread | None = None
        self._stopping = threading.Event()
        self._provider = None
        self._lock = threading.Lock()
        self._last_seen_ns: dict[str, int] = {f.feed: time.monotonic_ns() for f in feeds}
        self._last_msg_ns: dict[str, int] = {}
        self._dropped_events = 0

        if not self._enabled:
            return

        from opentelemetry import metrics
        from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        from opentelemetry.sdk.metrics.view import ExplicitBucketHistogramAggregation, View
        from opentelemetry.sdk.resources import Resource

        reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=settings.otlp_endpoint.rstrip("/") + "/v1/metrics"),
            export_interval_millis=settings.export_interval_ms,
        )
        views = [
            View(instrument_name=n, aggregation=ExplicitBucketHistogramAggregation(b))
            for n, b in (
                ("market_data_publish_latency_ms", _MS_BUCKETS),
                ("market_data_interarrival_ms", _MS_BUCKETS),
                ("market_data_payload_bytes", _BYTE_BUCKETS),
            )
        ]
        self._provider = MeterProvider(
            resource=Resource.create({
                "service.name": runtime.service_name,
                "service.namespace": settings.service_namespace,
                "deployment.environment": runtime.environment,
            }),
            metric_readers=[reader],
            views=views,
        )
        metrics.set_meter_provider(self._provider)
        meter = metrics.get_meter(runtime.service_name)

        self._messages = meter.create_counter(
            "market_data_messages_total", description="Messages by status.")
        self._payload_bytes = meter.create_histogram(
            "market_data_payload_bytes", description="Raw payload size.")
        self._interarrival = meter.create_histogram(
            "market_data_interarrival_ms", description="Gap between consecutive messages.")
        self._latency = meter.create_histogram(
            "market_data_publish_latency_ms", description="ws_recv -> kafka_ack.")
        self._reconnects = meter.create_counter(
            "market_data_reconnects_total", description="Reconnect attempts.")
        self._kafka_errors = meter.create_counter(
            "market_data_kafka_errors_total", description="Kafka send and delivery errors.")
        meter.create_observable_gauge(
            "market_data_last_message_age_ms",
            callbacks=[self._observe_age],
            description="Age of the most recent message.")

        self._queue = queue.Queue(maxsize=settings.queue_max)
        self._thread = threading.Thread(target=self._worker, name="otel-worker", daemon=True)
        self._thread.start()
        for f in feeds:
            self._emit({"kind": "baseline", "feed": f.feed})
        log.info("Telemetry enabled", extra={"otlp_endpoint": settings.otlp_endpoint})

    # -- hot path: enqueue only ------------------------------------------
    def _emit(self, ev: dict[str, Any]) -> None:
        if self._queue is None:
            return
        try:
            self._queue.put_nowait(ev)
        except queue.Full:
            self._dropped_events += 1

    def ws_message(self, feed: str, recv_ns: int) -> None:
        self._emit({"kind": "ws", "feed": feed, "recv_ns": recv_ns})

    def data_frame(self, feed: str, wire_code: str, payload_bytes: int, recv_ns: int) -> None:
        self._emit({"kind": "frame", "feed": feed, "wire_code": wire_code,
                    "bytes": payload_bytes, "recv_ns": recv_ns})

    def malformed(self, feed: str) -> None:
        self._emit({"kind": "malformed", "feed": feed})

    def published(self, feed: str, topic: str, wire_code: str, latency_ms: float) -> None:
        self._emit({"kind": "published", "feed": feed, "topic": topic,
                    "wire_code": wire_code, "latency_ms": latency_ms})

    def kafka_error(self, feed: str, topic: str, status: str) -> None:
        self._emit({"kind": "kafka_error", "feed": feed, "topic": topic, "status": status})

    def reconnect(self, feed: str, reason: str) -> None:
        self._emit({"kind": "reconnect", "feed": feed, "reason": reason})

    # -- worker ----------------------------------------------------------
    def _worker(self) -> None:
        assert self._queue is not None
        while not self._stopping.is_set() or not self._queue.empty():
            try:
                ev = self._queue.get(timeout=0.25)
            except queue.Empty:
                continue
            try:
                self._apply(ev)
            except Exception:
                log.exception("Failed to record metric")
            finally:
                self._queue.task_done()

    def _src(self, feed: str) -> str:
        for f in self._feeds:
            if f.feed == feed:
                return f.source
        return "unknown"

    def _attrs(self, feed: str, **kw: str) -> dict:
        base = {"source": self._src(feed), "feed": feed}
        base.update({k: v for k, v in kw.items() if v})
        return base

    def _apply(self, ev: dict[str, Any]) -> None:
        kind, feed = ev["kind"], ev.get("feed", "")

        if kind == "baseline":
            for status in ("received", "published"):
                self._messages.add(0, self._attrs(feed, status=status))
            self._messages.add(0, self._attrs(feed, status="dropped", reason="malformed"))
            self._reconnects.add(0, self._attrs(feed, reason="session_ended"))
            return

        if kind == "ws":
            with self._lock:
                prev = self._last_msg_ns.get(feed)
                self._last_msg_ns[feed] = ev["recv_ns"]
                self._last_seen_ns[feed] = ev["recv_ns"]
            if prev is not None and ev["recv_ns"] >= prev:
                self._interarrival.record((ev["recv_ns"] - prev) / 1e6, self._attrs(feed))
            return

        if kind == "frame":
            self._messages.add(1, self._attrs(feed, status="received"))
            self._payload_bytes.record(
                ev["bytes"], self._attrs(feed, wire_code=ev["wire_code"]))
            return

        if kind == "malformed":
            self._messages.add(1, self._attrs(feed, status="dropped", reason="malformed"))
            return

        if kind == "published":
            self._messages.add(1, self._attrs(feed, status="published"))
            self._latency.record(ev["latency_ms"], self._attrs(
                feed, topic=ev["topic"], wire_code=ev["wire_code"]))
            return

        if kind == "kafka_error":
            self._messages.add(1, self._attrs(feed, status="dropped", reason=ev["status"]))
            self._kafka_errors.add(1, self._attrs(feed, topic=ev["topic"], status=ev["status"]))
            return

        if kind == "reconnect":
            self._reconnects.add(1, self._attrs(feed, reason=ev["reason"]))

    def _observe_age(self, _opts) -> Iterable:
        from opentelemetry.metrics import Observation

        now = time.monotonic_ns()
        with self._lock:
            snap = tuple(self._last_seen_ns.items())
        return [Observation((now - ns) / 1e6, self._attrs(feed)) for feed, ns in snap]

    def shutdown(self) -> None:
        if self._dropped_events:
            log.warning("Telemetry dropped %d events due to a full queue", self._dropped_events)
        if self._thread is not None:
            self._stopping.set()
            self._thread.join(timeout=5.0)
        if self._provider is not None:
            self._provider.force_flush(timeout_millis=3000)
            self._provider.shutdown(timeout_millis=3000)
