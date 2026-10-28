# SSI FastConnect — WebSocket Data (bản chắt lọc)

> **Phạm vi:** chỉ tập trung vào **dữ liệu realtime qua WebSocket**, bao gồm toàn bộ
> phần xác thực (authentication) và các mô tả liên quan cần thiết để dựng được một
> ingestion service. Các nhóm REST khác (đặt lệnh, truy vấn OHLC, FCO REST...) chỉ
> nhắc đến khi có liên quan trực tiếp.
>
> **Nguồn:** <https://developers.ssi.com.vn/docs> — tải ngày **17/08/2026**.
> Bản nguyên văn đầy đủ nằm ở [`../details/`](../details/) (88 trang).
>
> Mọi khẳng định dưới đây đều truy vết được về file trong `details/`. Chỗ nào tài
> liệu gốc **không nói rõ** hoặc **tự mâu thuẫn**, tôi đánh dấu rõ ở
> [§10 Điểm chưa rõ & mâu thuẫn](#10-điểm-chưa-rõ--mâu-thuẫn-trong-tài-liệu-gốc) —
> đây là những chỗ bắt buộc phải kiểm chứng bằng kết nối thật trước khi code.

---

## Mục lục

1. [Kiến trúc & endpoint](#1-kiến-trúc--endpoint)
2. [Xác thực (bắt buộc đọc trước)](#2-xác-thực-bắt-buộc-đọc-trước)
3. [Khung message WebSocket chung](#3-khung-message-websocket-chung)
4. [Heartbeat & quản lý subscription](#4-heartbeat--quản-lý-subscription)
5. [Kênh DATA — dữ liệu thị trường](#5-kênh-data--dữ-liệu-thị-trường)
6. [Kênh TRADING — sự kiện lệnh & danh mục](#6-kênh-trading--sự-kiện-lệnh--danh-mục)
7. [SDK chính thức (lớp Streaming)](#7-sdk-chính-thức-lớp-streaming)
8. [Vận hành: reconnect, rate limit, giờ giao dịch](#8-vận-hành-reconnect-rate-limit-giờ-giao-dịch)
9. [Mã lỗi liên quan tới stream](#9-mã-lỗi-liên-quan-tới-stream)
10. [Điểm chưa rõ & mâu thuẫn trong tài liệu gốc](#10-điểm-chưa-rõ--mâu-thuẫn-trong-tài-liệu-gốc)
11. [Bảng tra nhanh field viết tắt](#11-bảng-tra-nhanh-field-viết-tắt)

---

## 1. Kiến trúc & endpoint

FastConnect API là nền tảng kết nối giao dịch của SSI, gồm 4 nhóm: **Authentication**,
**Market Data (REST)**, **Trading (REST)**, và **WebSocket Streaming**.

Luồng tích hợp chuẩn cho bài toán thu thập dữ liệu realtime:

```
1. POST /api/v3/auth/token   (apiKey + apiSecret [+ otp])  ──► accessToken
2. Mở WebSocket tới stream endpoint bằng accessToken
3. Gửi SUBSCRIBE cho các topic cần theo dõi
4. Đáp PONG mỗi khi server gửi PING (giữ session)
5. Mất kết nối ──► reconnect ──► SUBSCRIBE LẠI TOÀN BỘ topic
```

| Thành phần | URL |
|---|---|
| REST API | `https://api.ssi.com.vn` |
| **WebSocket** | `wss://stream.ssi.com.vn` |
| Developer Portal | `https://developers.ssi.com.vn` |

> ⚠️ SDK Python khai báo mặc định `streaming_url = "wss://stream.ssi.com.vn/ws/v3"` —
> **khác** với `wss://stream.ssi.com.vn` ghi trong đặc tả API. Xem [§10.1](#101-endpoint-websocket-có-hai-giá-trị-khác-nhau).

Môi trường **UAT** được nhắc tới nhưng *"thông tin môi trường UAT sẽ được thông báo
khi sẵn sàng"* — tức **hiện chưa có sandbox**. Mọi thứ chạy thẳng trên production,
và tài liệu cảnh báo rõ: *"Lệnh giao dịch qua API là lệnh thật"*.

*Nguồn: [`guide/tong_quan_he_thong.md`](../details/guide/tong_quan_he_thong.md),
[`guide/dieu_kien_su_dung_moi_truong.md`](../details/guide/dieu_kien_su_dung_moi_truong.md),
[`api_specifications/websocket/connectWebSocket.md`](../details/api_specifications/websocket/connectWebSocket.md),
[`sdk_document/python/02_configuration.md`](../details/sdk_document/python/02_configuration.md)*

---

## 2. Xác thực (bắt buộc đọc trước)

### 2.1. Nguyên tắc quan trọng nhất

| Loại dữ liệu | Có cần OTP không? |
|---|---|
| **Market data streaming** (kênh `DATA`) | **KHÔNG cần OTP** — token thường là đủ |
| Trading streaming (kênh `TRADING`) | **CẦN OTP** khi lấy token |
| REST market data | Không cần OTP |
| REST đặt/sửa/hủy lệnh | Cần OTP |

→ Với bài toán **thu thập dữ liệu thị trường**, ta chỉ cần luồng token đơn giản
nhất: `apiKey + apiSecret`, không đụng tới OTP/2FA.

> 🔴 **NHƯNG tài liệu tự mâu thuẫn ở đúng điểm này** — trang SDK ghi lớp `Stream`
> (client WebSocket) là *"Cần OTP"*, không phân biệt kênh. Đây là mâu thuẫn **tốn kém
> nhất** trong toàn bộ bộ tài liệu: nếu stream thật sự cần OTP thì một service thu
> thập dữ liệu 24/7 sẽ phải xoay OTP mỗi lần lấy token, tức không thể chạy hoàn toàn
> tự động (trừ khi dùng luồng Mobile Approval). Xem [§10.6](#106-stream-market-data-có-cần-otp-không).

*Nguồn: [`practice/10_websocket_market_data.md`](../details/practice/10_websocket_market_data.md)
("Không cần OTP cho market data"), [`practice/11_websocket_trading.md`](../details/practice/11_websocket_trading.md) ("Cần OTP"),
[`sdk_document/python/03_client_classes.md`](../details/sdk_document/python/03_client_classes.md) ("Stream ... **Cần OTP**").*

### 2.2. Lấy API Key / API Secret

1. Đăng nhập <https://developers.ssi.com.vn> bằng tài khoản SSI.
2. **Bảng điều khiển → Quản lý API Key → Tạo Key mới**, đặt tên rồi **Tạo**.
3. Lưu ngay `apiKey` + `apiSecret`.

> API Secret **chỉ hiển thị một lần** khi tạo; nếu mất thì phải vào chi tiết API Key
> để xem lại.

Điều kiện tiên quyết: có tài khoản giao dịch tại SSI, đã đăng ký FastConnect qua
Developer Portal và **được phê duyệt**.

### 2.3. `POST /api/v3/auth/token` — lấy access token

**Request body** (`application/json`):

| Field | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `apiKey` | string | ✅ | API key do SSI/FastConnect cấp cho ứng dụng |
| `apiSecret` | string | ✅ | API secret tương ứng với `apiKey` |
| `otp` | string \| null | ❌ | Mã OTP (SMS OTP hoặc SmartOTP). **Chỉ cần nếu muốn token có quyền giao dịch.** Chỉ truy vấn dữ liệu thì không cần |
| `transactionId` | string \| null | ❌ | Mã transaction trả về từ `auth/requestOtp` khi tài khoản dùng 2FA SmartOTP + luồng phê duyệt qua app iBoard |

```bash
curl -X POST "https://api.ssi.com.vn/api/v3/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "apiKey": "your_api_key",
    "apiSecret": "your_api_secret"
  }'
```

**Response 200:**

```json
{
  "tokenType": "Bearer",
  "accessToken": "eyJhbGciOiJIUzI1NiIs...",
  "refreshToken": "dGhpcyBpcyBhIHJlZnJl...",
  "expiresAt": 1772075293023,
  "refreshExpiresAt": 1772075293023
}
```

**Response 400:** `{ "code": 400, "msg": "apiKey is required" }`

> ⚠️ Đơn vị của `expiresAt` / `refreshExpiresAt` không nhất quán giữa hai trang tài
> liệu (giây vs mili-giây) — xem [§10.2](#102-đơn-vị-của-expiresat-không-nhất-quán).

**Dùng token cho REST:** header `Authorization: Bearer <accessToken>`.

### 2.4. `POST /api/v3/auth/refresh` — làm mới token

| Field | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `refreshToken` | string | ✅ | Refresh token còn hiệu lực |

Response giống hệt `auth/token` (trả về cặp token mới). Đây là cơ chế duy trì phiên
dài ngày cho một service chạy 24/7 — nên refresh **trước** khi `expiresAt` tới, đừng
đợi nhận lỗi `401004 Access Token Expired`.

### 2.5. `POST /api/v3/auth/requestOtp` — chỉ khi cần quyền giao dịch

Body: `apiKey` + `apiSecret` (đều bắt buộc).

Response 200 có 2 dạng tùy loại 2FA của tài khoản:

```json
{ "message": "Thành công" }
```
```json
{
  "message": "Please approve the login request via the iBoard mobile app.",
  "transactionId": "f306c510-0647-417b-9210-bb5b7e155e77"
}
```

**Ba tình huống 2FA:**

| Tình huống | Loại 2FA | Cách làm |
|---|---|---|
| 1. OTP qua SMS/Email | SMS / Email | Gọi `requestOtp` → nhận mã qua SMS/email → truyền vào `otp` khi gọi `auth/token` |
| 2. SmartOTP thủ công | SmartOTP | **Không cần** gọi `requestOtp`. Mở app iBoard → mục SmartOTP → lấy mã đang hiển thị → truyền vào `otp` |
| 3. Mobile Approval | SmartOTP | Gọi `requestOtp` → nhận `transactionId` → khách bấm **Phê duyệt** trên app iBoard → gọi `auth/token` kèm `transactionId` (không cần `otp`) |

> **`transactionId` chỉ có hiệu lực 30 giây** — phải phê duyệt trên app trong 30s.
>
> Tài liệu khuyến nghị: *"Để tự động hóa ứng dụng mà không phải nhập thủ công OTP mỗi
> ngày, bạn nên triển khai theo luồng Mobile Approval này."* (chỉ áp dụng khi cần
> quyền giao dịch; market data không cần).

### 2.6. Bảo mật credentials

**NÊN:** lưu key trong environment variables / secret manager; luôn HTTPS; rotate key
định kỳ; tạo key riêng cho từng ứng dụng; monitor API usage.

**KHÔNG NÊN:** commit key vào Git; hardcode trong source; share qua email/chat; dùng
key production để test; dùng chung key giữa nhiều ứng dụng.

Tài khoản API có thể bị **tạm khóa** khi: vi phạm điều khoản, phát hiện hoạt động bất
thường, yêu cầu từ UBCKNN, hoặc khách hàng yêu cầu.

*Nguồn: [`guide/cach_lay_api_key_access_token.md`](../details/guide/cach_lay_api_key_access_token.md),
[`api_specifications/authentication/`](../details/api_specifications/authentication/)*

---

## 3. Khung message WebSocket chung

### 3.1. Điều kiện kết nối

* Access token còn hiệu lực.
* Client **duy trì heartbeat** trong suốt phiên kết nối.
* Sau khi reconnect, **phải subscribe lại** các topic cần theo dõi.

### 3.2. Cấu trúc request tổng quát

Mọi message client gửi lên đều theo một khuôn:

```json
{
  "method": "SUBSCRIBE|UNSUBSCRIBE|LIST_SUBSCRIPTION|PING|PONG",
  "channel": "TRADING|DATA|HEARTBEAT",
  "topics": ["trade.SSI@tick", "trade.SSI@1m", "room.*"]
}
```

| Thành phần | Giá trị hợp lệ | Ghi chú |
|---|---|---|
| `method` | `SUBSCRIBE`, `UNSUBSCRIBE`, `LIST_SUBSCRIPTION`, `PING`, `PONG` | `LIST_SUBSCRIPTION` gửi một mình, không cần `channel`/`topics` |
| `channel` | `DATA` (thị trường), `TRADING` (lệnh/danh mục), `HEARTBEAT` (ping-pong) | |
| `topics` | mảng string theo cú pháp từng kênh | có thể nhiều topic trong 1 message |

### 3.3. Thông tin xác thực khi kết nối

Tài liệu mô tả việc lấy token từ `client_id`, `api_key`, `api_secret` qua API auth,
sau đó dùng token để kết nối stream, kèm khối JSON minh họa:

```json
{
  "client_id": "666666",
  "api_key": "<api-key>",
  "api_secret": "<api-secret>",
  "access_token": "<access-token>"
}
```

> ⚠️ Tài liệu **không nói rõ** khối JSON này được gửi như thế nào (frame đầu tiên sau
> khi mở socket? query string? header?). Đây là khoảng trống lớn nhất phải xác minh
> thực tế — xem [§10.3](#103-cách-truyền-token-khi-mở-socket-không-được-đặc-tả).

### 3.4. Danh sách event type

Các `eventType` server có thể đẩy về:

`connect` · `heartbeat` · `orderEvent` · `orderMatchEvent` · `clientPortfolioEvent` ·
`fcoEvent` · `trade` · `quote` · `room` · `put` · `oddlot` · `market`

*Nguồn: [`api_specifications/websocket/connectWebSocket.md`](../details/api_specifications/websocket/connectWebSocket.md)*

---

## 4. Heartbeat & quản lý subscription

### 4.1. Ping/Pong

Server gửi heartbeat định kỳ để xác nhận client còn online. **Client phải phản hồi
đúng định dạng, nếu không session sẽ bị đóng.**

Server → client:
```json
{ "method": "PING", "channel": "HEARTBEAT", "time": "dd-mm-yyyy hh-mm-ss" }
```

Client → server:
```json
{ "method": "PONG", "channel": "HEARTBEAT", "time": "dd-mm-yyyy hh-mm-ss" }
```

> Lưu ý định dạng `time` trong tài liệu là `dd-mm-yyyy hh-mm-ss` (dùng dấu `-` cả cho
> phần giờ), **khác** với định dạng `YYYY/MM/DD HH:mi:ss` của trường `t` trong dữ liệu
> thị trường. Chu kỳ ping của server **không được nêu con số cụ thể**.

SDK có `ping(interval=30)` để client chủ động ping theo chu kỳ giây — tức chiều
client→server cũng được hỗ trợ, không chỉ đáp PONG thụ động.

### 4.2. `LIST_SUBSCRIPTION`

Request:
```json
{ "method": "LIST_SUBSCRIPTION" }
```

Response (scope theo nhóm, chuỗi các topic ngăn bởi `;`):
```json
{
  "trading": "order.0901351;portfolio.0901351",
  "data": "trade.*;quote.*;room.*"
}
```

Dùng để: (a) kiểm tra quyền truy cập thực tế của API key, (b) đối chiếu trạng thái
subscribe sau reconnect.

### 4.3. Quy tắc subscribe/unsubscribe

* Có thể subscribe nhiều topic trong cùng một message.
* **Subscribe trùng không gây lỗi** — server bỏ qua topic đã subscribe.
* **Unsubscribe topic chưa subscribe không gây lỗi** — server bỏ qua.
* Unsubscribe **không** ảnh hưởng các topic khác đang subscribe.
* Sau reconnect **bắt buộc subscribe lại toàn bộ**.

*Nguồn: [`api_specifications/websocket/getHeartbeatStructure.md`](../details/api_specifications/websocket/getHeartbeatStructure.md),
[`api_specifications/websocket/subscribeUnsubscribeTradingData.md`](../details/api_specifications/websocket/subscribeUnsubscribeTradingData.md)*

---

## 5. Kênh DATA — dữ liệu thị trường

### 5.1. Sáu nhóm topic

| Topic | Mô tả |
|---|---|
| `trade` | Thông tin khớp lệnh |
| `quote` | Thông tin bid/ask |
| `room` | Thông tin room ngoại |
| `put` | Khớp lệnh thỏa thuận |
| `oddlot` | Giao dịch lô lẻ |
| `market` | Thông tin đầu ngày và cờ phiên |

### 5.2. Cú pháp topic

```text
trade.[index/exchange/symbol-symbol/*]@[tick/1m/5m]
quote.[index/exchange/symbol-symbol/*]@[tick/1m/5m]
room.[index/exchange/symbol-symbol/*]@[tick/1m/5m]
put.[index/exchange/symbol-symbol/*]@[tick/1m/5m]
oddlot.[index/exchange/symbol-symbol/*]@[tick/1m/5m]
market.[index/exchange/symbol-symbol/*]
```

**Phạm vi (phần sau dấu chấm):**

| Dạng | Ví dụ | Ý nghĩa |
|---|---|---|
| Một mã | `trade.SSI` | Message khớp của riêng mã SSI |
| Nhiều mã | `trade.ACB-SSI-GVR-KDH` | Nhiều mã nối bằng dấu `-` |
| Rổ chỉ số | `trade.vn30` | Toàn bộ mã thuộc rổ VN30 |
| Sàn | `trade.hose` | Toàn bộ mã thuộc sàn HOSE |
| Tất cả | `trade.*` | Toàn bộ mã **trong phạm vi quyền** |

**Interval (phần sau dấu `@`):**

* Giá trị hợp lệ: `tick`, `1m`, `5m`. Tài liệu ghi rõ: *"không có `3m`"*.
* Không truyền `@interval` → mặc định là `tick`.
* Riêng topic `market` **không có interval**.

> ⚠️ Trang Heartbeat lại ghi `trade.<symbol>@tick|1m|3m` — mâu thuẫn, xem
> [§10.4](#104-interval-1m5m-hay-1m3m).

**Ví dụ subscribe:**

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

Cú pháp tương tự cho `quote`, `room`, `put`, `oddlot`, `market` — chỉ đổi tiền tố.

**Unsubscribe:**
```json
{ "method": "UNSUBSCRIBE", "channel": "DATA", "topics": ["trade.SSI", "quote.SSI"] }
```

### 5.3. Payload từng nhóm

> **Đặc điểm chung cần lưu ý khi thiết kế schema:** hầu hết giá trị số đều trả về dưới
> dạng **String**, không phải number. Thời gian là chuỗi `YYYY/MM/DD HH:mi:ss` theo giờ
> Việt Nam, **không có epoch/nanosecond nào từ sàn**.

#### I. Trade — thông tin khớp lệnh

| Field | Name | Type | Mô tả |
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

```json
{ "s": "SSI", "t": "2026/07/29 09:15:32", "p": "45.50", "q": "1000",
  "a": "45.35", "si": "B", "o": "45.00", "h": "45.80", "l": "44.90", "v": "1250000" }
```

> `si` (Buy Up / Sell Down) chính là thông tin **chủ động mua/bán** — dữ liệu quý để
> tính dòng tiền, tương đương `action: BU/SD` của TCBS ouranos.

#### II. Room — room ngoại

| Field | Name | Type | Mô tả |
|---|---|---|---|
| `s` | symbol | String | Mã chứng khoán |
| `t` | tradingtime | String | `YYYY/MM/DD HH:mi:ss` |
| `tr` | totalRoom | String | Tổng room ngoại |
| `cr` | currentRoom | String | Room ngoại còn lại |
| `bq` | buyQuantity | String | Khối lượng mua của khối ngoại |
| `bv` | buyValue | String | Giá trị mua của khối ngoại |
| `sq` | sellQuantity | String | Khối lượng bán của khối ngoại |
| `sv` | sellValue | String | Giá trị bán của khối ngoại |

```json
{ "s": "SSI", "t": "2026/07/29 09:15:32", "tr": "1500000", "cr": "980000",
  "bq": "5000", "bv": "227500000", "sq": "3000", "sv": "136500000" }
```

#### III. Quote — bid/ask

| Field | Type | Mô tả |
|---|---|---|
| `s` | String | Mã chứng khoán |
| `t` | String | tradingtime, `YYYY/MM/DD HH:mi:ss` |
| `bids` | `List<String[2]>` | Danh sách mức giá mua `[price, quantity]` |
| `asks` | `List<String[2]>` | Danh sách mức giá bán `[price, quantity]` |

```json
{
  "s": "SSI", "t": "2026/07/29 09:15:32",
  "bids": [["45.45","3200"], ["45.40","1500"], ["45.35","4200"], ["45.30","2100"], ["45.25","3300"]],
  "asks": [["45.50","2800"], ["45.55","1900"], ["45.60","3600"], ["45.65","2200"], ["45.70","4100"]]
}
```

> 🔴 **Cảnh báo thiết kế:** tài liệu ghi *"Bản nâng cấp sau sẽ chỉ trả ra các giá trị
> thay đổi"* cho cả `bids` và `asks`. Nghĩa là hôm nay là **snapshot đầy đủ**, tương
> lai có thể chuyển sang **delta**. Nếu lưu thô byte-for-byte thì không sao; nhưng
> logic dựng sổ lệnh phải tách riêng và chuẩn bị cho cả hai chế độ.
>
> Mẫu cho thấy 5 mức giá, nhưng tài liệu **không cam kết số mức** (`List` độ dài tự do).

#### IV. Put — khớp lệnh thỏa thuận

| Field | Name | Type | Mô tả |
|---|---|---|---|
| `s` | symbol | String | Mã chứng khoán |
| `t` | tradingtime | String | `YYYY/MM/DD HH:mi:ss` |
| `p` | price | String | Giá khớp thỏa thuận |
| `q` | quantity | String | Khối lượng khớp thỏa thuận |
| `tq` | TotalQuantity | String | Tổng khối lượng thỏa thuận trong ngày |
| `tv` | TotalValue | String | Tổng giá trị thỏa thuận trong ngày |

#### V. Oddlot — giao dịch lô lẻ

| Field | Name | Type | Mô tả |
|---|---|---|---|
| `s` | symbol | String | Mã chứng khoán |
| `t` | tradingtime | String | `YYYY/MM/DD HH:mi:ss` |
| `p` | price | String | Giá khớp lô lẻ |
| `q` | quantity | String | Khối lượng khớp lô lẻ |
| `bids` | `List<String[2]>` | Mức giá mua lô lẻ `[price, quantity]` |
| `asks` | `List<String[2]>` | Mức giá bán lô lẻ `[price, quantity]` |

#### VI. Market — thông tin đầu ngày & cờ phiên

Topic `market` trả về **hai loại message khác cấu trúc nhau**:

**(a) Market streaming data** — giá trần/sàn/tham chiếu đầu ngày:

| Field | Name | Type | Mô tả |
|---|---|---|---|
| `s` | symbol | String | Mã chứng khoán |
| `b` | board | String | `HOSE`, `HNX`, `UPCOM` |
| `t` | tradingDate | String | `YYYY/MM/DD` |
| `ce` | ceilingPrice | String | Giá trần |
| `fl` | floorPrice | String | Giá sàn |
| `ref` | refPrice | String | Giá tham chiếu |

**(b) Market flag** — cờ phiên:

| Field | Name | Type | Mô tả |
|---|---|---|---|
| `b` | board | String | `HOSE`, `HNX`, `UPCOM`, `DERIVATIVES` |
| `t` | tradingTime | String | `YYYY/MM/DD HH:mm:ss` |
| `f` | flag | String | Cờ phiên: `ATO`, `LO`, `ATC`, v.v. |

```json
{ "b": "HOSE", "t": "2026/07/29 09:00:00", "f": "ATO" }
```

> Phân biệt hai loại bằng sự có mặt của `s`/`ce`/`fl`/`ref` (loại a) hay `f` (loại b).
> Chỉ có message loại (b) mới có giá trị `DERIVATIVES` ở trường `b`.

*Nguồn: [`api_specifications/websocket/subscribeUnsubscribeMarketData.md`](../details/api_specifications/websocket/subscribeUnsubscribeMarketData.md)*

---

## 6. Kênh TRADING — sự kiện lệnh & danh mục

Không thuộc "market data" nhưng cần cho một hệ thống trading hoàn chỉnh — tóm tắt gọn.

### 6.1. Topic

```text
order.[accountNo/*]
portfolio.[accountNo-accountNo/*]
```

| Topic | Mô tả |
|---|---|
| `order.<accountNo>` | Sự kiện lệnh (đặt/sửa/hủy/khớp) **và lệnh điều kiện FCO** của 1 tài khoản |
| `order.<acc1>-<acc2>` | Sự kiện lệnh của nhiều tài khoản |
| `order.*` | Tất cả tài khoản trong phạm vi quyền |
| `portfolio.<accountNo>` | Cập nhật danh mục (tài sản, vị thế) |
| `portfolio.*` | Danh mục của tất cả tài khoản trong phạm vi quyền |

> * Sự kiện **FCO đi chung kênh `order`** — không cần subscribe topic riêng.
> * `portfolio` hiện **chỉ hỗ trợ tài khoản đuôi 8 (phái sinh)**. Tài khoản cơ sở
>   (đuôi 1) và ký quỹ (đuôi 6) **chưa được hỗ trợ**.

### 6.2. Bốn loại event

Tất cả đều có `notifyId` (**Long, số serial của event message**) và `connectionId`.

> 💡 `notifyId` là serial tăng dần — **dùng để phát hiện mất message** sau reconnect.
> Đây là thứ mà kênh `DATA` **không có** (xem [§10.5](#105-kênh-data-không-có-sequence-number)).

| Event | `eventType` | Sinh ra khi |
|---|---|---|
| Order Event | `orderEvent` | Lệnh được đặt/sửa/hủy hoặc đổi trạng thái |
| Order Match Event | `orderMatchEvent` | Lệnh khớp (một phần hoặc toàn bộ) |
| Client Portfolio Event | `clientPortfolioEvent` | Số dư/tài sản thay đổi |
| FCO Event | `fcoEvent` | Lệnh điều kiện đổi trạng thái |

**Order Event** — các trường chính: `orderId`, `clientRequestId`, `symbol`, `side`
(`B`/`S`), `orderType` (`LO`/`ATO`/`ATC`...), `accountNo`, `price`, `quantity`,
`cancelQty`, `osQty` (chưa khớp), `filledQty`, `inputTime`, `modifiedTime`,
`orderStatus`, `rejectReason`, `errorCode`, `errorMessage`.

**Order Match Event** — `orderId`, `clientRequestId`, `symbol`, `side`, `accountNo`,
`matchPrice`, `matchQty`, `matchTime`.

**Client Portfolio Event** — `symbol`, `accountNo`, `longQty`, `shortQty`, `net`
(= long − short), `bidAvgPrice`, `askAvgPrice`, `tradePrice`, `marketPrice`,
`floatingPL` (lãi/lỗ tạm tính), `tradingPL` (lãi/lỗ đã chốt).

**FCO Event** — ⚠️ **cấu trúc khác hẳn 3 event trên**: bọc trong `{ "type": "fcoEvent",
"data": { ... } }` thay vì phẳng với khóa `eventType`:

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

Chú ý các khác biệt dễ gây bug khi parse: `type` (không phải `eventType`), `notifyID`
(chữ D hoa, không phải `notifyId`), `account` (không phải `accountNo`), `instrumentID`
(không phải `symbol`), và `updatedTime` là **Unix timestamp mili-giây dạng string** —
loại event duy nhất dùng epoch thay vì chuỗi ngày giờ.

*Nguồn: [`api_specifications/websocket/subscribeUnsubscribeTradingData.md`](../details/api_specifications/websocket/subscribeUnsubscribeTradingData.md)*

---

## 7. SDK chính thức (lớp Streaming)

SSI cung cấp SDK cho **Node.js, Python, C#, Go** (Java mới chỉ có trang trống). Dưới
đây là API của Python SDK — các SDK khác cùng cấu trúc.

### 7.1. Cấu hình

```python
from ssi_sdk import Config

config = Config(
    client_id="YOUR_CLIENT_ID",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
    private_key="YOUR_PRIVATE_KEY",   # dùng để ký lệnh giao dịch
)
```

| Tham số | Mặc định | Ghi chú |
|---|---|---|
| `api_url` | `https://api.ssi.com.vn` | REST |
| `streaming_url` | `wss://stream.ssi.com.vn/ws/v3` | **khác đặc tả API** |
| `timeout` | `60` | giây |
| `max_retries` | `5` | |
| `retry_delay` | `2.0` | exponential backoff, giây |
| `rate_limit_per_second` | `10` | 0 = không giới hạn |
| `proxy` | `None` | |
| `log_level` | `INFO` | |

### 7.2. Vòng đời & callback

```python
from ssi_sdk import Auth, Stream, Config

with Auth(config) as auth:
    ensure_auth(auth)                       # market data: KHÔNG cần OTP
    with Stream(auth) as stream:
        stream.streaming.connect()
        stream.streaming.on_data = on_market_data      # kênh DATA
        stream.streaming.on_trading = on_trading_event # kênh TRADING
        stream.streaming.on_heartbeat = on_heartbeat
        stream.streaming.subscribe_symbol(["SSI", "HPG", "VNM"])
        stream.streaming.subscribe_index(["VNINDEX", "HNX-INDEX"])
        stream.streaming.wait(timeout=300)
```

Bản async dùng `AsyncAuth` / `AsyncStream`, mọi lệnh `await`.

### 7.3. Toàn bộ method Streaming

| Nhóm | Method |
|---|---|
| Kết nối | `connect()`, `disconnect()`, `wait(timeout=None)` |
| Heartbeat | `ping(on_response=None, interval=None)` |
| Subscribe mã | `subscribe_symbol(symbols)` (= trade + quote + room), `subscribe_symbol_trade`, `subscribe_symbol_quote`, `subscribe_symbol_room`, `subscribe_symbol_put_through`, `subscribe_symbol_odd_lot` |
| OHLCV | `subscribe_symbol_ohlcv(symbols, interval=Timeframe.MINUTE_1)` |
| Theo sàn/chỉ số | `subscribe_board([Board.HOSE, Board.HNX])`, `subscribe_index(["VNINDEX", "VN30"])` |
| Giao dịch | `subscribe_order_status(account_no=None)`, `subscribe_portfolio(account_no=None)` |
| Hủy | `unsubscribe_*` tương ứng từng method trên |

### 7.4. Ánh xạ topic → kiểu message

Nhận qua `on_data`:

| Topic | Message type |
|---|---|
| `trade.*` | `TradeMessage` — `type`, `trading_time`, `symbol`, `price`, `quantity`, `side`, `total_volume` |
| `trade.*.<timeframe>` | `IntervalMessage` — `interval_time`, `trading_time`, `symbol`, `open`, `high`, `low`, `close`, `volume` |
| `quote.*` | `QuoteMessage` — `bid_prices`, `bid_volumes`, `ask_prices`, `ask_volumes` |
| `room.*` | `ForeignRoomMessage` — `total_room`, `current_room`, `buy_quantity`, `buy_value`, `sell_quantity`, `sell_value` |
| `market.*` | `MarketStatusMessage` — `market`, `status`, `trading_date` |
| `put.*` | `PutMessage` — `price`, `quantity`, `total_quantity`, `total_value` |
| `oddlot.*` | `OddLotMessage` — `price`, `quantity`, `bid_prices`, `bid_volumes`, `ask_prices`, `ask_volumes` |

Nhận qua `on_trading`:

| Topic | Message type |
|---|---|
| `order.*` | `OrderStatusMessage` |
| `order.*` (khi `event_type == "fcoEvent"`) | `FCOOrderUpdateMessage` |
| `portfolio.*` | `PortfolioMessage` — `account_no`, `total_asset`, `cash_balance`, `stock_value` |

`HeartbeatMessage`: `method`, `channel`, `status`, `message`.

> ⚠️ SDK **tách `bid_prices` / `bid_volumes` thành 2 mảng riêng**, trong khi wire
> protocol trả `bids` là mảng cặp `[price, quantity]`. Nếu tự viết client thì theo wire
> protocol; nếu đọc code mẫu SDK thì nhớ nó đã biến đổi dữ liệu.
>
> SDK có `Timeframe.MINUTE_3 = "3m"` — lại một dấu hỏi nữa về interval `3m`.

**Lỗi thường gặp:** `AuthenticationError` (xác thực), `WebSocketError` (stream),
`APIError` (HTTP lỗi nghiệp vụ).

*Nguồn: [`sdk_document/python/`](../details/sdk_document/python/),
[`practice/10_websocket_market_data.md`](../details/practice/10_websocket_market_data.md),
[`practice/11_websocket_trading.md`](../details/practice/11_websocket_trading.md)*

---

## 8. Vận hành: reconnect, rate limit, giờ giao dịch

### 8.1. Reconnect

* Tài liệu khuyến nghị rõ: *"Với WebSocket, luôn triển khai cơ chế reconnect và
  subscribe lại topic."*
* SDK *"tự xử lý reconnect khi mất kết nối"* — nhưng nếu tự viết client thì phải tự
  làm, kèm backoff.
* **Không có cơ chế replay/resume**: tài liệu không nhắc tới việc lấy lại message bị
  mất trong lúc rớt kết nối. Dữ liệu mất trong khoảng đứt là mất vĩnh viễn với kênh
  `DATA`.

### 8.2. Rate limit

Áp dụng cho **từng API Key**, trả về qua response header (REST):

| Header | Mô tả |
|---|---|
| `X-RATELIMIT-LIMIT` | Số request tối đa trong chu kỳ |
| `X-RATELIMIT-REMAINING` | Số request còn lại |
| `X-RATELIMIT-RESET` | Thời điểm reset |

Vượt hạn mức → HTTP `429 Too Many Requests`; phải đợi tới `X-RATELIMIT-RESET`.
Tài liệu **không công bố con số cụ thể**, cũng **không nói rate limit áp cho WebSocket**
(số kết nối đồng thời, số topic tối đa mỗi subscribe...).

### 8.3. Giờ giao dịch

**Cổ phiếu (HOSE/HNX):**

| Phiên | Giờ | Loại lệnh |
|---|---|---|
| ATO | 09:00 – 09:15 | ATO, LO |
| Liên tục sáng | 09:15 – 11:30 | LO, MP |
| Nghỉ trưa | 11:30 – 13:00 | Không giao dịch |
| Liên tục chiều | 13:00 – 14:30 | LO, MP |
| ATC | 14:30 – 14:45 | ATC, LO |

**Phái sinh:** ATO 08:45–09:00; liên tục 09:00–11:30 và 13:00–14:30; ATC 14:30–14:45.

> **API Market Data và WebSocket hoạt động 24/7.** Ngoài giờ giao dịch dữ liệu giá
> không cập nhật nhưng vẫn truy vấn được lịch sử. → Cảnh báo "feed stale" phải tính
> theo lịch phiên, không thể báo động cả ngày.

### 8.4. Giới hạn dữ liệu lịch sử (REST, để đối chiếu)

| Loại | Phạm vi |
|---|---|
| OHLCV daily | Từ ngày mã bắt đầu giao dịch |
| OHLCV intraday (1m, 5m, 15m, 30m, 1h) | **1 năm gần nhất** |
| File CSV | Link có hiệu lực 30 phút |

→ Muốn có tick/intraday quá 1 năm thì **bắt buộc phải tự lưu từ stream**.

---

## 9. Mã lỗi liên quan tới stream

Trích từ [`api_specifications/appendix/tra_cuu_ma_loi_errcode.md`](../details/api_specifications/appendix/tra_cuu_ma_loi_errcode.md):

**Token (401xxx):**

| Code | Ý nghĩa | Xử lý |
|---|---|---|
| `401000` | Missing Authorization Header | Thiếu header |
| `401002` | Access Token Missing | |
| `401003` | Access Token Invalid | Lấy token mới |
| `401004` | Access Token Expired | **Refresh token** |
| `401009` | Access Token Not Yet Valid | Lệch đồng hồ (claim `nbf`) — kiểm tra NTP |
| `401016` | Token Not Include OTP | Token không có quyền giao dịch → cần OTP |

**Refresh & OTP (4011xx):**

| Code | Ý nghĩa |
|---|---|
| `401100` | OTP Verification Failed |
| `401101` | Invalid Refresh Token |
| `401103` | Refresh Token Revoked or Expired → phải đăng nhập lại từ đầu |
| `401105` | Invalid API Key or Secret |
| `401114` | Push-approval is pending — SmartOTP đang chờ duyệt trên app; SDK tự poll lại, client tự viết thì **phải tự retry sau vài giây** |

**Quyền (403xxx):**

| Code | Ý nghĩa |
|---|---|
| `403001` | Insufficient Scope — token/API key không đủ quyền |
| `403100` | No Scopes Granted — API key chưa được cấp scope nào |

> `403100` là lỗi hay gặp với key mới tạo nhưng chưa được duyệt scope market data.
> Kiểm tra nhanh bằng `LIST_SUBSCRIPTION` — nếu `data` rỗng thì key chưa có quyền.

---

## 10. Điểm chưa rõ & mâu thuẫn trong tài liệu gốc

Đây là danh sách việc **bắt buộc xác minh bằng kết nối thật** trước khi thiết kế
schema hoặc chốt kiến trúc.

### 10.1. Endpoint WebSocket có hai giá trị khác nhau

| Nguồn | Giá trị |
|---|---|
| `connectWebSocket`, `terms-and-environments` | `wss://stream.ssi.com.vn` |
| SDK Config (Python/Node/Go/C#) | `wss://stream.ssi.com.vn/ws/v3` |

→ Nhiều khả năng `/ws/v3` là path thật; phải thử cả hai.

### 10.2. Đơn vị của `expiresAt` không nhất quán

| Nguồn | Mẫu | Suy ra |
|---|---|---|
| `guide/cach_lay_api_key_access_token.md` | `1779806203` (10 chữ số) | **giây** |
| `api_specifications/authentication/auth-token.md` | `1772075293023` (13 chữ số) | **mili-giây** |

→ Không được hardcode; hãy phát hiện theo độ dài số hoặc so với `time.time()`.

### 10.3. Cách truyền token khi mở socket không được đặc tả

Tài liệu chỉ đưa khối JSON `{client_id, api_key, api_secret, access_token}` mà không
nói gửi ở đâu: frame đầu tiên? query param? header `Authorization`? Cũng không mô tả
message phản hồi khi xác thực thành công/thất bại (chỉ liệt kê có event `connect`).

→ **Đây là khoảng trống lớn nhất.** Cách nhanh nhất để giải: đọc source SDK Python
(`ssi_sdk`) hoặc bắt gói khi chạy sample.

### 10.4. Interval: `1m/5m` hay `1m/3m`?

| Nguồn | Giá trị |
|---|---|
| `subscribeUnsubscribeMarketData` | `tick`, `1m`, `5m` — ghi rõ *"không có 3m"* |
| `getHeartbeatStructure` | `trade.<symbol>@tick\|1m\|3m` |
| SDK `Timeframe` enum | có cả `1m`, `3m`, `5m`, `15m`, `1h`, `1d`, `1w`, `1M` |

→ Trang market data mới hơn và cụ thể hơn nên đáng tin hơn, nhưng `Timeframe` của SDK
lại dùng chung cho cả REST OHLC. Phải thử từng giá trị.

### 10.5. Kênh DATA không có sequence number

Kênh `TRADING` có `notifyId` (serial) để phát hiện mất message; kênh `DATA` **không có
gì tương đương** — không seq, không epoch từ sàn, chỉ có `t` dạng chuỗi giây.

**Hệ quả trực tiếp cho thiết kế:**
* Không thể phát hiện mất message trong lúc rớt kết nối.
* Không thể khử trùng lặp theo ID của sàn → phải tự sinh identity (ví dụ
  `(topic, partition, offset)` của Kafka như pipeline trong `examples/`).
* Độ phân giải thời gian của sàn chỉ tới **giây** → nhiều tick cùng giây là chuyện
  bình thường, tuyệt đối không dùng `t` làm khóa.
* Phải tự đóng dấu `recv_ts_ns` tại thời điểm nhận, giống cách `examples/` đang làm.

### 10.6. Stream market data có cần OTP không?

| Nguồn | Khẳng định |
|---|---|
| `practice/10_websocket_market_data.md` | *"Nhận tick data real-time ... **Không cần OTP** cho market data"* — code mẫu gọi `ensure_auth(auth)` không tham số |
| `practice/11_websocket_trading.md` | *"**Cần OTP** khi authenticate"* — code mẫu gọi `ensure_auth(auth, otp="<your_otp>")` |
| `sdk_document/*/03_client_classes.md` | *"`Stream` — Client streaming realtime qua WebSocket. **Cần OTP**."* — không phân biệt kênh |
| `api_specifications/authentication/auth-token.md` | `otp` là *optional*, *"Trường hợp chỉ sử dụng để truy vấn dữ liệu (data, query trading) thì không cần truyền OTP"* |

**Đánh giá:** 2/4 nguồn nói không cần, và trang đặc tả API (nguồn đáng tin nhất) nói
`otp` chỉ cần khi muốn **quyền giao dịch**. Nhiều khả năng dòng "Cần OTP" ở trang SDK
là mô tả chung cho lớp `Stream` vì snippet của nó có gọi `subscribe_order_status()`
(kênh TRADING). Nhưng **phải thử thật**: nếu sai, toàn bộ mô hình vận hành tự động
của service thu thập dữ liệu sẽ thay đổi.

### 10.7. Những thứ hoàn toàn không được nêu

* Chu kỳ PING của server (bao nhiêu giây), timeout nếu không PONG.
* Số kết nối WebSocket đồng thời tối đa cho một API key.
* Số topic tối đa mỗi message SUBSCRIBE, và tổng số topic tối đa.
* Có giới hạn kích thước message không.
* Hành vi khi subscribe mã không tồn tại / không có quyền (báo lỗi hay im lặng).
* Message báo lỗi của kênh WebSocket trông như thế nào (bảng mã lỗi chỉ dành cho REST).
* Có hỗ trợ nén (permessage-deflate) không.
* `market.*` có bao gồm phái sinh không (chỉ thấy `DERIVATIVES` ở message cờ phiên).

---

## 11. Bảng tra nhanh field viết tắt

Kênh `DATA` dùng tên trường rút gọn. Bảng gộp toàn bộ:

| Mã | Tên đầy đủ | Xuất hiện ở |
|---|---|---|
| `s` | symbol | trade, quote, room, put, oddlot, market(a) |
| `t` | tradingTime / tradingDate | tất cả |
| `p` | price | trade, put, oddlot |
| `q` | quantity | trade, put, oddlot |
| `a` | avgPrice | trade |
| `si` | side (`B` = Buy Up, `S` = Sell Down) | trade |
| `o` | openPrice | trade |
| `h` | highPrice | trade |
| `l` | lowPrice | trade |
| `v` | totalVol | trade |
| `bids` | mảng `[price, quantity]` bên mua | quote, oddlot |
| `asks` | mảng `[price, quantity]` bên bán | quote, oddlot |
| `tr` | totalRoom | room |
| `cr` | currentRoom | room |
| `bq` / `bv` | buyQuantity / buyValue (khối ngoại) | room |
| `sq` / `sv` | sellQuantity / sellValue (khối ngoại) | room |
| `tq` / `tv` | TotalQuantity / TotalValue (thỏa thuận) | put |
| `b` | board (`HOSE`/`HNX`/`UPCOM`/`DERIVATIVES`) | market |
| `ce` | ceilingPrice — giá trần | market(a) |
| `fl` | floorPrice — giá sàn | market(a) |
| `ref` | refPrice — giá tham chiếu | market(a) |
| `f` | flag — cờ phiên (`ATO`, `LO`, `ATC`...) | market(b) |

---

## Phụ lục: đối chiếu với code mẫu trong `examples/ssi-data`

Project cũ trong [`examples/ssi-data/`](../../../examples/ssi-data/) subscribe 16 topic
bằng raw WebSocket qua SDK:

```
trade.*@tick|1m|5m, quote.*@tick|1m|5m, room.*@tick|1m|5m,
put.*@tick|1m|5m, oddlot.*@tick|1m|5m, market.*
```

Đối chiếu với tài liệu hiện tại thì cách đó **khớp** với đặc tả (`*` + interval
`tick/1m/5m`, `market` không interval), và nó lấy Kafka key bằng `data["s"]` hoặc
`data["market"]` — đúng với bảng field ở §11. Điểm cần sửa nếu tái sử dụng: nó gọi
`asyncio.create_task(publish(...))` trong callback đồng bộ nên **phá vỡ thứ tự
per-symbol**; và nó chọc vào private API `stream.streaming._ws` thay vì dùng
`on_data` như tài liệu SDK hướng dẫn.
