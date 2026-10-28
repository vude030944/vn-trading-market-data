# vnmd-transform

Turns raw frames sitting in Kafka into queryable tables in ClickHouse.

A **Flink job** (Java, `src/main/java/vnmd/transform/`) consumes the five raw
topics, routes and parses every frame, and **batch-inserts** typed rows into
ClickHouse. ClickHouse itself only stores tables and serves views (`sql/`); it
does **not** read Kafka.

---

## 1. Data flow

```
Kafka  *.data.raw.*  (5 topics, payload verbatim + headers)
   │
   ▼  Flink job "vnmd-transform"
   │    FrameDeserializer   headers -> source / feed / wire_code / recv_ts_ns
   │    FrameRouter         every frame -> 1 raw row
   │                                     + parsed rows (TcbsParser / SsiParser / DnseParser)
   │                                       or 1 unknown_frames row if nothing matched
   │    ClickHouseSink      per-table buffers -> INSERT ... FORMAT JSONEachRow (HTTP)
   ▼
ClickHouse  vnmd.raw  (payload VERBATIM, 7-day TTL)
            trades · book · index_values · foreign_flow · ohlc
            supply_demand · instrument_state · unknown_frames
```

`vnmd.raw` is the safety net: a wrong parser is fixed by truncating the target
tables and replaying. Had the landing layer transformed anything, the original
would be gone — which is why it transforms nothing.

**Message identity = `(kafka_topic, kafka_partition, kafka_offset)`.** No broker
provides a sequence number, and SSI's time resolution is only one second, so a
timestamp must never be used as a key.

---

## 2. Write path: batch inserts, AT_LEAST_ONCE, append-only

| Choice | Why |
|---|---|
| **Batch inserts** (`SINK_BATCH_SIZE=5000` rows or `SINK_BATCH_INTERVAL_MS=1000`, per table) | ClickHouse wants few, large inserts; one row per insert ends in "Too many parts" |
| **Checkpoint mode `AT_LEAST_ONCE`**, every 30 s | No barrier alignment, no two-phase-commit sink. The sink flushes before each barrier, so nothing read before a checkpoint is lost |
| **Append-only, no write-time dedup** | No lookup, no `ON CONFLICT`, no transaction per insert — maximum write throughput |

**The trade-off, accepted on purpose:** after a crash the job restarts from the
last checkpoint, and rows inserted after that checkpoint are inserted **again**.

**Where duplicates are resolved:** off the write path. Every target table is a
`ReplacingMergeTree` whose sorting key ends in `(kafka_partition, kafka_offset)`,
so a replayed row is byte-identical to its first copy and collapses on merge:

* fast reads, tolerating a few duplicates for real-time display → query the table
* absolute correctness → query the `*_v` views (which use `FINAL`)

---

## 3. Table model: three brokers, one schema

The goal of this project is consolidating Vietnamese market data, so the common
question is *"HPG's price at 10:15 according to all three sources"*. Answering
that cheaply requires all three in one table. The `source` column preserves
provenance and `wire_code` preserves the broker's own channel code for tracing
back to raw.

The two time columns **must not be conflated**:

| Column | Meaning |
|---|---|
| `exchange_ts` | The **broker's** timestamp. `NULL` when the broker supplies none |
| `recv_ts` | When **we** received it; always present, stamped by ingestion |

What each source actually provides:

| Source | `exchange_ts` |
|---|---|
| DNSE | **nanoseconds** (`{Seconds, Nanos}`) — the best of the three |
| TCBS ouranos | seconds (`timeSec`) |
| TCBS thesis (s\|1…s\|42) | **nothing at all** → always `NULL` |
| SSI | seconds, as the string `YYYY/MM/DD HH:mi:ss` |

That makes `recv_ts` the **only** value comparable across all three sources.

---

## 4. Three hard parts, and how they are handled

**The same field is a string on one broker and a number on another.** TCBS cash
sends `"matchPrice":"24550"` while its derivatives feed sends `1870.5`; DNSE sends
numbers except `"volume":"12"`. Every numeric field therefore goes through
`Json.num()` / `Json.lng()` — accept a string or a number, `null` when absent or
unparsable, never throw.

**DNSE cannot be routed by `wire_code`.** The docs say to classify by a field
called `T`, but no sample payload anywhere in the documentation contains it, so
ingestion tags `wire_code='unknown'`. `DnseParser` routes **by payload shape**
(`has("matchPrice")`, `has("bid") && has("offer")`, …). That does not depend on
the unknown and stays correct if DNSE adds `T` later.

**TCBS sends the futures family twice.** Wires 21/23/24/25/27 arrive
byte-identical on BOTH the normal and the derivative socket (production audit,
docs/tcbs/brief 11.2). Only one copy is parsed — the stock socket's, which arrives
~1 ms earlier; the other is kept in `raw` only. `TCBS_FUTURES_FROM=derivative|both`
changes that if a deployment subscribes futures on one socket only.

**Nothing is silently dropped.** A frame no parser rule claims — an unlisted
wire code, a missing `source` header, a payload that is not JSON — lands in
`unknown_frames` with its payload intact.

---

## 5. Running

```bash
make transform          # apply the ClickHouse schema (idempotent) — BEFORE the job
make transform-build    # build build/libs/vnmd-transform.jar (in docker, no local Java)
make transform-submit   # (re)submit the job to the dev Flink cluster
make transform-test     # unit tests
```

The job reads its settings from program arguments or environment variables
(`--clickhouse-url` / `CLICKHOUSE_URL`, `--kafka-servers` / `KAFKA_SERVERS`,
`--sink-batch-size`, …). Defaults target the dev stack; see `JobConfig.java`.

Checks:

```sql
SELECT * FROM vnmd.v_feed_health;      -- which feeds are alive and how long they have been quiet
SELECT * FROM vnmd.v_unknown_summary;  -- has a broker started emitting an unknown channel?
SELECT * FROM vnmd.v_feed_latency;     -- true latency (only for sources with exchange_ts)
SELECT * FROM vnmd.v_cross_source;     -- price divergence between the three sources
```

`v_unknown_summary` deserves an **alert**: growth there means a broker started
emitting a channel the documentation never mentioned — exactly how TCBS's `s|42`
went unnoticed.

**Upgrading a database built by an older `apply.sh`:** `10_landing.sql` drops the
old Kafka engine tables and materialized views. Without that, ClickHouse would
keep consuming Kafka next to Flink and write every row twice.

---

## 6. Verification status

`FrameRouterTest` runs payloads copied from the three vendors' documentation
through the router and checks the typed values (DNSE nanoseconds preserved as
`.101000000`, TCBS string prices, SSI `data` unwrapping, unknown frames kept). It
also checks **every emitted row against the DDL in `sql/`**: each key must be an
insertable column of its table, and every column without a `DEFAULT` must be
present.

**End to end:** [`environment/e2e`](../../environment/e2e/) runs this job against
Redpanda and ClickHouse fed by the broker simulator; its check pauses the market,
waits for the drain and compares every `(source, feed, wire_code)` delivered with
what landed in `vnmd.raw`, plus the routing invariants above. **Not yet verified:**
the real brokers' feeds.

Assumption: `DNSE_ENCODING=json`. With `msgpack`, DNSE frames are not JSON: they
still land in `raw` (with `error` set) and `unknown_frames`, but are not parsed.
