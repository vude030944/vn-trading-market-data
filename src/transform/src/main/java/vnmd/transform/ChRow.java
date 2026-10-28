package vnmd.transform;

import java.io.Serializable;

/**
 * One fully parsed row on its way to ClickHouse: the destination table plus the
 * row already serialized as a JSONEachRow line. Parsing happens once, in the
 * router; the sink only concatenates lines, so it stays a dumb batcher.
 */
public class ChRow implements Serializable {
    private static final long serialVersionUID = 1L;

    public Table table;
    public String json;

    public ChRow() {
    }

    public ChRow(Table table, String json) {
        this.table = table;
        this.json = json;
    }
}
