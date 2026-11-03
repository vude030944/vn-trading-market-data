-- ============================================================================
-- 90 — Read views and operational views
--
-- The target tables use ReplacingMergeTree: duplicates only disappear AFTER a
-- merge, and when that merge runs is ClickHouse's decision. Guaranteeing no
-- duplicates at read time requires `FINAL` — more expensive, but correct.
--     fast reads, tolerating rare duplicates -> query the table directly
--     absolute correctness required          -> query the *_v views below
-- ============================================================================

CREATE VIEW IF NOT EXISTS vnmd.trades_v            AS SELECT * FROM vnmd.trades FINAL;
CREATE VIEW IF NOT EXISTS vnmd.book_v              AS SELECT * FROM vnmd.book FINAL;
CREATE VIEW IF NOT EXISTS vnmd.index_values_v      AS SELECT * FROM vnmd.index_values FINAL;
CREATE VIEW IF NOT EXISTS vnmd.foreign_flow_v      AS SELECT * FROM vnmd.foreign_flow FINAL;
CREATE VIEW IF NOT EXISTS vnmd.ohlc_v              AS SELECT * FROM vnmd.ohlc FINAL;
CREATE VIEW IF NOT EXISTS vnmd.supply_demand_v     AS SELECT * FROM vnmd.supply_demand FINAL;
CREATE VIEW IF NOT EXISTS vnmd.instrument_state_v  AS SELECT * FROM vnmd.instrument_state FINAL;

-- --------------------------------------------------------------- operations

-- FEED HEALTH. A "dead feed" alert must be read together with the session
-- calendar: outside trading hours the connection is alive but silent, and that is
-- NORMAL.
CREATE VIEW IF NOT EXISTS vnmd.v_feed_health AS
SELECT
    source, feed,
    count()                                            AS msgs_today,
    max(recv_ts)                                       AS last_recv_ts,
    dateDiff('second', max(recv_ts), now64(3, 'Asia/Ho_Chi_Minh')) AS age_s,
    uniqExact(wire_code)                               AS wire_codes,
    countIf(error != '')                               AS kafka_errors
FROM vnmd.raw
WHERE recv_ts >= toStartOfDay(now64(3, 'Asia/Ho_Chi_Minh'))
GROUP BY source, feed
ORDER BY source, feed;

-- BROKER-CHANGED-PROTOCOL ALARM. An unfamiliar wire code shows up here long
-- before anyone notices the documentation went stale. This table growing deserves
-- an alert.
CREATE VIEW IF NOT EXISTS vnmd.v_unknown_summary AS
SELECT source, wire_code, count() AS n,
       min(recv_ts) AS lan_dau, max(recv_ts) AS lan_cuoi,
       any(substring(payload, 1, 300)) AS mau_payload
FROM vnmd.unknown_frames
GROUP BY source, wire_code
ORDER BY n DESC;

-- FEED LATENCY. Only computable for brokers that DO stamp a time: DNSE
-- (nanoseconds) and TCBS ouranos (seconds). The TCBS thesis family has none, so
-- it stays NULL forever — a broker limitation, not a bug on our side.
CREATE VIEW IF NOT EXISTS vnmd.v_feed_latency AS
SELECT
    source, wire_code,
    count()                                                       AS n,
    round(avg(dateDiff('millisecond', exchange_ts, recv_ts)), 1)  AS avg_lag_ms,
    quantile(0.5)(dateDiff('millisecond', exchange_ts, recv_ts))  AS p50_lag_ms,
    quantile(0.99)(dateDiff('millisecond', exchange_ts, recv_ts)) AS p99_lag_ms
FROM vnmd.trades
WHERE exchange_ts IS NOT NULL
  AND recv_ts >= toStartOfDay(now64(3, 'Asia/Ho_Chi_Minh'))
GROUP BY source, wire_code
ORDER BY source, wire_code;

-- --------------------------------------------------------------- analytics

-- The latest traded price per symbol, PER source.
CREATE VIEW IF NOT EXISTS vnmd.v_last_trade AS
SELECT symbol, source,
       argMax(price, recv_ts)        AS price,
       argMax(qty, recv_ts)          AS qty,
       argMax(side, recv_ts)         AS side,
       argMax(total_volume, recv_ts) AS total_volume,
       max(recv_ts)                  AS last_recv_ts
FROM vnmd.trades
WHERE recv_ts >= toStartOfDay(now64(3, 'Asia/Ho_Chi_Minh'))
GROUP BY symbol, source;

-- CROSS-SOURCE COMPARISON — the main reason for unifying into one table.
-- A price gap between sources at the same moment means either one source is
-- lagging or one parser is wrong. Both need to be known immediately.
CREATE VIEW IF NOT EXISTS vnmd.v_cross_source AS
SELECT
    symbol,
    countDistinct(source)                    AS sources,
    anyIf(price, source = 'ssi')             AS price_ssi,
    anyIf(price, source = 'dnse')            AS price_dnse,
    anyIf(price, source = 'tcbs')            AS price_tcbs,
    max(price) - min(price)                  AS price_spread,
    max(last_recv_ts)                        AS last_recv_ts
FROM vnmd.v_last_trade
GROUP BY symbol
HAVING sources > 1
ORDER BY price_spread DESC;

-- The latest book per symbol. TCBS sends the bid and ask sides as separate
-- messages, so they must be recombined: take the most recent non-empty array for
-- each side.
CREATE VIEW IF NOT EXISTS vnmd.v_last_book AS
SELECT
    symbol, source,
    argMaxIf(bid_price, recv_ts, length(bid_price) > 0) AS bid_price,
    argMaxIf(bid_qty,   recv_ts, length(bid_qty)   > 0) AS bid_qty,
    argMaxIf(ask_price, recv_ts, length(ask_price) > 0) AS ask_price,
    argMaxIf(ask_qty,   recv_ts, length(ask_qty)   > 0) AS ask_qty,
    max(recv_ts)                                        AS last_recv_ts
FROM vnmd.book
WHERE recv_ts >= toStartOfDay(now64(3, 'Asia/Ho_Chi_Minh'))
GROUP BY symbol, source;
