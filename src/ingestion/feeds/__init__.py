"""
Registry: broker name -> (config, list of FeedSpec).

Deliberately HAND-WRITTEN rather than auto-discovering modules. With three
brokers a dict is readable, greppable, and free of import-time magic. Entry
points can wait until there really are a dozen brokers.
"""

from __future__ import annotations

from typing import Callable

from ..config.dnse import DNSEConfig
from ..config.ssi import SSIConfig
from ..config.tcbs import TCBSConfig
from ..core.spec import FeedSpec
from . import dnse as _dnse
from . import ssi as _ssi
from . import tcbs as _tcbs

BROKERS = ("ssi", "dnse", "tcbs")


def load(broker: str) -> tuple[object, list[FeedSpec], dict[str, str]]:
    """
    Returns (config, specs, {feed_name: kafka_topic}).

    The config is `validate()`d right here, so bad configuration fails at startup
    with a clear message rather than at 09:30 in the middle of a session.
    """
    if broker == "ssi":
        cfg = SSIConfig()
        cfg.validate()
        specs = _ssi.build_specs(cfg)
        topics = {s.name: cfg.kafka_topic for s in specs}
    elif broker == "dnse":
        cfg = DNSEConfig()
        cfg.validate()
        specs = _dnse.build_specs(cfg)
        topics = {s.name: cfg.kafka_topic for s in specs}
    elif broker == "tcbs":
        cfg = TCBSConfig()
        cfg.validate()
        specs = _tcbs.build_specs(cfg)
        topics = {
            "tcbs.stock": cfg.stock.kafka_topic,
            "tcbs.derivative": cfg.derivative.kafka_topic,
            "tcbs.ouranos": cfg.ouranos.kafka_topic,
        }
    else:
        raise ValueError(f"Unsupported broker: {broker!r}. Valid: {BROKERS}")
    return cfg, specs, topics
