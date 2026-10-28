package vnmd.transform;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import static vnmd.transform.Json.firstNum;
import static vnmd.transform.Json.num;
import static vnmd.transform.Json.str;

/**
 * SSI: the payload is the WHOLE message `{"channel":"DATA","topic":"...","data":{...}}`
 * — ingestion deliberately does not unwrap `data`, to keep the original bytes — so
 * every field is read from payload.data.
 *
 * SSI abbreviates every field name: s=symbol, t=time, p=price, q=qty, si=side...
 * The full lookup table is in docs/ssi/brief/DOCUMENT.md section 11.
 *
 * `wire_code` is produced by ingestion from the topic: trade_tick, quote_tick,
 * room_tick, put_tick, oddlot_tick, trade_1m, trade_5m, market.
 *
 * SSI gives the exchange time as the string 'YYYY/MM/DD HH:mi:ss' — resolved only
 * to SECONDS, so several ticks per second are normal; never use it as a key.
 */
final class SsiParser {
    private SsiParser() {
    }

    static void parse(RawFrame f, JsonNode p, FrameRouter.Emitter out) {
        JsonNode d = p.get("data");
        if (d == null || !d.isObject()) {
            return;
        }
        String w = f.wireCode;
        // oddlot_tick may carry a trade AND/OR a book: the rules are independent.
        if ((w.equals("trade_tick") || w.equals("put_tick") || w.equals("oddlot_tick")) && d.has("p")) {
            out.emit(Table.TRADES, trade(f, d));
        }
        if ((w.equals("quote_tick") || w.equals("oddlot_tick")) && d.has("bids")) {
            out.emit(Table.BOOK, book(f, d));
        }
        if (w.equals("room_tick")) {
            out.emit(Table.FOREIGN_FLOW, foreign(f, d));
        }
        // trade.*@1m / @5m: the SDK describes these as IntervalMessage
        // (open/high/low/close/volume). The DATA channel docs are silent -> only accept
        // them when the payload ACTUALLY has 'open'; otherwise they fall into
        // unknown_frames so the mismatch is visible instead of silently mis-parsed.
        if ((w.equals("trade_1m") || w.equals("trade_5m")) && d.has("open")) {
            out.emit(Table.OHLC, ohlc(f, d));
        }
        if (w.equals("market")) {
            out.emit(Table.INSTRUMENT_STATE, state(f, d));
        }
    }

    private static ObjectNode trade(RawFrame f, JsonNode d) {
        ObjectNode r = Rows.target(f);
        r.put("symbol", str(d, "s"));
        r.put("instrument", switch (f.wireCode) {
            case "put_tick" -> "pt";
            case "oddlot_tick" -> "oddlot";
            default -> "stock";
        });
        r.put("exchange_ts", Rows.ts9(Rows.parseDateTime(str(d, "t"))));
        r.put("price", num(d, "p"));
        r.put("qty", num(d, "q"));
        r.put("side", str(d, "si"));          // B = buy-up, S = sell-down
        r.put("avg_price", num(d, "a"));
        r.put("total_volume", firstNum(d, "v", "tq"));
        r.put("total_value", num(d, "tv"));
        r.putNull("change");
        r.putNull("change_percent");
        return r;
    }

    // Both quote and oddlot return `bids`/`asks` as arrays of [price, quantity] pairs.
    // WARNING from the SSI docs: "a later upgrade will return only the CHANGED values"
    // -> today it is a snapshot, tomorrow it may be a delta. This table stores exactly
    // what arrived; book-building logic belongs one layer up and must not assume
    // snapshots forever.
    private static ObjectNode book(RawFrame f, JsonNode d) {
        ObjectNode r = Rows.target(f);
        r.put("symbol", str(d, "s"));
        r.put("instrument", f.wireCode.equals("oddlot_tick") ? "oddlot" : "stock");
        r.put("exchange_ts", Rows.ts9(Rows.parseDateTime(str(d, "t"))));
        pairs(r, d.get("bids"), "bid_price", "bid_qty");
        pairs(r, d.get("asks"), "ask_price", "ask_qty");
        r.putNull("total_bid_qty");
        r.putNull("total_ask_qty");
        r.putNull("level");
        r.putNull("bid_cum_qty");
        r.putNull("ask_cum_qty");
        return r;
    }

    /** [[price, qty], ...] -> two parallel arrays; an unreadable number becomes 0. */
    private static void pairs(ObjectNode r, JsonNode levels, String priceCol, String qtyCol) {
        ArrayNode prices = r.putArray(priceCol);
        ArrayNode qtys = r.putArray(qtyCol);
        if (levels == null || !levels.isArray()) {
            return;
        }
        for (JsonNode lv : levels) {
            Double price = lv.isArray() ? Json.num(lv.get(0)) : null;
            Double qty = lv.isArray() ? Json.num(lv.get(1)) : null;
            prices.add(price == null ? 0.0 : price);
            qtys.add(qty == null ? 0.0 : qty);
        }
    }

    private static ObjectNode foreign(RawFrame f, JsonNode d) {
        ObjectNode r = Rows.target(f);
        r.put("symbol", str(d, "s"));
        r.put("exchange_ts", Rows.ts9(Rows.parseDateTime(str(d, "t"))));
        r.put("buy_qty", num(d, "bq"));
        r.put("sell_qty", num(d, "sq"));
        r.put("buy_value", num(d, "bv"));
        r.put("sell_value", num(d, "sv"));
        r.put("room_total", num(d, "tr"));
        r.put("room_left", num(d, "cr"));
        return r;
    }

    private static ObjectNode ohlc(RawFrame f, JsonNode d) {
        ObjectNode r = Rows.target(f);
        r.put("symbol", str(d, "s"));
        r.put("resolution", f.wireCode.replaceFirst("^trade_", ""));
        r.put("bar_ts", Rows.ts3(Rows.parseDateTime(str(d, "t"))));
        r.put("open", num(d, "open"));
        r.put("high", num(d, "high"));
        r.put("low", num(d, "low"));
        r.put("close", num(d, "close"));
        r.put("volume", num(d, "volume"));
        r.put("closed", 0);
        return r;
    }

    // The `market` topic returns TWO different shapes on the same channel:
    //   (a) start of day : s, b, t, ce, fl, ref  -> ceiling/floor/reference
    //   (b) session flag : b, t, f               -> ATO/LO/ATC
    private static ObjectNode state(RawFrame f, JsonNode d) {
        ObjectNode r = Rows.target(f);
        r.put("symbol", str(d, "s"));
        r.put("board", str(d, "b"));
        r.put("exchange_ts", Rows.ts9(Rows.parseDateTime(str(d, "t"))));
        r.put("ceiling_price", num(d, "ce"));
        r.put("floor_price", num(d, "fl"));
        r.put("ref_price", num(d, "ref"));
        r.putNull("open_price");
        r.putNull("high_price");
        r.putNull("low_price");
        r.putNull("avg_price");
        r.put("status", str(d, "f"));         // the session flag for shape (b)
        return r;
    }
}
