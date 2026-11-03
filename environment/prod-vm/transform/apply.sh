#!/usr/bin/env bash
# ============================================================================
# Apply the ClickHouse schema (tables + views) the Flink job writes into.
# Idempotent — safe to re-run any number of times (every DDL statement is
# IF [NOT] EXISTS). Run it BEFORE submitting the job.
#
#   ./apply.sh                      # apply into the `clickhouse` container
#   CH_CONTAINER=ch ./apply.sh      # a different container
#   CH_HOST=1.2.3.4 ./apply.sh      # over the network instead of docker exec
# ============================================================================
set -euo pipefail

CH_CONTAINER=${CH_CONTAINER:-clickhouse}
CH_USER=${CH_USER:-vnmd}
CH_PASSWORD=${CH_PASSWORD:-vnmd_dev_password}
CH_HOST=${CH_HOST:-}

run() {
    if [[ -n "$CH_HOST" ]]; then
        clickhouse-client --host "$CH_HOST" --user "$CH_USER" --password "$CH_PASSWORD" \
            --multiquery < "$1"
    else
        docker exec -i "$CH_CONTAINER" clickhouse-client \
            --user "$CH_USER" --password "$CH_PASSWORD" --multiquery < "$1"
    fi
}

cd "$(dirname "$0")/sql"
for f in 00_database.sql 10_landing.sql 20_targets.sql 90_views.sql; do
    printf '==> %-20s ' "$f"
    run "$f" && echo OK
done

echo
echo "Quick check:"
echo "  docker exec -it $CH_CONTAINER clickhouse-client --user $CH_USER --password *** \\"
echo "    --query 'SELECT * FROM vnmd.v_feed_health FORMAT PrettyCompact'"
