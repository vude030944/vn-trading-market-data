#!/usr/bin/env bash
# ============================================================================
# Configure Redpanda cluster settings to fit the 30G disk budget (10G/broker),
# then create the five raw topics.
#
# WHY THIS IS NEEDED: Redpanda sees the entire /dev/sda1 volume (234G) and has
# no idea we only allotted it 10G per broker. There is no way to hard-cap by
# directory — limiting RETENTION is the only lever that keeps us in budget.
#
# FORMULA:  disk per broker ~= (total partitions across all topics) x retention_bytes
#           (RF=3 over 3 brokers means each broker holds exactly one copy of
#            every partition)
#
# With the defaults below (192 MiB/partition) and the 51 partitions of 5 topics:
#   51 x 192 MiB ~= 9.56 GiB/broker  -> fits the 10 GiB budget
#
# Safe to re-run at any time (idempotent).
# ============================================================================
set -euo pipefail

BROKER=${BROKER:-redpanda-0}

# 192 MiB per partition (per replica).
# Derived from the budget: 10 GiB/broker / 51 partitions ~= 200 MiB -> round to
# 192 MiB, giving ~9.56 GiB/broker. Adding topics means lowering this number.
RETENTION_BYTES=${RETENTION_BYTES:-201326592}
# 3 days — dev does not need the 7-day default.
RETENTION_MS=${RETENTION_MS:-259200000}
# 64 MiB segments: smaller than the 128 MiB default so retention trims finer.
SEGMENT_SIZE=${SEGMENT_SIZE:-67108864}

echo "==> Applying cluster config on ${BROKER}"
docker exec "${BROKER}" rpk cluster config set retention_bytes   "${RETENTION_BYTES}"
docker exec "${BROKER}" rpk cluster config set log_retention_ms  "${RETENTION_MS}"
docker exec "${BROKER}" rpk cluster config set log_segment_size  "${SEGMENT_SIZE}"

echo
echo "==> Current values"
for p in retention_bytes log_retention_ms log_segment_size disk_reservation_percent; do
  printf '  %-26s %s\n' "$p" "$(docker exec "${BROKER}" rpk cluster config get "$p")"
done

echo
echo "==> Creating topics (idempotent — rpk reports and skips existing ones)"

# PARTITION COUNTS are chosen from measured traffic, not guessed:
#   * Kafka guarantees ordering WITHIN a partition. The key is the symbol, so a
#     symbol always maps to one partition -> per-symbol ordering holds regardless
#     of partition count.
#   * More partitions means more consumer parallelism, but an empty partition
#     still costs file handles and metadata.
#   * Multiples of 3 (the broker count) so they spread evenly.
#
#   tcbs stock   12 : thousands of symbols, keys spread well, headroom for Flink
#   tcbs future   3 : one front-month contract carries >90% of the traffic and is
#                     pinned to ONE partition -> more would simply sit idle
#   tcbs ouranos 12 : per-symbol, spreads like stock
#   ssi market   12 : one topic carries all six groups (trade/quote/room/put/oddlot/market)
#   dnse market  12 : same
#
# retention.bytes is set PER TOPIC, overriding the cluster default above.
create_topic() {
  local name=$1 parts=$2
  docker exec "${BROKER}" rpk topic create "${name}" -p "${parts}" -r 3 \
      -c retention.bytes="${RETENTION_BYTES}" \
      -c retention.ms="${RETENTION_MS}" \
      -c segment.bytes="${SEGMENT_SIZE}" \
      -c compression.type=producer 2>&1 | tail -1
}

create_topic tcbs.data.raw.stock    12
create_topic tcbs.data.raw.future    3
create_topic tcbs.data.raw.ouranos  12
create_topic ssi.data.raw.market    12
create_topic dnse.data.raw.market   12

echo
echo "==> Topics now present"
docker exec "${BROKER}" rpk topic list

echo
echo "Disk estimate: (total partitions) x retention_bytes"
echo "  51 partitions x 192 MiB = ~9.56 GiB/broker   (budget 10 GiB)"
echo "Adding topics requires lowering it:  RETENTION_BYTES=<bytes> ./bootstrap.sh"
