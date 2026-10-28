package vnmd.transform;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import static vnmd.transform.Json.lng;
import static vnmd.transform.Json.num;
import static vnmd.transform.Json.str;

/**
 * DNSE: ROUTED BY PAYLOAD SHAPE, NOT BY wire_code.
 *
 * The DNSE docs say to classify data messages by the `T` field, yet NO sample
 * payload anywhere in the documentation contains it (see docs/dnse/brief/DOCUMENT.md
 * section 11.1) — meaning its valid value set is unknown. Ingestion therefore tags
 * wire_code='unknown' when `T` is absent. Routing on distinctive fields does not
 * depend on that unknown and stays correct if DNSE adds `T` later.
 *
 * DNSE is the ONLY broker giving an exchange timestamp at NANOSECOND resolution
 * ({Seconds, Nanos}) — see Rows.dnseTs().
 *
 * Assumption: DNSE_ENCODING=json. msgpack frames are not JSON and land in
 * unknown_frames (raw.error says so).
 */
final class DnseParser {
    private DnseParser() {
    }

    static void parse(RawFrame f, JsonNode p, FrameRouter.Emitter out) {
        // The rules are independent, exactly as the shapes are.
        if (p.has("matchPrice")) {
            out.emit(Table.TRADES, trade(f, p));
        }
        if (p.has("bid") && p.has("offer")) {
            out.emit(Table.BOOK, book(f, p));
        }
        if (p.has("valueIndexes")) {
            out.emit(Table.INDEX_VALUES, index(f, p));
        }
        if (p.has("foreignerOrderLimitQuantity")) {
            out.emit(Table.FOREIGN_FLOW, foreign(f, p));
        }
        if (p.has("resolution") && p.has("close")) {
            out.emit(Table.OHLC, ohlc(f, p));
        }
        if (p.has("ceilingPrice")) {
            out.emit(Table.INSTRUMENT_STATE, state(f, p));
        }
    }

    private static String instrument(JsonNode p) {
        return str(p, "marketId").equals("DVX") ? "derivative" : "stock";
    }

    private static ObjectNode trade(RawFrame f, JsonNode p) {
        ObjectNode r = Rows.target(f);
        r.put("symbol", str(p, "symbol"));
        r.put("instrument", instrument(p));
        r.put("exchange_ts", Rows.ts9(Rows.dnseTs(p, "time")));
        r.put("price", num(p, "matchPrice"));
        r.put("qty", num(p, "matchQtty"));
        r.put("side", str(p, "side"));        // only tick_extra carries BUY/SELL
        r.put("avg_price", num(p, "avgPrice"));
        r.put("total_volume", num(p, "totalVolumeTraded"));
        r.put("total_value", num(p, "grossTradeAmount"));
        r.putNull("change");
        r.putNull("change_percent");
        return r;
    }

    private static ObjectNode book(RawFrame f, JsonNode p) {
        ObjectNode r = Rows.target(f);
        r.put("symbol", str(p, "symbol"));
        r.put("instrument", instrument(p));
        r.put("exchange_ts", Rows.ts9(Rows.dnseTs(p, "time")));
        // DNSE returns an array of {price, quantity} objects, unlike SSI's pair arrays.
        levels(r, p.get("bid"), "bid_price", "bid_qty");
        levels(r, p.get("offer"), "ask_price", "ask_qty");
        r.put("total_bid_qty", num(p, "totalBidQtty"));
        r.put("total_ask_qty", num(p, "totalOfferQtty"));
        r.putNull("level");
        r.putNull("bid_cum_qty");
        r.putNull("ask_cum_qty");
        return r;
    }

    private static void levels(ObjectNode r, JsonNode side, String priceCol, String qtyCol) {
        ArrayNode prices = r.putArray(priceCol);
        ArrayNode qtys = r.putArray(qtyCol);
        if (side == null || !side.isArray()) {
            return;
        }
        for (JsonNode lv : side) {
            Double price = num(lv, "price");
            Double qty = num(lv, "quantity");
            prices.add(price == null ? 0.0 : price);
            qtys.add(qty == null ? 0.0 : qty);
        }
    }

    private static ObjectNode index(RawFrame f, JsonNode p) {
        ObjectNode r = Rows.target(f);
        r.put("index_name", str(p, "indexName"));
        // market_index uses the field name `transactTime`, while
        // estimated_market_index uses `time` as a STRING. Try both.
        Long ts = Rows.dnseTs(p, "transactTime");
        r.put("exchange_ts", Rows.ts9(ts != null ? ts : Rows.parseDateTime(str(p, "time"))));
        r.put("value", num(p, "valueIndexes"));
        r.put("change", num(p, "changedValue"));
        r.put("change_percent", num(p, "changedRatio"));
        r.put("volume", num(p, "totalVolumeTraded"));
        r.put("turnover", num(p, "grossTradeAmount"));
        r.put("advances", lng(p, "fluctuationUpIssueCount"));
        r.put("declines", lng(p, "fluctuationDownIssueCount"));
        r.put("unchanged", lng(p, "fluctuationSteadinessIssueCount"));
        r.put("ceiling_count", lng(p, "fluctuationUpperLimitIssueCount"));
        // The documentation's own example leaves this field null -> every count column is nullable.
        r.put("floor_count", lng(p, "fluctuationLowerLimitIssueCount"));
        r.put("session_code", str(p, "tradingSessionId"));
        return r;
    }

    private static ObjectNode foreign(RawFrame f, JsonNode p) {
        ObjectNode r = Rows.target(f);
        r.put("symbol", str(p, "symbol"));
        // The `foreign` channel has NO {Seconds,Nanos}; only transactTime like
        // "035200011", meaning undocumented.
        r.putNull("exchange_ts");
        r.put("buy_qty", num(p, "totalBuyVolume"));
        r.put("sell_qty", num(p, "totalSellVolume"));
        r.put("buy_value", num(p, "totalBuyTradedAmount"));
        r.put("sell_value", num(p, "totalSellTradedAmount"));
        r.put("room_total", num(p, "foreignerOrderLimitQuantity"));
        r.put("room_left", num(p, "foreignerBuyPossibleQuantity"));
        return r;
    }

    private static ObjectNode ohlc(RawFrame f, JsonNode p) {
        ObjectNode r = Rows.target(f);
        r.put("symbol", str(p, "symbol"));
        r.put("resolution", str(p, "resolution"));
        r.put("bar_ts", Rows.ts3(Rows.secondsToNs(num(p, "time"))));
        r.put("open", num(p, "open"));
        r.put("high", num(p, "high"));
        r.put("low", num(p, "low"));
        r.put("close", num(p, "close"));
        r.put("volume", num(p, "volume"));
        // ohlc and ohlc_closed are indistinguishable from the payload (identical
        // schema); marking this correctly needs either `T` or separate topics.
        r.put("closed", 0);
        return r;
    }

    private static ObjectNode state(RawFrame f, JsonNode p) {
        ObjectNode r = Rows.target(f);
        r.put("symbol", str(p, "symbol"));
        r.put("board", str(p, "boardId"));
        r.put("exchange_ts", Rows.ts9(Rows.dnseTs(p, "time")));
        r.put("ceiling_price", num(p, "ceilingPrice"));
        r.put("floor_price", num(p, "floorPrice"));
        r.put("ref_price", num(p, "basicPrice"));
        r.putNull("open_price");
        r.putNull("high_price");
        r.putNull("low_price");
        r.putNull("avg_price");
        r.put("status", str(p, "securityStatus"));
        return r;
    }
}
