# environment/e2e — the whole pipeline against simulated brokers

```
market-sim ──ws──► ingest-ssi / ingest-dnse / ingest-tcbs ──► Redpanda ×3 ──► Flink job ──► ClickHouse
(src/simulator)    (the real ingestion image)                 (5 topics)      (src/transform)
```

Self-contained: one compose file, named volumes (no host paths, so it runs on
Docker Desktop for Windows/macOS as well as Linux), no `.env`, no `make`.

## Run

```bash
docker compose -f environment/e2e/docker-compose.yml up -d --build
docker compose -f environment/e2e/docker-compose.yml run --rm e2e-check
docker compose -f environment/e2e/docker-compose.yml down -v      # -v wipes the data
```

`e2e-check` waits for all three sources to reach ClickHouse, lets the market run
30 s, **pauses** the simulator, waits for the pipeline to drain, then compares
per `(source, feed, wire_code)` the frames the simulator delivered with the
distinct Kafka records in `vnmd.raw` — they must be equal. It also checks every
parsed table has rows, routing invariants (e.g. TCBS futures parsed once though
they arrive on two sockets), feed latency and cross-source prices. Exit code 0 =
nothing lost.

| UI | URL |
|---|---|
| Simulator stats | <http://localhost:18080/stats> |
| Redpanda Console | <http://localhost:18088> |
| Flink | <http://localhost:18081> |
| ClickHouse HTTP | `localhost:18123` (user `vnmd` / `vnmd_e2e_password`) |

Ports are offset from `environment/dev` (`1xxxx`), so both stacks can coexist
— except Kafka's `19092`, which is shared: stop one stack before starting the other.

## Memory: ≤ 20 GiB

Every container has a hard `mem_limit`:

| Service | Limit |
|---|---:|
| redpanda ×3 | 3 × 2.0 G |
| clickhouse | 5.0 G |
| flink taskmanager / jobmanager | 4.0 G + 1.5 G |
| ingestion ssi / dnse / tcbs | 0.4 + 0.4 + 0.5 G |
| market-sim | 0.5 G |
| redpanda console | 0.4 G |
| **long-running total** | **18.7 G** |
| one-shot: topics, ch-schema, flink-submit | ≤ 1.0 G, before steady state |

Docker Desktop on WSL2 gives its VM **50 % of host RAM by default** (16 GB on a
32 GB machine). Caps are ceilings, not reservations, and the stack actually
uses far less (see `docker stats`), so it runs under the default. To let it use
the full 20 GB, add to `%UserProfile%\.wslconfig`, then `wsl --shutdown`:

```ini
[wsl2]
memory=20GB
```

## Knobs

`SIM_TRADES_PER_SEC=200 docker compose ... up -d` raises the load;
`SIM_CHAOS_DROP_EVERY_S=20` drops a connection per broker every 20 s to exercise
reconnect (with chaos on, a few in-flight frames may legitimately be lost —
the brokers have no replay); `SIM_MARKET_HOURS=1` trades only in real HOSE
sessions.
