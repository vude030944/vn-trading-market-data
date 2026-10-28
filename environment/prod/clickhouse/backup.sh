#!/usr/bin/env bash
# Back up the vnmd database into /backup inside the container (bind-mounted to the
# host). Run from cron. Keeps the 7 most recent archives.
set -euo pipefail
C=${CH_CONTAINER:-ch-prod}
U=${CH_USER:-vnmd}; P=${CH_PASSWORD:?CH_PASSWORD is required}
NAME="vnmd-$(date +%Y%m%d-%H%M%S)"

docker exec "$C" clickhouse-client --user "$U" --password "$P" --query \
  "BACKUP DATABASE vnmd TO Disk('backups', '${NAME}.zip')"
echo "backup written: ${NAME}.zip"

# Prune old archives, keep 7
docker exec "$C" sh -c "ls -1t /backup/*.zip 2>/dev/null | tail -n +8 | xargs -r rm -f"
