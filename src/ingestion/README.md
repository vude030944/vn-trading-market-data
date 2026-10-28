# vnmd-ingestion

Collects real-time market data from **SSI**, **DNSE** and **TCBS** over WebSocket
and publishes it to Kafka. The payload is forwarded **byte-for-byte**; turning it
into typed columns is the transformation layer's job (the Flink job), not this
service's.

---

## 1. Design principles

**The payload is never touched.** A wrong parser is fixed by replaying from
Kafka; if ingestion had already transformed the data, the original would be lost
forever. Metadata travels out-of-band in Kafka headers (`source`, `feed`,
`wire_code`, `recv_ts_ns`) rather than being injected into the payload.

**Invariant engine, varying specs.** The connect → handshake → subscribe → pump →
backoff lifecycle lives in `core/`, which knows nothing about any specific broker.
If adding a fourth broker requires editing `core/`, the design is wrong.

**No broker can constrain another.** The three modules under `feeds/` and the
three files under `config/` do not inherit from one another. When a vendor changes
policy, only that vendor's file changes. Only infrastructure *we* own — Kafka,
telemetry, runtime, backoff — is shared.

**Unknowns become parameters, not silent guesses.** The SSI docs never say how the
token reaches the socket, so all three possibilities are implemented and selected
with `SSI_AUTH_MODE`.

**Never discard data we do not understand.** An unrecognised frame is still
published with a marker `wire_code`, and increments a `malformed` counter for
alerting.

---

## 2. Architecture

```
                    ┌──────────────── core/ (invariant) ─────────────────────┐
                    │  WsEngine: connect → handshake → subscribe →           │
   feeds/ssi.py ──▶ │            [heartbeat ‖ pump] → backoff → repeat       │ ──▶ KafkaPublisher ──▶ Kafka
   feeds/dnse.py ─▶ │  Runner  : hosts N feeds, bulkheaded, graceful stop    │
   feeds/tcbs/* ──▶ │  Telemetry: queue + dedicated thread, drops when full  │
                    └────────────────────────────────────────────────────────┘
```

| Directory | Role | Pattern |
|---|---|---|
| `config/` | Values only. Shared infrastructure attached by composition | Composition over inheritance |
| `core/spec.py` | The single contract between engine and brokers | **Strategy** |
| `core/engine.py` | Fixed lifecycle, broker-agnostic | **Template Method** |
| `core/runner.py` | Hosts N feeds, one task each | **Bulkhead** |
| `feeds/__init__.py` | `broker → specs` | **Registry** (hand-written, no module scanning) |
| `core/connection.py` | Wraps the websockets library | **Adapter** |

The `FeedSpec` contract has exactly **five** responsibilities: `connect_kwargs`,
`handshake`, `subscribe_frames`, `heartbeat_*`, `on_message`. Each additional
method would be a constraint imposed on all three brokers; an interface that grows
optional methods to accommodate exceptions is a rotting interface.

---

## 3. Service split

| Service | Feeds inside | Why |
|---|---|---|
| `ingest-tcbs` | `tcbs.stock`, `tcbs.derivative`, `tcbs.ouranos` | **Forced together**: TCBS ties one token to one connection, so the three feeds must share a token in one process. Inside it they remain 3 independent tasks — a broken ouranos feed does not take the cash price board down |
| `ingest-ssi` | `ssi.market` | SSI has exactly one WebSocket connection (the `DATA` channel) |
| `ingest-dnse` | `dnse.market` | One connection; scales horizontally by sharding |

All three run the **same image**, differing only in `--broker`.

### Scaling DNSE horizontally

DNSE's `auth_success` reports `subscriptions_max` (currently 100). Once the
universe exceeds it, run several replicas, each taking one slice:

```bash
DNSE_SHARD_COUNT=3   DNSE_SHARD_INDEX=0|1|2
```

Sharding uses `crc32(symbol) % shard_count` — stable, so adding or removing
symbols does not reshuffle everything and a symbol always lands on one replica.

---

## 4. Running

```bash
cp .env.example .env      # fill in credentials
docker network create vnmd-dev            # if it does not exist yet
docker compose up -d --build
docker compose logs -f ingest-tcbs
```

Running a single broker by hand:

```bash
uv venv .venv && uv pip install -p .venv -r <(uv pip compile pyproject.toml)
.venv/bin/python -m ingestion --broker tcbs
```

Tests (run **any time**, no open market needed):

```bash
.venv/bin/python -m pytest tests/ -q
```

---

## 5. Resource budget

| Service | RAM | CPU |
|---|---:|---:|
| ingest-ssi | 384 M | 0.35 |
| ingest-dnse | 384 M | 0.35 |
| ingest-tcbs | 512 M | 0.50 |
| **Total** | **1.25 G** | **1.20** |

Added to the infrastructure in `environment/dev` (13.67 G / 7.75 cores), the sum
of CPU *limits* exceeds the 8 physical cores. That is **acceptable**: `cpus` is a
*limit*, not a *reservation* — containers only consume while busy, and the three
ingestion services spend most of their time waiting on socket I/O. For hard
guarantees, lower the Flink TaskManager from `2.0 → 1.5` and ClickHouse from
`2.0 → 1.5` in `environment/dev/*/.env`.

`stop_grace_period: 30s` is deliberately longer than `KAFKA_FLUSH_TIMEOUT_S=15`,
so shutdown has time to flush the producer buffer.

---

## 6. Vendor ambiguities (parameterised, still unverified)

| Broker | Uncertainty | Environment variable | Default |
|---|---|---|---|
| SSI | How the token is passed at connect (10.3) | `SSI_AUTH_MODE` | `query` |
| SSI | Two conflicting endpoints (10.1) | `SSI_STREAM_URL` | `.../ws/v3` (the SDK value) |
| SSI | `expiresAt` in seconds or milliseconds (10.2) | `SSI_EXPIRES_AT_UNIT` | `auto` |
| SSI | Does streaming require OTP? (10.6) | `SSI_REQUIRE_OTP` | `0` |
| DNSE | The value set of the `T` field | — | absent `T` → `wire_code=unknown`, **still forwarded** |
| TCBS | The real heartbeat threshold | — | read from `d\|33\|N`; config is only a default |

Two things are **absent** from the vendor documentation yet implemented here on
the strength of production evidence from `examples/`:

* **`dtn`** in the TCBS derivatives channel codes — it unlocks channel `s|42`
  (the 10-level depth book), roughly 94% of the futures topic's traffic. Omitting
  it loses the single largest channel.
* **`d|pi`** — a server-initiated ouranos ping arriving about every 10 seconds.
  Unfiltered, it floods the logs with "unrecognised message" warnings.

One bug from `examples/` is also fixed here: index frames `s|8` carry only
`indexNumber` as a **number** (no `indexId`), so the old regex returned `None`,
leaving the Kafka key empty on 100% of index frames and destroying per-index
ordering. `framing.extract_key()` now tries `symbol → indexId → indexNumber`.

---

## 7. Operations

**Three different clocks — do not conflate them.**
`recv_ns` (monotonic) is only for **measuring durations**, immune to NTP steps.
`recv_ts_ns` (epoch) is the **event-time label** shipped in the Kafka header.
The broker's own timestamp, where one exists, stays inside the payload for the
transform layer to read.

**Backpressure is real.** The sink does `await publisher.publish(...)` rather than
`create_task` — when the producer buffer fills, the socket read loop slows down.
Using `create_task` would break **per-symbol ordering**, exactly the bug
`examples/ssi-data` had.

**No broker offers a sequence number.** Messages lost during a disconnect cannot
be detected, which is why message identity is Kafka's
`(topic, partition, offset)` and never a timestamp.

**Key metrics** (`market_data_*`, labelled `source`/`feed`/`status`):
`messages_total`, `publish_latency_ms`, `interarrival_ms`, `last_message_age_ms`,
`reconnects_total`, `kafka_errors_total`. A dead-feed alert must combine
`last_message_age_ms` **with the session calendar** — outside trading hours the
connection is alive but silent, and that is normal.

**If Kafka is unreachable the service exits immediately** (fail fast) and Docker's
`restart: unless-stopped` brings it back — deliberate, rather than running on in a
state where it cannot deliver anything.
