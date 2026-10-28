package vnmd.transform;

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.configuration.RestartStrategyOptions;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.KafkaSourceBuilder;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.kafka.clients.consumer.OffsetResetStrategy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;

/**
 * Kafka (5 raw topics) -> Flink (route + parse) -> ClickHouse (batch INSERT).
 *
 *   flink run -d /opt/flink/jobs/vnmd-transform.jar
 *
 * One job for all three brokers: the streams share nothing, but at this volume a
 * single slot carries all of them, and a broker-specific parse problem never
 * fails the job (it lands in unknown_frames instead).
 */
public final class Main {

    private static final Logger LOG = LoggerFactory.getLogger(Main.class);

    static final String JOB_NAME = "vnmd-transform: Kafka -> ClickHouse";

    public static void main(String[] args) throws Exception {
        JobConfig cfg = JobConfig.fromEnvAndArgs(args);
        LOG.info("Starting {} — {}", JOB_NAME, cfg);

        StreamExecutionEnvironment env =
                StreamExecutionEnvironment.getExecutionEnvironment(buildJobConfiguration());

        OffsetsInitializer offsets = switch (cfg.startingOffsets) {
            case "latest" -> OffsetsInitializer.latest();
            case "earliest" -> OffsetsInitializer.earliest();
            // First start reads the whole retention window; restarts resume.
            default -> OffsetsInitializer.committedOffsets(OffsetResetStrategy.EARLIEST);
        };

        KafkaSourceBuilder<RawFrame> source = KafkaSource.<RawFrame>builder()
                .setBootstrapServers(cfg.bootstrapServers)
                .setTopics(cfg.topics)
                .setGroupId(cfg.groupId)
                .setStartingOffsets(offsets)
                .setDeserializer(new FrameDeserializer())
                .setProperty("commit.offsets.on.checkpoint", "true")
                .setProperty("partition.discovery.interval.ms", "60000");
        if (!cfg.kafkaSecurityProtocol.isEmpty()) {
            source.setProperty("security.protocol", cfg.kafkaSecurityProtocol);
        }
        if (!cfg.kafkaSaslMechanism.isEmpty()) {
            source.setProperty("sasl.mechanism", cfg.kafkaSaslMechanism);
        }
        if (!cfg.kafkaSaslJaasConfig.isEmpty()) {
            source.setProperty("sasl.jaas.config", cfg.kafkaSaslJaasConfig);
        }

        env.fromSource(source.build(), WatermarkStrategy.noWatermarks(), "kafka-raw")
                .uid("kafka-raw")
                .flatMap(new FrameRouter(cfg.tcbsFuturesFrom))
                .name("route-and-parse")
                .uid("route-and-parse")
                .sinkTo(new ClickHouseSink(cfg))
                .name("clickhouse-batch-insert")
                .uid("clickhouse-batch-insert");

        env.execute(JOB_NAME);
    }

    /**
     * Job-level execution settings, set IN CODE so the job can diverge from the
     * cluster's FLINK_PROPERTIES without a cluster restart.
     *
     * AT_LEAST_ONCE, not EXACTLY_ONCE: barriers are not aligned (no stalls behind
     * a slow partition) and the sink needs no two-phase commit. The price is
     * duplicates after a crash — see ClickHouseSink.
     */
    private static Configuration buildJobConfiguration() {
        Configuration conf = new Configuration();
        conf.set(RestartStrategyOptions.RESTART_STRATEGY, "fixed-delay");
        conf.set(RestartStrategyOptions.RESTART_STRATEGY_FIXED_DELAY_ATTEMPTS, Integer.MAX_VALUE);
        conf.set(RestartStrategyOptions.RESTART_STRATEGY_FIXED_DELAY_DELAY, Duration.ofSeconds(10));
        // String keys (stable public names) — the typed option classes moved
        // packages between Flink 1.x and 2.x, the keys did not.
        conf.setString("execution.checkpointing.interval", "30s");
        conf.setString("execution.checkpointing.mode", "AT_LEAST_ONCE");
        conf.setString("execution.checkpointing.timeout", "60s");
        conf.setString("execution.checkpointing.min-pause", "10s");
        conf.setString("execution.checkpointing.max-concurrent-checkpoints", "1");
        conf.setString("execution.checkpointing.tolerable-failed-checkpoints", "3");
        conf.setString("execution.checkpointing.externalized-checkpoint-retention",
                "RETAIN_ON_CANCELLATION");
        return conf;
    }

    private Main() {
    }
}
