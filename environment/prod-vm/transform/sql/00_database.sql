-- ============================================================================
-- 00 — Database
--
-- Parsing lives in the Flink job (src/transform/src/main/java), not in SQL, so
-- ClickHouse needs no helper functions any more: it stores rows and serves views.
-- ============================================================================

CREATE DATABASE IF NOT EXISTS vnmd;
