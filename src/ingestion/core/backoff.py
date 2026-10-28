"""Reconnect delay computation. Pure functions, easy to test."""

from __future__ import annotations

import random

from ..config.base import BackoffSettings


def delay_seconds(cfg: BackoffSettings, attempt: int, *, rng: random.Random | None = None) -> float:
    """
    delay = min(initial * multiplier^(attempt-1), max) * U(1-jitter, 1+jitter)

    Jitter is mandatory, not decoration: when Kafka or a broker recovers from an
    outage, every client reconnecting on the same beat piles on and knocks it
    over again.
    """
    if attempt < 1:
        attempt = 1
    base = cfg.initial_ms * (cfg.multiplier ** (attempt - 1))
    capped = min(base, cfg.max_ms)
    r = rng or random
    factor = r.uniform(1.0 - cfg.jitter, 1.0 + cfg.jitter) if cfg.jitter else 1.0
    return max(0.0, capped * factor / 1000.0)


def exhausted(cfg: BackoffSettings, attempt: int) -> bool:
    return cfg.max_attempts > 0 and attempt >= cfg.max_attempts
