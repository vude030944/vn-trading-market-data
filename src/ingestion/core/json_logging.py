"""JSON logs on stdout so Loki/Promtail can parse straight from Docker logs."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from logging.handlers import QueueHandler, QueueListener
from queue import SimpleQueue

_RESERVED = frozenset(
    logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys()
) | {"message", "asctime", "taskName"}


class JsonFormatter(logging.Formatter):
    def __init__(self, service_name: str, environment: str) -> None:
        super().__init__()
        self._service = service_name
        self._env = environment

    def format(self, record: logging.LogRecord) -> str:
        doc = {
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service_name": self._service,
            "development_environment": self._env,
            "caller": f"{record.filename}:{record.lineno}",
        }
        if record.exc_info:
            doc["exception"] = self.formatException(record.exc_info)
        # Extra fields passed via logger.info(..., extra={...})
        for k, v in record.__dict__.items():
            if k not in _RESERVED and not k.startswith("_"):
                doc[k] = v
        return json.dumps(doc, ensure_ascii=False, default=str)


class LoggingRuntime:
    """
    Logs go through a queue: the event loop only enqueues, while formatting and
    I/O happen on a separate thread. One slow log line must never stall the
    socket read loop.
    """

    def __init__(self, listener: QueueListener) -> None:
        self._listener = listener

    def shutdown(self) -> None:
        self._listener.stop()


def configure(service_name: str, environment: str, level: str) -> LoggingRuntime:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter(service_name, environment))

    queue: SimpleQueue = SimpleQueue()
    listener = QueueListener(queue, handler, respect_handler_level=True)
    listener.start()

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(QueueHandler(queue))
    root.setLevel(level.upper())

    # Noisy libraries
    logging.getLogger("websockets").setLevel(logging.WARNING)
    logging.getLogger("aiokafka").setLevel(logging.WARNING)
    return LoggingRuntime(listener)
