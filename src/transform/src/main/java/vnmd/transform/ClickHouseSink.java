package vnmd.transform;

import org.apache.flink.api.connector.sink2.Sink;
import org.apache.flink.api.connector.sink2.SinkWriter;
import org.apache.flink.api.connector.sink2.WriterInitContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.EnumMap;
import java.util.Map;

/**
 * Batched, append-only writer to ClickHouse over its HTTP interface
 * (`INSERT INTO vnmd.<table> FORMAT JSONEachRow`, one request per table per flush).
 *
 * Delivery is AT_LEAST_ONCE, by design:
 *   * flush() runs before every checkpoint barrier, so every row read before a
 *     checkpoint is in ClickHouse before that checkpoint commits its offsets.
 *   * Nothing deduplicates at write time — no lookups, no ON CONFLICT, no
 *     transactions. A crash replays from the last checkpoint, and rows written
 *     after it are inserted a second time. That is the accepted trade-off for
 *     write throughput; duplicates are resolved off the write path (the
 *     ReplacingMergeTree key ends in (kafka_partition, kafka_offset), and the
 *     *_v views read with FINAL).
 */
public class ClickHouseSink implements Sink<ChRow> {
    private static final long serialVersionUID = 1L;

    private final JobConfig cfg;

    public ClickHouseSink(JobConfig cfg) {
        this.cfg = cfg;
    }

    @Override
    public SinkWriter<ChRow> createWriter(WriterInitContext context) throws IOException {
        return new Writer(cfg);
    }

    // =========================================================================

    static final class Writer implements SinkWriter<ChRow> {
        private static final Logger LOG = LoggerFactory.getLogger(Writer.class);

        private final JobConfig cfg;
        private final HttpClient http;
        private final Map<Table, StringBuilder> buffers = new EnumMap<>(Table.class);
        private final Map<Table, Integer> counts = new EnumMap<>(Table.class);
        private final Map<Table, URI> insertUri = new EnumMap<>(Table.class);
        private long lastFlushNanos = System.nanoTime();
        private long written = 0;

        Writer(JobConfig cfg) {
            this.cfg = cfg;
            this.http = HttpClient.newBuilder()
                    .connectTimeout(Duration.ofMillis(cfg.clickhouseTimeoutMs))
                    .build();
            for (Table t : Table.values()) {
                buffers.put(t, new StringBuilder());
                counts.put(t, 0);
                String sql = "INSERT INTO " + cfg.clickhouseDb + "." + t.tableName + " FORMAT JSONEachRow";
                insertUri.put(t, URI.create(cfg.clickhouseUrl + "/?query="
                        + URLEncoder.encode(sql, StandardCharsets.UTF_8)));
            }
            LOG.info("ClickHouseSink writer ready: {} db={} (batch={}, interval={}ms)",
                    cfg.clickhouseUrl, cfg.clickhouseDb, cfg.batchSize, cfg.batchIntervalMs);
        }

        @Override
        public void write(ChRow row, Context context) throws IOException {
            if (row == null || row.table == null) {
                return;
            }
            buffers.get(row.table).append(row.json).append('\n');
            int n = counts.merge(row.table, 1, Integer::sum);
            if (n >= cfg.batchSize) {
                flushTable(row.table);
            }
            if (System.nanoTime() - lastFlushNanos >= cfg.batchIntervalMs * 1_000_000L) {
                flushAll();
            }
        }

        @Override
        public void flush(boolean endOfInput) throws IOException {
            flushAll();
        }

        @Override
        public void close() throws Exception {
            try {
                flushAll();
            } finally {
                http.close();
            }
            LOG.info("ClickHouseSink writer closed (written={})", written);
        }

        // ---------------------------------------------------------------------

        private void flushAll() throws IOException {
            for (Table t : Table.values()) {
                flushTable(t);
            }
            lastFlushNanos = System.nanoTime();
        }

        private void flushTable(Table table) throws IOException {
            int n = counts.get(table);
            if (n == 0) {
                return;
            }
            StringBuilder buf = buffers.get(table);
            String body = buf.toString();
            buf.setLength(0);
            counts.put(table, 0);

            HttpRequest req = HttpRequest.newBuilder(insertUri.get(table))
                    .timeout(Duration.ofMillis(cfg.clickhouseTimeoutMs))
                    .header("X-ClickHouse-User", cfg.clickhouseUser)
                    .header("X-ClickHouse-Key", cfg.clickhousePassword)
                    .header("Content-Type", "application/x-ndjson")
                    .POST(HttpRequest.BodyPublishers.ofString(body, StandardCharsets.UTF_8))
                    .build();
            HttpResponse<String> resp;
            try {
                resp = http.send(req, HttpResponse.BodyHandlers.ofString());
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new IOException("Interrupted while inserting into " + table.tableName, e);
            }
            if (resp.statusCode() != 200) {
                // Rethrow: Flink restarts from the last checkpoint and the replayed
                // rows are inserted again — the accepted AT_LEAST_ONCE duplicate.
                String err = resp.body();
                throw new IOException("INSERT INTO " + table.tableName + " failed (HTTP "
                        + resp.statusCode() + ", " + n + " rows): "
                        + (err.length() > 500 ? err.substring(0, 500) + "..." : err));
            }
            written += n;
        }
    }
}
