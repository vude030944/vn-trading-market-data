"""
End-to-end verdict: did every frame the simulated brokers sent land in ClickHouse,
and was each one routed where the transform says it should go?

  1. wait until all three sources have data in vnmd.raw, then let it run WARMUP_S
  2. PAUSE the simulated market, read the simulator's delivery counters
  3. poll ClickHouse until the pipeline has drained
  4. compare, per (source, feed, wire_code):  sent  vs  distinct Kafka records in raw
  5. check the parsed tables, the routing invariants, latency, cross-source prices
  6. RESUME the market

Exit code 0 only if nothing was lost and the invariants hold. Stdlib only.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.parse
import urllib.request

SIM = os.environ.get("SIM_URL", "http://localhost:18080")
CH = os.environ.get("CH_URL", "http://localhost:18123")
CH_AUTH = {"X-ClickHouse-User": os.environ.get("CH_USER", "vnmd"),
           "X-ClickHouse-Key": os.environ.get("CH_PASSWORD", "vnmd_e2e_password")}
WARMUP_S = float(os.environ.get("WARMUP_S", "30"))
DRAIN_TIMEOUT_S = float(os.environ.get("DRAIN_TIMEOUT_S", "150"))

failures: list[str] = []
# Only frames received since the simulator last started are compared: its counters
# reset on restart, while ClickHouse keeps everything.
SINCE = 0


def http(url: str, data: bytes | None = None, headers: dict | None = None) -> bytes:
    req = urllib.request.Request(url, data=data, headers=headers or {},
                                 method="POST" if data is not None else "GET")
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def ch(sql: str) -> list[dict]:
    body = http(f"{CH}/?" + urllib.parse.urlencode({"default_format": "JSONEachRow"}),
                sql.encode(), CH_AUTH)
    return [json.loads(line) for line in body.decode().splitlines() if line]


def sim_stats() -> dict:
    return json.loads(http(f"{SIM}/stats"))


def sim_control(action: str) -> None:
    http(f"{SIM}/control/{action}", b"")


def table(rows: list[list], header: list[str]) -> None:
    widths = [max(len(str(x)) for x in col) for col in zip(header, *rows)]
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*header))
    print(fmt.format(*("-" * w for w in widths)))
    for r in rows:
        print(fmt.format(*r))
    print()


def landed() -> dict[tuple[str, str, str], tuple[int, int]]:
    rows = ch(f"""SELECT source, feed, wire_code,
                        uniqExact(kafka_topic, kafka_partition, kafka_offset) AS distinct_records,
                        count() AS row_count
                 FROM vnmd.raw WHERE recv_ts_ns >= {SINCE} GROUP BY source, feed, wire_code""")
    return {(r["source"], r["feed"], r["wire_code"]): (int(r["distinct_records"]), int(r["row_count"]))
            for r in rows}


def main() -> int:
    global SINCE
    print(f"simulator {SIM}   clickhouse {CH}\n")

    # 1. warm-up ---------------------------------------------------------------
    deadline = time.time() + 300
    while True:
        try:
            have = {r["source"] for r in ch("SELECT DISTINCT source FROM vnmd.raw")}
        except Exception as exc:                     # ClickHouse / schema not ready yet
            have = set()
            print(f"  waiting for ClickHouse: {exc!r}")
        if {"ssi", "dnse", "tcbs"} <= have:
            break
        if time.time() > deadline:
            print(f"FAIL: after 300 s only {sorted(have)} have reached vnmd.raw")
            return 1
        print(f"  waiting for data from all three sources (have {sorted(have)})")
        time.sleep(5)
    print(f"all three sources are flowing; running {WARMUP_S:.0f} s more before pausing\n")
    time.sleep(WARMUP_S)

    # 2. freeze the market ------------------------------------------------------
    sim_control("pause")
    try:
        time.sleep(2)                                # let queued frames reach the sockets
        def sent_now() -> tuple[dict, dict]:
            # Re-read every time: while paused the market is silent, but a client
            # reconnecting still gets snapshots (TCBS s|38, s|4; SSI/DNSE start of day).
            st = sim_stats()
            return st, {(s, f, w): n for s, feeds in st["frames"].items()
                        for f, wires in feeds.items() for w, n in wires.items()}

        stats, sent = sent_now()
        SINCE = int(stats["started"] * 1e9)
        print(f"market paused — simulator delivered {sum(sent.values()):,} data frames "
              f"over {stats['uptime_s']:.0f} s; connection events: {json.dumps(stats['events'])}\n")

        # 3. drain ----------------------------------------------------------------
        start, prev = time.time(), None
        while True:
            stats, sent = sent_now()
            got = landed()
            missing = sum(max(0, n - got.get(k, (0, 0))[0]) for k, n in sent.items())
            if missing == 0:
                print(f"pipeline drained in {time.time() - start:.0f} s\n")
                break
            if time.time() - start > DRAIN_TIMEOUT_S:
                print(f"drain timeout: {missing:,} frames still missing\n")
                break
            if missing != prev:
                print(f"  draining: {missing:,} frames not yet in ClickHouse")
                prev = missing
            time.sleep(5)

        # 4. delivery, frame by frame ------------------------------------------------
        print("== DELIVERY: simulator -> ingestion -> Kafka -> Flink -> vnmd.raw")
        rows, keys = [], sorted(set(sent) | set(got))
        for k in keys:
            n_sent = sent.get(k, 0)
            n_distinct, n_rows = got.get(k, (0, 0))
            status = "ok" if n_distinct == n_sent else ("LOST" if n_distinct < n_sent else "EXTRA")
            if status != "ok":
                failures.append(f"raw {k}: sent {n_sent}, landed {n_distinct}")
            rows.append([*k, n_sent, n_distinct, n_rows - n_distinct, status])
        table(rows, ["source", "feed", "wire_code", "sent", "landed", "replayed_dups", "status"])

        # 5a. parsed tables --------------------------------------------------------
        print("== PARSED TABLES (distinct Kafka records per source)")
        targets = ["trades", "book", "index_values", "foreign_flow", "ohlc",
                   "supply_demand", "instrument_state", "unknown_frames"]
        union = " UNION ALL ".join(
            f"SELECT '{t}' AS tbl, source, uniqExact(kafka_topic, kafka_partition, kafka_offset) AS n "
            f"FROM vnmd.{t} WHERE recv_ts_ns >= {SINCE} GROUP BY source" for t in targets)
        parsed = {(r["tbl"], r["source"]): int(r["n"]) for r in ch(union)}
        table([[t] + [parsed.get((t, s), 0) for s in ("ssi", "dnse", "tcbs")] for t in targets],
              ["table", "ssi", "dnse", "tcbs"])
        expected = {"trades": ("ssi", "dnse", "tcbs"), "book": ("ssi", "dnse", "tcbs"),
                    "index_values": ("dnse", "tcbs"), "foreign_flow": ("ssi", "dnse", "tcbs"),
                    "ohlc": ("dnse",), "supply_demand": ("tcbs",),
                    "instrument_state": ("ssi", "dnse", "tcbs")}
        for t, sources in expected.items():
            for s in sources:
                if not parsed.get((t, s)):
                    failures.append(f"{t} has no rows from {s}")

        print("== UNKNOWN FRAMES (by design these are channels no parser claims)")
        table([[r["source"], r["wire_code"], r["n"]] for r in ch(
            f"SELECT source, wire_code, count() AS n FROM vnmd.unknown_frames "
            f"WHERE recv_ts_ns >= {SINCE} GROUP BY source, wire_code ORDER BY n DESC")] or [["-", "-", 0]],
              ["source", "wire_code", "frames"])

        # 5b. routing invariants -----------------------------------------------------
        print("== ROUTING INVARIANTS")

        def raw_n(source, feed, wires):
            return sum(got.get((source, feed, w), (0, 0))[0] for w in wires)

        def tgt_n(tbl, source, cond="1"):
            return int(ch(f"SELECT uniqExact(kafka_topic, kafka_partition, kafka_offset) AS n "
                          f"FROM vnmd.{tbl} WHERE source = '{source}' AND {cond} "
                          f"AND recv_ts_ns >= {SINCE}")[0]["n"])

        checks = [
            ("ssi trades = trade_tick + put_tick + oddlot_tick frames",
             tgt_n("trades", "ssi"),
             raw_n("ssi", "ssi.market", ("trade_tick", "put_tick", "oddlot_tick"))),
            ("tcbs futures trades parsed ONCE (stock-socket copy only)",
             tgt_n("trades", "tcbs", "wire_code = 's|21'"),
             raw_n("tcbs", "tcbs.stock", ("s|21",))),
            ("tcbs s|42 depth levels all parsed into book",
             tgt_n("book", "tcbs", "wire_code = 's|42'"),
             raw_n("tcbs", "tcbs.derivative", ("s|42",))),
            ("tcbs ouranos C001 trades all parsed",
             tgt_n("trades", "tcbs", "wire_code = 'C001'"),
             raw_n("tcbs", "tcbs.ouranos", ("C001",))),
            ("dnse ticks (matchPrice) = trades rows",
             tgt_n("trades", "dnse"),
             int(ch("SELECT uniqExact(kafka_topic, kafka_partition, kafka_offset) AS n FROM vnmd.raw "
                    f"WHERE source='dnse' AND JSONHas(payload, 'matchPrice') AND recv_ts_ns >= {SINCE}"
                    )[0]["n"])),
        ]
        rows = []
        for name, a, b in checks:
            ok = a == b and b > 0
            if not ok:
                failures.append(f"invariant: {name}: {a} != {b}")
            rows.append([name, a, b, "ok" if ok else "FAIL"])
        dup_copies = raw_n("tcbs", "tcbs.derivative", ("s|21",))
        rows.append(["  (s|21 copies on the derivative socket, kept only in raw)", dup_copies,
                     "", "info"])
        table(rows, ["invariant", "parsed", "expected", "status"])

        # 5c. latency and cross-source --------------------------------------------
        print("== FEED LATENCY (exchange_ts -> recv_ts), sources that stamp a time")
        table([[r["source"], r["wire_code"], r["n"], r["p50_lag_ms"], r["p99_lag_ms"]]
               for r in ch("SELECT * FROM vnmd.v_feed_latency")] or [["-"] * 5],
              ["source", "wire_code", "n", "p50_ms", "p99_ms"])

        print("== CROSS-SOURCE last price, 5 VN30 names (units differ by broker: SSI/DNSE "
              "quote thousand VND, TCBS VND)")
        table([[r["symbol"], r["price_ssi"], r["price_dnse"], r["price_tcbs"]] for r in ch(
            "SELECT symbol, price_ssi, price_dnse, price_tcbs FROM vnmd.v_cross_source "
            "WHERE symbol IN ('HPG','FPT','TCB','VNM','SSI') ORDER BY symbol")] or [["-"] * 4],
              ["symbol", "ssi", "dnse", "tcbs"])
    finally:
        sim_control("resume")
        print("market resumed")

    if failures:
        print("\nFAILED:")
        for f in failures:
            print("  -", f)
        return 1
    print("\nPASSED: every frame delivered, every invariant holds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
