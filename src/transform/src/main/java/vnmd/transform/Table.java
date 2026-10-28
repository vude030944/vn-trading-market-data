package vnmd.transform;

/** Destination tables in database vnmd (src/transform/sql/10_landing.sql, 20_targets.sql). */
public enum Table {
    RAW("raw"),
    TRADES("trades"),
    BOOK("book"),
    INDEX_VALUES("index_values"),
    FOREIGN_FLOW("foreign_flow"),
    OHLC("ohlc"),
    SUPPLY_DEMAND("supply_demand"),
    INSTRUMENT_STATE("instrument_state"),
    UNKNOWN_FRAMES("unknown_frames");

    public final String tableName;

    Table(String tableName) {
        this.tableName = tableName;
    }
}
