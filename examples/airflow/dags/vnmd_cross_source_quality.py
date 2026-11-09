"""
vnmd_cross_source_quality — cross-broker data-quality check for the trading day.

Compares SSI / DNSE / TCBS inside ClickHouse after the session closes and
writes a Markdown report the morning after.

Design notes
------------
* The DAG runs against the PROD ClickHouse on the GCP VM over HTTP (8123), not
  against the local Airflow stack's own database. Credentials come from env vars
  so nothing secret lives in this file.
* Everything is driven by ONE trading day (`run_date`), because a day is the
  unit a trader cares about. Cross-midnight data is pulled with an explicit
  [00:00, 24:00) window instead of `toStartOfDay(now())` so a re-run after
  midnight still reports the right day.
* Checks are read-only. Nothing here mutates the target tables.
"""

from __future__ import annotations

import os
import textwrap
from datetime import date, datetime, timedelta

from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.python.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup

# --------------------------------------------------------------------------
# Connection / environment
# --------------------------------------------------------------------------
CH_HTTP_URL = os.environ.get("VNMD_CH_URL", "http://34.87.180.247:8123")
CH_DATABASE = os.environ.get("VNMD_CH_DATABASE", "vnmd")
CH_USER = os.environ.get("VNMD_CH_USER", "default")
CH_PASSWORD = os.environ.get("VNMD_CH_PASSWORD", "")
REPORT_DIR = os.environ.get("VNMD_REPORT_DIR", "/opt/airflow/reports")

# The connection id must exist in Airflow's metadata DB; create it from env if
# the operator complains, but keep the default working out of the box.
CONN_ID = os.environ.get("VNMD_CH_CONN_ID", "vnmd_clickhouse")

# A day of trading at HOSE/DNSE/TCBS is 09:15-11:30 + 13:00-14:30 (ATC to 15:00).
# We scan the whole calendar day and report per-session counts ourselves.
SESSION_BOUNDARIES = [
    ("ato", "08:45:00", "09:15:00"),
    ("morning", "09:15:00", "11:30:00"),
    ("afternoon", "13:00:00", "14:30:00"),
    ("atc", "14:30:00", "15:00:00"),
]

default_args = {
    "owner": "vnmd",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}


def _conn() -> dict:
    """Connection parameters for the common.sql ClickHouse provider."""
    return {
        "conn_type": "clickhouse",
        "host": CH_HTTP_URL.replace("http://", "").replace("https://", ""),
        "port": 8123,
        "schema": CH_DATABASE,
        "login": CH_USER,
        "password": CH_PASSWORD,
    }


def _ch_query(sql: str, task_id: str, **kwargs) -> SQLExecuteQueryOperator:
    return SQLExecuteQueryOperator(
        task_id=task_id,
        conn_id=CONN_ID,
        sql=sql,
        hook_params={"conn": _conn()},
        **kwargs,
    )


def day_window(run_date: date) -> tuple[str, str]:
    """[start, end) of the trading day, in the broker's timezone."""
    start = f"{run_date.isoformat()} 00:00:00"
    end = f"{(run_date + timedelta(days=1)).isoformat()} 00:00:00"
    return start, end


with DAG(
    dag_id="vnmd_cross_source_quality",
    description="Cross-broker (SSI/DNSE/TCBS) data-quality checks for one trading day",
    schedule="@daily",
    start_date=datetime(2026, 11, 1),
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["vnmd", "data-quality", "cross-source"],
) as dag:
    start, end = day_window(date(2026, 11, 6))

    # ------------------------------------------------------------------
    # 1. Feed health: is every source alive and how much did it deliver?
    # ------------------------------------------------------------------
    feed_health = _ch_query(
        textwrap.dedent(
            f"""
            SELECT
                source,
                feed,
                count()                                       AS msgs,
                uniqExact(wire_code)                          AS wire_codes,
                countIf(error != '')                          AS kafka_errors,
                min(recv_ts)                                  AS first_msg,
                max(recv_ts)                                  AS last_msg,
                dateDiff('second', max(recv_ts), max(recv_ts)) AS age_s
            FROM {CH_DATABASE}.raw
            WHERE recv_ts >= toDateTime64('{start}', 9, 'Asia/Ho_Chi_Minh')
              AND recv_ts <  toDateTime64('{end}', 9, 'Asia/Ho_Chi_Minh')
            GROUP BY source, feed
            ORDER BY source, feed
            """
        ),
        "feed_health",
    )

    # ------------------------------------------------------------------
    # 2. Unknown frames: did a broker emit a channel we do not parse?
    #    This is the alarm that catches a silently changed protocol.
    # ------------------------------------------------------------------
    unknown_frames = _ch_query(
        textwrap.dedent(
            f"""
            SELECT
                source,
                feed,
                wire_code,
                count()                    AS n,
                min(recv_ts)                AS first_seen,
                max(recv_ts)                AS last_seen,
                any(substring(payload, 1, 400)) AS sample_payload
            FROM {CH_DATABASE}.unknown_frames
            WHERE recv_ts >= toDateTime64('{start}', 9, 'Asia/Ho_Chi_Minh')
              AND recv_ts <  toDateTime64('{end}', 9, 'Asia/Ho_Chi_Minh')
            GROUP BY source, feed, wire_code
            ORDER BY n DESC
            """
        ),
        "unknown_frames",
    )

    # ------------------------------------------------------------------
    # 3. Wire-code inventory: what each broker actually sent today.
    #    Compared against docs/<broker>/brief/DOCUMENT.md by the report task.
    # ------------------------------------------------------------------
    wire_inventory = _ch_query(
        textwrap.dedent(
            f"""
            SELECT
                source,
                wire_code,
                count()                        AS n,
                uniqExact(kafka_key)           AS distinct_keys,
                min(recv_ts)                    AS first_seen,
                max(recv_ts)                    AS last_seen,
                any(substring(payload, 1, 400)) AS sample_payload
            FROM {CH_DATABASE}.raw
            WHERE recv_ts >= toDateTime64('{start}', 9, 'Asia/Ho_Chi_Minh')
              AND recv_ts <  toDateTime64('{end}', 9, 'Asia/Ho_Chi_Minh')
            GROUP BY source, wire_code
            ORDER BY source, n DESC
            """
        ),
        "wire_inventory",
    )

    # ------------------------------------------------------------------
    # 4. Trade volume per source and per session window.
    # ------------------------------------------------------------------
    per_session = _ch_query(
        textwrap.dedent(
            f"""
            SELECT
                source,
                count()                                   AS trades,
                uniqExact(symbol)                         AS symbols,
                min(recv_ts)                              AS first_trade,
                max(recv_ts)                              AS last_trade,
                countIf(price IS NULL)                    AS null_price,
                countIf(qty IS NULL)                      AS null_qty,
                round(avg(price), 4)                      AS avg_price,
                min(price)                                AS min_price,
                max(price)                                AS max_price
            FROM {CH_DATABASE}.trades FINAL
            WHERE recv_ts >= toDateTime64('{start}', 9, 'Asia/Ho_Chi_Minh')
              AND recv_ts <  toDateTime64('{end}', 9, 'Asia/Ho_Chi_Minh')
            GROUP BY source
            ORDER BY source
            """
        ),
        "trades_per_session",
    )

    # ------------------------------------------------------------------
    # 5. Cross-source price divergence on the same symbol.
    #    A large spread means one source lags or one parser mis-reads.
    # ------------------------------------------------------------------
    cross_source = _ch_query(
        textwrap.dedent(
            f"""
            SELECT
                symbol,
                countDistinct(source)                     AS sources,
                anyIf(price, source = 'ssi')              AS price_ssi,
                anyIf(price, source = 'dnse')             AS price_dnse,
                anyIf(price, source = 'tcbs')             AS price_tcbs,
                round(max(price) - min(price), 4)         AS price_spread,
                round((max(price) - min(price))
                      / nullIf(max(price), 0) * 100, 4)  AS spread_pct,
                max(last_recv_ts)                         AS last_recv_ts
            FROM {CH_DATABASE}.v_last_trade
            GROUP BY symbol
            HAVING sources > 1
            ORDER BY spread_pct DESC
            LIMIT 200
            """
        ),
        "cross_source_divergence",
    )

    # ------------------------------------------------------------------
    # 6. Latency: only computable where the broker stamps its own time.
    #    TCBS thesis has no exchange_ts at all -> stays NULL by design.
    # ------------------------------------------------------------------
    latency = _ch_query(
        textwrap.dedent(
            f"""
            SELECT
                source,
                wire_code,
                count()                                                      AS n,
                round(avg(dateDiff('millisecond', exchange_ts, recv_ts)), 1) AS avg_lag_ms,
                quantile(0.5)(dateDiff('millisecond', exchange_ts, recv_ts))  AS p50_lag_ms,
                quantile(0.99)(dateDiff('millisecond', exchange_ts, recv_ts)) AS p99_lag_ms,
                max(dateDiff('millisecond', exchange_ts, recv_ts))            AS max_lag_ms
            FROM {CH_DATABASE}.trades FINAL
            WHERE exchange_ts IS NOT NULL
              AND recv_ts >= toDateTime64('{start}', 9, 'Asia/Ho_Chi_Minh')
              AND recv_ts <  toDateTime64('{end}', 9, 'Asia/Ho_Chi_Minh')
            GROUP BY source, wire_code
            ORDER BY source, wire_code
            """
        ),
        "feed_latency",
    )

    # ------------------------------------------------------------------
    # 7. Book depth: TCBS cash sends 3 levels, TCBS futures s|42 sends 10.
    # ------------------------------------------------------------------
    book_depth = _ch_query(
        textwrap.dedent(
            f"""
            SELECT
                source,
                wire_code,
                count()                                     AS rows,
                max(length(bid_price))                      AS max_bid_levels,
                max(length(ask_price))                      AS max_ask_levels,
                countIf(length(bid_price) = 0 AND length(ask_price) = 0) AS empty_sides,
                uniqExact(symbol)                           AS symbols
            FROM {CH_DATABASE}.book FINAL
            WHERE recv_ts >= toDateTime64('{start}', 9, 'Asia/Ho_Chi_Minh')
              AND recv_ts <  toDateTime64('{end}', 9, 'Asia/Ho_Chi_Minh')
            GROUP BY source, wire_code
            ORDER BY source, wire_code
            """
        ),
        "book_depth",
    )

    # ------------------------------------------------------------------
    # 8. Schema probe: the ACTUAL column set of each target table.
    #    Feeds the "what the data really looks like vs the docs" section.
    # ------------------------------------------------------------------
    schema_probe = _ch_query(
        textwrap.dedent(
            """
            SELECT table, name, type, default_kind, default_expression
            FROM system.columns
            WHERE database = 'vnmd'
              AND table IN ('raw','trades','book','index_values','foreign_flow',
                            'ohlc','supply_demand','instrument_state','unknown_frames')
            ORDER BY table, position
            """
        ),
        "schema_probe",
    )

    # ------------------------------------------------------------------
    # 9. Sample payloads per source/wire_code — the "giá trị mẫu" evidence.
    # ------------------------------------------------------------------
    payload_samples = _ch_query(
        textwrap.dedent(
            f"""
            SELECT
                source,
                wire_code,
                any(substring(payload, 1, 1200)) AS sample
            FROM {CH_DATABASE}.raw
            WHERE recv_ts >= toDateTime64('{start}', 9, 'Asia/Ho_Chi_Minh')
              AND recv_ts <  toDateTime64('{end}', 9, 'Asia/Ho_Chi_Minh')
            GROUP BY source, wire_code
            ORDER BY source, wire_code
            """
        ),
        "payload_samples",
    )

    with TaskGroup(group_id="checks") as checks:
        for op in (
            feed_health,
            unknown_frames,
            wire_inventory,
            per_session,
            cross_source,
            latency,
            book_depth,
            schema_probe,
            payload_samples,
        ):
            op

    # ------------------------------------------------------------------
    # 10. Assemble the Markdown report from the check results.
    #     Each check hands its rows to this task via XCom; the task renders
    #     tables and writes the file into the shared logs volume.
    # ------------------------------------------------------------------
    def _md_table(rows: list[dict], columns: list[str] | None = None) -> str:
        """Render a list of dicts as a GitHub-flavoured Markdown table."""
        if not rows:
            return "_(khong co du lieu)_\n"
        cols = columns or list(rows[0].keys())
        out = ["| " + " | ".join(cols) + " |",
               "|" + "|".join("---" for _ in cols) + "|"]
        for r in rows:
            cells = []
            for c in cols:
                v = r.get(c)
                if v is None:
                    cells.append("")
                elif isinstance(v, (dict, list)):
                    cells.append("`" + str(v).replace("|", "\\|")[:220] + "`")
                else:
                    cells.append(str(v).replace("|", "\\|")[:220])
            out.append("| " + " | ".join(cells) + " |")
        return "\n".join(out) + "\n"

    def build_report(**context) -> str:
        import json
        import os

        day = context["ds"]
        ti = context["ti"]

        def rows(task_id: str) -> list[dict]:
            raw = ti.xcom_pull(task_ids=task_id)
            if not raw:
                return []
            if isinstance(raw, str):
                raw = json.loads(raw)
            return raw

        parts: list[str] = []
        parts.append(f"# VNMD data quality - trading day {day}\n")
        parts.append(
            "Ket qua kiem tra chat luong du lieu cho 3 nguon SSI / DNSE / TCBS.\n"
            "Tao bang ClickHouse `vnmd.raw` (payload verbatim) va cac bang target.\n"
        )

        parts.append("\n## 1. Feed health (mot feed = mot socket)\n")
        parts.append(
            _md_table(
                rows("checks.feed_health"),
                ["source", "feed", "msgs", "wire_codes", "kafka_errors",
                 "first_msg", "last_msg"],
            )
        )

        parts.append("\n## 2. Wire-code inventory\n")
        parts.append(
            "Wire code nao thuc su chay hom nay. So voi `docs/<broker>/brief/DOCUMENT.md`\n"
            "de thay kenh nao khong co trong tai lieu.\n"
        )
        parts.append(
            _md_table(
                rows("checks.wire_inventory"),
                ["source", "wire_code", "n", "distinct_keys",
                 "first_seen", "last_seen"],
            )
        )

        parts.append("\n## 3. Unknown frames (protocol changed?)\n")
        parts.append(
            _md_table(
                rows("checks.unknown_frames"),
                ["source", "feed", "wire_code", "n", "first_seen", "last_seen",
                 "sample_payload"],
            )
        )

        parts.append("\n## 4. Trades per source\n")
        parts.append(
            _md_table(
                rows("checks.trades_per_session"),
                ["source", "trades", "symbols", "null_price", "null_qty",
                 "min_price", "max_price", "first_trade", "last_trade"],
            )
        )

        parts.append("\n## 5. Cross-source price divergence\n")
        parts.append(
            "Gia cung ma o ba nguon. `spread_pct` lon nghia la mot nguon cham\n"
            "hoac parser doc sai.\n"
        )
        parts.append(
            _md_table(
                rows("checks.cross_source_divergence"),
                ["symbol", "sources", "price_ssi", "price_dnse", "price_tcbs",
                 "price_spread", "spread_pct", "last_recv_ts"],
            )
        )

        parts.append("\n## 6. Feed latency (chi tinh duoc o nguon co timestamp)\n")
        parts.append(
            _md_table(
                rows("checks.feed_latency"),
                ["source", "wire_code", "n", "avg_lag_ms", "p50_lag_ms",
                 "p99_lag_ms", "max_lag_ms"],
            )
        )

        parts.append("\n## 7. Book depth\n")
        parts.append(
            _md_table(
                rows("checks.book_depth"),
                ["source", "wire_code", "rows", "max_bid_levels",
                 "max_ask_levels", "empty_sides", "symbols"],
            )
        )

        parts.append("\n## 8. Schema thatuoc (system.columns)\n")
        parts.append(
            _md_table(
                rows("checks.schema_probe"),
                ["table", "name", "type", "default_kind"],
            )
        )

        parts.append("\n## 9. Sample payload theo wire code\n")
        parts.append(
            _md_table(
                rows("checks.payload_samples"),
                ["source", "wire_code", "sample"],
            )
        )

        text = "\n".join(parts)
        os.makedirs(REPORT_DIR, exist_ok=True)
        path = os.path.join(REPORT_DIR, f"vnmd-quality-{day}.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"report written: {path} ({len(text)} bytes)")
        return path

    report = PythonOperator(
        task_id="build_report",
        python_callable=build_report,
        op_kwargs={},
    )

    checks >> report
