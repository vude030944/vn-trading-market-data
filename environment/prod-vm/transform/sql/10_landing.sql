-- ============================================================================
-- 10 — LANDING layer: the raw table
--
-- Written by the Flink job (src/transform/src/main/java), one row per Kafka
-- record, payload VERBATIM. A wrong parser is fixed by truncating the target
-- tables and replaying; had the landing layer transformed anything, the
-- original would be gone.
--
-- Message identity = (kafka_topic, kafka_partition, kafka_offset).
-- Timestamps are never used as a key: no broker provides a sequence number, and
-- SSI's time resolution is only one second.
-- ============================================================================

-- ------------------------------------------------- retired: ClickHouse as consumer
-- ClickHouse used to consume Kafka itself (Kafka engine + materialized views).
-- Flink owns that now. Dropping the old objects is what stops a database that
-- ran an older apply.sh from consuming in parallel and writing every row twice.
DROP VIEW IF EXISTS vnmd.mv_raw_tcbs;
DROP VIEW IF EXISTS vnmd.mv_raw_ssi;
DROP VIEW IF EXISTS vnmd.mv_raw_dnse;
DROP TABLE IF EXISTS vnmd.kafka_tcbs;
DROP TABLE IF EXISTS vnmd.kafka_ssi;
DROP TABLE IF EXISTS vnmd.kafka_dnse;
DROP VIEW IF EXISTS vnmd.mv_tcbs_trades;
DROP VIEW IF EXISTS vnmd.mv_tcbs_book;
DROP VIEW IF EXISTS vnmd.mv_tcbs_foreign;
DROP VIEW IF EXISTS vnmd.mv_tcbs_state;
DROP VIEW IF EXISTS vnmd.mv_tcbs_index;
DROP VIEW IF EXISTS vnmd.mv_tcbs_supply_demand;
DROP VIEW IF EXISTS vnmd.mv_tcbs_unknown;
DROP VIEW IF EXISTS vnmd.mv_ssi_trades;
DROP VIEW IF EXISTS vnmd.mv_ssi_book;
DROP VIEW IF EXISTS vnmd.mv_ssi_foreign;
DROP VIEW IF EXISTS vnmd.mv_ssi_ohlc;
DROP VIEW IF EXISTS vnmd.mv_ssi_state;
DROP VIEW IF EXISTS vnmd.mv_ssi_unknown;
DROP VIEW IF EXISTS vnmd.mv_dnse_trades;
DROP VIEW IF EXISTS vnmd.mv_dnse_book;
DROP VIEW IF EXISTS vnmd.mv_dnse_index;
DROP VIEW IF EXISTS vnmd.mv_dnse_foreign;
DROP VIEW IF EXISTS vnmd.mv_dnse_ohlc;
DROP VIEW IF EXISTS vnmd.mv_dnse_state;
DROP VIEW IF EXISTS vnmd.mv_dnse_unknown;

-- ------------------------------------------------------------------ raw table
-- ReplacingMergeTree keyed on Kafka identity: the Flink job is AT_LEAST_ONCE,
-- so a crash re-inserts what was written after the last checkpoint; the sorting
-- key ends with (partition, offset) so those duplicates collapse on merge.
CREATE TABLE IF NOT EXISTS vnmd.raw
(
    source          LowCardinality(String),
    feed            LowCardinality(String),
    wire_code       LowCardinality(String),
    kafka_key       String,
    payload         String CODEC(ZSTD(3)),
    recv_ts_ns      UInt64,
    recv_ts         DateTime64(9, 'Asia/Ho_Chi_Minh') MATERIALIZED fromUnixTimestamp64Nano(recv_ts_ns, 'Asia/Ho_Chi_Minh'),
    kafka_topic     LowCardinality(String),
    kafka_partition UInt16,
    kafka_offset    UInt64,
    error           String DEFAULT '',     -- set by Flink when the payload is not a JSON object
    dw_ts           DateTime64(3, 'Asia/Ho_Chi_Minh') DEFAULT now64(3, 'Asia/Ho_Chi_Minh')
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMMDD(recv_ts)
ORDER BY (source, feed, wire_code, recv_ts_ns, kafka_partition, kafka_offset)
-- Raw is only the safety net for rebuilding targets; 7 days is enough and fits the 25G budget.
TTL toDateTime(recv_ts) + INTERVAL 7 DAY
SETTINGS index_granularity = 8192;
