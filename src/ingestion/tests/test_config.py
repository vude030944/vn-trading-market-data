"""Bad configuration must fail at startup — not at 09:30 mid-session."""

import pytest

from ingestion.config.base import BackoffSettings, InfraSettings, KafkaSettings
from ingestion.config.dnse import DNSEConfig
from ingestion.config.ssi import SSIConfig
from ingestion.config.tcbs import TCBSConfig, ThesisFeedSettings


def test_infra_shares_one_kafka_cluster():
    """Composition: all three brokers point at one cluster, config is not duplicated."""
    infra = InfraSettings()
    a = SSIConfig(api_key="k", api_secret="s", infra=infra)
    b = DNSEConfig(api_key="k", api_secret="s", symbols=("ACB",), infra=infra)
    assert a.infra.kafka is b.infra.kafka


def test_override_kafka_for_a_single_broker():
    other = InfraSettings(kafka=KafkaSettings(bootstrap_servers="kafka-b:9092"))
    cfg = SSIConfig(api_key="k", api_secret="s", infra=other)
    assert cfg.infra.kafka.bootstrap_servers == "kafka-b:9092"


@pytest.mark.parametrize("topic", ["tradex.*@tick", "trade.*@3m", "market.*@1m"])
def test_ssi_rejects_invalid_topics(topic):
    with pytest.raises(ValueError):
        SSIConfig(api_key="k", api_secret="s", topics=(topic,)).validate()


def test_ssi_rejects_unknown_auth_mode():
    with pytest.raises(ValueError):
        SSIConfig(api_key="k", api_secret="s", auth_mode="magic").validate()


def test_dnse_shards_cover_everything_without_overlap():
    from dataclasses import replace
    base = DNSEConfig(api_key="k", api_secret="s",
                      symbols=tuple(f"S{i:03d}" for i in range(97)))
    seen = []
    for i in range(4):
        c = replace(base, shard_index=i, shard_count=4)
        c.validate()
        seen += list(c.shard_symbols)
    assert sorted(seen) == sorted(base.symbols)


def test_dnse_rejects_out_of_range_shard_index():
    with pytest.raises(ValueError):
        DNSEConfig(api_key="k", api_secret="s", symbols=("ACB",),
                   shard_index=3, shard_count=3).validate()


def test_tcbs_rejects_heartbeat_sparser_than_timeout():
    """A real trap: /ws/aither tolerates only 7s, so pinging every 5s is fatal."""
    bad = ThesisFeedSettings(enabled=True, path="/ws/aither", heartbeat_frame="ping|1",
                             heartbeat_interval_s=5.0, heartbeat_timeout_s=7,
                             kafka_topic="x", floors=("1",))
    with pytest.raises(ValueError, match="too sparse"):
        TCBSConfig(token="t", stock=bad).validate()


def test_tcbs_requires_token_or_apikey_otp():
    with pytest.raises(ValueError):
        TCBSConfig(token="", api_key="", otp="").validate()


def test_backoff_rejects_nonsense_parameters():
    with pytest.raises(ValueError):
        BackoffSettings(initial_ms=5000, max_ms=1000).validate()
    with pytest.raises(ValueError):
        BackoffSettings(jitter=1.5).validate()
