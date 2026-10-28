package vnmd.transform;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * Tolerant JSON field accessors.
 *
 * The three brokers return the same kind of value in different types, and the
 * documented type frequently disagrees with the sample payload printed right
 * next to it (see docs/BROKER/brief/DOCUMENT.md section 11):
 *     TCBS cash       : "matchPrice":"24550"   <- STRING
 *     TCBS derivatives: "matchPrice":1870.5    <- NUMBER
 *     SSI             : "p":"45.50"            <- STRING
 *     DNSE            : "matchPrice":24.35     <- NUMBER, yet "volume":"12" is a STRING
 * Therefore EVERY numeric field is read through num()/lng(), which accept both
 * and return null for missing / null / unparsable — they never throw.
 */
final class Json {
    static final ObjectMapper MAPPER = new ObjectMapper();

    private Json() {
    }

    /** null when the payload is not a JSON object (empty, truncated, msgpack...). */
    static JsonNode parseObject(String payload) {
        if (payload == null || payload.isEmpty()) {
            return null;
        }
        try {
            JsonNode n = MAPPER.readTree(payload);
            return n != null && n.isObject() ? n : null;
        } catch (Exception e) {
            return null;
        }
    }

    /** Scalars as text; "" when missing, null or a container (target columns are non-Nullable). */
    static String str(JsonNode n, String field) {
        JsonNode v = n == null ? null : n.get(field);
        if (v == null || v.isNull() || v.isContainerNode()) {
            return "";
        }
        return v.asText();
    }

    static Double num(JsonNode n, String field) {
        return num(n == null ? null : n.get(field));
    }

    static Double num(JsonNode v) {
        if (v == null || v.isNull()) {
            return null;
        }
        if (v.isNumber()) {
            return v.doubleValue();
        }
        if (v.isTextual()) {
            try {
                String s = v.asText().trim();
                return s.isEmpty() ? null : Double.parseDouble(s);
            } catch (NumberFormatException e) {
                return null;
            }
        }
        return null;
    }

    static Long lng(JsonNode n, String field) {
        JsonNode v = n == null ? null : n.get(field);
        if (v == null || v.isNull()) {
            return null;
        }
        if (v.isNumber()) {
            return v.longValue();
        }
        if (v.isTextual()) {
            try {
                String s = v.asText().trim();
                return s.isEmpty() ? null : Long.parseLong(s);
            } catch (NumberFormatException e) {
                return null;
            }
        }
        return null;
    }

    /** The first non-null of several candidate fields (brokers rename fields per family). */
    static Double firstNum(JsonNode n, String... fields) {
        for (String f : fields) {
            Double v = num(n, f);
            if (v != null) {
                return v;
            }
        }
        return null;
    }
}
