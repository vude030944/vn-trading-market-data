# environment/prod

The hardened counterpart to `environment/dev`. **Not deployable as-is** — several
values must be supplied first, marked `<<< FILL IN >>>` in each `.env.example`.

---

## 1. What differs from dev, and why

| | dev | prod | Reason |
|---|---|---|---|
| Redpanda mode | `--mode dev-container` | **removed** | dev-container **disables fsync**. A power loss then loses acknowledged data. Never acceptable in production |
| Redpanda RAM | 1.2 G/broker | **≥ 4 G/broker** | Redpanda recommends ~2 GB per core; below that invites hard-to-reproduce failures |
| Kafka auth | PLAINTEXT | **SASL_SSL + SCRAM** | |
| ClickHouse | single node | single node + backups | Replication needs ClickHouse Keeper — see section 4 |
| Flink | 1 JM + 1 TM, no HA | **HA + several TMs** | A lone JobManager is a single point of failure |
| Flink checkpoints | local disk | **S3/MinIO** | A JM crash loses local checkpoints |
| Ingestion | 1 replica/broker | 1 replica/broker | **Must NOT scale beyond 1** per credential — see section 3 |
| Secrets | `.env` in the repo | **secret manager** | |
| Kafka retention | 3 days | 7–30 days | Production needs room to replay when a parser bug surfaces |

---

## 2. Deployment order

```bash
cd kafka         && cp .env.example .env && $EDITOR .env && docker compose up -d && ./bootstrap.sh
cd ../clickhouse && cp .env.example .env && $EDITOR .env && docker compose up -d
cd ../../../src/transform && CH_HOST=<prod-host> ./apply.sh   # schema BEFORE the job
# Flink cluster up, then submit the transform job — see flink/README.md
cd ../../environment/prod/ingestion && cp .env.example .env && $EDITOR .env && docker compose up -d
```

---

## 3. Never run multiple ingestion replicas on one credential

Each replica opens its own connection and publishes **every message twice**. Those
duplicates cannot be removed downstream, because the two connections produce two
different `(partition, offset)` pairs — by Kafka identity they are two
legitimately distinct records.

To increase throughput instead:

* **DNSE** — use sharding: `DNSE_SHARD_COUNT=N` with a distinct
  `DNSE_SHARD_INDEX` per replica. The universe is split by
  `crc32(symbol) % N`, so slices never overlap.
* **TCBS** — cannot be split. The one-token-one-connection constraint forces all
  three feeds into a single process. More throughput requires additional
  tokens/accounts.
* **SSI** — a single connection exists; there is nothing to split.

Hence the prod compose files pin `deploy.replicas: 1` and deliberately avoid
`--scale`.

---

## 4. Known gaps (better known now than discovered at 9am)

* **ClickHouse is a single node with no replication.** Adequate for the early
  stage, but losing the disk loses the parsed data (raw data remains in Kafka and
  can be rebuilt within the retention window). For HA, add ClickHouse Keeper and
  switch to `ReplicatedReplacingMergeTree` in
  `src/transform/sql/20_targets.sql`; everything else stays the same.
* **No ClickHouse backup schedule yet.** At minimum, run
  `BACKUP DATABASE vnmd TO Disk(...)` on a timer (`clickhouse/backup.sh`), or rely
  on replay from Kafka.
* **The TCBS token expires after 8 hours and has NO refresh token.** That is a
  broker constraint, not a gap in the code. Production needs a token-provisioning
  procedure; the service warns 30 minutes ahead
  (`TCBS_TOKEN_REFRESH_LEAD_S`).
* **Three ambiguities in the SSI documentation** (how the token is passed, the
  unit of `expiresAt`, whether OTP is required) are already parameterised — see
  `docs/ssi/brief/DOCUMENT.md` section 10. Verify them against the live
  environment before trusting the defaults.
