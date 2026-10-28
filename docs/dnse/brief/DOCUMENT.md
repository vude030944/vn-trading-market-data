# DNSE LightSpeed API — WebSocket Data (bản chắt lọc)

> **Phạm vi:** chỉ tập trung vào **dữ liệu realtime qua WebSocket**, bao gồm toàn bộ
> phần xác thực (authentication) và các mô tả liên quan cần thiết để dựng một
> ingestion service. REST API chỉ nhắc tới khi liên quan trực tiếp (lấy `accountNo`,
> `investorId`, bù dữ liệu bị bỏ lỡ, rate limit).
>
> **Nguồn:** <https://developers.dnse.com.vn/docs> — tải ngày **18/08/2026**.
> Bản nguyên văn đầy đủ nằm ở [`../details/`](../details/).
>
> **Nhận xét chung:** tài liệu WebSocket của DNSE **rõ ràng và đầy đủ hơn SSI rất
> nhiều** — có hẳn một trang đặc tả protocol để tự viết client
> ([`sdk_document/build_websocket.md`](../details/sdk_document/build_websocket.md)),
> nêu rõ thuật toán ký, cửa sổ thời gian, close code, và cơ chế reconnect. Những chỗ
> còn thiếu/mâu thuẫn được ghi ở [§11](#11-điểm-chưa-rõ--mâu-thuẫn-trong-tài-liệu-gốc).

---

## Mục lục

1. [Kiến trúc & endpoint](#1-kiến-trúc--endpoint)
2. [Ba loại WebSocket của DNSE](#2-ba-loại-websocket-của-dnse)
3. [Xác thực](#3-xác-thực)
4. [Protocol WebSocket — 6 bước](#4-protocol-websocket--6-bước)
5. [Keepalive, vòng đời 8 giờ & reconnect](#5-keepalive-vòng-đời-8-giờ--reconnect)
6. [Market Data — toàn bộ channel & payload](#6-market-data--toàn-bộ-channel--payload)
7. [Trading Data & Broker WebSocket](#7-trading-data--broker-websocket)
8. [Enums](#8-enums)
9. [Giới hạn & rate limit](#9-giới-hạn--rate-limit)
10. [Mã lỗi liên quan tới stream](#10-mã-lỗi-liên-quan-tới-stream)
11. [Điểm chưa rõ & mâu thuẫn trong tài liệu gốc](#11-điểm-chưa-rõ--mâu-thuẫn-trong-tài-liệu-gốc)
12. [Đối chiếu nhanh DNSE vs SSI](#12-đối-chiếu-nhanh-dnse-vs-ssi)

---

## 1. Kiến trúc & endpoint

DNSE gọi bộ API của họ là **LightSpeed API** (thương hiệu cũ: OpenAPI).

| Thành phần | URL |
|---|---|
| REST API | `https://openapi.dnse.com.vn` |
| **WebSocket** | `wss://ws-openapi.dnse.com.vn` |
| Endpoint stream đầy đủ | `wss://ws-openapi.dnse.com.vn/v1/stream?encoding={json\|msgpack}` |
| Developer Portal | `https://developers.dnse.com.vn` |
| Trang đăng ký / quản lý key | `https://entradex.dnse.com.vn` (Entrade X) |
| SDK & code samples | <https://github.com/dnse-tech/openapi-sdk> |

Luồng chuẩn:

```
1. Đăng ký LightSpeed API trên Entrade X   ──►  API Key + API Secret
2. Mở WebSocket  wss://ws-openapi.dnse.com.vn/v1/stream?encoding=json
3. Nhận welcome  { action: "welcome", session_id, ... }
4. Gửi auth      HMAC-SHA256("{api_key}:{timestamp}:{nonce}", key=api_secret)
5. Nhận auth_success  ──► mới được phép subscribe
6. Gửi subscribe { action: "subscribe", channels: [{name, symbols}] }
7. Đọc data + đáp pong cho mỗi ping
8. Sau 8 giờ (hoặc khi đứt) ──► reconnect, auth lại với nonce MỚI, subscribe lại
```

### Chọn encoding

| Encoding | Đặc điểm | Frame WebSocket |
|---|---|---|
| `json` | Phổ biến, dễ đọc khi phát triển/debug | **text frame** UTF-8 |
| `msgpack` | Nhanh hơn, tiết kiệm băng thông — khuyến nghị cho production | **binary frame** |

`encoding` xuất hiện ở **hai chỗ** và phải nhất quán: query param của URL kết nối
**và** hậu tố trong tên channel (ví dụ `tick.G1.msgpack`).

> Mọi mã chứng khoán truyền lên phải **CHỮ IN HOA**: `ACB`, `HPG`, `41I1G2000`.

*Nguồn: [`sdk_document/build_websocket.md`](../details/sdk_document/build_websocket.md),
[`guide/market-data/connect.md`](../details/guide/market-data/connect.md),
[`guide/intro/api_platform.md`](../details/guide/intro/api_platform.md)*

---

## 2. Ba loại WebSocket của DNSE

Cùng một base URL và cùng protocol, khác nhau ở **tên channel**:

| Loại | Dùng cho | Channel |
|---|---|---|
| **Market Data** | Dữ liệu thị trường (tick, quote, OHLC, index, foreign...) | `tick.*`, `top_price.*`, `ohlc.*`, `market_index.*`, ... |
| **Trading Data** | Lệnh & vị thế của **chính tài khoản mình** | `order.{market_type}.{encoding}`, `position.{market_type}.{encoding}` |
| **Broker** | Lệnh & vị thế của **khách hàng do môi giới quản lý** | `order.broker.{market_type}.{investor_id}.{encoding}`, `position.broker.…` |

Với bài toán thu thập dữ liệu thị trường, ta chỉ cần **Market Data**.

---

## 3. Xác thực

### 3.1. Lấy API Key / API Secret

1. Đăng nhập <https://entradex.dnse.com.vn> → **Thông tin tài khoản** → **LightSpeed API** → **Đăng ký**.
2. Chọn **duy nhất một** phương thức 2FA: **Smart OTP** hoặc **Email OTP**.
3. Xác nhận + xác thực OTP → hệ thống hiển thị **API Key** và **API Secret**.

Điều kiện: có tài khoản chứng khoán DNSE trạng thái **ACTIVE**.

> * **API Secret chỉ hiển thị MỘT LẦN duy nhất.** Mất thì phải **Tạo lại API Key** —
>   bộ khóa cũ **vô hiệu ngay lập tức**.
> * **Tạo lại API Key** ≠ **Hủy API Key**: "Hủy" là hủy toàn bộ dịch vụ OpenAPI, muốn
>   dùng lại phải đăng ký mới từ đầu.
> * Tạo lại API Key **không** ảnh hưởng phương thức OTP đang dùng.

### 3.2. Xác thực WebSocket (HMAC-SHA256) — cái ta cần

Đây là cơ chế **riêng của WebSocket**, khác hoàn toàn với chữ ký REST ở §3.3.

**Công thức:**

```text
message   = "{api_key}:{timestamp}:{nonce}"
signature = HMAC-SHA256(key=api_secret, msg=message).hexdigest()
```

| Trường | Kiểu | Mô tả |
|---|---|---|
| `api_key` | string | API Key của bạn |
| `timestamp` | integer | Unix timestamp tính bằng **giây** |
| `nonce` | string | Unix timestamp tính bằng **microseconds** — đảm bảo unique mỗi request |
| `api_secret` | string | Dùng làm **HMAC key** — **không** đưa vào message |

**Ràng buộc bắt buộc:**

* `timestamp` phải nằm trong **±5 phút** so với giờ server, nếu không auth bị từ chối
  (`timestamp outside valid window`) → **đồng hồ client phải đồng bộ NTP**.
* `nonce` **không được tái sử dụng trong vòng 10 phút** (server lưu để chống replay).
  Mỗi lần auth — **kể cả khi reconnect** — phải sinh `nonce` mới.
* Phải auth thành công **trong 30 giây** kể từ khi kết nối.

**Auth request:**

```json
{
  "action": "auth",
  "api_key": "your_api_key",
  "signature": "a3f9c2d1e8b74...",
  "timestamp": 1750000000,
  "nonce": "1750000000123456"
}
```

**Auth response — thành công:**

```json
{
  "action": "auth_success",
  "user_id": "your_api_key",
  "capabilities": { "batch_delivery": false },
  "rate_limit": { "messages_per_second": 100, "subscriptions_max": 100 }
}
```

> 💡 `rate_limit` trong `auth_success` là **nguồn duy nhất** cho biết giới hạn của
> WebSocket: `messages_per_second: 100`, `subscriptions_max: 100`. Nên **đọc và log
> lại giá trị này** thay vì hardcode, vì nó theo tier của từng key.

**Auth response — thất bại:** server trả control message `error` (**không có** action
`auth_error`) rồi **đóng kết nối**:

```json
{ "action": "error", "code": "AUTH_FAILED", "message": "authentication failed: invalid signature" }
```

| `code` | Nguyên nhân |
|---|---|
| `AUTH_FAILED` | Sai signature, sai `api_key`, `nonce` đã dùng, hoặc `timestamp` ngoài cửa sổ |
| `AUTH_TIMEOUT` | Không auth thành công trong 30 giây |
| `MAX_CONNECTIONS_EXCEEDED` | Vượt số kết nối tối đa của tier |

**Ví dụ Python (nguyên văn tài liệu):**

```python
import hmac, hashlib, time

api_key    = "your_api_key"
api_secret = "your_api_secret"

timestamp = int(time.time())                  # giây, integer
nonce     = str(int(time.time() * 1_000_000)) # microseconds, string
message   = f"{api_key}:{timestamp}:{nonce}"

signature = hmac.new(
    api_secret.encode("utf-8"),
    message.encode("utf-8"),
    hashlib.sha256
).hexdigest()
```

### 3.3. Xác thực REST (HTTP Signature) — để đối chiếu

Mọi REST API bắt buộc 3 header: `x-api-key`, `x-Signature`, `Date` (header `version`
là tùy chọn nhưng nên truyền tường minh).

**Signing string** (mỗi dòng kết thúc `\n`, trừ dòng cuối):

```text
(request-target): get /accounts
date: Fri, 15 May 2026 07:11:30 +0000
nonce: c9a8f88b472c9721fde161e0d89df8cc
```

* Method viết **thường** (`get`, `post`), tên field (`date`, `nonce`) viết **thường**.
* `nonce` = **UUID4 hex 32 ký tự, không dấu gạch ngang**, sinh mới mỗi request.
* `Date` theo **RFC1123 UTC**, lệch tối đa **±1 phút** (khác WS: ±5 phút).

**Ký:** HMAC-SHA256(API Secret, signing string) → **Base64** → **URL-encode chỉ 3 ký
tự** `+`→`%2B`, `/`→`%2F`, `=`→`%3D` (không double-encode).

**Header:**

```text
Signature keyId="{API_KEY}",algorithm="hmac-sha256",headers="(request-target) date",signature="{ENCODED_SIGNATURE}",nonce="{NONCE}"
```

Lỗi sai chữ ký: `{"status":"error","code":"OA-400","message":"Authorization field missing, malformed or invalid"}`

### 3.4. Trading Token (2FA) — KHÔNG cần cho market data

Trading Token là lớp bảo mật thứ 2, **chỉ bắt buộc cho Đặt/Sửa/Hủy lệnh và Đóng vị
thế**. Hiệu lực **8 tiếng**.

| Phương thức | Nguồn lấy mã | Hiệu lực | Tự động hóa được? |
|---|---|---|---|
| **Smart OTP** | App DNSE/EntradeX trên điện thoại (SmartOTP → *Lấy mã OTP cho thiết bị khác*) | 30 giây | ❌ thủ công |
| **Email OTP** | Gọi `POST /openapi/registration/send-email-otp` | 2 phút | ✅ có thể tự động |

Lấy token: `POST /openapi/registration/trading-token` với body
`{"otpType": "email_otp" | "smart_otp", "passcode": "1234"}` →
`{"trading-token": "7ceef658-9f01-414e-8b3e-faa77bb9061e"}`, truyền vào header
`trading-token` cho các request giao dịch.

> Tại mỗi thời điểm **chỉ 1 phương thức OTP** active; truyền `otpType` sai sẽ bị từ
> chối: `{"status":400,"code":"OA-100","message":"Invalid input: email otp is not registered for this account"}`.
>
> → **Với ingestion market data thuần, ta không bao giờ cần Trading Token.** Đây là
> lợi thế lớn so với sự mơ hồ của SSI về OTP cho stream.

*Nguồn: [`guide/intro/authentication.md`](../details/guide/intro/authentication.md),
[`guide/intro/register_guide.md`](../details/guide/intro/register_guide.md),
[`guide/faq.md`](../details/guide/faq.md)*

---

## 4. Protocol WebSocket — 6 bước

### Bước 1 — Kết nối

```text
wss://ws-openapi.dnse.com.vn/v1/stream?encoding={encoding}
```

Nhận **welcome message**:

```json
{
  "action": "welcome",
  "session_id": "conn_1782199800969809263",
  "timestamp": 1750000000,
  "message": "Please authenticate within 30 seconds"
}
```

`session_id` dùng để định danh kết nối — **nên log lại để debug**. Nhận được message
này là tín hiệu sẵn sàng auth.

### Bước 2 — Auth

Xem [§3.2](#32-xác-thực-websocket-hmac-sha256--cái-ta-cần). Server **không chấp nhận
subscribe trước khi auth thành công**.

### Bước 3 — Subscribe

```json
{
  "action": "subscribe",
  "channels": [
    { "name": "tick.G1.json", "symbols": ["ACB", "HPG"] }
  ]
}
```

| Trường | Mô tả |
|---|---|
| `action` | Luôn là `"subscribe"` |
| `channels[].name` | Tên channel (xem [§6](#6-market-data--toàn-bộ-channel--payload)) |
| `channels[].symbols` | Danh sách mã (CHỮ IN HOA). Truyền `[]` cho channel không filter theo mã |

Nhiều channel trong một message:

```json
{
  "action": "subscribe",
  "channels": [
    { "name": "tick.G1.json",      "symbols": ["ACB", "HPG"] },
    { "name": "top_price.G1.json", "symbols": ["ACB"] }
  ]
}
```

Response: `{ "action": "subscribed" }`

### Bước 4 — Đọc dữ liệu

**Control messages** (điều khiển vòng đời):

| `action` | Hướng | Mô tả |
|---|---|---|
| `welcome` | S→C | Message đầu tiên sau khi kết nối (kèm `session_id`) |
| `auth_success` | S→C | Auth thành công |
| `subscribed` | S→C | Xác nhận subscribe thành công |
| `unsubscribed` | S→C | Xác nhận unsubscribe thành công |
| `ping` | S→C | Keepalive — phải phản hồi `pong` ngay |
| `pong` | S→C | Xác nhận ping từ client |
| `connection_expired` | S→C | Đạt giới hạn 8 giờ, server sắp đóng — client nên reconnect |
| `error` | S→C | Lỗi — đọc `code` và `message` |

> Message lỗi có dạng `{ "action": "error", "code": "...", "message": "..." }` — dùng
> trường **`message`**, không phải `msg`.

**Data messages** — payload thị trường, nhận biết qua trường **`T`**.

> ⚠️ Tài liệu cảnh báo rõ: **KHÔNG** phân loại bằng "có trường `action` hay không".
> Phần lớn data message không có `action`, **nhưng một số loại (ví dụ
> `estimated_market_index`) có cả `action` lẫn `T`**. Cách an toàn:

```python
CONTROL_ACTIONS = {
    "welcome", "auth_success", "subscribed", "unsubscribed",
    "ping", "pong", "connection_expired", "error",
}

action = data.get("action")
if action in CONTROL_ACTIONS:
    ...  # control message
else:
    msg_type = data.get("T")   # data message
```

### Bước 5 — Unsubscribe

```json
{
  "action": "unsubscribe",
  "channels": [ { "name": "tick.G1.json", "symbols": ["ACB"] } ]
}
```

### Bước 6 — Keepalive

Xem [§5](#5-keepalive-vòng-đời-8-giờ--reconnect).

*Nguồn: [`sdk_document/build_websocket.md`](../details/sdk_document/build_websocket.md)*

---

## 5. Keepalive, vòng đời 8 giờ & reconnect

### 5.1. PING/PONG ở tầng application

Đây là ping/pong **trong payload JSON/msgpack** (trường `action`), **khác** với
ping/pong frame của chính protocol WebSocket. Nhiều thư viện WS tự xử lý frame-level
ping và **ẩn nó khỏi ứng dụng** — nên phải tự làm tầng application.

**Server gửi định kỳ mỗi 3 phút** (kèm `timestamp` tính bằng **milliseconds**):

```json
{ "action": "ping", "timestamp": 1750000000123 }
```

**Client phải phản hồi trong 60 giây**, nếu không server đóng kết nối (close code
`1008`):

```json
{ "action": "pong", "timestamp": 1750000000123 }
```

> Nên **echo lại `timestamp`** để server đo được round-trip latency. Bỏ trường này thì
> keepalive vẫn hoạt động, chỉ mất số liệu latency.

**Khuyến nghị:** client **chủ động gửi `ping` mỗi 25 giây** để phòng PING của server
bị miss do NAT timeout / mobile network. Khi client gửi `ping`, server trả `pong`
(kèm `timestamp` tính bằng **giây**). SDK Python mặc định `heartbeat_interval=25.0`.

Ba tình huống trong tài liệu:

| Case | Diễn biến | Kết quả |
|---|---|---|
| 1. Tốt | T+0 S→PING, T+1 C→PONG, T+3 S→PING, T+4 C→PONG | ✅ giữ kết nối |
| 2. Xấu | T+0 S→PING, không có PONG, T+1 server ngắt | ❌ dead connection |
| 3. Client chủ động | Client gửi ping/pong mỗi ≤3 phút | ✅ giữ kết nối |

### 5.2. Giới hạn 8 giờ

**Một kết nối WebSocket có hiệu lực tối đa 8 giờ**, server sẽ chủ động ngắt. Trước khi
đóng, server gửi:

```json
{ "action": "connection_expired", "code": "MAX_DURATION_EXCEEDED", "message": "Connection expired after 8 hours. Please reconnect." }
```

rồi đóng với close code `1008`. Đây là **hành vi bình thường, không phải lỗi** —
client nên reconnect ngay.

> 🔴 **Hệ quả thiết kế:** một service chạy 24/7 sẽ bị ngắt **ít nhất 3 lần/ngày**.
> Reconnect + resubscribe phải là đường đi thường trực, được test kỹ, không phải nhánh
> xử lý ngoại lệ. Nếu muốn không mất tick nào, cân nhắc **mở kết nối mới trước khi
> kết nối cũ hết hạn (overlap)** rồi mới đóng cái cũ — tài liệu không cấm, nhưng nhớ
> `subscriptions_max` và số kết nối tối đa của tier.

### 5.3. Reconnect

Khi đứt, phải làm **lại toàn bộ luồng**:

1. Kết nối lại → nhận welcome mới (`session_id` mới).
2. Gửi lại auth — **phải tạo `timestamp` và `nonce` MỚI**, không tái dùng.
3. Gửi lại **tất cả** subscribe message.

**Close code:**

| Code | Ý nghĩa | Nên reconnect? |
|---|---|---|
| `1000` | Normal closure (server đóng bình thường) | Có (trừ khi client chủ động đóng) |
| `1008` | Policy violation — heartbeat timeout, **hết 8 giờ** (kèm `connection_expired`), hoặc admin ngắt | Có |
| `1013` | Try again later — **client quá chậm**, không kịp tiêu thụ message (write queue đầy) | Có, nhưng **backoff lâu hơn và/hoặc giảm số channel** |
| `1001` | Going away (không do server gửi) | Có |
| `1006` | Abnormal closure — mất kết nối đột ngột, không có closing handshake | Có |
| `1011` / `1012` | Internal server error / restart (thường gặp khi qua proxy/gateway) | Có |

Dùng **exponential backoff**: `1s → 2s → 4s → 8s → … → 60s (tối đa)`.

> 💡 `1013` là tín hiệu **backpressure** rất giá trị: nó nói thẳng rằng consumer của
> ta chậm hơn feed. Phải đếm và alert riêng mã này — nếu xuất hiện thì kiến trúc đang
> có vấn đề (parse trên hot path, sink chậm...), thêm channel chỉ làm tệ hơn.

*Nguồn: [`sdk_document/build_websocket.md`](../details/sdk_document/build_websocket.md),
[`guide/market-data/connect.md`](../details/guide/market-data/connect.md)*

---

## 6. Market Data — toàn bộ channel & payload

### 6.1. Bảng tổng quan

| Kênh dữ liệu | Channel name | Phân loại | Tần suất |
|---|---|---|---|
| Security Definition | `security_definition.{board_id}.{encoding}` | Batch (BOD) | Gửi trước giờ giao dịch (≈ 08:00) — xem [§11.2](#112-security-definition-gửi-1-lần-hay-2-lần) |
| Trade | `tick.{board_id}.{encoding}` | Real-time | Khi có thay đổi trong phiên liên tục |
| Trade Extra | `tick_extra.{board_id}.{encoding}` | Real-time | Khi có thay đổi trong phiên liên tục |
| Quotes (độ sâu) | `top_price.{board_id}.{encoding}` | Real-time | Khi có thay đổi trong phiên |
| OHLC (đang hình thành) | `ohlc.{resolution}.{encoding}` | Real-time | Khi có giá khớp trong phiên liên tục |
| OHLC Closed (đã đóng nến) | `ohlc_closed.{resolution}.{encoding}` | Periodic | Khi đóng nến |
| Expected Price | `expected_price.{board_id}.{encoding}` | Real-time | Trong phiên định kỳ ATO/ATC |
| Market Index | `market_index.{market_index}.{encoding}` | Periodic | **Chu kỳ 5 giây** + tổng hợp cuối ngày |
| Foreign Investor | `foreign.{board_id}.{encoding}` | Real-time | Khi có thay đổi |
| Estimated VN30 | `estimated_market_index.{market_index}.{encoding}` | Real-time | Khi có thay đổi |
| Thông tin phiên (Session) | `session.{product_group_id}.{board_id}.{encoding}` | Real-time | Khi có thay đổi |

**Phân loại dữ liệu:**

* **Real-time** — push ngay khi có sự kiện, độ trễ thấp nhất.
* **Periodic** — cập nhật theo khoảng thời gian cố định hoặc theo giai đoạn phiên.
* **Batch** — snapshot theo đợt lớn: **BOD** (đầu ngày: danh mục mã, giá trần/sàn),
  **EOD** (cuối ngày: giá đóng cửa chính thức).

### 6.2. Trường `time` — điểm mạnh nhất của DNSE

Phần lớn payload thị trường mang:

```json
"time": { "Seconds": 1779757279, "Nanos": 101000000 }
```

> 🟢 **Đây là timestamp của sàn với độ phân giải nano-giây** — thứ mà SSI hoàn toàn
> không có (SSI chỉ trả chuỗi `"YYYY/MM/DD HH:mi:ss"` độ phân giải giây). Với DNSE ta
> có **event time thật**, cho phép: đo độ trễ thật của feed (`recv_ts − exchange_ts`),
> sắp xếp lại đúng thứ tự sự kiện, và khử trùng lặp chính xác hơn.
>
> Lưu ý các biến thể không nhất quán: `market_index` dùng tên trường `transactTime`
> (vẫn dạng `{Seconds, Nanos}`); `estimated_market_index` và `session` lại dùng
> **chuỗi** (`"2026-06-08 13:56:29.371"` / `"2025-10-01T02:15:00.487Z"`);
> `foreign` dùng `transactTime` dạng chuỗi `"035200011"`; OHLC dùng `time` là
> **integer epoch giây**. Parser phải xử lý cả 4 dạng.

### 6.3. Security Definition

**Channel:** `security_definition.{board_id}.{encoding}` · **Input:** `symbols`, `board_id`

Cung cấp giá trần/sàn/tham chiếu và trạng thái mã trong ngày giao dịch.

```json
{
  "marketId": "DVX",            // Mã thị trường niêm yết
  "boardId": "G1",              // Mã bảng giao dịch
  "isin": "VN41I1G20009",       // Mã định danh quốc tế
  "symbol": "41I1G2000",
  "productGrpId": "FIO",        // Nhóm sản phẩm theo thị trường
  "securityGroupId": "FU",      // Nhóm chứng khoán
  "basicPrice": 2066.6,         // Giá tham chiếu
  "ceilingPrice": 2211.2,       // Giá trần
  "floorPrice": 1922.0,         // Giá sàn
  "openInterestQuantity": 24473,// KL hợp đồng phái sinh mở qua đêm
  "securityStatus": "NO_HALT",
  "symbolAdminStatusCode": "NRM",
  "symbolTradingMethodStatusCode": "NRM",
  "symbolTradingSanctionStatusCode": "NRM",
  "listingDate": 20260223,      // Ngày niêm yết
  "finalTradeDate": 20260416,   // Ngày GD cuối (phái sinh, chứng quyền)
  "time": { "Seconds": 1779757279, "Nanos": 101000000 }
}
```

> Nếu kết nối **sau** thời điểm gửi, dùng REST `GET /secdef` để bù. Đây là dữ liệu
> **bắt buộc** để validate giá đặt lệnh và để biết biên độ trong ngày.
>
> Lưu ý `listingDate`/`finalTradeDate` là số dạng `20260223` nhưng tài liệu ghi kiểu
> `string` — xem [§11.4](#114-kiểu-dữ-liệu-ghi-không-khớp-với-giá-trị-mẫu).

### 6.4. Trade & Trade Extra

**Channel:** `tick.{board_id}.{encoding}` và `tick_extra.{board_id}.{encoding}`

`tick_extra` = `tick` + `side` (mua/bán chủ động) + `avgPrice` (giá khớp trung bình).
Tài liệu khuyến nghị: **không cần 2 field đó thì dùng `tick` để tối ưu tốc độ**.

```json
{
  "marketId": "STO", "boardId": "G1", "isin": "VN000000HPG4", "symbol": "HPG",
  "matchPrice": 24.35,          // Giá khớp gần nhất
  "matchQtty": 40,              // KL khớp gần nhất
  "totalVolumeTraded": 1184240, // Tổng KL khớp trong ngày
  "grossTradeAmount": 287.17458,// Tổng giá trị GD trong ngày
  "highestPrice": 24.35, "lowestPrice": 24.15, "openPrice": 24.25,
  "tradingSessionId": "40",     // Mã phiên hiện tại
  "time": { "Seconds": 1779762571, "Nanos": 101000000 }
}
```

`tick_extra` thêm:

```json
  "side": "SELL",     // Chiều mua/bán CHỦ ĐỘNG (BUY | SELL | UNSPECIFIED)
  "avgPrice": 2023.92 // Giá khớp trung bình
```

> `side` chủ động là dữ liệu quý để tính dòng tiền (tương đương `si` B/S của SSI và
> `action` BU/SD của TCBS ouranos).
>
> Chú ý `matchQtty` là `integer` ở ví dụ cổ phiếu nhưng `1.0` (**float**) ở ví dụ phái
> sinh — schema phải chấp nhận cả hai.

### 6.5. Quotes — độ sâu thị trường

**Channel:** `top_price.{board_id}.{encoding}`

* **Sàn HOSE: 3 mức giá.**
* **Sàn HNX, UPCOM: 10 mức giá.**

```json
{
  "marketId": "DVX", "boardId": "G1", "isin": "VN41I1G60005", "symbol": "41I1G6000",
  "bid": [
    { "price": 2023.4, "quantity": 9.0 },
    { "price": 2023.3, "quantity": 22.0 },
    { "price": 2023.2, "quantity": 15.0 }
  ],
  "offer": [
    { "price": 2023.6, "quantity": 3.0 },
    { "price": 2023.7, "quantity": 62.0 },
    { "price": 2023.8, "quantity": 16.0 }
  ],
  "totalOfferQtty": 8353.0,   // Tổng KL chào bán
  "totalBidQtty": 6447.0,     // Tổng KL chào mua
  "time": { "Seconds": 1779767143, "Nanos": 736000000 }
}
```

> Khác SSI: DNSE dùng **mảng object** `{price, quantity}` (SSI dùng mảng cặp
> `["price","quantity"]` dạng string). DNSE trả **number thật**, không phải string —
> đỡ một bước parse.
>
> Tài liệu **không nói** đây là snapshot đầy đủ hay delta. Ví dụ cho thấy snapshot 3
> mức; suy đoán là snapshot toàn bộ mức của mã đó nhưng **cần xác minh** (xem
> [§11.5](#115-quotes-là-snapshot-hay-delta-số-mức-luôn-đủ-không)).

### 6.6. OHLC & OHLC Closed

**Channel:** `ohlc.{resolution}.{encoding}` (nến đang hình thành) và
`ohlc_closed.{resolution}.{encoding}` (nến đã đóng, không đổi sau đó).

**Input:** `symbols` + `resolution` (`1`, `3`, `5`, `15`, `30`, `1H`, `1D`, `1W`).

> ⚠️ **Với phái sinh phải truyền `symbolType` (VD `VN30F1M`) thay vì `symbol` cụ thể
> (VD `41I1G4000`).** Đây là ngoại lệ duy nhất trong toàn bộ market data.

Payload giống nhau cho cả hai channel, khác nhau ở `type`:

```json
{
  "time": 1757992500,        // integer — thời gian BẮT ĐẦU nến (epoch giây)
  "open": 30.4, "high": 30.4, "low": 30.25, "close": 30.3,
  "volume": 1398200,
  "symbol": "HPG",
  "resolution": "15",
  "lastUpdated": 1757993014, // integer — cập nhật lần cuối
  "type": "STOCK"            // STOCK | DERIVATIVE | INDEX
}
```

Ba biến thể: `type: "STOCK"` (symbol `HPG`), `type: "DERIVATIVE"` (symbol `VN30F1M`,
lưu ý `"volume": "12"` là **string** trong ví dụ phái sinh), `type: "INDEX"`
(symbol `VNINDEX`, resolution `1D`).

> 🟢 Có OHLC realtime qua WebSocket là điểm cộng: không phải tự dựng nến từ tick.
> Nhưng nếu cần chính xác tuyệt đối thì vẫn nên tự dựng từ `tick` và dùng
> `ohlc_closed` để đối chiếu.

### 6.7. Expected Price (giá dự khớp ATO/ATC)

**Channel:** `expected_price.{board_id}.{encoding}`

```json
{
  "marketId": "DVX", "boardId": "G1", "symbol": "41I1G1000", "isin": "VN41I1G10000",
  "closePrice": 28.45,
  "expectedTradePrice": 28.45,     // Giá dự khớp
  "expectedTradeQuantity": 133780, // KL dự khớp
  "time": { "Seconds": 1779694639, "Nanos": 736000000 }
}
```

### 6.8. Market Index

**Channel:** `market_index.{market_index}.{encoding}` · **Input:** `market_index`

Cập nhật **chu kỳ 5 giây** + tổng hợp cuối ngày. Payload rất giàu — gồm giá trị chỉ
số, độ rộng thị trường và thanh khoản tách theo phương thức khớp lệnh/thỏa thuận:

```json
{
  "indexName": "VNINDEX",
  "valueIndexes": 1669.38,        // Giá trị hiện tại
  "priorValueIndexes": 1662.54,   // Tham chiếu
  "changedValue": 6.84, "changedRatio": 0.41,
  "highestValueIndexes": 1677.83, "lowestValueIndexes": 1662.05,
  "fluctuationUpIssueCount": 144,        // Số mã tăng
  "fluctuationDownIssueCount": 158,      // Số mã giảm
  "fluctuationSteadinessIssueCount": 67, // Số mã đứng giá
  "fluctuationUpperLimitIssueCount": 7,  // Số mã tăng trần
  "fluctuationLowerLimitIssueCount": null, // Số mã giảm sàn (có thể null!)
  "fluctuationUpIssueVolume": 446927155,
  "fluctuationDownIssueVolume": 220246500,
  "fluctuationSteadinessIssueVolume": 39390038,
  "contauctAccTrdVal": 15609.88011093,  // Tổng GT khớp lệnh
  "contauctAccTrdVol": 606182599,       // Tổng KL khớp lệnh
  "blkTrdAccTrdVal": 3040.58723198,     // Tổng GT thỏa thuận
  "blkTrdAccTrdVol": 100381155,         // Tổng KL thỏa thuận
  "grossTradeAmount": 18650.46734291,   // Tổng GT trong ngày
  "totalVolumeTraded": 706563754,       // Tổng KL trong ngày
  "currencyCode": "VND", "indexTypeCode": "001",
  "marketIndexClass": 1, "marketId": "STO", "tradingSessionId": "40",
  "transactTime": { "Seconds": 1774940705, "Nanos": 0 }
}
```

> `fluctuationLowerLimitIssueCount: null` trong chính ví dụ của tài liệu → **mọi field
> integer đều phải nullable** trong schema.

### 6.9. Estimated VN30

**Channel:** `estimated_market_index.{market_index}.{encoding}` — hiện **chỉ hỗ trợ
`VN30`**.

```json
{
  "indexName": "VN30",
  "valueIndexes": 1948.57, "changedValue": -37.71, "changedRatio": -1.9,
  "fluctuationUpIssueCount": 5, "fluctuationDownIssueCount": 25,
  "fluctuationSteadinessIssueCount": 0,
  "grossTradeAmount": 6391.86, "totalVolumeTraded": 184907600,
  "time": "2026-06-08 13:56:29.371"   // string, KHÔNG phải {Seconds,Nanos}
}
```

> Đây chính là loại message mà tài liệu cảnh báo **có cả `action` lẫn `T`** — nhớ luật
> phân loại ở [§4 Bước 4](#bước-4--đọc-dữ-liệu).

### 6.10. Foreign Investor

**Channel:** `foreign.{board_id}.{encoding}`

```json
{
  "marketId": "STO", "boardId": "G1", "tradingSessionId": "40", "symbol": "FPT",
  "transactTime": "035200011",          // string — thời điểm cập nhật
  "foreignInvestorTypeCode": "10",
  "sellVolume": 1449400, "sellTradedAmount": 109774810000,
  "buyVolume": 608300,  "buyTradedAmount": 46040960000,
  "totalSellVolume": 1449716, "totalSellTradedAmount": 109798718600,
  "totalBuyVolume": 608370,   "totalBuyTradedAmount": 46046280000,
  "foreignerOrderLimitQuantity": 341884580,  // Tổng room tối đa
  "foreignerBuyPossibleQuantity": 351900000  // Room còn lại có thể mua
}
```

> Đây là channel **duy nhất không có trường `time`** dạng `{Seconds, Nanos}` — chỉ có
> `transactTime` dạng chuỗi `"035200011"` (nhìn như `HHMMSSmmm`, tài liệu không giải
> thích). Cần tự đóng dấu thời gian nhận.
>
> Cũng lưu ý: `buyVolume`/`sellVolume` là "trong ngày **theo bảng giao dịch**", còn
> `totalBuyVolume`/`totalSellVolume` là tổng cả ngày — hai cặp khác nhau, dễ nhầm.

### 6.11. Session (thông tin phiên)

**Channel:** `session.{product_group_id}.{board_id}.{encoding}` ·
**Input:** `tsc_prod_grp_id`, `board_id`

```json
{
  "marketId": "DVX", "boardId": "G1",
  "eventId": "AB2",           // Mã sự kiện chuyển trạng thái phiên
  "tradingSessionId": "40",   // Mã phiên hiện tại
  "tscProdGrpId": "STO",
  "time": "2025-10-01T02:15:00.487Z"
}
```

> Channel này là **cách đúng để biết thị trường đang ở phiên nào** (ATO/liên
> tục/nghỉ trưa/ATC/đóng bảng) thay vì hardcode giờ — rất cần cho cảnh báo "feed
> stale" đúng đắn. Xem enum `eventId` và `tradingSessionId` ở [§8](#8-enums).

*Nguồn: [`guide/market-data/connect.md`](../details/guide/market-data/connect.md),
[`sdk_document/market_data.md`](../details/sdk_document/market_data.md)*

---

## 7. Trading Data & Broker WebSocket

### 7.1. Trading Data (tài khoản của mình)

| Channel | Nội dung |
|---|---|
| `order.{market_type}.{encoding}` | Lệnh giao dịch realtime |
| `position.{market_type}.{encoding}` | Vị thế nắm giữ realtime |

`market_type`: `STOCK` (cơ sở) hoặc `DERIVATIVE` (phái sinh).

**Order Event** — đẩy khi có lệnh mới, đổi trạng thái, hoặc đổi giá/KL khớp:

```json
{
  "id": 596, "side": "NS",              // NB: Mua, NS: Bán
  "accountNo": "0001179019", "symbol": "41I1G5000",
  "orderType": "LO", "price": 1920.0, "priceSecure": 1920.0, "averagePrice": 1921,
  "quantity": 5, "fillQuantity": 2, "canceledQuantity": 0, "leaveQuantity": 3,
  "orderStatus": "PartiallyFilled",
  "loanPackageId": 2278, "marketType": "DERIVATIVE",
  "transDate": "2026-04-06T00:00:00Z",
  "createdDate": "2026-04-13T04:24:05.274Z",
  "modifiedDate": "2026-04-13T04:28:27.749Z"
}
```

Trạng thái lệnh: `Pending` → `PendingNew` → `New` → `PartiallyFilled` → `Filled`;
ngoài ra `PendingReplace`, `PendingCancel`, `Canceled`, `Rejected`, `Expired`,
`DoneForDay`.

**Position Event** — đẩy khi mở/đóng vị thế, đổi KL, giá vốn, giá thị trường, trạng
thái. Hai biến thể:

* **Phái sinh:** `status` ∈ {`OPEN`, `CLOSED`}, có `overNightQuantity`,
  `tradeQuantity = null`.
* **Cơ sở:** `status` ∈ {`OPEN`, `PENDING_CLOSE`, `CLOSED`, `ODD_LOT`},
  `tradeQuantity` = KL có thể bán, `overNightQuantity = null`.

Field chung: `id`, `accountNo`, `symbol`, `loanPackageId`, `side` (NB/NS),
`accumulateQuantity`, `closedQuantity`, `costPrice`, `marketPrice`, `breakEvenPrice`,
`openQuantity`, `averageClosePrice`, `marketType`, `createdDate`, `modifiedDate`.

### 7.2. Broker WebSocket (dành cho môi giới/SACO)

| Channel | Nội dung |
|---|---|
| `order.broker.{market_type}.{investor_id}.{encoding}` | Lệnh của KH được ủy quyền |
| `position.broker.{market_type}.{investor_id}.{encoding}` | Vị thế của KH được ủy quyền |

**Giới hạn quan trọng:**

* **Mỗi kết nối WebSocket chỉ subscribe được cho DUY NHẤT 1 `investor_id`.** Muốn theo
  dõi nhiều KH → phải mở nhiều kết nối riêng.
* Chỉ dùng `investor_id` đã được ủy quyền; sai sẽ nhận lỗi
  `user does not have permissions for investorId`.
* `investor_id` lấy từ REST `GET /brokers/accounts/care-by`.
* Quyền `ADVISOR` = chỉ xem; `BROKER` = xem + đặt lệnh.

### 7.3. `accountNo` vs `investorId` — dễ nhầm

| | Dùng ở đâu |
|---|---|
| `accountNo` (tiểu khoản) | REST API giao dịch (đặt lệnh, sổ lệnh, số dư). Một KH có **nhiều** tiểu khoản |
| `investorId` | **Kết nối WebSocket Trading Data**. Mỗi KH có **1** `investorId` duy nhất |

Cả hai lấy từ `GET /accounts` (`investorId`, `custodyCode`, `accounts[].id`,
`accounts[].derivativeAccount`).

> ⚠️ FAQ nói `investorId` "dùng cho kết nối WebSocket Trading Data", nhưng định dạng
> channel `order.{market_type}.{encoding}` **không có chỗ cho `investor_id`** — chỉ
> channel Broker mới có. Xem [§11.3](#113-investorid-dùng-ở-đâu-trong-trading-websocket).

*Nguồn: [`guide/market-data/trading_connect.md`](../details/guide/market-data/trading_connect.md),
[`guide/market-data/broker_connect.md`](../details/guide/market-data/broker_connect.md),
[`guide/faq.md`](../details/guide/faq.md)*

---

## 8. Enums

Trích [`guide/enum/market_data.md`](../details/guide/enum/market_data.md) — phần cần
cho market data.

### boardId (bảng giao dịch)

| Giá trị | Mô tả |
|---|---|
| `UNSPECIFIED` | Không xác định |
| `AL` | **Tất cả bảng** |
| `G1` | Lô chẵn |
| `G3` | Board phiên sau giờ (PLO) |
| `G4` | Lô lẻ |
| `T1` | Thỏa thuận lô chẵn 9h–14h45 |
| `T3` | Thỏa thuận lô chẵn 14h45–15h |
| `T4` | Thỏa thuận lô lẻ 9h–14h45 |
| `T6` | Thỏa thuận lô lẻ 14h45–15h |

> `AL` (tất cả bảng) chỉ xuất hiện trong trang enum, **không** có trong bảng `boardId`
> của trang Market Data WebSocket — nhưng nếu dùng được thì đây là cách gọn nhất để
> lấy cả lô chẵn + lô lẻ + thỏa thuận trong một subscribe. **Cần thử.**

### resolution (khung nến)

`1`, `3`, `5`, `15`, `30` (phút) · `1H` · `1D` · `1W`

### marketIndex

`VNINDEX`, `HNX`, `HNX30`, `VN30`, `VN100`, `VNXALLSHARE`, `UPCOM`, `VNMITECH`,
`VN50GROWTH`, `VNDIVIDEND`

### marketId (thị trường)

| Giá trị | Mô tả |
|---|---|
| `DVX` | Phái sinh sàn HNX |
| `HCX` | Trái phiếu doanh nghiệp sàn HNX |
| `STO` | Cổ phiếu sàn HOSE |
| `STX` | Cổ phiếu sàn HNX |
| `UPX` | Cổ phiếu sàn UPCOM |

### productGrpId / tscProdGrpId (nhóm sản phẩm)

`FBX` (HĐTL trái phiếu) · `FIO` (HĐTL chỉ số) · `HCX` (TPDN HNX) · `STO` (CP HOSE) ·
`STX` (CP HNX) · `UPX` (CP UPCOM)

### tradingSessionId (phiên, theo từng mã)

| Giá trị | Mô tả |
|---|---|
| `10` | ATO |
| `30` | ATC |
| `40` | Phiên liên tục |
| `80` | PCA mã halt |
| `99` | Đóng bảng |

### eventId (sự kiện chuyển trạng thái phiên)

| Giá trị | Mô tả |
|---|---|
| `AA1` | Bắt đầu phiên khớp lệnh định kỳ mở cửa |
| `AB1` | Bắt đầu phiên khớp lệnh liên tục |
| `AB2` | Kết thúc giao dịch của bảng |
| `AC2` | Thực hiện khớp lệnh định kỳ đóng cửa |
| `AD1` | Bắt đầu nhận lệnh |
| `AD2` | Thực hiện khớp lệnh định kỳ |
| `AW8` | Nghỉ trưa |
| `AW9` | Tiếp tục giao dịch sau nghỉ trưa |
| `AX1` | Bảng giao dịch bắt đầu hoạt động |
| `BB1` | Bắt đầu phiên KLLT cho chứng khoán thông thường |
| `BC1` | Bắt đầu phiên khớp lệnh định kỳ đóng cửa |
| `CC1` | Bắt đầu phiên PCA đóng cửa |
| `CD1` | Bắt đầu phiên PCA |
| `CD3` | Thực hiện khớp lệnh PCA |

### Các enum trạng thái mã

* **securityStatus:** `HALT` (ngừng GD) · `NO_HALT`
* **securityGroupId:** `BS` (TPDN) · `EF` (ETF) · `EW` (chứng quyền) · `FU` (HĐTL) ·
  `SR` (quyền mua) · `ST` (cổ phiếu)
* **symbolAdminStatusCode:** `NRM` (bình thường) · `CTR` (kiểm soát) · `CR` (kiểm soát
  + hạn chế GD) · `RES` (hạn chế GD) · `WFR` (cảnh báo vi phạm BCTC) · `WID` (cảnh báo
  vi phạm CBTT) · `WOV` (cảnh báo vi phạm khác)
* **symbolTradingMethodStatusCode:** `NRM` · `NWE` (niêm yết mới biên độ đặc biệt) ·
  `NWN` (niêm yết mới biên độ thường) · `SLS` (GD đặc biệt sau halt) · `SNE` (GD đặc biệt)
* **symbolTradingSanctionStatusCode:** `NRM` · `SUS` (tạm ngừng) · `DTL` (hủy niêm yết
  chuyển sàn) · `TFR` (ngưng GD do hạn chế)
* **side:** `BUY` (mua chủ động) · `SELL` (bán chủ động) · `UNSPECIFIED`
* **type:** `STOCK` · `DERIVATIVE` · `INDEX`
* **indexTypeCode:** `001`=VNINDEX, `002`=HNX, `100`=HNX30, `101`=VN30, `104`=VN100,
  `151`=VNXALLSHARE, `301`=UPCOM, `504`=VNMITECH, `505`=VN50GROWTH, `506`=VNDIVIDEND

---

## 9. Giới hạn & rate limit

### 9.1. WebSocket

| Giới hạn | Giá trị | Nguồn |
|---|---|---|
| Thời lượng 1 kết nối | **8 giờ** | tài liệu WS |
| Server PING | mỗi **3 phút** | tài liệu WS |
| Deadline trả PONG | **60 giây** | tài liệu WS |
| Client nên ping | mỗi **25 giây** | khuyến nghị + default SDK |
| Deadline auth sau khi kết nối | **30 giây** | tài liệu WS |
| Cửa sổ `timestamp` khi auth | **±5 phút** | tài liệu WS |
| Thời gian không được tái dùng `nonce` | **10 phút** | tài liệu WS |
| `messages_per_second` | **100** | trả về trong `auth_success` |
| `subscriptions_max` | **100** | trả về trong `auth_success` |
| Số kết nối tối đa | *không công bố* — vượt thì lỗi `MAX_CONNECTIONS_EXCEEDED` | — |

> `subscriptions_max: 100` là ràng buộc thiết kế quan trọng: nếu muốn theo dõi hàng
> nghìn mã, phải xem một "subscription" được tính theo **channel** hay theo
> **(channel × symbol)**. Tài liệu không nói rõ — xem [§11.6](#116-subscriptions_max-đếm-theo-channel-hay-theo-channel--symbol).

### 9.2. REST (để bù dữ liệu)

Rate limit theo **từng API Key** và **từng endpoint**, hai ngưỡng: **Rate** (số
request/giờ) và **Quota** (số request/24 giờ). Một số mốc liên quan market data:

| Endpoint | Rate/giờ | Quota/ngày |
|---|---|---|
| Lịch sử OHLC | 50,000 | 100,000 |
| Lịch sử khớp lệnh / Dữ liệu khớp gần nhất | 10,000 | 100,000 |
| Lịch sử bid/ask / bid-ask gần nhất | 10,000 | 100,000 |
| Chi tiết mã chứng khoán | 10,000 | 100,000 |
| Thông tin giao dịch chứng khoán (secdef) | 1,000 | 10,000 |
| Giá đóng cửa / Ngày làm việc | 1,000 | 10,000 |

Header response: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.
Vượt → HTTP **429** `{"error": "Rate Limit Exceeded"}`.

### 9.3. API versioning

Date-based: header `version: YYYY-MM-DD`. **Mặc định nếu không truyền: `2026-05-07`.**
Version mới chỉ sinh khi có **breaking change** (đổi/xóa endpoint, đổi tên/xóa field,
đổi kiểu dữ liệu, đổi validation, đổi auth). Thêm field/endpoint/optional param/enum
value mới **không** tạo version mới.

> Khuyến nghị của DNSE: **pin version cụ thể** trong code, và viết parser
> **forward-compatible — bỏ qua field không nhận diện**. Hiện **chưa có sunset** cho
> version cũ. Sai định dạng version → `{"status":"error","code":"OA-401","message":"This API version does not seem to exist"}`.
>
> Tài liệu **không nói** WebSocket có versioning hay không (endpoint là `/v1/stream`).

---

## 10. Mã lỗi liên quan tới stream

**Control message lỗi của WebSocket:**

| `code` | Ý nghĩa | Xử lý |
|---|---|---|
| `AUTH_FAILED` | Sai signature/api_key, nonce đã dùng, timestamp lệch | **Không retry mù** — sửa gốc (kiểm NTP, sinh nonce mới) |
| `AUTH_TIMEOUT` | Không auth trong 30s | Reconnect, auth ngay sau welcome |
| `MAX_CONNECTIONS_EXCEEDED` | Vượt số kết nối của tier | Giảm số kết nối, đừng reconnect dồn |
| `MAX_DURATION_EXCEEDED` | Hết 8 giờ (kèm `connection_expired`) | Reconnect — **bình thường, không phải lỗi** |

**Mã lỗi REST liên quan (khi bù dữ liệu / lấy secdef):**

| HTTP | Code | Ý nghĩa |
|---|---|---|
| 400 | `OA-400` | Request không hợp lệ (kể cả **sai/thiếu Signature**) |
| 401 | `OA-401` | API Key không hợp lệ hoặc đã bị xóa (cũng dùng cho version sai) |
| 403 | `OA-403` | Không có quyền / thiếu permission |
| 404 | `OA-404` | Endpoint hoặc tài nguyên không tồn tại |
| 422 | `OA-422` | Đúng format nhưng không thỏa điều kiện nghiệp vụ |
| 429 | `OA-429` | Vượt rate limit |
| 500 | `OA-500` | Lỗi hệ thống tạm thời |
| 503 | `OA-503` | Dịch vụ tạm không khả dụng |

Ngoài ra: `SYMBOL_NOT_EXIST`, `INVALID_SYMBOL`, `TIMEOUT`, `SYSTEM_ERROR`,
`REMOTE_SERVER_ERROR`, `THIRD_PARTY_ERROR`, `RESOURCE_NOT_FOUND`.

**Chính sách retry theo tài liệu:**

* **Không retry** với 401, 403, 400, 422 — phải sửa root cause.
* **Được retry với backoff** (tối đa 3 lần) cho 500, 503, `TIMEOUT`.
* Với 429: đọc `X-RateLimit-Reset` rồi chờ đến thời điểm đó.

> Response lỗi của DNSE **không nhất quán về hình dạng**: có lúc
> `{status:"error", code, message}`, lúc `{code}` trơ, lúc `{success:false, code, message}`,
> lúc `{status:400, code, message}` (`status` là số). Tài liệu chốt: **luôn đọc trường
> `code`**. Parser phải chịu được cả 4 dạng.

*Nguồn: [`guide/error_codes.md`](../details/guide/error_codes.md),
[`guide/ratelimits.md`](../details/guide/ratelimits.md),
[`guide/versioning/api.md`](../details/guide/versioning/api.md)*

---

## 11. Điểm chưa rõ & mâu thuẫn trong tài liệu gốc

### 11.1. Trường `T` được nói tới nhưng không có trong bất kỳ payload mẫu nào

Trang protocol nói data message "nhận biết qua trường `T`" và code mẫu dùng
`data.get("T")` để phân loại. Nhưng **toàn bộ payload mẫu ở trang Market Data
WebSocket, Trading Data và Broker đều KHÔNG có trường `T`**.

→ Không rõ `T` là gì (tên channel? mã loại message?) và giá trị hợp lệ gồm những gì.
**Đây là khoảng trống lớn nhất** — phải bắt message thật để biết, vì nó quyết định
cách route message sang đúng parser.

### 11.2. Security Definition gửi 1 lần hay 2 lần?

| Nguồn | Khẳng định |
|---|---|
| Bảng tổng quan (`market-data/connect`) | *"Gửi 1 lần trước giờ giao dịch (≈ 08:00)"* |
| Phần mô tả (`market-data/connect`) | *"gửi hai lần vào lúc ... kết thúc chạy dữ liệu cuối ngày (khoảng 8 giờ tối) và vào đầu ngày giao dịch hôm sau (khoảng 8 giờ sáng)"* |
| `sdk/market_data` | *"gửi một lần duy nhất vào 8h sáng đầu ngày giao dịch"* |
| FAQ #43 | *"gửi 2 lần/ngày (~8h sáng và ~20h tối)"* |

→ 2/4 nguồn nói 2 lần. Dù sao cũng phải có đường bù bằng REST `GET /secdef`, nên ảnh
hưởng thực tế nhỏ — nhưng đừng thiết kế dựa trên giả định "chỉ 1 lần".

### 11.3. `investorId` dùng ở đâu trong Trading WebSocket?

FAQ #26 nói `investorId` "dùng cho kết nối WebSocket Trading Data", nhưng channel
Trading Data là `order.{market_type}.{encoding}` — **không có chỗ cho `investor_id`**.
Chỉ channel **Broker** mới có (`order.broker.{market_type}.{investor_id}.{encoding}`).

→ Suy đoán: với tài khoản của chính mình, danh tính suy ra từ API Key, còn `investorId`
chỉ cần cho Broker. Cần xác nhận.

### 11.4. Kiểu dữ liệu ghi không khớp với giá trị mẫu

Nhiều chỗ comment kiểu dữ liệu sai so với giá trị thật ngay bên cạnh:

| Field | Tài liệu ghi | Giá trị mẫu |
|---|---|---|
| `listingDate`, `finalTradeDate` | `string` | `20260223` (số) |
| `volume` (OHLC phái sinh) | `integer` | `"12"` (string) |
| `matchQtty` (tick phái sinh) | `float` | `1.0` — còn ví dụ cổ phiếu là `40` (integer) |
| `openInterestQuantity` | `integer` | `24473` ✔ |
| `fluctuationLowerLimitIssueCount` | `integer` | `null` |

→ **Không tin comment kiểu dữ liệu.** Schema nên nhận number-hoặc-string cho mọi
trường số và cho phép `null` ở mọi field. Nếu lưu thô byte-for-byte (như pipeline
trong `examples/`) thì rủi ro này biến mất ở tầng ingest.

### 11.5. Quotes là snapshot hay delta? Số mức luôn đủ không?

Tài liệu nói HOSE 3 mức, HNX/UPCOM 10 mức, nhưng **không nói** mỗi message có luôn trả
đủ số mức đó hay chỉ trả mức thay đổi, và điều gì xảy ra khi bên bid/offer rỗng
(`[]`? thiếu field?). SSI thì nói thẳng là hiện snapshot, tương lai chuyển delta.

### 11.6. `subscriptions_max` đếm theo channel hay theo (channel × symbol)?

Nếu đếm theo `(channel, symbol)` thì 100 là **rất ít** — không đủ cho một universe
1600+ mã, và ta sẽ phải mở rất nhiều kết nối (nhưng số kết nối tối đa cũng không được
công bố). Nếu đếm theo channel thì 100 là thoải mái.

→ Đây là **câu hỏi quyết định kiến trúc**, phải thử trước khi thiết kế: thử subscribe
`tick.G1.json` với 500 symbol và xem `subscriptions_max` bị tính thế nào.

### 11.7. `boardId = AL` có dùng được cho subscribe không?

`AL` (Tất cả bảng) có trong trang enum nhưng không có trong bảng `boardId` của trang
Market Data. Nếu dùng được thì gộp được lô chẵn/lẻ/thỏa thuận trong 1 subscribe.

### 11.8. Lỗi copy-paste trong bảng tổng quan channel

Trong bảng "Tổng quan các kênh dữ liệu", dòng **Thông tin phiên (Session)** có mô tả là
*"Dữ liệu dự tính của chỉ số VN30"* — copy nguyên từ dòng Estimated VN30 phía trên.
Mô tả đúng nằm ở phần chi tiết của channel (§6.11). Vô hại, nhưng là dấu hiệu bảng tổng
quan không đáng tin bằng phần mô tả chi tiết.

### 11.9. Những thứ hoàn toàn không được nêu

* **Không có sequence number** cho message market data (Trading Data cũng không) →
  không thể phát hiện mất message; phải tự đóng dấu `recv_ts_ns` và tự sinh identity.
* Có **snapshot đầu kết nối** không? Khi subscribe giữa phiên, có nhận được trạng thái
  hiện tại (giá khớp gần nhất, sổ lệnh hiện tại) hay phải đợi tick tiếp theo? (Có REST
  `latest-trades`/`latest-quotes` để bù, nhưng tài liệu không nói WS có replay
  snapshot.)
* Kích thước message tối đa; có nén (permessage-deflate) không.
* Hành vi khi subscribe mã không tồn tại hoặc channel sai tên — báo `error` hay im lặng.
* Có giới hạn số symbol trong một message `subscribe` không.
* WebSocket có versioning theo header `version` như REST không.
* `batch_delivery` trong `capabilities` là gì (mẫu trả `false`) — có thể là chế độ gộp
  nhiều message, nhưng không có mô tả nào.
* Ý nghĩa chính xác của `transactTime: "035200011"` ở channel `foreign`.

---

## 12. Đối chiếu nhanh DNSE vs SSI

| Tiêu chí | **DNSE** | **SSI** |
|---|---|---|
| Endpoint WS | `wss://ws-openapi.dnse.com.vn/v1/stream?encoding=…` (rõ ràng) | 2 giá trị mâu thuẫn nhau |
| Cách auth WS | HMAC-SHA256 trong message `auth`, **đặc tả đầy đủ** | **Không đặc tả** cách truyền token |
| OTP cho market data | **Không cần** (chỉ cần cho đặt lệnh) | Tài liệu tự mâu thuẫn |
| Encoding | `json` **hoặc `msgpack`** | chỉ JSON |
| Timestamp của sàn | **`{Seconds, Nanos}` — nano-giây** | chuỗi độ phân giải **giây** |
| Sequence number | không | không (kênh DATA) |
| Độ sâu sổ lệnh | HOSE 3 mức, HNX/UPCOM 10 mức | mẫu 5 mức, không cam kết |
| OHLC qua WS | có (đang hình thành + đã đóng nến) | có (`@1m`, `@5m`) |
| Kiểu số trong payload | number thật | phần lớn là **String** |
| Thông tin phiên | channel `session` + enum `eventId` đầy đủ | `market` flag (ATO/LO/ATC) |
| Giới hạn kết nối | **8 giờ/kết nối** (buộc reconnect ≥3 lần/ngày) | không nêu |
| Rate limit WS | `messages_per_second: 100`, `subscriptions_max: 100` | không nêu |
| Close code / backpressure | đặc tả rõ, có `1013` báo client chậm | không nêu |
| Chất lượng tài liệu WS | **Tốt** — có trang riêng để tự viết client | Sơ lược, nhiều lỗ hổng |

**Kết luận cho thiết kế:** DNSE là nguồn dữ liệu **dễ tích hợp đúng đắn hơn** và cho
event time nano-giây; đổi lại phải xử lý tốt vòng đời 8 giờ và giới hạn subscription.
Cả hai sàn **đều không có sequence number**, nên bài học từ `examples/` vẫn nguyên giá
trị: lưu payload thô, tự đóng dấu `recv_ts_ns` ngay khi nhận, và dùng
`(topic, partition, offset)` của Kafka làm identity.
