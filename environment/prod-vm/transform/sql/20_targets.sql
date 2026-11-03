-- ============================================================================
-- 20 — Target tables: one UNIFIED model across all three brokers
--
-- Why unified rather than a schema per broker like examples/ did:
--   the goal of this project is consolidating Vietnamese market data, so the
--   common question is "HPG's traded price at 10:15 according to all three
--   sources". Answering that cheaply requires one table. The `source` column
--   preserves provenance and `wire_code` preserves the broker's own channel
--   code so any row can be traced back to raw.
--
-- Columns present on every table:
--   exchange_ts  the BROKER's timestamp — NULL when the broker provides none
--                (the entire TCBS thesis family carries no time field at all)
--   recv_ts      when WE received it; always present
-- These two must NEVER be conflated: the first is business time, the second is
-- observation time. No broker offers a sequence number, so recv_ts is the only
-- thing comparable across sources.
-- ============================================================================

-- The repeated tail block below is hand-written because ClickHouse has no
-- include mechanism; column order is kept identical everywhere for easy diffing.

CREATE TABLE IF NOT EXISTS vnmd.trades
(
    source          LowCardinality(String),
    symbol          LowCardinality(String),
    instrument      LowCardinality(String),      -- stock | derivative | cw
    exchange_ts     Nullable(DateTime64(9, 'Asia/Ho_Chi_Minh')),
    recv_ts         DateTime64(9, 'Asia/Ho_Chi_Minh') CODEC(DoubleDelta, ZSTD(1)),
    price           Nullable(Float64),
    qty             Nullable(Float64),
    side            LowCardinality(String),      -- B/S (SSI) - BU/SD (ouranos) - BUY/SELL (DNSE)
    avg_price       Nullable(Float64),
    total_volume    Nullable(Float64),
    total_value     Nullable(Float64),
    change          Nullable(Float64),
    change_percent  Nullable(Float64),
    wire_code       LowCardinality(String),
    feed            LowCardinality(String),
    recv_ts_ns      UInt64,
    kafka_topic     LowCardinality(String),
    kafka_partition UInt16,
    kafka_offset    UInt64,
    dw_ts           DateTime64(3, 'Asia/Ho_Chi_Minh') DEFAULT now64(3, 'Asia/Ho_Chi_Minh')
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMMDD(recv_ts)
ORDER BY (symbol, source, recv_ts, kafka_partition, kafka_offset);

-- Order book. TCBS sends the bid side (s|1) and the ask side (s|2) as TWO
-- separate messages, while SSI/DNSE send both sides in one -> arrays are used and
-- the absent side stays empty. Query `length(bid_price) > 0` to tell which side a
-- row carries.
CREATE TABLE IF NOT EXISTS vnmd.book
(
    source          LowCardinality(String),
    symbol          LowCardinality(String),
    instrument      LowCardinality(String),
    exchange_ts     Nullable(DateTime64(9, 'Asia/Ho_Chi_Minh')),
    recv_ts         DateTime64(9, 'Asia/Ho_Chi_Minh') CODEC(DoubleDelta, ZSTD(1)),
    bid_price       Array(Float64),
    bid_qty         Array(Float64),
    ask_price       Array(Float64),
    ask_qty         Array(Float64),
    total_bid_qty   Nullable(Float64),
    total_ask_qty   Nullable(Float64),
    -- Specific to TCBS s|42 (the 10-level derivatives depth book): each message
    -- carries exactly ONE price level plus its `top` index, unlike SSI/DNSE which
    -- send the whole array at once. That channel is ~94% of the futures topic's
    -- traffic, so it earns dedicated columns.
    level           Nullable(UInt8),
    bid_cum_qty     Nullable(Float64),
    ask_cum_qty     Nullable(Float64),
    wire_code       LowCardinality(String),
    feed            LowCardinality(String),
    recv_ts_ns      UInt64,
    kafka_topic     LowCardinality(String),
    kafka_partition UInt16,
    kafka_offset    UInt64,
    dw_ts           DateTime64(3, 'Asia/Ho_Chi_Minh') DEFAULT now64(3, 'Asia/Ho_Chi_Minh')
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMMDD(recv_ts)
ORDER BY (symbol, source, recv_ts, kafka_partition, kafka_offset);

CREATE TABLE IF NOT EXISTS vnmd.index_values
(
    source          LowCardinality(String),
    index_name      LowCardinality(String),      -- VNINDEX / VN30 / TCBS numeric code
    exchange_ts     Nullable(DateTime64(9, 'Asia/Ho_Chi_Minh')),
    recv_ts         DateTime64(9, 'Asia/Ho_Chi_Minh') CODEC(DoubleDelta, ZSTD(1)),
    value           Nullable(Float64),
    change          Nullable(Float64),
    change_percent  Nullable(Float64),
    volume          Nullable(Float64),
    turnover        Nullable(Float64),
    advances        Nullable(Int64),             -- advancing issues
    declines        Nullable(Int64),
    unchanged       Nullable(Int64),
    ceiling_count   Nullable(Int64),
    floor_count     Nullable(Int64),
    session_code    LowCardinality(String),
    wire_code       LowCardinality(String),
    feed            LowCardinality(String),
    recv_ts_ns      UInt64,
    kafka_topic     LowCardinality(String),
    kafka_partition UInt16,
    kafka_offset    UInt64,
    dw_ts           DateTime64(3, 'Asia/Ho_Chi_Minh') DEFAULT now64(3, 'Asia/Ho_Chi_Minh')
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMMDD(recv_ts)
ORDER BY (index_name, source, recv_ts, kafka_partition, kafka_offset);

CREATE TABLE IF NOT EXISTS vnmd.foreign_flow
(
    source          LowCardinality(String),
    symbol          LowCardinality(String),
    exchange_ts     Nullable(DateTime64(9, 'Asia/Ho_Chi_Minh')),
    recv_ts         DateTime64(9, 'Asia/Ho_Chi_Minh') CODEC(DoubleDelta, ZSTD(1)),
    buy_qty         Nullable(Float64),
    sell_qty        Nullable(Float64),
    buy_value       Nullable(Float64),
    sell_value      Nullable(Float64),
    room_total      Nullable(Float64),
    room_left       Nullable(Float64),
    wire_code       LowCardinality(String),
    feed            LowCardinality(String),
    recv_ts_ns      UInt64,
    kafka_topic     LowCardinality(String),
    kafka_partition UInt16,
    kafka_offset    UInt64,
    dw_ts           DateTime64(3, 'Asia/Ho_Chi_Minh') DEFAULT now64(3, 'Asia/Ho_Chi_Minh')
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMMDD(recv_ts)
ORDER BY (symbol, source, recv_ts, kafka_partition, kafka_offset);

-- Candles. DNSE provides ohlc/ohlc_closed; SSI provides trade.*@1m|5m (IntervalMessage).
CREATE TABLE IF NOT EXISTS vnmd.ohlc
(
    source          LowCardinality(String),
    symbol          LowCardinality(String),
    resolution      LowCardinality(String),      -- 1 / 5 / 15 / 1H / 1D ...
    bar_ts          Nullable(DateTime64(3, 'Asia/Ho_Chi_Minh')),  -- candle OPEN time
    recv_ts         DateTime64(9, 'Asia/Ho_Chi_Minh') CODEC(DoubleDelta, ZSTD(1)),
    open            Nullable(Float64),
    high            Nullable(Float64),
    low             Nullable(Float64),
    close           Nullable(Float64),
    volume          Nullable(Float64),
    closed          UInt8,                       -- 1 = finalised candle (ohlc_closed)
    wire_code       LowCardinality(String),
    feed            LowCardinality(String),
    recv_ts_ns      UInt64,
    kafka_topic     LowCardinality(String),
    kafka_partition UInt16,
    kafka_offset    UInt64,
    dw_ts           DateTime64(3, 'Asia/Ho_Chi_Minh') DEFAULT now64(3, 'Asia/Ho_Chi_Minh')
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMMDD(recv_ts)
ORDER BY (symbol, source, resolution, recv_ts, kafka_partition, kafka_offset);

-- Aggressor-side supply/demand. Only TCBS ouranos provides it (C002S60 / C002S900).
-- Note: the TCBS docs label C002S900 as "foreign investor trading" — that is WRONG;
-- its schema is identical to C002S60, only the 900-second window differs.
CREATE TABLE IF NOT EXISTS vnmd.supply_demand
(
    source          LowCardinality(String),
    symbol          LowCardinality(String),
    exchange_ts     Nullable(DateTime64(9, 'Asia/Ho_Chi_Minh')),
    recv_ts         DateTime64(9, 'Asia/Ho_Chi_Minh') CODEC(DoubleDelta, ZSTD(1)),
    timeframe_s     Nullable(Int64),             -- 60 | 900
    buy_up_vol      Nullable(Float64),
    buy_up_vol_acc  Nullable(Float64),
    sell_down_vol   Nullable(Float64),
    sell_down_vol_acc Nullable(Float64),
    bs_ratio_acc    Nullable(Float64),
    wire_code       LowCardinality(String),
    feed            LowCardinality(String),
    recv_ts_ns      UInt64,
    kafka_topic     LowCardinality(String),
    kafka_partition UInt16,
    kafka_offset    UInt64,
    dw_ts           DateTime64(3, 'Asia/Ho_Chi_Minh') DEFAULT now64(3, 'Asia/Ho_Chi_Minh')
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMMDD(recv_ts)
ORDER BY (symbol, source, recv_ts, kafka_partition, kafka_offset);

-- Per-instrument state and price bands: ceiling, floor, reference plus session stats.
CREATE TABLE IF NOT EXISTS vnmd.instrument_state
(
    source          LowCardinality(String),
    symbol          LowCardinality(String),
    board           LowCardinality(String),
    exchange_ts     Nullable(DateTime64(9, 'Asia/Ho_Chi_Minh')),
    recv_ts         DateTime64(9, 'Asia/Ho_Chi_Minh') CODEC(DoubleDelta, ZSTD(1)),
    ceiling_price   Nullable(Float64),
    floor_price     Nullable(Float64),
    ref_price       Nullable(Float64),
    open_price      Nullable(Float64),
    high_price      Nullable(Float64),
    low_price       Nullable(Float64),
    avg_price       Nullable(Float64),
    status          LowCardinality(String),
    wire_code       LowCardinality(String),
    feed            LowCardinality(String),
    recv_ts_ns      UInt64,
    kafka_topic     LowCardinality(String),
    kafka_partition UInt16,
    kafka_offset    UInt64,
    dw_ts           DateTime64(3, 'Asia/Ho_Chi_Minh') DEFAULT now64(3, 'Asia/Ho_Chi_Minh')
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMMDD(recv_ts)
ORDER BY (symbol, source, recv_ts, kafka_partition, kafka_offset);

-- SAFETY NET. Every frame that cannot be routed lands here with its payload
-- intact. Better to over-collect than to lose a frame: when a broker introduces a
-- new wire code it shows up here immediately instead of vanishing silently.
CREATE TABLE IF NOT EXISTS vnmd.unknown_frames
(
    source          LowCardinality(String),
    feed            LowCardinality(String),
    wire_code       LowCardinality(String),
    kafka_key       String,
    payload         String CODEC(ZSTD(3)),
    recv_ts         DateTime64(9, 'Asia/Ho_Chi_Minh') CODEC(DoubleDelta, ZSTD(1)),
    recv_ts_ns      UInt64,
    kafka_topic     LowCardinality(String),
    kafka_partition UInt16,
    kafka_offset    UInt64,
    dw_ts           DateTime64(3, 'Asia/Ho_Chi_Minh') DEFAULT now64(3, 'Asia/Ho_Chi_Minh')
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMMDD(recv_ts)
ORDER BY (source, wire_code, recv_ts, kafka_partition, kafka_offset);
