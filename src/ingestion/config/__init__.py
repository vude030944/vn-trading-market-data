"""
Configuration for the ingestion service (WebSocket -> Kafka).

    base.py   infrastructure WE own: Kafka, telemetry, runtime, backoff
    ssi.py    SSI FastConnect
    dnse.py   DNSE LightSpeed
    tcbs.py   TCBS iFlash

The three broker modules do not inherit from one another and there is no shared
"BrokerConfig" class — each broker is free to change shape when its vendor
changes policy, without dragging the other two along.
"""

from .base import (
    BackoffSettings,
    InfraSettings,
    KafkaSettings,
    RuntimeSettings,
    TelemetrySettings,
)
from .dnse import DNSEConfig
from .ssi import SSIConfig
from .tcbs import TCBSConfig

__all__ = [
    "BackoffSettings",
    "InfraSettings",
    "KafkaSettings",
    "RuntimeSettings",
    "TelemetrySettings",
    "SSIConfig",
    "DNSEConfig",
    "TCBSConfig",
]
