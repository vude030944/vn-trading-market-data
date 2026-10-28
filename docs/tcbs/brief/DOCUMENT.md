# TCBS iFlash Open API — WebSocket Data (bản chắt lọc)

> **Phạm vi:** chỉ tập trung vào **dữ liệu realtime qua WebSocket**, kèm toàn bộ phần
> xác thực và mô tả liên quan để dựng được một ingestion service. REST chỉ nhắc khi
> liên quan trực tiếp (lấy token, bù dữ liệu).
>
> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0> — tải ngày **19/08/2026**
> (phiên bản tài liệu `v1.0.0`, phát hành 31/07/2026). Bản nguyên văn đầy đủ ở
> [`../details/`](../details/) (53 trang).
>
> **Đặc thù lớn nhất:** TCBS là sàn duy nhất trong ba sàn **không dùng JSON làm khung
> message**. Wire protocol là **text frame phân tách bằng dấu `|`**, JSON chỉ nằm ở
> phần payload cuối. Và TCBS có tới **5 endpoint WebSocket khác nhau, mỗi cái một
> phương ngữ riêng** về auth, heartbeat và định dạng dữ liệu.
>
> Repo `examples/` chính là một pipeline TCBS chạy thật, nên §11 đối chiếu tài liệu
> với **bằng chứng thực nghiệm** từ đó — và tìm ra vài chỗ tài liệu thiếu/sai.

---

## Mục lục

1. [Năm endpoint WebSocket](#1-năm-endpoint-websocket)
2. [Xác thực](#2-xác-thực)
3. [Luật chung của mọi kết nối](#3-luật-chung-của-mọi-kết-nối)
4. [Nhóm `thesis` — bảng giá cơ sở & phái sinh](#4-nhóm-thesis--bảng-giá-cơ-sở--phái-sinh)
5. [Channel ID & payload — cơ sở](#5-channel-id--payload--cơ-sở)
6. [Channel ID & payload — phái sinh](#6-channel-id--payload--phái-sinh)
7. [Nhóm `ouranos` — lịch sử khớp & cung cầu](#7-nhóm-ouranos--lịch-sử-khớp--cung-cầu)
8. [Nhóm `aither` / `nesoi` — sự kiện lệnh riêng tư](#8-nhóm-aither--nesoi--sự-kiện-lệnh-riêng-tư)
9. [Bảng mã sàn / chỉ số](#9-bảng-mã-sàn--chỉ-số)
10. [Lỗi, reconnect, giờ giao dịch](#10-lỗi-reconnect-giờ-giao-dịch)
11. [Đối chiếu tài liệu với thực tế production](#11-đối-chiếu-tài-liệu-với-thực-tế-production)
12. [Điểm chưa rõ trong tài liệu](#12-điểm-chưa-rõ-trong-tài-liệu)
13. [Đối chiếu nhanh TCBS vs DNSE vs SSI](#13-đối-chiếu-nhanh-tcbs-vs-dnse-vs-ssi)

---

## Bảng nguồn — mỗi phần lấy từ file nào

| Phần | File nguyên văn trong `details/` |
|---|---|
| §1, §3, §4, §5 | [`5_chung_khoan_co_so_thi_truong/5_2_bang_gia_co_so_websocket.md`](../details/5_chung_khoan_co_so_thi_truong/5_2_bang_gia_co_so_websocket.md) |
| §2.1 | [`1_xac_thuc/1_1_trao_doi_api_key_de_lay_jwt_token.md`](../details/1_xac_thuc/1_1_trao_doi_api_key_de_lay_jwt_token.md) · [`0_bat_dau/so_do_hoat_dong.md`](../details/0_bat_dau/so_do_hoat_dong.md) |
| §6 | [`7_chung_khoan_phai_sinh_thi_truong/7_2_bang_gia_phai_sinh_websocket.md`](../details/7_chung_khoan_phai_sinh_thi_truong/7_2_bang_gia_phai_sinh_websocket.md) |
| §7 | [`5_chung_khoan_co_so_thi_truong/5_10_lich_su_gia_khop_cung_cau_websocket.md`](../details/5_chung_khoan_co_so_thi_truong/5_10_lich_su_gia_khop_cung_cau_websocket.md) |
| §8 | [`5_..._5_9_thay_doi_thong_tin_lenh_co_so_websocket.md`](../details/5_chung_khoan_co_so_thi_truong/5_9_thay_doi_thong_tin_lenh_co_so_websocket.md) · [`7_..._7_3_thay_doi_thong_tin_lenh_phai_sinh_websocket.md`](../details/7_chung_khoan_phai_sinh_thi_truong/7_3_thay_doi_thong_tin_lenh_phai_sinh_websocket.md) |
| §9 (kiểu dữ liệu) | [`0_bat_dau/kieu_du_lieu.md`](../details/0_bat_dau/kieu_du_lieu.md) |
| §11 (đối chiếu thực tế) | [`examples/`](../../../examples/) — audit 6.1 triệu message ngày 10/07/2026 |

Danh mục đầy đủ 53 trang: [`../details/README.md`](../details/README.md).

---

## 1. Năm endpoint WebSocket

| # | Endpoint | Nội dung | Auth | Heartbeat | Timeout |
|---|---|---|---|---|---|
| 1 | `/ws/thesis/v1/stream/normal` | Bảng giá **cổ phiếu cơ sở** | `d\|a\|\|\|<b64>` | `d\|p\|\|\|` | 15 s |
| 2 | `/ws/thesis/v1/stream/derivative` | Bảng giá **phái sinh** | `d\|a\|\|\|<b64>` | `d\|p\|\|\|` | 15 s |
| 3 | `/ws/ouranos/v1/stream` | **Lịch sử khớp + cung cầu** (1 phút) | `d\|a\|\|\|<b64>` | `d\|po` | 15 s |
| 4 | `/ws/aither` | Thay đổi **lệnh cơ sở** (riêng tư) | `authenticate\|<b64>` | `ping\|1` | **7 s** |
| 5 | `/ws/nesoi` | Thay đổi **lệnh phái sinh** (riêng tư) | `authenticate\|<b64>` | `ping\|1` | **45 s** |

Base: `wss://openapi.tcbs.com.vn` · REST: `https://openapi.tcbs.com.vn`

Với bài toán **thu thập dữ liệu thị trường**, ta cần endpoint **1, 2, 3**. Endpoint 4
và 5 là stream tài khoản riêng (giống `order.*` của DNSE / `TRADING` của SSI).

> 🔴 Ba giá trị timeout **khác nhau** (15 / 7 / 45 giây) và **ba cú pháp heartbeat khác
> nhau** trên cùng một nhà cung cấp. Đây là nguồn lỗi vận hành lớn nhất khi làm nhiều
> endpoint cùng lúc — đừng dùng chung một hằng số.

---

## 2. Xác thực

### 2.1. Lấy API Key và token

1. Đăng ký **miễn phí** tại <https://tcinvest.tcbs.com.vn/iflash-open-api>
   (TCInvest → menu trái → **Tiện ích** → **iFlash Open API**).
2. Đổi API Key lấy JWT:

```bash
curl -X POST https://openapi.tcbs.com.vn/gaia/v1/oauth2/openapi/token \
  -H "Content-Type: application/json" \
  -d '{"apiKey":"<API_KEY>","otp":"111111"}'
```

| Field | Mô tả |
|---|---|
| `apiKey` | API Key sinh trên TCInvest |
| `otp` | Mã OTP từ ứng dụng TCInvest (iOTP / TOTP) |

Response: `{"token":"eyJ4NXQiOiJaaWpkaFpqVmlNamMwWmdfUlMyNTYi..."}`

> ⏱ **Token có hiệu lực tối đa 8 giờ** kể từ khi xác thực iOTP. Hết hạn phải lấy mã
> mới — và **cần OTP từ app mỗi lần**. Đây là điểm bất lợi lớn nhất của TCBS cho một
> service chạy 24/7: không có refresh token, không có luồng phê duyệt tự động như
> Mobile Approval của SSI. Trên thực tế phải chuẩn bị cơ chế nạp token thủ công hoặc
> tự sinh TOTP.

### 2.2. Xác thực WebSocket — hai phương ngữ

**Nhóm `thesis` + `ouranos`** — base64 **trực tiếp** chuỗi token, không bọc JSON:

```text
d|a|||<BASE64(token)>
```

Ví dụ nguyên văn tài liệu:

| | |
|---|---|
| Token | `igwfUq9M2IqWVhrFrYybEYKWxAxDbYzxz1RzOkp0L0S95lrMtrJDbMgFwy86r8Ir` |
| Base64 | `aWd3ZlVxOU0ySXFXVmhyRnJZeWJFWUtXeEF4RGJZenh6MVJ6T2twMEwwUzk1bHJNdHJKRGJNZ0Z3eTg2cjhJcg==` |
| Gửi | `d\|a\|\|\|aWd3ZlVxOU0y...` |

Server trả về:

```text
d|0|{"success":true,"error":null}          ← thành công
d|0|{"success":false,"error":{"code":"211110","message":"Invalid JWT"}}   ← thất bại
d|33|15                                     ← cấu hình timeout heartbeat (giây)
```

**Nhóm `aither` / `nesoi`** — base64 của một **JSON object**:

```text
authenticate|<BASE64({"jwt":"<token>"})>
```

Server trả về **hai** message:

```text
pingTimeout|7            ← (aither)  hoặc  pingTimeout|45  (nesoi)
authenticate|{"success":true,"error":null}
```

> ⚠️ **PHẢI đợi response auth thành công trước khi gửi subscribe.** Gửi sớm sẽ bị
> server reject. Điều này lặp lại ở cả 5 trang tài liệu.

---

## 3. Luật chung của mọi kết nối

### 3.1. Bắt buộc tắt auto-ping của thư viện WebSocket

Đây là cảnh báo được nhắc lại ở **cả 5 trang**, và tài liệu gọi thẳng nó là
*"nguyên nhân #1 gây disconnect liên tục mà developer khó debug"*.

TCBS **chỉ chấp nhận heartbeat dạng TEXT frame**. Nếu thư viện tự gửi ping frame theo
RFC 6455 (binary control frame) → server trả **`1002 Protocol Error`** và ngắt kết nối
(trang phái sinh nói ngắt sau ~15–20 giây).

| Ngôn ngữ | Thư viện | Cách tắt |
|---|---|---|
| Python | `websockets` | `connect(url, ping_interval=None, ping_timeout=None)` |
| JavaScript | `ws` | Mặc định tắt — **đừng** dựa vào ping của thư viện |
| Go | `gorilla/websocket` | Không gọi `SetPingHandler`; tự quản lý ping |
| Java | `javax.websocket` | Cấu hình endpoint: không set ping |

### 3.2. Nhịp heartbeat

Client gửi **mỗi 2 giây** ở cả 5 endpoint. Chỉ khác nội dung frame và ngưỡng timeout:

| Endpoint | Frame | Timeout |
|---|---|---|
| thesis normal / derivative | `d\|p\|\|\|` | 15 s |
| ouranos | `d\|po` | 15 s |
| aither | `ping\|1` | **7 s** |
| nesoi | `ping\|1` | **45 s** |

`aither` chỉ cho phép trễ **7 giây** — chưa bằng 4 nhịp heartbeat. Bất kỳ GC pause hay
event-loop bị block nào cũng đủ làm rớt kết nối.

### 3.3. Phân loại message

| Prefix | Loại | Ví dụ |
|---|---|---|
| `d\|` | Control | `d\|0\|{...}` auth · `d\|33\|15` timeout · `d\|34\|1` ack subscribe · `d\|p\|\|\|` pong |
| `s\|` | Data (thesis) | `s\|<CHANNEL_ID>\|<JSON>` |
| `CODE\|SYMBOL\|` | Data (ouranos) | `C001\|TCB\|{...}` |
| `message_proto\|TOPIC\|` | Data (aither/nesoi) | `message_proto\|DE_ORDER\|{...}` |

---

## 4. Nhóm `thesis` — bảng giá cơ sở & phái sinh

### 4.1. Subscribe

```text
d|s|<objectType>|<properties>|<object list>
```

| objectType | Ý nghĩa | Ví dụ |
|---|---|---|
| `tk` | Theo **mã** chứng khoán | `d\|s\|tk\|bp+bi+tm+mp+op+fe\|FPT,VCS,PNJ,PTB` |
| `ro` | Theo **sàn** | `d\|s\|ro\|bp+bi+tm+mp+op+fe\|1,2` |
| `si` | Theo **chỉ số** | `d\|s\|si\|rt\|1,2` |
| `pt` | Giao dịch **thỏa thuận** | `d\|s\|pt\|ptm+ptb+pts\|1,2,3` |

**Channel code → Channel ID (cơ sở):**

| Code | Ý nghĩa | Channel ID |
|---|---|---|
| `bi` | Sổ lệnh mua | `s\|1` |
| `op` | Sổ lệnh bán | `s\|2` |
| `fe` | Khối ngoại | `s\|3` |
| `bp` | Giá trần/sàn/tham chiếu | `s\|4` |
| `mp` | Thông tin phiên | `s\|5` |
| `tm` | Giao dịch khớp | `s\|6` |
| `tmh` | **Lịch sử khớp trong ngày** | `s\|22` |

### 4.2. Unsubscribe

Đổi action `s` → `u`, cú pháp giữ nguyên: `d|u|tk|bp+bi+tm+mp+op+fe|TCB,VCB`.
Có thể huỷ **một phần** danh sách mã; các mã còn lại vẫn tiếp tục chảy dữ liệu.

### 4.3. Snapshot một lần (request)

```text
d|r|<objectType>||<object list>
```

Lưu ý **hai dấu pipe liên tiếp** (`properties` để trống). Ví dụ `d|r|tk||TCB,VCB` →
server trả channel **`s|38`** (Tickers snapshot) chứa toàn bộ trạng thái hiện tại.

> 💡 Đây là cơ chế **duy nhất** để đồng bộ lại state sau reconnect mà không phải chờ
> tick tiếp theo. Cả SSI lẫn DNSE đều **không có** thứ tương đương trên WebSocket.
> Rất đáng dùng ngay sau mỗi lần reconnect.

### 4.4. `tmh` — backfill lịch sử khớp trong ngày

Khi subscribe kèm `tmh`, server **push toàn bộ lịch sử khớp lệnh trong ngày** (backfill)
rồi mới tiếp tục realtime. Kết hợp với `d|r` snapshot, đây là hai công cụ giúp
reconnect không mất dữ liệu.

---

## 5. Channel ID & payload — cơ sở

> 🔴 **Giá và khối lượng của cổ phiếu cơ sở trả về dạng `string`**, còn `change`,
> `changePercent`, và toàn bộ channel 4/5/8/16/17 lại là `number`. Không nhất quán
> ngay trong cùng một endpoint.

### `s|1` — Bid Info (sổ lệnh mua top 3)

```text
s|1|{"symbol":"TCB","bidPrice01":"24550","bidPrice02":"24500","bidPrice03":"24450","bidQtty01":"137200","bidQtty02":"354000","bidQtty03":"292900"}
```
`symbol`, `bidPrice01..03`, `bidQtty01..03` — tất cả **string**.

### `s|2` — Offer Info (sổ lệnh bán top 3)

`symbol`, `offerPrice01..03`, `offerQtty01..03` — **string**.

### `s|3` — Foreign Exchange (khối ngoại)

```text
s|3|{"symbol":"HPG","buyForeignQtty":"112400","sellForeignQtty":"17380","room":"1773708397"}
```
`buyForeignQtty`, `sellForeignQtty`, `room` — **string**.

### `s|4` — Base Price (trần/sàn/tham chiếu)

```text
s|4|{"symbol":"VPD","ceilPrice":25000,"floorPrice":24100,"refPrice":24300}
```
`ceilPrice`, `floorPrice`, `refPrice` — **number**.

### `s|5` — Matched Price (thông tin phiên)

```text
s|5|{"symbol":"VPD","high":25000,"low":24100,"avg":24300.0,"open":24600}
```
`high`, `low`, `avg`, `open` — **number**.

### `s|6` — Ticker Match (giao dịch khớp) — kênh quan trọng nhất

```text
s|6|{"symbol":"TCB","matchPrice":"24550","matchQtty":"5000","change":200.0,"changePercent":0.8213552361396304,"totalVolume":"9745500","totalValue":"240774655000"}
```

| Field | Kiểu | Mô tả |
|---|---|---|
| `symbol` | string | Mã chứng khoán |
| `matchPrice` | **string** | Giá khớp |
| `matchQtty` | **string** | Khối lượng khớp |
| `change` | number | Thay đổi so với tham chiếu |
| `changePercent` | number | % thay đổi |
| `totalVolume` | **string** | Tổng KL khớp trong phiên |
| `totalValue` | **string** | Tổng giá trị giao dịch (VND) |

> ⚠️ Không có trường **chiều mua/bán chủ động** ở `s|6`. Muốn có thông tin đó phải
> dùng `ouranos` C001 (`action`: BU/SD) — xem §7.

### `s|8` — Stock Index (chỉ số)

```text
s|8|{"indexNumber":5,"index":91.43,"change":1.75,"changePercent":1.96,"volume":5.5936E7,"value":7.287094199E11,"increase":246,"decrease":58,"notChange":63,"session":"5","ceilIncrease":19,"floorDecrease":8}
```

`indexNumber` (mã chỉ số), `index`, `change`, `changePercent`, `volume`, `value`,
`increase`/`decrease`/`notChange` (độ rộng thị trường), `session`,
`ceilIncrease`/`floorDecrease` (số mã trần/sàn).

> Lưu ý số dạng **ký hiệu khoa học** (`5.5936E7`) — parser JSON chuẩn xử lý được,
> nhưng nếu dùng regex/xử lý chuỗi thì sẽ vỡ.

### `s|16` — PT Advertisement (chào mua/bán thỏa thuận)

```text
s|16|{"symbol":"VIC124003","price":1.00528E8,"vol":1000.0,"time":"20250808-04:10:33.917","status":1,"color":5,"orderId":"92025080800181048","side":"B"}
```
`side`: `B` (mua) / `S` (bán). Định dạng `time` ở đây là `yyyyMMdd-HH:mm:ss.SSS` —
**khác** mọi channel còn lại.

### `s|17` — PT Match (khớp thỏa thuận)

```text
s|17|{"symbol":"VND","price":23500.0,"vol":200000.0,"val":4.7E9,"time":"10:56:50","color":4,"accumulatedValue":4.7E9}
```
`time` ở đây lại là `HH:mm:ss`.

### `s|22` — Ticker Match History (`tmh`)

```text
s|22|{"symbol":"TCB","time":"14:29:30","matchPrice":"24550","matchQtty":"5000","change":200.0}
```

### `s|38` — Tickers snapshot (trả lời `d|r`)

---

## 6. Channel ID & payload — phái sinh

Endpoint `/ws/thesis/v1/stream/derivative`. Subscribe cùng cú pháp `d|s|tk|...`.

| Code | Ý nghĩa | Channel ID |
|---|---|---|
| `tm` | Giao dịch khớp | `s\|21` |
| `bi` | Sổ lệnh mua | `s\|23` |
| `op` | Sổ lệnh bán | `s\|24` |
| `mp` | Thông tin phiên | `s\|27` |
| `bp`, `fe` | **Được chấp nhận nhưng không phát frame nào** | — |

```text
s|21|{"symbol":"41I1G8000","matchPrice":1870.5,"matchQtty":2,"change":-4.5,"changePercent":-0.24,"totalVolume":15234}
```

### Bảng đối chiếu channel ID (nguyên văn tài liệu)

| Dữ liệu | Cơ sở (`/stream/normal`) | Phái sinh (`/stream/derivative`) |
|---|---|---|
| Bid info | `s\|1` | `s\|23` |
| Offer info | `s\|2` | `s\|24` |
| Foreign exchange | `s\|3` | — |
| Base price | `s\|4` | — |
| Matched / day summary | `s\|5` | `s\|27` |
| Ticker match | `s\|6` | `s\|21` |
| Stock index | `s\|8` | — |

> 🔴 Cảnh báo nguyên văn: *"Channel ID hoàn toàn khác giữa 2 endpoint, và data type
> cũng khác (cổ phiếu trả string cho giá/khối lượng, phái sinh trả number). **KHÔNG
> dùng chung parser** cho cổ phiếu và phái sinh."*
>
> Nhưng bảng này **chưa đầy đủ** so với thực tế production — xem [§11.1](#111-tài-liệu-thiếu-hẳn-nhiều-wire-code-đang-chạy-thật).

---

## 7. Nhóm `ouranos` — lịch sử khớp & cung cầu

Endpoint `/ws/ouranos/v1/stream`. Đây là nguồn dữ liệu **giá trị nhất** của TCBS cho
phân tích dòng tiền, vì nó có **event time thật từ sàn** và **chiều mua/bán chủ động**.

### 7.1. Subscribe

```text
d|st|<code1+code2+...>|<ticker1,ticker2,...>      ← đăng ký
d|ut|<code1+code2+...>|<ticker1,ticker2,...>      ← huỷ
```

Ví dụ: `d|st|C001+C002S60+C002S900|POW,TCB,VIC`

| Code | Tài liệu mô tả | Chu kỳ |
|---|---|---|
| `C001` | Lịch sử giá khớp | 1 phút |
| `C002S60` | Cung cầu tích luỹ | 1 phút |
| `C002S900` | *"Giao dịch khối ngoại"* — **mô tả SAI**, xem [§11.3](#113-c002s900-bị-đặt-tên-sai) | 15 phút |

### 7.2. Định dạng data

```text
<CODE>|<SYMBOL>|{JSON}
```

Khác hẳn nhóm `thesis`: **symbol nằm ngay trong khung message**, không cần đọc payload
để biết mã. Rất tiện cho việc chọn partition key khi đẩy vào Kafka.

### 7.3. `C001` — lịch sử giá khớp

```text
C001|TCB|{"symbol":"TCB","closePrice":38600.0,"closeVol":1000.0,"change":1100.0,"reference":37500.0,"totalTrading":2.42776E7,"totalTradingValue":9.3340061E11,"timeSec":"1755144180","action":"SD","unitTimeFrame":"60","tradingValue":3.86E7,"buyUpAcc":1.51419E7,"sellDownAcc":8481600.0,"bidPrice":38600.0,"bidVol":34100.0,"askPrice":38650.0,"askVol":89600.0,"prevChange":1100.0}
```

| Field | Kiểu | Mô tả |
|---|---|---|
| `symbol` | string | Mã chứng khoán |
| `closePrice` / `closeVol` | number | Giá khớp / KL khớp trong 1 phút |
| `change` / `prevChange` | number | Thay đổi so với tham chiếu / so với khớp gần nhất |
| `reference` | number | Giá tham chiếu |
| `totalTrading` / `totalTradingValue` | number | Tổng KL / GT trong ngày |
| **`timeSec`** | **string** | **Thời gian epoch giây — event time THẬT từ sàn** |
| **`action`** | string | **`BU` = mua chủ động, `SD` = bán chủ động** |
| `unitTimeFrame` | string | Khung thời gian (giây): `60` |
| `tradingValue` | number | Giá trị khớp trong 1 phút |
| `buyUpAcc` / `sellDownAcc` | number | KL mua/bán chủ động **tích luỹ** |
| `bidPrice` / `bidVol` | number | Giá & KL đặt mua tốt nhất |
| `askPrice` / `askVol` | number | Giá & KL đặt bán tốt nhất |

> 🟢 `timeSec` là **trường thời gian duy nhất của TCBS mang epoch từ sàn**. Toàn bộ
> nhóm `thesis` chỉ có chuỗi `HH:mm:ss` (channel 22/17) hoặc **không có thời gian gì
> cả** (channel 1–8). Nghĩa là: với bảng giá `thesis`, ta **bắt buộc** phải tự đóng dấu
> `recv_ts_ns` lúc nhận — đúng như pipeline trong `examples/` đang làm.

### 7.4. `C002S60` / `C002S900` — cung cầu

```text
C002S60|TCB|{"symbol":"TCB","timeSec":"1755144120","totalBUVol":200.0,"totalBUVolAcc":1.51419E7,"totalSDVol":49700.0,"totalSDVolAcc":8480600.0,"bsAccRatio":0.6409948,"unitTimeFrame":"60"}
```

| Field | Mô tả |
|---|---|
| `totalBUVol` / `totalSDVol` | KL mua / bán chủ động trong khung |
| `totalBUVolAcc` / `totalSDVolAcc` | Tích luỹ từ đầu ngày |
| `bsAccRatio` | Tỷ lệ mua/bán chủ động tích luỹ (0–1) |
| `unitTimeFrame` | `60` hoặc `900` |

Hai channel **cùng schema**, chỉ khác `unitTimeFrame`.

---

## 8. Nhóm `aither` / `nesoi` — sự kiện lệnh riêng tư

Không thuộc "market data" nhưng cần cho hệ thống trading đầy đủ.

| | `/ws/aither` (cơ sở) | `/ws/nesoi` (phái sinh) |
|---|---|---|
| Auth | `authenticate\|base64({"jwt":token})` | như bên trái |
| Timeout | `pingTimeout\|7` | `pingTimeout\|45` |
| Heartbeat | `ping\|1` mỗi 2 s | như bên trái |
| Data | `message_proto\|TOPIC\|{JSON}` | như bên trái |
| Topic | `STOCK_ORDER` | `DE_ORDER`, `DE_CONDITIONAL_ORDER`, `DE_OPEN_POSITION` |

Subscribe bằng base64 của `{"topic":"<TÊN>"}`:

| Topic | Chuỗi subscribe |
|---|---|
| `STOCK_ORDER` | `subscribe\|eyJ0b3BpYyI6IlNUT0NLX09SREVSIn0=` |
| `DE_ORDER` | `subscribe\|eyJ0b3BpYyI6IkRFX09SREVSIn0=` |
| `DE_CONDITIONAL_ORDER` | `subscribe\|eyJ0b3BpYyI6IkRFX0NPTkRJVElPTkFMX09SREVSIn0=` |
| `DE_OPEN_POSITION` | `subscribe\|eyJ0b3BpYyI6IkRFX09QRU5fUE9TSVRJT04ifQ==` |

Ví dụ payload `DE_ORDER`:

```text
message_proto|DE_ORDER|{"subAccount":"738764A","orderNo":"41","pkOrderNo":"7861546","orderTime":"14:34:10","accountCode":"738764A","side":"B","symbol":"VN30F2110","volume":1,"showPrice":"MTL","status":"P","orderStatus":"2","channel":"D","group":"FU","isCancel":"1","isAmend":"1"}
```

---

## 9. Bảng mã sàn / chỉ số

Dùng cho `ro` (theo sàn) và `si` (theo chỉ số):

| Mã | Sàn / Chỉ số |
|---|---|
| `1` | VN-INDEX |
| `2` | VN30-INDEX |
| `3` | HNX |
| `4` | HNX30-INDEX |
| `5` | UPCOM |
| `7` | Covered warrant |
| `8` | Derivative-VN30 |
| `9` | Derivative-VGB5 |

Với `pt` (thỏa thuận): `1` = HOSE, `2` = HNX, `3` = UPCOM.

### Quy ước kiểu dữ liệu chung của API

| Kiểu | Ghi chú |
|---|---|
| `int64` | ID, **số tiền (VND)**, giá, khối lượng — **luôn số nguyên, không thập phân** |
| `number` | Tỷ lệ, phần trăm, lãi suất |
| `date` / `datetime` | `yyyy-MM-dd` / ISO 8601 kèm timezone |

* **Field `null` không xuất hiện trong JSON** — parser phải chịu được field thiếu.
* Timezone mặc định **Asia/Ho_Chi_Minh (+07:00)**.

---

## 10. Lỗi, reconnect, giờ giao dịch

### Nguyên nhân disconnect (nguyên văn)

| Nguyên nhân | Triệu chứng | Giải pháp |
|---|---|---|
| Không heartbeat > timeout | Close `1000` | Kiểm tra task heartbeat |
| Thư viện gửi RFC ping | **Error `1002`** | Tắt auto-ping |
| Token hết hạn | `d\|0\|{"error":...}` | Lấy token mới, reconnect |
| Server bảo trì | Connection refused | Exponential backoff |
| Ngoài giờ giao dịch | Connect OK, **không có data** | Bình thường — chờ phiên mở |

### Reconnect

`delay = min(2^attempt, 30)` giây, tối đa **10 lần** rồi dừng và alert:
`1s → 2s → 4s → 8s → 16s → 30s...`

### Giờ giao dịch

Phiên cơ sở **9:00–11:30** và **13:00–14:45**, ATC đến ~**14:45–15:00** tuỳ sàn.

> Ngoài giờ: kết nối vẫn mở, **heartbeat vẫn phải gửi**, nhưng không có data message.
> Khi phiên mở lại data tự chảy — **không cần reconnect**. → Cảnh báo "feed stale"
> phải tính theo lịch phiên, không báo động cả ngày.

---

## 11. Đối chiếu tài liệu với thực tế production

Repo [`examples/`](../../../examples/) là một pipeline TCBS đã chạy thật và có
**audit toàn bộ lịch sử topic Kafka (6.1 triệu message, 10/07/2026)**. Đối chiếu với
tài liệu `v1.0.0` (phát hành 31/07/2026) cho ra mấy điểm sau.

### 11.1. Tài liệu thiếu hẳn nhiều wire code đang chạy thật

Bảng đối chiếu channel ở §6 chỉ liệt kê 7 dòng. Thực tế quan sát được:

| Wire code | Thực tế (từ audit) | Có trong tài liệu? |
|---|---|---|
| `s\|18`, `s\|28`, `s\|29`, `s\|30`, `s\|32` | **Chứng quyền (covered warrant)** — ticker match / bid / offer / foreign / matched price | ❌ **Không hề nhắc** |
| `s\|25` | Foreign của **phái sinh** (chỉ buy/sell, không có `room`) | ❌ Bảng ghi "—" |
| `s\|42` | **Sổ lệnh 10 mức (depth book)** của phái sinh — chiếm ~94% traffic topic future | ❌ **Không hề nhắc** |
| `s\|22`, `s\|38` | Có mô tả ở trang cơ sở | ⚠️ Thiếu trong bảng đối chiếu |

> `s|42` mở khoá bằng cách thêm code `dtn` vào subscribe (`bp+bi+tm+mp+op+fe+dtn`) —
> **hoàn toàn không có trong tài liệu**, chỉ biết được từ code `examples/`. Đây là kênh
> dữ liệu **lớn nhất và giá trị nhất** của phái sinh mà tài liệu bỏ sót.

### 11.2. Family phái sinh được phát trên CẢ HAI endpoint

Audit chéo cho thấy TCBS phát các wire `21/23/24/25/27` **byte-identical trên cả
`/stream/normal` lẫn `/stream/derivative`**, và bản trên socket **normal đến sớm hơn
~1 ms (median)**. Tài liệu không nhắc gì về chuyện này.

→ Hệ quả: nếu subscribe cả hai endpoint, bạn sẽ **nhận trùng** toàn bộ family phái
sinh cơ bản và phải tự khử. `examples/` xử lý bằng cách lấy bản từ topic stock và drop
bản từ topic future.

### 11.3. `C002S900` bị đặt tên sai

Tài liệu ghi `C002S900` = *"Giao dịch khối ngoại (15 phút)"*. Nhưng **schema của nó
giống hệt `C002S60`** — toàn bộ field là `totalBUVol`, `totalSDVol`, `bsAccRatio`, tức
**cung cầu mua/bán chủ động**, không liên quan gì tới khối ngoại. Ngay chính payload
mẫu trong tài liệu cũng chứng minh điều đó.

→ Đúng ra: `C002S900` = **cung cầu khung 15 phút** (`unitTimeFrame: "900"`).
`examples/` gọi nó là `ouranos_supply_demand` — chính xác hơn tài liệu.

### 11.4. Con số timeout của ouranos không khớp

Tài liệu nói ouranos gửi `d|33|15`. Thăm dò thực tế trong `examples/`
(`tests/ouranos_probe.py`) ghi nhận **`d|33|30`**, và ngoài ra **server còn tự gửi ping
`d|pi` mỗi ~10 giây** — điều tài liệu **không hề nhắc**.

→ Client nên xử lý được cả `d|pi` (bỏ qua hoặc đáp) và **đọc giá trị timeout từ frame
`d|33|` thay vì hardcode 15**.

### 11.5. Wire code có trong tài liệu nhưng chưa từng xuất hiện

`s|16` (PT Advertisement) được tài liệu mô tả đầy đủ, nhưng audit **6.1 triệu message
không tìm thấy message nào**. Bảng dữ liệu tương ứng cũng rỗng suốt 3 ngày chạy thử.
Có thể TCBS không còn phát kênh này.

### 11.6. Một frame = một message (tính chất thực nghiệm)

Audit toàn bộ lịch sử topic cho thấy TCBS gửi **đúng 1 frame mỗi WebSocket message**
(3.05 triệu message, không có `recv_ts_ns` trùng). Nhưng đây là **quan sát, không phải
cam kết** — tài liệu không nói gì về việc có ghép nhiều frame trong một message hay
không, nên bộ tách frame vẫn nên giữ.

---

## 12. Điểm chưa rõ trong tài liệu

* **Không có sequence number** ở bất kỳ channel nào → không phát hiện được mất message.
* **Không có timestamp từ sàn** ở toàn bộ nhóm `thesis` (channel 1–8). Chỉ `s|22` và
  `s|17` có `HH:mm:ss` (không có ngày), `s|16` có `yyyyMMdd-HH:mm:ss.SSS`, và chỉ
  `ouranos` có epoch thật. → **Bắt buộc tự đóng dấu thời gian nhận.**
* **Không công bố rate limit** cho WebSocket: bao nhiêu kết nối đồng thời, bao nhiêu mã
  tối đa mỗi subscribe, có giới hạn tổng số mã không.
* **Không mô tả hành vi khi subscribe mã không tồn tại** — báo lỗi hay im lặng.
* **Không nói có snapshot khi mới subscribe** cho nhóm `thesis` (ngoài `tmh` backfill và
  `d|r` request). Với `ouranos` cũng không rõ.
* **Không có refresh token.** Token 8 giờ, hết hạn phải làm lại OTP từ app → chưa rõ
  cách tự động hoá hoàn toàn.
* **Ý nghĩa `color`, `status` ở `s|16`/`s|17`** chỉ ghi "Màu", "Trạng thái" mà không
  liệt kê giá trị.
* **`session` ở `s|8`** là string (`"5"`) nhưng không có bảng giá trị.
* Không nói `d|34|N` (ack subscribe) có ý nghĩa gì ở phần `N`.

---

## 13. Đối chiếu nhanh TCBS vs DNSE vs SSI

| Tiêu chí | **TCBS** | **DNSE** | **SSI** |
|---|---|---|---|
| Khung message | **Text pipe-delimited** | JSON / msgpack | JSON |
| Số endpoint WS | **5** (mỗi cái một phương ngữ) | 1 | 1 |
| Auth WS | 2 kiểu: `d\|a\|\|\|b64` và `authenticate\|b64(json)` | HMAC-SHA256 message | **không đặc tả** |
| OTP cho market data | **Cần** (token 8 h, không refresh token) | Không cần | Tài liệu mâu thuẫn |
| Timestamp từ sàn | Chỉ `ouranos` (epoch giây); `thesis` **không có** | **`{Seconds, Nanos}` nano-giây** | chuỗi độ phân giải giây |
| Sequence number | không | không | không |
| Độ sâu sổ lệnh | 3 mức (`s\|1/2`); **10 mức** qua `s\|42` (không tài liệu) | HOSE 3 / HNX-UPCOM 10 | mẫu 5 mức |
| Mua/bán chủ động | `ouranos` C001 `action` BU/SD | `tick_extra.side` | `trade.si` B/S |
| Snapshot khi reconnect | **Có** (`d\|r` → `s\|38`, `tmh` backfill) | không | không |
| Heartbeat | **3 cú pháp, 3 timeout khác nhau** | `ping`/`pong` app-level, 3 phút | PING/PONG, chu kỳ không nêu |
| Giới hạn kết nối | không nêu | **8 giờ/kết nối** | không nêu |
| Rate limit WS | không nêu | 100 msg/s, 100 sub | không nêu |
| Chất lượng tài liệu WS | **Tốt về chi tiết** (có code mẫu, bảng lỗi, sequence diagram) nhưng **thiếu nhiều kênh đang chạy thật** | Tốt và nhất quán | Sơ lược, nhiều lỗ hổng |

**Kết luận cho thiết kế:**

* TCBS có **dữ liệu phong phú nhất** trong ba sàn (chứng quyền, thỏa thuận, depth 10
  mức, cung cầu chủ động theo phút) nhưng **tài liệu không phản ánh hết** — bắt buộc
  phải audit thực tế như `examples/` đã làm.
* TCBS là sàn **duy nhất có cơ chế snapshot/backfill**, nên reconnect ít mất dữ liệu
  hơn — bù lại vòng đời token 8 giờ kèm OTP là điểm yếu vận hành lớn nhất.
* Cả ba sàn **đều không có sequence number**. Kết luận chung không đổi: lưu payload
  thô byte-for-byte, tự đóng dấu `recv_ts_ns` ngay khi nhận, và dùng
  `(topic, partition, offset)` của Kafka làm identity.
