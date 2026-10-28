package vnmd.transform;

import java.io.Serializable;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Job configuration, captured once in main() (on the JobManager) and shipped to
 * the operators as a serialized field.
 *
 * Every key can be given as a program argument (`--clickhouse-url ...`) or as an
 * environment variable (`CLICKHOUSE_URL`); the argument wins. Defaults match
 * environment/dev, so `flink run ... vnmd-transform.jar` with no arguments works
 * against the dev stack.
 */
public final class JobConfig implements Serializable {
    private static final long serialVersionUID = 1L;

    public final String bootstrapServers;
    public final List<String> topics;
    public final String groupId;
    public final String startingOffsets;   // committed | earliest | latest
    public final String kafkaSecurityProtocol;
    public final String kafkaSaslMechanism;
    public final String kafkaSaslJaasConfig;

    public final String clickhouseUrl;
    public final String clickhouseUser;
    public final String clickhousePassword;
    public final String clickhouseDb;
    public final int clickhouseTimeoutMs;

    public final int batchSize;
    public final long batchIntervalMs;

    /** Which TCBS socket's copy of the futures family is parsed: stock | derivative | both. */
    public final String tcbsFuturesFrom;

    private JobConfig(Map<String, String> env, Map<String, String> argMap) {
        bootstrapServers = getAny(argMap, env,
                "redpanda-0:9092,redpanda-1:9092,redpanda-2:9092",
                "KAFKA_SERVERS", "KAFKA_BOOTSTRAP_SERVERS");
        topics = Arrays.stream(getAny(argMap, env,
                        "tcbs.data.raw.stock,tcbs.data.raw.future,tcbs.data.raw.ouranos,"
                                + "ssi.data.raw.market,dnse.data.raw.market",
                        "TOPICS").split(","))
                .map(String::trim).filter(s -> !s.isEmpty()).toList();
        groupId = getAny(argMap, env, "vnmd-transform", "KAFKA_GROUP_ID");
        startingOffsets = getAny(argMap, env, "committed", "STARTING_OFFSETS");
        kafkaSecurityProtocol = getAny(argMap, env, "", "KAFKA_SECURITY_PROTOCOL");
        kafkaSaslMechanism = getAny(argMap, env, "", "KAFKA_SASL_MECHANISM");
        kafkaSaslJaasConfig = getAny(argMap, env, "", "KAFKA_SASL_JAAS_CONFIG");

        clickhouseUrl = getAny(argMap, env, "http://clickhouse:8123", "CLICKHOUSE_URL");
        clickhouseUser = getAny(argMap, env, "vnmd", "CLICKHOUSE_USER", "CH_USER");
        clickhousePassword = getAny(argMap, env, "vnmd_dev_password", "CLICKHOUSE_PASSWORD", "CH_PASSWORD");
        clickhouseDb = getAny(argMap, env, "vnmd", "CLICKHOUSE_DB", "CH_DB");
        clickhouseTimeoutMs = Integer.parseInt(getAny(argMap, env, "30000", "CLICKHOUSE_TIMEOUT_MS"));

        // ClickHouse wants FEW, LARGE inserts: every INSERT creates a part per
        // partition, and too many small parts end in "Too many parts".
        batchSize = Integer.parseInt(getAny(argMap, env, "5000", "SINK_BATCH_SIZE"));
        batchIntervalMs = Long.parseLong(getAny(argMap, env, "1000", "SINK_BATCH_INTERVAL_MS"));

        tcbsFuturesFrom = getAny(argMap, env, "stock", "TCBS_FUTURES_FROM");
        if (!List.of("stock", "derivative", "both").contains(tcbsFuturesFrom)) {
            throw new IllegalArgumentException("TCBS_FUTURES_FROM must be stock|derivative|both, got "
                    + tcbsFuturesFrom);
        }
    }

    public static JobConfig fromEnvAndArgs(String[] args) {
        return new JobConfig(System.getenv(), parseArgs(args));
    }

    static JobConfig defaults() {
        return new JobConfig(Map.of(), Map.of());
    }

    private static Map<String, String> parseArgs(String[] args) {
        Map<String, String> values = new HashMap<>();
        for (int i = 0; i < args.length; i++) {
            String arg = args[i];
            if (!arg.startsWith("--")) {
                throw new IllegalArgumentException("Unexpected positional argument: " + arg);
            }
            if (i + 1 >= args.length || args[i + 1].startsWith("--")) {
                throw new IllegalArgumentException("Missing value for argument: " + arg);
            }
            String key = arg.substring(2).replace('-', '_').toUpperCase();
            values.put(key, args[++i]);
        }
        return values;
    }

    private static String getAny(Map<String, String> argMap, Map<String, String> env, String def, String... keys) {
        for (String key : keys) {
            String v = argMap.get(key);
            if (v == null || v.isEmpty()) {
                v = env.get(key);
            }
            if (v != null && !v.isEmpty()) {
                return v;
            }
        }
        return def;
    }

    @Override
    public String toString() {
        return "JobConfig(kafka=" + bootstrapServers + ", topics=" + topics
                + ", group=" + groupId + ", offsets=" + startingOffsets
                + ", security=" + (kafkaSecurityProtocol.isEmpty() ? "PLAINTEXT" : kafkaSecurityProtocol)
                + ", clickhouse=" + clickhouseUrl + "/" + clickhouseDb + " user=" + clickhouseUser
                + ", batch=" + batchSize + "/" + batchIntervalMs + "ms"
                + ", tcbsFuturesFrom=" + tcbsFuturesFrom + ")";
    }
}
