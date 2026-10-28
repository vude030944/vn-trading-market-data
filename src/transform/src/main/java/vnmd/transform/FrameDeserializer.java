package vnmd.transform;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.connector.kafka.source.reader.deserializer.KafkaRecordDeserializationSchema;
import org.apache.flink.util.Collector;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.common.header.Header;

import java.nio.charset.StandardCharsets;
import java.time.Instant;

/** Kafka record -> RawFrame. Reads the four ingestion headers; never touches the payload. */
public class FrameDeserializer implements KafkaRecordDeserializationSchema<RawFrame> {
    private static final long serialVersionUID = 1L;

    @Override
    public void deserialize(ConsumerRecord<byte[], byte[]> record, Collector<RawFrame> out) {
        String source = "";
        String feed = "";
        String wire = "";
        long recvTsNs = 0L;
        for (Header h : record.headers()) {
            if (h.value() == null) {
                continue;
            }
            String v = new String(h.value(), StandardCharsets.UTF_8);
            switch (h.key()) {
                case "source" -> source = v;
                case "feed" -> feed = v;
                case "wire_code" -> wire = v;
                case "recv_ts_ns" -> {
                    try {
                        recvTsNs = Long.parseLong(v);
                    } catch (NumberFormatException ignored) {
                        // left 0 -> replaced by "now" below
                    }
                }
                default -> {
                    // unknown header: ignore
                }
            }
        }
        if (recvTsNs <= 0) {
            // A frame without the header still lands, stamped with OUR clock — once,
            // here, so its raw and parsed rows carry the same value.
            Instant now = Instant.now();
            recvTsNs = now.getEpochSecond() * 1_000_000_000L + now.getNano();
        }
        String key = record.key() == null ? "" : new String(record.key(), StandardCharsets.UTF_8);
        String payload = record.value() == null ? "" : new String(record.value(), StandardCharsets.UTF_8);
        out.collect(new RawFrame(record.topic(), record.partition(), record.offset(),
                key, source, feed, wire, recvTsNs, payload));
    }

    @Override
    public TypeInformation<RawFrame> getProducedType() {
        return TypeInformation.of(RawFrame.class);
    }
}
