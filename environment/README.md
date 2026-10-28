# environment/ — local infrastructure

```
environment/
├── dev/
│   ├── kafka/          Redpanda: 3 brokers + Console
│   ├── flink/          Flink 2.3 (1 JobManager + 1 TaskManager)
│   ├── clickhouse/     ClickHouse, single node
│   └── observability/  OTel + Prometheus + Grafana (optional)
└── prod/               hardened production variants
```

Each stack is its own `docker-compose.yml`, wired together by **one shared Docker
network named `vnmd-dev`**. That allows starting, stopping and restarting any
piece independently while they still address each other by hostname
(`redpanda-0`, `jobmanager`, `clickhouse`).

---

## 1. Resource allocation

Budget: **16 GB RAM · 8 cores · 64 GB disk**.

| Service | RAM | CPU | Disk |
|---|---:|---:|---:|
| redpanda-0 | 1.6 G | 1.0 | 10 G |
| redpanda-1 | 1.6 G | 1.0 | 10 G |
| redpanda-2 | 1.6 G | 1.0 | 10 G |
| redpanda-console | 0.4 G | 0.25 | – |
| flink-jobmanager | 1.2 G | 0.5 | ~1 G |
| flink-taskmanager | 3.5 G | 2.0 | ~4 G |
| clickhouse | 4.0 G | 2.0 | 25 G |
| **Total** | **13.9 G** | **7.75** | **60 G** |
| *Headroom* | *2.1 G* | *0.25* | *4 G* |

The headroom is deliberate: the Docker daemon, page cache, and room for the
machine to breathe with all three stacks running. The numbers live in each
directory's `.env` — change them there, not in the compose files.

**Why leave RAM unused rather than allocate all 16 G:** `mem_limit` is a hard
cgroup boundary. Hitting it means the container is **OOM-killed**, not "slowed
down". Flink is more delicate still: `*.memory.process.size` is set **below**
`mem_limit` (1024m < 1200m, 3072m < 3500m) so JVM heap, metaspace and overhead
still have room before the cgroup intervenes.

### Data lives on the HDD, not on `/`

```
DATA_ROOT=/home/vude030944/Data_HDD/vn-trading-market-data/dev
```

The `/` partition (`/dev/nvme0n1p1`) has only **53 G free** — short of the 64 G
budget — and Docker places volumes under `/var/lib/docker` on that very
partition. `/dev/sda1`, mounted at `/home/vude030944/Data_HDD`, has **222 G**, so
every data directory is bind-mounted there. Only images (~2 G) remain on `/`.

### Kafka's disk budget is enforced by retention

Redpanda sees the whole 234 G volume and has no idea it was allotted 10 G per
broker, and **there is no way to hard-cap by directory**. Retention is the only
lever:

```bash
cd dev/kafka && ./bootstrap.sh
```

The script sets `retention_bytes=192 MiB` per partition, `log_retention_ms=3 days`
and `log_segment_size=64 MiB`, then creates the five raw topics. The estimate:

```
disk per broker ≈ (total partitions across all topics) × retention_bytes
```

51 partitions × 192 MiB ≈ 9.56 GiB per broker, inside the 10 G budget. Adding
topics means lowering `retention_bytes` accordingly.

---

## 2. Bringing it up

```bash
# First time: shared network and data directories
docker network create vnmd-dev
mkdir -p /home/vude030944/Data_HDD/vn-trading-market-data/dev/{redpanda-0,redpanda-1,redpanda-2,clickhouse/{data,logs},flink/{checkpoints,savepoints,uploads}}

# Order matters: Kafka -> ClickHouse -> Flink (Flink consumes from both)
cd dev/kafka      && docker compose up -d && ./bootstrap.sh
cd ../clickhouse  && docker compose up -d
cd ../flink       && docker compose up -d
```

Or simply `make up` from the repository root, which waits for health checks
between steps.

Shutting down: `docker compose down` in each directory. Adding `-v` does **not**
delete data because bind mounts are used; to wipe it, delete the directories under
`DATA_ROOT`.

---

## 3. Ports

| Service | Host | Notes |
|---|---|---|
| Kafka API | `localhost:19092`, `:19093`, `:19094` | for clients on **the host** |
| Kafka (in-network) | `redpanda-0:9092`, `redpanda-1:9092`, `redpanda-2:9092` | for clients **in containers** |
| Schema Registry | `localhost:18081` / `:18084` / `:18086` | |
| HTTP Proxy | `localhost:18082` / `:18083` / `:18085` | |
| Redpanda Admin | `localhost:19644` / `:19645` / `:19646` | |
| Redpanda Console | <http://localhost:8080> | |
| Flink UI / REST | <http://localhost:8081> | job submission |
| ClickHouse HTTP | `localhost:8123` | |
| ClickHouse Native | `localhost:9000` | |
| Prometheus / Grafana | `:9090` / `:3000` | only with the observability stack up |

Schema Registry sits on `18081` rather than the default `8081` specifically to
**avoid colliding with the Flink UI**.

---

## 4. Quick checks

```bash
# Kafka: did the three brokers form a cluster?
docker exec redpanda-0 rpk cluster info

# Kafka: produce and consume
echo hello | docker exec -i redpanda-0 rpk topic produce ssi.data.raw.market
docker exec redpanda-0 rpk topic consume ssi.data.raw.market -n 1 -o start

# Flink: has the TaskManager registered? (expect slots-total = 2)
curl -s http://localhost:8081/overview

# ClickHouse: the client ships inside the server image
docker exec -it clickhouse clickhouse-client --user vnmd --password vnmd_dev_password
```

---

## 5. ClickHouse: server and client are one image

**Yes, they are merged.** Verified on the `clickhouse:26.7.3.19` image itself:

```
/usr/bin/clickhouse-client -> /usr/bin/clickhouse
/usr/bin/clickhouse-local  -> /usr/bin/clickhouse
/usr/bin/clickhouse-server -> /usr/bin/clickhouse
```

All three are symlinks to **one multi-call binary**. Therefore:

* Do **NOT** add a separate `clickhouse-client` service. The
  `clickhouse/clickhouse-client` image has been **unpublished since 2022** (its
  newest tag is `21.8`), so referencing it fails — there is no `26.7.3.19` tag.
* Use the client with `docker exec -it clickhouse clickhouse-client ...`
* The image used here is the Docker Official Image named `clickhouse`.
  `clickhouse/clickhouse-server:26.7.3.19` also exists and is equivalent;
  `clickhouse/clickhouse:26.7.3.19` does **not** exist.

---

## 6. Three traps hit while building this (do not repeat them)

None of these surface during `docker compose config` — only when actually running:

1. **Mounting over ClickHouse's whole `config.d` directory.** The image ships
   `config.d/docker_related_config.xml` containing
   `<listen_host>0.0.0.0</listen_host>`. Bind-mounting over the directory hides
   that file, so ClickHouse listens only on `127.0.0.1`. The internal health check
   still reports **green** while Flink gets `Connection refused`. → Mount
   **individual files**.

2. **`users.d` must not be `:ro`.** With `CLICKHOUSE_USER`/`CLICKHOUSE_PASSWORD`
   set, the entrypoint **writes** `users.d/default-user.xml`. Marking it read-only
   causes a restart loop with `Read-only file system`. → The file
   `users.d/default-user.xml` is container-generated, not a source file.

3. **Lowering ClickHouse's `background_pool_size` kills the server at startup.**
   A sanity check requires
   `background_pool_size × background_merges_mutations_concurrency_ratio ≥
   number_of_free_entries_in_pool_to_execute_mutation` (default 20). Setting
   `background_pool_size=8` (8×2=16 < 20) yields `BAD_ARGUMENTS` and the container
   never starts. → Keep the default; core usage is already bounded by
   `cpus: 2.0`.

Also: `CLICKHOUSE_DB` only creates the database on the **first** initialisation of
the data directory. If that directory already exists — even from a previous failed
run — the database is **not** created; delete `$DATA_ROOT/clickhouse/data` and
bring it up again.

---

## 7. Production

See [`prod/README.md`](prod/README.md). The critical differences are that
Redpanda **drops `--mode dev-container`** (that mode disables fsync and loses
acknowledged data on power failure), Kafka requires SASL/TLS, ClickHouse stops
publishing its ports, and ingestion **must not be scaled beyond one replica per
broker**.
