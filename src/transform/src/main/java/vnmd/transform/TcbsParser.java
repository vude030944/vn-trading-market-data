package vnmd.transform;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import static vnmd.transform.Json.firstNum;
import static vnmd.transform.Json.lng;
import static vnmd.transform.Json.num;
import static vnmd.transform.Json.str;

/**
 * TCBS: routing is by wire_code. The table below comes from the documentation PLUS
 * a production audit of 6.1M messages in examples/ — the docs do NOT list s|42,
 * s|18/28/29/30/32 or s|25, yet all of them run in production.
 *
 *   trades           s|6 (cash) - s|21 (derivatives) - s|18 (covered warrants)
 *                    s|22 (intraday match history) - s|17 (put-through match)
 *                    C001 (ouranos, 1-minute, carries the BU/SD side)
 *   book             s|1/s|2 (cash) - s|23/s|24 (derivatives) - s|28/s|29 (CW)
 *                    s|42 (10-level derivatives, one level per message)
 *   foreign_flow     s|3 (cash, has room) - s|25 (derivatives) - s|30 (CW)
 *   instrument_state s|4 (ceiling/floor/ref) - s|5, s|27, s|32 (session stats)
 *   index_values     s|8
 *   supply_demand    C002S60 - C002S900
 *   unknown_frames   everything else (including s|16 and s|38)
 *
 * The thesis family carries NO time field -> exchange_ts = null; only ouranos
 * (timeSec) and s|17 (an HH:mm:ss clock) provide one.
 */
final class TcbsParser {
    private TcbsParser() {
    }

    /**
     * TCBS broadcasts the futures family 21/23/24/25/27 byte-identical on BOTH the
     * normal and the derivative socket (audit in examples/, DOCUMENT.md 11.2), so
     * parsing both copies doubles every futures trade and quote. `from` names the
     * socket whose copy is kept: stock (default — it arrives ~1 ms earlier),
     * derivative, or both (when only one socket actually carries them).
     */
    static boolean isDuplicateFuturesCopy(RawFrame f, String from) {
        if (!"tcbs".equals(f.source) || "both".equals(from)) {
            return false;
        }
        boolean family = switch (f.wireCode) {
            case "s|21", "s|23", "s|24", "s|25", "s|27" -> true;
            default -> false;
        };
        String dropFeed = "derivative".equals(from) ? "tcbs.stock" : "tcbs.derivative";
        return family && dropFeed.equals(f.feed);
    }

    static void parse(RawFrame f, JsonNode p, FrameRouter.Emitter out) {
        switch (f.wireCode) {
            case "s|6", "s|21", "s|18", "s|22", "s|17", "C001" -> out.emit(Table.TRADES, trade(f, p));
            case "s|1", "s|2", "s|23", "s|24", "s|28", "s|29", "s|42" -> out.emit(Table.BOOK, book(f, p));
            case "s|3", "s|25", "s|30" -> out.emit(Table.FOREIGN_FLOW, foreign(f, p));
            case "s|4", "s|5", "s|27", "s|32" -> out.emit(Table.INSTRUMENT_STATE, state(f, p));
            case "s|8" -> out.emit(Table.INDEX_VALUES, index(f, p));
            case "C002S60", "C002S900" -> out.emit(Table.SUPPLY_DEMAND, supplyDemand(f, p));
            default -> {
                // not ours -> unknown_frames
            }
        }
    }

    private static ObjectNode trade(RawFrame f, JsonNode p) {
        ObjectNode r = Rows.target(f);
        r.put("symbol", str(p, "symbol"));
        r.put("instrument", switch (f.wireCode) {
            case "s|21" -> "derivative";
            case "s|18" -> "cw";
            case "s|17" -> "pt";
            default -> "stock";
        });
        r.put("exchange_ts", Rows.ts9(switch (f.wireCode) {
            case "C001" -> Rows.secondsToNs(num(p, "timeSec"));
            case "s|17" -> Rows.hmsOn(str(p, "time"), f.recvTsNs);
            default -> null;
        }));
        r.put("price", firstNum(p, "matchPrice", "closePrice", "price"));
        r.put("qty", firstNum(p, "matchQtty", "closeVol", "vol"));
        // Only ouranos C001 reveals the AGGRESSOR side (BU = buy-up, SD = sell-down).
        r.put("side", str(p, "action"));
        r.put("avg_price", num(p, "avgPrice"));
        r.put("total_volume", firstNum(p, "totalVolume", "totalTrading"));
        r.put("total_value", firstNum(p, "totalValue", "totalTradingValue", "val"));
        r.put("change", num(p, "change"));
        r.put("change_percent", num(p, "changePercent"));
        return r;
    }

    private static ObjectNode book(RawFrame f, JsonNode p) {
        String w = f.wireCode;
        ObjectNode r = Rows.target(f);
        r.put("symbol", str(p, "symbol"));
        r.put("instrument", switch (w) {
            case "s|23", "s|24", "s|42" -> "derivative";
            case "s|28", "s|29" -> "cw";
            default -> "stock";
        });
        r.putNull("exchange_ts");
        // TCBS sends the bid side (s|1/s|23/s|28) and the ask side (s|2/s|24/s|29)
        // as TWO messages of 3 levels each; s|42 carries ONE level, index in `top`.
        boolean depth = w.equals("s|42");
        boolean bid = w.equals("s|1") || w.equals("s|23") || w.equals("s|28");
        boolean ask = w.equals("s|2") || w.equals("s|24") || w.equals("s|29");
        if (depth) {
            Rows.putNums(r, "bid_price", num(p, "bidPrice"));
            Rows.putNums(r, "bid_qty", num(p, "bidQty"));
            Rows.putNums(r, "ask_price", num(p, "offerPrice"));
            Rows.putNums(r, "ask_qty", num(p, "offerQty"));
        } else {
            Rows.putNums(r, "bid_price", bid ? levels(p, "bidPrice") : new Double[0]);
            Rows.putNums(r, "bid_qty", bid ? levels(p, "bidQtty") : new Double[0]);
            Rows.putNums(r, "ask_price", ask ? levels(p, "offerPrice") : new Double[0]);
            Rows.putNums(r, "ask_qty", ask ? levels(p, "offerQtty") : new Double[0]);
        }
        r.putNull("total_bid_qty");
        r.putNull("total_ask_qty");
        Long top = lng(p, "top");
        r.put("level", top == null || top < 0 || top > 255 ? null : top);
        r.put("bid_cum_qty", num(p, "bidCumulativeQty"));
        r.put("ask_cum_qty", num(p, "offerCumulativeQty"));
        return r;
    }

    private static Double[] levels(JsonNode p, String prefix) {
        return new Double[]{num(p, prefix + "01"), num(p, prefix + "02"), num(p, prefix + "03")};
    }

    private static ObjectNode foreign(RawFrame f, JsonNode p) {
        ObjectNode r = Rows.target(f);
        r.put("symbol", str(p, "symbol"));
        r.putNull("exchange_ts");
        r.put("buy_qty", num(p, "buyForeignQtty"));
        r.put("sell_qty", num(p, "sellForeignQtty"));
        r.putNull("buy_value");
        r.putNull("sell_value");
        r.putNull("room_total");
        // s|3 has `room`; s|25 (derivatives) does not; s|30 (CW) has `foreignNet`
        r.put("room_left", num(p, "room"));
        return r;
    }

    private static ObjectNode state(RawFrame f, JsonNode p) {
        ObjectNode r = Rows.target(f);
        r.put("symbol", str(p, "symbol"));
        r.put("board", "");
        r.putNull("exchange_ts");
        r.put("ceiling_price", num(p, "ceilPrice"));
        r.put("floor_price", num(p, "floorPrice"));
        r.put("ref_price", num(p, "refPrice"));
        r.put("open_price", num(p, "open"));
        r.put("high_price", num(p, "high"));
        r.put("low_price", num(p, "low"));
        r.put("avg_price", num(p, "avg"));
        r.put("status", "");
        return r;
    }

    private static ObjectNode index(RawFrame f, JsonNode p) {
        ObjectNode r = Rows.target(f);
        // s|8 only carries indexNumber as a NUMBER (no name) -> keep the numeric code.
        r.put("index_name", str(p, "indexNumber"));
        r.putNull("exchange_ts");
        r.put("value", num(p, "index"));
        r.put("change", num(p, "change"));
        r.put("change_percent", num(p, "changePercent"));
        r.put("volume", num(p, "volume"));
        r.put("turnover", num(p, "value"));
        r.put("advances", lng(p, "increase"));
        r.put("declines", lng(p, "decrease"));
        r.put("unchanged", lng(p, "notChange"));
        r.put("ceiling_count", lng(p, "ceilIncrease"));
        r.put("floor_count", lng(p, "floorDecrease"));
        r.put("session_code", str(p, "session"));
        return r;
    }

    // Aggressor-side supply/demand. Note: the TCBS docs label C002S900 as "foreign
    // investor trading" — that is WRONG; its schema is identical to C002S60, only
    // the 900-second window differs.
    private static ObjectNode supplyDemand(RawFrame f, JsonNode p) {
        ObjectNode r = Rows.target(f);
        r.put("symbol", str(p, "symbol"));
        r.put("exchange_ts", Rows.ts9(Rows.secondsToNs(num(p, "timeSec"))));
        r.put("timeframe_s", lng(p, "unitTimeFrame"));
        r.put("buy_up_vol", num(p, "totalBUVol"));
        r.put("buy_up_vol_acc", num(p, "totalBUVolAcc"));
        r.put("sell_down_vol", num(p, "totalSDVol"));
        r.put("sell_down_vol_acc", num(p, "totalSDVolAcc"));
        r.put("bs_ratio_acc", num(p, "bsAccRatio"));
        return r;
    }
}
