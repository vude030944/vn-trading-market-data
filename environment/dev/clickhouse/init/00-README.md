Any `.sql` or `.sh` file placed here runs ONCE, when ClickHouse initialises its
data directory for the first time (the same idea as `docker-entrypoint-initdb.d`
in Postgres/MySQL).

If `${DATA_ROOT}/clickhouse/data` already contains data, these scripts do NOT run
again. To re-run them: stop the stack, delete the data directory, then
`docker compose up -d`.
