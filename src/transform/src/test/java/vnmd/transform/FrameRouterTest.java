package vnmd.transform;

import com.fasterxml.jackson.databind.JsonNode;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

/** Payloads below are copied verbatim from docs/BROKER/brief/DOCUMENT.md unless noted. */
class FrameRouterTest {

    private static final long RECV = 1755144185_123456789L;   // 2025-08-14 11:03:05.123456789 +07

    private final FrameRouter router = new FrameRouter();

    private static RawFrame frame(String source, String wire, String payload) {
        return new RawFrame(source + ".data.raw.x", 3, 42L, "TCB", source, "feed", wire, RECV, payload);
    }

    private static JsonNode only(List<ChRow> rows, Table expected) throws IOException {
        assertEquals(Table.RAW, rows.get(0).table);
        assertEquals(2, rows.size(), "expected raw + exactly one parsed row");
        assertEquals(expected, rows.get(1).table);
        return Json.MAPPER.readTree(rows.get(1).json);
    }

    // ------------------------------------------------------------------ TCBS

    @Test
    void tcbsCashTradeReadsStringNumbers() throws IOException {
        JsonNode r = only(router.route(frame("tcbs", "s|6",
                "{\"symbol\":\"TCB\",\"matchPrice\":\"24550\",\"matchQtty\":\"5000\",\"change\":200.0,"
                        + "\"changePercent\":0.8213552361396304,\"totalVolume\":\"9745500\",\"totalValue\":\"240774655000\"}")),
                Table.TRADES);
        assertEquals("TCB", r.get("symbol").asText());
        assertEquals("stock", r.get("instrument").asText());
        assertEquals(24550.0, r.get("price").asDouble());
        assertEquals(5000.0, r.get("qty").asDouble());
        assertEquals(9745500.0, r.get("total_volume").asDouble());
        assertTrue(r.get("exchange_ts").isNull(), "thesis family has no time field");
        assertEquals("2025-08-14 11:03:05.123456789", r.get("recv_ts").asText());
        assertEquals(42L, r.get("kafka_offset").asLong());
    }

    @Test
    void tcbsBidSideFillsOnlyBidArrays() throws IOException {
        JsonNode r = only(router.route(frame("tcbs", "s|1",
                "{\"symbol\":\"TCB\",\"bidPrice01\":\"24550\",\"bidPrice02\":\"24500\",\"bidPrice03\":\"24450\","
                        + "\"bidQtty01\":\"137200\",\"bidQtty02\":\"354000\",\"bidQtty03\":\"292900\"}")),
                Table.BOOK);
        assertEquals(3, r.get("bid_price").size());
        assertEquals(24450.0, r.get("bid_price").get(2).asDouble());
        assertEquals(0, r.get("ask_price").size());
    }

    @Test
    void tcbsIndexKeepsNumericIndexNumber() throws IOException {
        JsonNode r = only(router.route(frame("tcbs", "s|8",
                "{\"indexNumber\":5,\"index\":91.43,\"change\":1.75,\"changePercent\":1.96,\"volume\":5.5936E7,"
                        + "\"value\":7.287094199E11,\"increase\":246,\"decrease\":58,\"notChange\":63,\"session\":\"5\","
                        + "\"ceilIncrease\":19,\"floorDecrease\":8}")),
                Table.INDEX_VALUES);
        assertEquals("5", r.get("index_name").asText());
        assertEquals(246L, r.get("advances").asLong());
        assertEquals(7.287094199E11, r.get("turnover").asDouble());
    }

    @Test
    void tcbsPutThroughTimeIsAnchoredOnReceiveDate() throws IOException {
        JsonNode r = only(router.route(frame("tcbs", "s|17",
                "{\"symbol\":\"TCB\",\"price\":\"24550\",\"vol\":\"1000\",\"val\":\"24550000\",\"time\":\"10:56:50\"}")),
                Table.TRADES);
        assertEquals("pt", r.get("instrument").asText());
        assertEquals("2025-08-14 10:56:50.000000000", r.get("exchange_ts").asText());
    }

    @Test
    void tcbsOuranosTickHasSecondsAndSide() throws IOException {
        JsonNode r = only(router.route(frame("tcbs", "C001",
                "{\"symbol\":\"TCB\",\"closePrice\":38600.0,\"closeVol\":1000.0,\"change\":1100.0,\"reference\":37500.0,"
                        + "\"totalTrading\":2.42776E7,\"totalTradingValue\":9.3340061E11,\"timeSec\":\"1755144180\","
                        + "\"action\":\"SD\",\"unitTimeFrame\":\"60\"}")),
                Table.TRADES);
        assertEquals("2025-08-14 11:03:00.000000000", r.get("exchange_ts").asText());
        assertEquals("SD", r.get("side").asText());
        assertEquals(38600.0, r.get("price").asDouble());
    }

    @Test
    void tcbsSupplyDemand() throws IOException {
        JsonNode r = only(router.route(frame("tcbs", "C002S60",
                "{\"symbol\":\"TCB\",\"timeSec\":\"1755144120\",\"totalBUVol\":200.0,\"totalBUVolAcc\":1.51419E7,"
                        + "\"totalSDVol\":49700.0,\"totalSDVolAcc\":8480600.0,\"bsAccRatio\":0.6409948,\"unitTimeFrame\":\"60\"}")),
                Table.SUPPLY_DEMAND);
        assertEquals(60L, r.get("timeframe_s").asLong());
    }

    @Test
    void tcbsDepthLevelKeepsTop() throws IOException {
        // Shape from the production audit in examples/ (s|42 is undocumented).
        JsonNode r = only(router.route(frame("tcbs", "s|42",
                "{\"symbol\":\"41I1G8000\",\"top\":3,\"bidPrice\":1870.5,\"bidQty\":12,\"offerPrice\":1871.0,"
                        + "\"offerQty\":7,\"bidCumulativeQty\":40,\"offerCumulativeQty\":25}")),
                Table.BOOK);
        assertEquals("derivative", r.get("instrument").asText());
        assertEquals(3, r.get("level").asInt());
        assertEquals(1871.0, r.get("ask_price").get(0).asDouble());
    }

    @Test
    void tcbsUnlistedWireCodeIsKeptAsUnknown() throws IOException {
        JsonNode r = only(router.route(frame("tcbs", "s|38", "{\"symbol\":\"TCB\"}")), Table.UNKNOWN_FRAMES);
        assertEquals("s|38", r.get("wire_code").asText());
        assertEquals("{\"symbol\":\"TCB\"}", r.get("payload").asText());
    }

    @Test
    void tcbsFuturesCopyFromTheDerivativeSocketIsNotParsedTwice() {
        String body = "{\"symbol\":\"41I1G8000\",\"matchPrice\":1870.5,\"matchQtty\":2}";
        RawFrame onStock = new RawFrame("tcbs.data.raw.stock", 0, 1L, "41I1G8000", "tcbs",
                "tcbs.stock", "s|21", RECV, body);
        RawFrame onDeriv = new RawFrame("tcbs.data.raw.future", 0, 1L, "41I1G8000", "tcbs",
                "tcbs.derivative", "s|21", RECV, body);

        List<ChRow> stockRows = router.route(onStock);
        List<ChRow> derivRows = router.route(onDeriv);
        assertEquals(Table.TRADES, stockRows.get(1).table);
        assertEquals(1, derivRows.size(), "only the raw row — not a second trade, not unknown");
        assertEquals(Table.RAW, derivRows.get(0).table);

        // s|42 exists only on the derivative socket and is always kept.
        assertEquals(2, router.route(new RawFrame("tcbs.data.raw.future", 0, 2L, "41I1G8000",
                "tcbs", "tcbs.derivative", "s|42", RECV, "{\"symbol\":\"41I1G8000\",\"top\":1}")).size());
        // "both" keeps every copy (only one socket subscribed).
        assertEquals(2, new FrameRouter("both").route(onDeriv).size());
    }

    // ------------------------------------------------------------------ SSI

    @Test
    void ssiStartOfDayDateOnlyTime() throws IOException {
        JsonNode r = only(router.route(frame("ssi", "market",
                "{\"channel\":\"DATA\",\"data\":{\"s\":\"SSI\",\"b\":\"HOSE\",\"t\":\"2025/08/14\","
                        + "\"ce\":\"48.65\",\"fl\":\"42.35\",\"ref\":\"45.50\"}}")),
                Table.INSTRUMENT_STATE);
        assertEquals("2025-08-14 00:00:00.000000000", r.get("exchange_ts").asText());
        assertEquals(48.65, r.get("ceiling_price").asDouble());
    }

    @Test
    void ssiTradeUnwrapsData() throws IOException {
        // Field names per docs/ssi/brief section 11.
        JsonNode r = only(router.route(frame("ssi", "trade_tick",
                "{\"channel\":\"DATA\",\"topic\":\"trade.SSI\",\"data\":{\"s\":\"SSI\",\"t\":\"2025/08/14 10:15:30\","
                        + "\"p\":\"45.50\",\"q\":\"100\",\"si\":\"B\",\"a\":\"45.3\",\"v\":\"1000\",\"tv\":\"45500\"}}")),
                Table.TRADES);
        assertEquals("SSI", r.get("symbol").asText());
        assertEquals(45.5, r.get("price").asDouble());
        assertEquals("B", r.get("side").asText());
        assertEquals("2025-08-14 10:15:30.000000000", r.get("exchange_ts").asText());
    }

    @Test
    void ssiQuotePairsBecomeParallelArrays() throws IOException {
        JsonNode r = only(router.route(frame("ssi", "quote_tick",
                "{\"channel\":\"DATA\",\"data\":{\"s\":\"SSI\",\"t\":\"2025/08/14 10:15:30\","
                        + "\"bids\":[[\"45.45\",\"1200\"],[\"45.40\",\"800\"]],\"asks\":[[\"45.50\",\"300\"]]}}")),
                Table.BOOK);
        assertEquals(2, r.get("bid_price").size());
        assertEquals(800.0, r.get("bid_qty").get(1).asDouble());
        assertEquals(45.5, r.get("ask_price").get(0).asDouble());
    }

    @Test
    void ssiIntervalWithoutOpenIsUnknown() throws IOException {
        only(router.route(frame("ssi", "trade_1m",
                "{\"channel\":\"DATA\",\"data\":{\"s\":\"SSI\",\"p\":\"45.5\"}}")), Table.UNKNOWN_FRAMES);
    }

    // ------------------------------------------------------------------ DNSE

    @Test
    void dnseTradeKeepsNanosecondsExactly() throws IOException {
        JsonNode r = only(router.route(frame("dnse", "unknown",
                "{\"marketId\":\"STO\",\"boardId\":\"G1\",\"isin\":\"VN000000HPG4\",\"symbol\":\"HPG\","
                        + "\"matchPrice\":24.35,\"matchQtty\":40,\"totalVolumeTraded\":1184240,\"grossTradeAmount\":287.17458,"
                        + "\"highestPrice\":24.35,\"lowestPrice\":24.15,\"openPrice\":24.25,\"tradingSessionId\":\"40\","
                        + "\"time\":{\"Seconds\":1779762571,\"Nanos\":101000000}}")),
                Table.TRADES);
        assertTrue(r.get("exchange_ts").asText().endsWith(".101000000"), r.get("exchange_ts").asText());
        assertEquals("stock", r.get("instrument").asText());
        assertEquals(1184240.0, r.get("total_volume").asDouble());
    }

    @Test
    void dnseBookFromObjectLevels() throws IOException {
        JsonNode r = only(router.route(frame("dnse", "unknown",
                "{\"symbol\":\"HPG\",\"marketId\":\"DVX\",\"bid\":[{\"price\":24.3,\"quantity\":\"12\"}],"
                        + "\"offer\":[{\"price\":24.35,\"quantity\":5}],\"totalBidQtty\":12,\"totalOfferQtty\":5}")),
                Table.BOOK);
        assertEquals("derivative", r.get("instrument").asText());
        assertEquals(12.0, r.get("bid_qty").get(0).asDouble(), "string quantity is still a number");
        assertEquals(24.35, r.get("ask_price").get(0).asDouble());
    }

    @Test
    void msgpackOrBrokenPayloadStillLands() throws IOException {
        List<ChRow> rows = router.route(frame("dnse", "unknown", "\u0082¡T¡x"));
        JsonNode raw = Json.MAPPER.readTree(rows.get(0).json);
        assertTrue(!raw.get("error").asText().isEmpty());
        assertEquals(Table.UNKNOWN_FRAMES, rows.get(1).table);
    }

    @Test
    void missingSourceHeaderIsUnknown() throws IOException {
        only(router.route(frame("", "s|6", "{\"symbol\":\"TCB\"}")), Table.UNKNOWN_FRAMES);
    }

    // ------------------------------------------------------------------ schema contract

    /**
     * Every row the router emits must name only real, insertable columns of its
     * table, and supply every column that has no DEFAULT — checked against the
     * DDL that apply.sh actually runs.
     */
    @Test
    void everyEmittedRowMatchesTheDdl() throws IOException {
        Map<String, Set<String>[]> ddl = readDdl();
        List<RawFrame> samples = List.of(
                frame("tcbs", "s|6", "{\"symbol\":\"TCB\",\"matchPrice\":\"1\"}"),
                frame("tcbs", "s|2", "{\"symbol\":\"TCB\",\"offerPrice01\":\"1\"}"),
                frame("tcbs", "s|3", "{\"symbol\":\"TCB\",\"room\":\"1\"}"),
                frame("tcbs", "s|4", "{\"symbol\":\"TCB\",\"ceilPrice\":\"1\"}"),
                frame("tcbs", "s|8", "{\"indexNumber\":1}"),
                frame("tcbs", "C002S900", "{\"symbol\":\"TCB\",\"timeSec\":1}"),
                frame("tcbs", "s|99", "{}"),
                frame("ssi", "room_tick", "{\"data\":{\"s\":\"SSI\"}}"),
                frame("ssi", "trade_5m", "{\"data\":{\"s\":\"SSI\",\"open\":1,\"t\":\"2025/08/14 10:15:00\"}}"),
                frame("ssi", "market", "{\"data\":{\"b\":\"HOSE\",\"f\":\"ATO\"}}"),
                frame("dnse", "unknown", "{\"indexName\":\"VNINDEX\",\"valueIndexes\":1,\"transactTime\":{\"Seconds\":1}}"),
                frame("dnse", "unknown", "{\"symbol\":\"HPG\",\"foreignerOrderLimitQuantity\":1}"),
                frame("dnse", "unknown", "{\"symbol\":\"HPG\",\"resolution\":\"1\",\"close\":1,\"time\":1755144180}"),
                frame("dnse", "unknown", "{\"symbol\":\"HPG\",\"ceilingPrice\":1}"));
        Set<Table> seen = new HashSet<>();
        for (RawFrame f : samples) {
            for (ChRow row : router.route(f)) {
                seen.add(row.table);
                Set<String>[] cols = ddl.get(row.table.tableName);
                Set<String> keys = new HashSet<>();
                Iterator<String> it = Json.MAPPER.readTree(row.json).fieldNames();
                it.forEachRemaining(keys::add);
                for (String k : keys) {
                    assertTrue(cols[0].contains(k), row.table + " has no insertable column " + k);
                }
                for (String required : cols[1]) {
                    assertTrue(keys.contains(required), row.table + " row lacks " + required + " (" + f.wireCode + ")");
                }
            }
        }
        assertEquals(Set.of(Table.values()), seen, "samples must cover every table");
    }

    /** table -> [insertable columns, columns without DEFAULT]. */
    @SuppressWarnings("unchecked")
    private static Map<String, Set<String>[]> readDdl() throws IOException {
        String sql = Files.readString(Path.of("sql/10_landing.sql")) + Files.readString(Path.of("sql/20_targets.sql"));
        Matcher table = Pattern.compile("CREATE TABLE IF NOT EXISTS vnmd\\.(\\w+)\\s*\\((.*?)\\n\\)\\s*ENGINE",
                Pattern.DOTALL).matcher(sql);
        Pattern column = Pattern.compile("^\\s{4}([a-z_]+)\\s+(.*)$");
        Map<String, Set<String>[]> out = new HashMap<>();
        while (table.find()) {
            Set<String> insertable = new HashSet<>();
            Set<String> required = new HashSet<>();
            for (String line : table.group(2).split("\n")) {
                Matcher c = column.matcher(line);
                if (!c.matches()) {
                    continue;
                }
                String def = c.group(2);
                if (def.contains("MATERIALIZED")) {
                    continue;
                }
                insertable.add(c.group(1));
                if (!def.contains("DEFAULT")) {
                    required.add(c.group(1));
                }
            }
            out.put(table.group(1), new Set[]{insertable, required});
        }
        return out;
    }
}
