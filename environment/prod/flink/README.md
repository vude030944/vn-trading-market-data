# Flink — PROD

**Required by the pipeline.** Flink runs the transform job (`src/transform/`):
it consumes the `*.data.raw.*` topics, parses every frame and batch-inserts the
rows into ClickHouse. If Flink is down, Kafka keeps buffering (within retention)
and ClickHouse simply stops receiving new rows.

Submit the job with the production endpoints:

```bash
flink run -d vnmd-transform.jar \
  --kafka-servers <brokers> \
  --kafka-security-protocol SASL_SSL --kafka-sasl-mechanism SCRAM-SHA-512 \
  --kafka-sasl-jaas-config '<jaas line>' \
  --clickhouse-url http://<clickhouse>:8123 \
  --clickhouse-user <user> --clickhouse-password <password>
```

Mandatory differences from dev:

| | dev | prod |
|---|---|---|
| JobManager | 1, no HA | HA (ZooKeeper or Kubernetes) — a single JM is a single point of failure |
| TaskManager | 1 | several, sized to real parallelism |
| Checkpoints | local disk | S3/MinIO — a JM crash loses local checkpoints, and with them the resume offsets |
| Savepoints | local disk | S3/MinIO |
