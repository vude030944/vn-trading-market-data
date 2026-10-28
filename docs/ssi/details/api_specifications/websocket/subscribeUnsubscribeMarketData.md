<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/subscribeUnsubscribeMarketData
Tieu de goc: Sub/Unsub Market Data
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/subscribeUnsubscribeMarketData>

# Sub/Unsub Market Data

Theo dõi và hủy theo dõi dữ liệu thị trường qua WebSocket FastConnect.

## Tổng quan

Kênh **DATA** trả về 6 nhóm thông tin thị trường:

| Topic | Mô tả |
|---|---|
| `trade` | Thông tin khớp lệnh |
| `quote` | Thông tin bid/ask |
| `room` | Thông tin room ngoại |
| `put` | Khớp lệnh thỏa thuận |
| `oddlot` | Giao dịch lô lẻ |
| `market` | Thông tin đầu ngày và cờ phiên |

## Topic pattern
```text
trade.[index/exchange/symbol-symbol/*]@[tick/1m/5m]
quote.[index/exchange/symbol-symbol/*]@[tick/1m/5m]
room.[index/exchange/symbol-symbol/*]@[tick/1m/5m]
put.[index/exchange/symbol-symbol/*]@[tick/1m/5m]
oddlot.[index/exchange/symbol-symbol/*]@[tick/1m/5m]
market.[index/exchange/symbol-symbol/*]
```

  * Nhiều mã nối bằng dấu `-` (ví dụ `ACB-SSI-GVR-KDH`); `*` cho toàn bộ mã trong phạm vi quyền.
  * Không truyền `@interval` thì mặc định là `tick`. Riêng topic `market` không có interval.

> **Lưu ý:** interval hợp lệ hiện tại là `tick`, `1m`, `5m` (không có `3m`).

## Subscribe market data
```json
{
  "method": "SUBSCRIBE",
  "channel": "DATA",
  "topics": [
    "trade.SSI",
    "trade.ACB-SSI-GVR-KDH",
    "trade.vn30",
    "trade.hose"
  ]
}
```

  * `trade.SSI` — đăng ký nhận message khớp của một mã SSI
  * `trade.ACB-SSI-GVR-KDH` — đăng ký nhận message khớp của nhiều mã ACB, SSI, GVR, KDH
  * `trade.vn30` — đăng ký nhận message khớp của toàn bộ các mã thuộc rổ VN30
  * `trade.hose` — đăng ký nhận message khớp của toàn bộ các mã thuộc sàn HOSE

Cú pháp tương tự áp dụng cho `quote`, `room`, `put`, `oddlot`, `market` — chỉ thay tiền tố topic (ví dụ `quote.SSI`, `room.vn30`, `market.hose`).

## Unsubscribe market data
```json
{
  "method": "UNSUBSCRIBE",
  "channel": "DATA",
  "topics": ["trade.SSI", "quote.SSI"]
}
```

* * *

## I. Trade — thông tin khớp lệnh

| Field | Name | Type | Description |
|---|---|---|---|
| `s` | symbol | String | Mã chứng khoán |
| `t` | tradingTime | String | `YYYY/MM/DD HH:mi:ss` |
| `p` | price | String | Giá khớp |
| `q` | quantity | String | Khối lượng khớp |
| `a` | avgPrice | String | Giá khớp trung bình |
| `si` | side | String | `B`: Buy Up (mua chủ động) / `S`: Sell Down (bán chủ động) |
| `o` | openPrice | String | Giá mở cửa |
| `h` | highPrice | String | Giá cao nhất |
| `l` | lowPrice | String | Giá thấp nhất |
| `v` | totalVol | String | Tổng khối lượng khớp trong ngày |

**Sample output:**
```json
{
  "s": "SSI",
  "t": "2026/07/29 09:15:32",
  "p": "45.50",
  "q": "1000",
  "a": "45.35",
  "si": "B",
  "o": "45.00",
  "h": "45.80",
  "l": "44.90",
  "v": "1250000"
}
```

## II. Room — thông tin room ngoại

| Field | Name | Type | Description |
|---|---|---|---|
| `s` | symbol | String | Mã chứng khoán |
| `t` | tradingtime | String | `YYYY/MM/DD HH:mi:ss` |
| `tr` | totalRoom | String | Tổng room ngoại |
| `cr` | currentRoom | String | Room ngoại còn lại |
| `bq` | buyQuantity | String | Khối lượng mua của khối ngoại |
| `bv` | buyValue | String | Giá trị mua của khối ngoại |
| `sq` | sellQuantity | String | Khối lượng bán của khối ngoại |
| `sv` | sellValue | String | Giá trị bán của khối ngoại |

**Sample output:**
```json
{
  "s": "SSI",
  "t": "2026/07/29 09:15:32",
  "tr": "1500000",
  "cr": "980000",
  "bq": "5000",
  "bv": "227500000",
  "sq": "3000",
  "sv": "136500000"
}
```

## III. Quote — thông tin bid/ask

| Field | Type | Description |
|---|---|---|
| `s` | String | Mã chứng khoán |
| `t` | String | tradingtime, `YYYY/MM/DD HH:mi:ss` |
| `bids` | `List<String[2]>` | Danh sách mức giá mua `[price, quantity]`. Bản nâng cấp sau sẽ chỉ trả ra các giá trị thay đổi. |
| `asks` | `List<String[2]>` | Danh sách mức giá bán `[price, quantity]`. Bản nâng cấp sau sẽ chỉ trả ra các giá trị thay đổi. |

**Sample output:**
```json
{
  "s": "SSI",
  "t": "2026/07/29 09:15:32",
  "bids": [
    ["45.45", "3200"],
    ["45.40", "1500"],
    ["45.35", "4200"],
    ["45.30", "2100"],
    ["45.25", "3300"]
  ],
  "asks": [
    ["45.50", "2800"],
    ["45.55", "1900"],
    ["45.60", "3600"],
    ["45.65", "2200"],
    ["45.70", "4100"]
  ]
}
```

## IV. Put — khớp lệnh thỏa thuận

| Field | Name | Type | Description |
|---|---|---|---|
| `s` | symbol | String | Mã chứng khoán |
| `t` | tradingtime | String | `YYYY/MM/DD HH:mi:ss` |
| `p` | price | String | Giá khớp thỏa thuận |
| `q` | quantity | String | Khối lượng khớp thỏa thuận |
| `tq` | TotalQuantity | String | Tổng khối lượng thỏa thuận trong ngày |
| `tv` | TotalValue | String | Tổng giá trị thỏa thuận trong ngày |

**Sample output:**
```json
{
  "s": "SSI",
  "t": "2026/07/29 10:05:12",
  "p": "45.00",
  "q": "50000",
  "tq": "350000",
  "tv": "15750000000"
}
```

## V. Oddlot — giao dịch lô lẻ

| Field | Name | Type | Description |
|---|---|---|---|
| `s` | symbol | String | Mã chứng khoán |
| `t` | tradingtime | String | `YYYY/MM/DD HH:mi:ss` |
| `p` | price | String | Giá khớp lô lẻ |
| `q` | quantity | String | Khối lượng khớp lô lẻ |
| `bids` | `List<String[2]>` | Danh sách mức giá mua lô lẻ `[price, quantity]` |  |
| `asks` | `List<String[2]>` | Danh sách mức giá bán lô lẻ `[price, quantity]` |  |

**Sample output:**
```json
{
  "s": "SSI",
  "t": "2026/07/29 09:16:05",
  "p": "45.50",
  "q": "80",
  "bids": [
    ["45.45", "50"],
    ["45.40", "30"]
  ],
  "asks": [
    ["45.55", "40"],
    ["45.60", "20"]
  ]
}
```

## VI. Market — thông tin đầu ngày và phiên

Cú pháp subscribe không có interval: `market.[index/exchange/symbol-symbol/*]`.

**Market streaming data:**

| Field | Name | Type | Description |
|---|---|---|---|
| `s` | symbol | String | Mã chứng khoán |
| `b` | board | String | `HOSE`, `HNX`, `UPCOM` |
| `t` | tradingDate | String | `YYYY/MM/DD` |
| `ce` | ceilingPrice | String | Giá trần |
| `fl` | floorPrice | String | Giá sàn |
| `ref` | refPrice | String | Giá tham chiếu |

**Sample output:**
```json
{
  "s": "SSI",
  "b": "HOSE",
  "t": "2026/07/29",
  "ce": "48.50",
  "fl": "42.10",
  "ref": "45.30"
}
```

**Market flag (message cờ phiên):**

| Field | Name | Type | Description |
|---|---|---|---|
| `b` | board | String | `HOSE`, `HNX`, `UPCOM`, `DERIVATIVES` |
| `t` | tradingTime | String | `YYYY/MM/DD HH:mm:ss` |
| `f` | flag | String | Cờ phiên: `ATO`, `LO`, `ATC`, v.v. |

**Sample output:**
```json
{
  "b": "HOSE",
  "t": "2026/07/29 09:00:00",
  "f": "ATO"
}
```

* * *

## Tham khảo thêm

  * [Kết nối WebSocket](/docs/api-reference/connectWebSocket) — thiết lập kết nối
  * [Heartbeat](/docs/api-reference/getHeartbeatStructure) — cơ chế ping/pong giữ kết nối
  * [Sub/Unsub Trading Data](/docs/api-reference/subscribeUnsubscribeTradingData) — theo dõi dữ liệu giao dịch
