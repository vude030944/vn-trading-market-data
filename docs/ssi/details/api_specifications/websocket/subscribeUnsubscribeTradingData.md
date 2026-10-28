<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/subscribeUnsubscribeTradingData
Tieu de goc: Sub/Unsub Trading Data
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/subscribeUnsubscribeTradingData>

# Sub/Unsub Trading Data

Theo dõi và hủy theo dõi dữ liệu giao dịch qua WebSocket FastConnect — bao gồm lệnh thường, khớp lệnh, danh mục và lệnh điều kiện (FCO).

## Tổng quan

Kênh **TRADING** cho phép client nhận các sự kiện giao dịch theo thời gian thực: trạng thái lệnh, khớp lệnh, thay đổi danh mục và sự kiện lệnh điều kiện (FCO).

Client cần subscribe theo tài khoản (`accountNo`) để nhận event. Mỗi topic tương ứng với một nhóm sự kiện cụ thể.

## Topic pattern
```text
order.[accountNo/*]
portfolio.[accountNo-accountNo/*]
```

| Topic | Mô tả | Ví dụ |
|---|---|---|
| `order.<accountNo>` | Sự kiện lệnh (đặt/sửa/hủy/khớp) và lệnh điều kiện (FCO) của một tài khoản cụ thể | `order.1231991` |
| `order.<accountNo1>-<accountNo2>` | Sự kiện lệnh của nhiều tài khoản cụ thể | `order.1231996-1231998` |
| `order.*` | Sự kiện lệnh và lệnh điều kiện (FCO) của tất cả tài khoản trong phạm vi quyền | `order.*` |
| `portfolio.<accountNo>` | Cập nhật danh mục (tài sản, vị thế) của một tài khoản cụ thể | `portfolio.1231991` |
| `portfolio.<accountNo1>-<accountNo2>` | Cập nhật danh mục của nhiều tài khoản cụ thể | `portfolio.1231996-1231998` |
| `portfolio.*` | Cập nhật danh mục của tất cả tài khoản trong phạm vi quyền | `portfolio.*` |

> **Lưu ý:** Sự kiện lệnh điều kiện (FCO) được trả về trên cùng kênh `order` — không cần subscribe topic riêng.
>
> **Lưu ý:** Subscribe topic `portfolio` hiện **_chỉ hỗ trợ tài khoản đuôi 8 (tài khoản phái sinh)_**. Tài khoản cơ sở (đuôi 1) hoặc ký quỹ (đuôi 6) chưa được hỗ trợ.

## Subscribe

Gửi message với `method: "SUBSCRIBE"` và `channel: "TRADING"`:
```json
{
  "method": "SUBSCRIBE",
  "channel": "TRADING",
  "topics": [
    "order.1231991",
    "order.1231996-1231998",
    "order.*",
    "portfolio.0901351"
  ]
}
```

### Quy tắc subscribe

  * Có thể subscribe nhiều topic trong cùng một message.
  * Subscribe `order.*` sẽ nhận event lệnh của **tất cả** tài khoản (bao gồm cả lệnh điều kiện FCO).
  * Subscribe `portfolio.*` sẽ nhận event danh mục của **tất cả** tài khoản.
  * Subscribe cùng topic nhiều lần không gây lỗi — server bỏ qua topic đã subscribe.
  * Sau khi reconnect, client **phải subscribe lại** toàn bộ topic cần theo dõi.

## Unsubscribe

Gửi message với `method: "UNSUBSCRIBE"` và `channel: "TRADING"`:
```json
{
  "method": "UNSUBSCRIBE",
  "channel": "TRADING",
  "topics": ["order.0901351", "portfolio.0901351"]
}
```

### Quy tắc unsubscribe

  * Chỉ unsubscribe các topic đã subscribe trước đó.
  * Unsubscribe topic chưa subscribe không gây lỗi — server bỏ qua.
  * Unsubscribe **không** ảnh hưởng đến các topic khác đang subscribe.
  * Để kiểm tra danh sách topic đang subscribe, dùng `LIST_SUBSCRIPTION`.

## Kiểm tra subscription hiện tại
```json
{
  "method": "LIST_SUBSCRIPTION"
}
```

Response trả về scope theo nhóm:
```json
{
  "trading": "order.0901351;portfolio.0901351",
  "data": ""
}
```

* * *

## Các loại event

Sau khi subscribe thành công, client sẽ nhận các event sau theo thời gian thực.

### Binding event trong SDK
```javascript
client.bind(client.events.onOrderEvent, function (e, data) {
  console.log(e + ": ");
  console.log(JSON.stringify(data));
});

client.bind(client.events.onOrderMatchEvent, function (e, data) {
  console.log(e + ": ");
  console.log(JSON.stringify(data));
});

client.bind(client.events.onClientPortfolioEvent, function (e, data) {
  console.log(e + ": ");
  console.log(JSON.stringify(data));
});
```

> Sự kiện lệnh điều kiện (FCO) được trả về qua cùng binding `onClientPortfolioEvent`.

* * *

### Order Event

Sự kiện trạng thái lệnh — phát sinh khi lệnh được đặt, sửa, hủy hoặc thay đổi trạng thái.
```json
{
  "eventType": "orderEvent",
  "notifyId": 123456789,
  "connectionId": "conn-001",
  "clientRequestId": "req-20240226-001",
  "orderId": "ORD123456",
  "symbol": "VNM",
  "side": "B",
  "orderType": "LO",
  "accountNo": "0901351",
  "price": "72000",
  "quantity": 1000,
  "cancelQty": 0,
  "osQty": 1000,
  "filledQty": 0,
  "inputTime": "2026/03/01 14:20:55",
  "modifiedTime": "2026/03/01 14:20:55",
  "orderStatus": "PD",
  "rejectReason": "",
  "errorCode": "",
  "errorMessage": ""
}
```

| Trường | Kiểu | Mô tả |
|---|---|---|
| `eventType` | string | Loại event: `"orderEvent"` |
| `notifyId` | Long | Số serial của event message |
| `connectionId` | string | Định danh phiên kết nối stream của client |
| `clientRequestId` | string | Định danh lệnh trong ngày, tự động sinh nếu không truyền. Dùng để đối chiếu tương ứng với lệnh từ đầu client |
| `orderId` | string | Số định danh lệnh được ghi nhận tại hệ thống giao dịch |
| `symbol` | string | Mã chứng khoán |
| `side` | string | Chiều mua/bán của lệnh (`B` → BUY / `S` → SELL) |
| `orderType` | string | Loại lệnh (`LO`, `ATO`, `ATC`,...) |
| `accountNo` | string | Số tài khoản đặt lệnh |
| `price` | string | Giá |
| `quantity` | number | Khối lượng |
| `cancelQty` | number | Khối lượng đã hủy |
| `osQty` | number | Khối lượng chưa khớp |
| `filledQty` | number | Khối lượng khớp |
| `inputTime` | string | Thời gian tiếp nhận đặt lệnh (format theo quy chuẩn chung) |
| `modifiedTime` | string | Thời gian sửa, cập nhật trạng thái lệnh (format theo quy chuẩn chung) |
| `orderStatus` | string | Trạng thái lệnh, tham chiếu theo bảng trạng thái lệnh |
| `rejectReason` | string | Lý do từ chối |
| `errorCode` | string | Mã lỗi lệnh |
| `errorMessage` | string | Thông tin lệnh lỗi |

* * *

### Order Match Event

Sự kiện khớp lệnh — phát sinh khi lệnh được khớp (một phần hoặc toàn bộ).
```json
{
  "eventType": "orderMatchEvent",
  "notifyId": 1061597,
  "connectionId": "connection_id_value",
  "clientRequestId": "91530521",
  "orderId": "26022601219922",
  "symbol": "MSR",
  "side": "S",
  "accountNo": "Q276811",
  "matchPrice": "43100.0",
  "matchQty": 500,
  "matchTime": "2026/03/01 14:20:55"
}
```

| Trường | Kiểu | Mô tả |
|---|---|---|
| `eventType` | string | Loại event: `"orderMatchEvent"` |
| `notifyId` | Long | Số serial của event message |
| `connectionId` | string | Định danh phiên kết nối stream của client |
| `clientRequestId` | string | Định danh lệnh trong ngày, tự động sinh nếu không truyền. Dùng để đối chiếu tương ứng với lệnh từ đầu client |
| `orderId` | string | Số định danh lệnh được ghi nhận tại hệ thống giao dịch |
| `symbol` | string | Mã chứng khoán |
| `side` | string | Chiều mua/bán của lệnh (`B` → BUY / `S` → SELL) |
| `accountNo` | string | Số tài khoản đặt lệnh |
| `matchPrice` | string | Giá khớp |
| `matchQty` | number | Khối lượng khớp |
| `matchTime` | string | Thời gian khớp (format theo quy chuẩn chung) |

* * *

### Client Portfolio Event

Sự kiện cập nhật danh mục — phát sinh khi số dư hoặc tài sản thay đổi.
```json
{
  "eventType": "clientPortfolioEvent",
  "notifyId": 1023456,
  "connectionId": "CONN-8899-XYZZ",
  "symbol": "VND",
  "accountNo": "0123456789",
  "longQty": 1500,
  "shortQty": 500,
  "net": 1000,
  "bidAvgPrice": "12.35",
  "askAvgPrice": "12.40",
  "tradePrice": "12.38",
  "marketPrice": "12.45",
  "floatingPL": "1500.75",
  "tradingPL": "2500.50"
}
```

| Trường | Kiểu | Mô tả |
|---|---|---|
| `eventType` | string | Loại event: `"clientPortfolioEvent"` |
| `notifyId` | Long | Số serial của event message |
| `connectionId` | string | Định danh phiên kết nối stream của client |
| `symbol` | string | Mã chứng khoán |
| `accountNo` | string | Số tài khoản |
| `longQty` | number | Vị thế long |
| `shortQty` | number | Vị thế short |
| `net` | number | Vị thế net (tính bằng long - short) |
| `bidAvgPrice` | string | Giá mua trung bình |
| `askAvgPrice` | string | Giá bán trung bình |
| `tradePrice` | string | Giá khớp |
| `marketPrice` | string | Giá thị trường |
| `floatingPL` | string | Lãi/lỗ tạm tính |
| `tradingPL` | string | Lãi/lỗ đã chốt |

* * *

### FCO Event (Lệnh điều kiện)

Sự kiện lệnh điều kiện (FCO — FastConnect Conditional Order) — phát sinh khi lệnh điều kiện thay đổi trạng thái (khởi tạo, kích hoạt, khớp, hủy...).

> FCO Event được trả về trên cùng kênh streaming `order` — client nhận qua binding `onClientPortfolioEvent`.
```javascript
client.bind(client.events.onClientPortfolioEvent, function (e, data) {
  // Xử lý FCO event
  console.log(e + ": ");
  console.log(JSON.stringify(data));
});
```

**Ví dụ FCO Event Response:**
```json
{
  "type": "fcoEvent",
  "data": {
    "fcoId": "7528ac20-a340-4233-8bb7-a2379fc3c638",
    "notifyID": 1249008,
    "processStatus": "INIT",
    "matchedQuantity": 0,
    "isPlaceOrder": false,
    "instrumentID": "ssi",
    "quantity": 4000,
    "price": "MP",
    "account": "1231496",
    "updatedTime": "1751966448000",
    "status": "200",
    "message": "Success",
    "username": "123149"
  }
}
```

| Trường | Kiểu | Mô tả | Giá trị hợp lệ / Định dạng |
|---|---|---|---|
| `type` | string | Loại event | `"fcoEvent"` |
| `data` | object | Thông tin chi tiết của event | — |
| `data.fcoId` | string | ID lệnh điều kiện | UUID |
| `data.notifyID` | number | ID thông báo | — |
| `data.processStatus` | string | Trạng thái xử lý lệnh điều kiện | Tham khảo [Phụ lục FCO](/docs/api-reference/appendix/fco-reference) |
| `data.matchedQuantity` | number | Khối lượng đã khớp | — |
| `data.isPlaceOrder` | boolean | Trạng thái phát sinh lệnh con | `true`: Có lệnh thực phát sinh (xuất hiện lệnh ở Orderbook). `false`: Chưa có lệnh thực phát sinh |
| `data.instrumentID` | string | Mã chứng khoán. Đối với phái sinh, truyền theo mã tổng quát hoặc chi tiết: `1M`, `2M`, `1Q`, `2Q`, `VN30FYYMM` | — |
| `data.quantity` | number | Khối lượng muốn đặt lệnh | — |
| `data.price` | string | Giá đặt (đơn vị đồng) | Giá số (vd: `"23500"`) hoặc `"MP"`, `"MOK"`, `"MTL"` |
| `data.account` | string | Tiểu khoản đặt lệnh (ví dụ tài khoản đuôi 8, đuôi 6) | — |
| `data.updatedTime` | string | Thời gian cập nhật (Unix timestamp milliseconds) | `"1751966448000"` |
| `data.status` | string | Mã trạng thái | Tham chiếu [bảng mã lỗi](/docs/api-reference/appendix/error-codes) |
| `data.message` | string | Thông báo kết quả hoặc lỗi | — |
| `data.username` | string | ID người dùng tại SSI | — |

* * *

## Tham khảo thêm

  * [Kết nối WebSocket](/docs/api-reference/connectWebSocket) — thiết lập kết nối và xác thực
  * [Heartbeat](/docs/api-reference/getHeartbeatStructure) — cơ chế ping/pong giữ kết nối
  * [Sub/Unsub Market Data](/docs/api-reference/subscribeUnsubscribeMarketData) — theo dõi dữ liệu thị trường
  * [Phụ lục FCO](/docs/api-reference/appendix/fco-reference) — chi tiết các loại lệnh điều kiện
  * [Bảng mã lỗi](/docs/api-reference/appendix/error-codes) — tra cứu mã trạng thái và lỗi
