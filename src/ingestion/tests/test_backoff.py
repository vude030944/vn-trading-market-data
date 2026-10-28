import random

from ingestion.config.base import BackoffSettings
from ingestion.core.backoff import delay_seconds, exhausted


def test_grows_exponentially_and_is_capped():
    cfg = BackoffSettings(initial_ms=1000, max_ms=8000, multiplier=2.0, jitter=0.0)
    got = [delay_seconds(cfg, i) for i in range(1, 7)]
    assert got == [1.0, 2.0, 4.0, 8.0, 8.0, 8.0]


def test_jitter_stays_within_bounds():
    cfg = BackoffSettings(initial_ms=1000, max_ms=1000, jitter=0.2)
    rng = random.Random(42)
    for _ in range(200):
        assert 0.8 <= delay_seconds(cfg, 1, rng=rng) <= 1.2


def test_max_attempts_zero_means_forever():
    cfg = BackoffSettings(max_attempts=0)
    assert not exhausted(cfg, 10_000)


def test_finite_max_attempts():
    cfg = BackoffSettings(max_attempts=10)      # TCBS's recommendation
    assert not exhausted(cfg, 9)
    assert exhausted(cfg, 10)
