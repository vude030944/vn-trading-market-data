"""Assemble the TCBS feeds from config. All three SHARE one TokenProvider."""

from __future__ import annotations

from ...config.tcbs import TCBSConfig
from ...core.spec import FeedSpec
from .ouranos import OuranosSpec
from .thesis import ThesisSpec
from .token import TokenProvider

__all__ = ["build_specs", "TokenProvider", "ThesisSpec", "OuranosSpec"]


def build_specs(cfg: TCBSConfig) -> list[FeedSpec]:
    tokens = TokenProvider(cfg)      # <- the "one token" constraint lives here
    specs: list[FeedSpec] = []
    if cfg.stock.enabled:
        specs.append(ThesisSpec(cfg, cfg.stock, "stock", tokens))
    if cfg.derivative.enabled:
        specs.append(ThesisSpec(cfg, cfg.derivative, "derivative", tokens))
    if cfg.ouranos.enabled:
        specs.append(OuranosSpec(cfg, cfg.ouranos, tokens))
    return specs
