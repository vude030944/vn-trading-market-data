package vnmd.transform;

import java.io.Serializable;

/**
 * One raw Kafka record — payload untouched, metadata from the ingestion contract
 * (key = symbol, headers source / feed / wire_code / recv_ts_ns; see
 * src/ingestion/core/publisher.py).
 * Public non-final fields + no-arg constructor -> Flink POJO serializer.
 */
public class RawFrame implements Serializable {
    private static final long serialVersionUID = 1L;

    public String topic;
    public int partition;
    public long offset;
    public String key;        // "" when absent (e.g. index frames)
    public String source;     // ssi | dnse | tcbs, "" when the header is missing
    public String feed;
    public String wireCode;
    public long recvTsNs;     // epoch nanoseconds when INGESTION received it
    public String payload;    // the broker's bytes, verbatim

    public RawFrame() {
    }

    public RawFrame(String topic, int partition, long offset, String key, String source,
                    String feed, String wireCode, long recvTsNs, String payload) {
        this.topic = topic;
        this.partition = partition;
        this.offset = offset;
        this.key = key;
        this.source = source;
        this.feed = feed;
        this.wireCode = wireCode;
        this.recvTsNs = recvTsNs;
        this.payload = payload;
    }
}
