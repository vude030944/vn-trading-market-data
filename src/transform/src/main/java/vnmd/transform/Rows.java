package vnmd.transform;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeFormatterBuilder;
import java.time.format.DateTimeParseException;
import java.time.temporal.ChronoField;
import java.time.temporal.TemporalAccessor;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Row skeletons and time conversions shared by the three broker parsers.
 *
 * Every target row carries two time columns that must NEVER be conflated:
 *   exchange_ts  the BROKER's timestamp — null when the broker provides none
 *   recv_ts      when WE received it; always present
 * No broker offers a sequence number, so recv_ts is the only value comparable
 * across sources, and message identity is (kafka_topic, kafka_partition,
 * kafka_offset) — never a timestamp.
 *
 * DateTime64 values are sent to ClickHouse as wall-clock text in the column's
 * own timezone (Asia/Ho_Chi_Minh, no DST), which ClickHouse parses exactly.
 */
final class Rows {
    static final ZoneId VN = ZoneId.of("Asia/Ho_Chi_Minh");

    private static final DateTimeFormatter TS9 =
            DateTimeFormatter.ofPattern("uuuu-MM-dd HH:mm:ss.SSSSSSSSS").withZone(VN);
    private static final DateTimeFormatter TS3 =
            DateTimeFormatter.ofPattern("uuuu-MM-dd HH:mm:ss.SSS").withZone(VN);

    // Lenient "best effort" input: 2025/08/14 10:15:30, 2025-08-14T10:15:30.123+07:00, 14/08/2025 10:15:30
    private static final DateTimeFormatter BEST_EFFORT = new DateTimeFormatterBuilder()
            .appendPattern("uuuu-MM-dd HH:mm:ss")
            .optionalStart().appendFraction(ChronoField.NANO_OF_SECOND, 1, 9, true).optionalEnd()
            .optionalStart().appendOffset("+HH:MM", "Z").optionalEnd()
            .toFormatter();
    private static final Pattern DMY = Pattern.compile("^(\\d{2})-(\\d{2})-(\\d{4})(.*)$");
    private static final Pattern HMS = Pattern.compile("^(\\d{2}):(\\d{2}):(\\d{2})$");

    private Rows() {
    }

    // ------------------------------------------------------------------ rows

    /** Columns common to every target table (20_targets.sql). */
    static ObjectNode target(RawFrame f) {
        ObjectNode r = Json.MAPPER.createObjectNode();
        r.put("source", f.source);
        r.put("recv_ts", ts9(f.recvTsNs));
        r.put("wire_code", f.wireCode);
        r.put("feed", f.feed);
        r.put("recv_ts_ns", f.recvTsNs);
        r.put("kafka_topic", f.topic);
        r.put("kafka_partition", f.partition);
        r.put("kafka_offset", f.offset);
        return r;
    }

    /** vnmd.raw — the payload verbatim. recv_ts is MATERIALIZED there, so it is not sent. */
    static ObjectNode raw(RawFrame f, String error) {
        ObjectNode r = Json.MAPPER.createObjectNode();
        r.put("source", f.source);
        r.put("feed", f.feed);
        r.put("wire_code", f.wireCode);
        r.put("kafka_key", f.key);
        r.put("payload", f.payload);
        r.put("recv_ts_ns", f.recvTsNs);
        r.put("kafka_topic", f.topic);
        r.put("kafka_partition", f.partition);
        r.put("kafka_offset", f.offset);
        r.put("error", error);
        return r;
    }

    static ObjectNode unknown(RawFrame f) {
        ObjectNode r = target(f);
        r.put("kafka_key", f.key);
        r.put("payload", f.payload);
        return r;
    }

    /** Array(Float64) column from candidate values, dropping the absent ones. */
    static void putNums(ObjectNode r, String column, Double... values) {
        ArrayNode a = r.putArray(column);
        for (Double v : values) {
            if (v != null) {
                a.add(v);
            }
        }
    }

    static String json(ObjectNode r) {
        try {
            return Json.MAPPER.writeValueAsString(r);
        } catch (Exception e) {
            throw new IllegalStateException("cannot serialize row", e);
        }
    }

    // ------------------------------------------------------------------ time

    static String ts9(Long epochNs) {
        if (epochNs == null) {
            return null;
        }
        return TS9.format(Instant.ofEpochSecond(Math.floorDiv(epochNs, 1_000_000_000L),
                Math.floorMod(epochNs, 1_000_000_000L)));
    }

    /** For DateTime64(3) columns (ohlc.bar_ts). */
    static String ts3(Long epochNs) {
        if (epochNs == null) {
            return null;
        }
        return TS3.format(Instant.ofEpochSecond(Math.floorDiv(epochNs, 1_000_000_000L),
                Math.floorMod(epochNs, 1_000_000_000L)));
    }

    /** Epoch seconds (possibly fractional, possibly a string upstream) -> epoch ns. */
    static Long secondsToNs(Double seconds) {
        if (seconds == null) {
            return null;
        }
        long whole = (long) Math.floor(seconds);
        return whole * 1_000_000_000L + Math.round((seconds - whole) * 1e9);
    }

    /**
     * DNSE returns {"Seconds":..,"Nanos":..}. The two are combined as INTEGERS —
     * going through a double first loses precision (101000000 becomes 101000192).
     */
    static Long dnseTs(JsonNode payload, String field) {
        JsonNode t = payload.get(field);
        if (t == null || !t.isObject() || !t.has("Seconds")) {
            return null;
        }
        Long s = Json.lng(t, "Seconds");
        if (s == null) {
            return null;
        }
        Long n = Json.lng(t, "Nanos");
        return s * 1_000_000_000L + (n == null ? 0L : n);
    }

    /**
     * Time-only fields (TCBS s|17 returns "10:56:50" with no date). Combined with
     * the DATE we received the message, in Vietnam time.
     */
    static Long hmsOn(String hms, long baseNs) {
        Matcher m = HMS.matcher(hms == null ? "" : hms);
        if (!m.matches()) {
            return null;
        }
        LocalDate day = Instant.ofEpochSecond(Math.floorDiv(baseNs, 1_000_000_000L)).atZone(VN).toLocalDate();
        Instant at = day.atTime(Integer.parseInt(m.group(1)), Integer.parseInt(m.group(2)),
                Integer.parseInt(m.group(3))).atZone(VN).toInstant();
        return at.getEpochSecond() * 1_000_000_000L;
    }

    /** Date-time text -> epoch ns; no offset means Vietnam time. null when unparsable. */
    static Long parseDateTime(String s) {
        if (s == null || s.isBlank()) {
            return null;
        }
        String t = s.trim().replace('/', '-').replace('T', ' ');
        Matcher dmy = DMY.matcher(t);
        if (dmy.matches()) {
            t = dmy.group(3) + "-" + dmy.group(2) + "-" + dmy.group(1) + dmy.group(4);
        }
        if (t.length() == 10) {
            t += " 00:00:00";      // date only (SSI market start-of-day: "YYYY/MM/DD")
        }
        try {
            TemporalAccessor ta = BEST_EFFORT.parse(t);
            LocalDateTime ldt = LocalDateTime.from(ta);
            Instant i = ta.isSupported(ChronoField.OFFSET_SECONDS)
                    ? ldt.toInstant(ZoneOffset.ofTotalSeconds(ta.get(ChronoField.OFFSET_SECONDS)))
                    : ldt.atZone(VN).toInstant();
            return i.getEpochSecond() * 1_000_000_000L + i.getNano();
        } catch (DateTimeParseException e) {
            return null;
        }
    }
}
