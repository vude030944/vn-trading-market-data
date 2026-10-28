"""Ordered cleanup on exit. Split from the runner so the runner only orchestrates."""

from __future__ import annotations

import asyncio
import logging

from .publisher import KafkaPublisher

log = logging.getLogger(__name__)


async def drain(publisher: KafkaPublisher, flush_timeout_s: float) -> None:
    """
    The order is mandatory: feeds already stopped -> FLUSH Kafka -> only then
    close the producer.

    Reversing it loses whatever is still sitting in the producer's buffer.
    """
    log.info("Flushing Kafka", extra={"sent": publisher.stats.sent,
                                      "errors": publisher.stats.errors})
    try:
        await asyncio.wait_for(publisher.flush(), timeout=flush_timeout_s)
        log.info("Kafka flush complete")
    except asyncio.TimeoutError:
        log.warning("Kafka flush exceeded %.1fs — some messages may be undelivered",
                    flush_timeout_s)
    except Exception as exc:
        log.error("Kafka flush failed: %r", exc)
    await publisher.stop()
