<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/ws-price-board
Tieu de goc: 5.2. Bảng giá cơ sở (WebSocket)
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/ws-price-board>

# 5.2. Bảng giá cơ sở (WebSocket)

Nhận bảng giá cổ phiếu cơ sở (HOSE, HNX, UPCOM) theo thời gian thực qua WebSocket. Bạn chỉ cần mở một kết nối duy nhất — server sẽ tự động đẩy dữ liệu mỗi khi có thay đổi. Dữ liệu bao gồm:

  * Sổ lệnh mua/bán top 3 (bid/offer)
  * Giá khớp, khối lượng khớp
  * Giá trần, sàn, tham chiếu
  * Room khối ngoại
  * Chỉ số (VN-INDEX, VN30...)
  * Giao dịch thỏa thuận

Trang này dành cho cổ phiếu cơ sở (endpoint `/stream/normal`). Nếu bạn cần bảng giá phái sinh, xem trang 7.2 — endpoint, channel ID và data type đều khác.

## Demo tương tác

Địa chỉ WSS

`WSSwss://openapi.tcbs.com.vn/ws/thesis/v1/stream/normal`

Payload kết nối / xác thực
```json
{
  "note": "Conceptual only — real auth is pipe-delimited: d|a|||[base64_token]",
  "format": "d|a|||[BASE64_JWT]"
}
```

Kênh / Chủ đề

  * `s|1 (bid info)`Sổ lệnh mua top 3: giá và khối lượng.
  * `s|2 (offer info)`Sổ lệnh bán top 3: giá và khối lượng.
  * `s|3 (foreign)`Khối lượng mua/bán khối ngoại và room còn lại.
  * `s|4 (base price)`Giá trần, sàn, tham chiếu.
  * `s|5 (matched price)`Thông tin phiên: cao, thấp, trung bình, mở cửa.
  * `s|6 (ticker match)`Giao dịch khớp: giá, khối lượng, thay đổi.

Đã ngắt

Kết nốiXóa

// Nhấn Kết nối để bắt đầu luồng mô phỏng…

⚠️ Demo trên chỉ mang tính minh họa. Protocol thực tế trên wire là TEXT frame phân tách bằng pipe (|), KHÔNG phải JSON. Xem các phần bên dưới để biết chi tiết format thật.

* * *

## Kết nối

WSS`/ws/thesis/v1/stream/normal`

Địa chỉ đầy đủ để kết nối:
```text
wss://openapi.tcbs.com.vn/ws/thesis/v1/stream/normal
```

⚠️ BẮT BUỘC: Phải disable auto-ping (RFC 6455 ping frame) của WebSocket library. Server TCBS chỉ chấp nhận heartbeat dạng text frame d|p|||. Nếu library tự gửi binary ping → server trả 1002 Protocol Error và ngắt kết nối.

Cách disable auto-ping theo từng ngôn ngữ:

| Ngôn ngữ | Thư viện | Disable auto-ping |
|---|---|---|
| Python | `websockets` | `connect(url, ping_interval=None, ping_timeout=None)` |
| JavaScript | `ws` | Default off — do NOT rely on library ping |
| Go | `gorilla/websocket` | Do not call `SetPingHandler`; manage ping manually |
| Java | `javax.websocket` | Endpoint config: do not set ping |

* * *

## Xác thực (Authentication)

Sau khi kết nối WebSocket thành công, bạn phải gửi auth message trước khi subscribe bất kỳ kênh nào. Token OpenAPI cần được **base64 encode** trước khi gửi. Format auth message gửi tới server (`xxx` = base64 của token_openapi):
```text
d|a|||xxx
```

Ví dụ cụ thể với một token thực tế:

Token OpenAPI`igwfUq9M2IqWVhrFrYybEYKWxAxDbYzxz1RzOkp0L0S95lrMtrJDbMgFwy86r8Ir`

Base64(token)`aWd3ZlVxOU0ySXFXVmhyRnJZeWJFWUtXeEF4RGJZenh6MVJ6T2twMEwwUzk1bHJNdHJKRGJNZ0Z3eTg2cjhJcg==`

Message gửi server`d|a|||aWd3ZlVxOU0ySXFXVmhyRnJZeWJFWUtXeEF4RGJZenh6MVJ6T2twMEwwUzk1bHJNdHJKRGJNZ0Z3eTg2cjhJcg==`

Nếu auth thành công, server trả về:
```text
d|0|{"success":true,"error":null}
```

Nếu auth thất bại, server trả về:
```text
d|0|{"success":false,"error":{"code":"211110","message":"Invalid JWT"}}
```

Ngoài ra, server cũng gửi bản tin cấu hình timeout `d|33|15` — nghĩa là nếu client không gửi heartbeat trong 15 giây thì kết nối sẽ bị ngắt.
```text
d|33|15
```

⚠️ PHẢI đợi nhận response auth (d|0|{...success:true...}) trước khi gửi subscribe. Gửi subscribe ngay mà không đợi → có thể bị server reject.

PythonNode.js

Sao chép
```python
import base64

token = "igwfUq9M2IqWVhrFrYybEYKWxAxDbYzxz1RzOkp0L0S95lrMtrJDbMgFwy86r8Ir"
encoded = base64.b64encode(token.encode()).decode()
auth_message = f"d|a|||{encoded}"

await ws.send(auth_message)

# Wait for response: d|0|{"success":true,"error":null}
response = await ws.recv()
```

* * *

## Đăng ký kênh (Subscribe)

Sau khi auth thành công, bạn có 4 cách đăng ký dữ liệu tuỳ nhu cầu: theo mã, theo sàn, theo chỉ số, và theo thỏa thuận.

### 1\. Theo mã cổ phiếu (tk)

Message subscribe theo mã gửi tới server:
```text
d|s|tk|bp+bi+tm+mp+op+fe|<SYMBOLS>
```

Ví dụ: `d|s|tk|bp+bi+tm+mp+op+fe|FPT,VCS,PNJ,PTB` Bảng channel codes tương ứng với channel ID mà server trả về:

| Code | Ý nghĩa | Channel ID |
|---|---|---|
| `bi` | Sổ lệnh mua | `s\|1` |
| `op` | Sổ lệnh bán | `s\|2` |
| `fe` | Khối ngoại | `s\|3` |
| `bp` | Giá trần-sàn-tham chiếu | `s\|4` |
| `mp` | Thông tin phiên | `s\|5` |
| `tm` | Giao dịch khớp | `s\|6` |
| `tmh` | Lịch sử khớp trong ngày | `s\|22` |

### 2\. Theo sàn (ro)

Message subscribe theo sàn gửi tới server:
```text
d|s|ro|bp+bi+tm+mp+op+fe|<BOARDS>
```

Ví dụ: `d|s|ro|bp+bi+tm+mp+op+fe|1,2` — server sẽ trả về các channel s|1, s|2, s|3, s|4, s|5, s|6 như trên.

### 3\. Theo chỉ số (si)

Message subscribe theo chỉ số gửi tới server:
```text
d|s|si|rt|<BOARDS>
```

Ví dụ: `d|s|si|rt|1,2` — server trả về channel s|8 (rt / stock index). Bảng mã sàn / chỉ số (dùng cho cả `ro` và `si`):

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

### 4\. Theo giao dịch thỏa thuận (pt)

Message subscribe thỏa thuận gửi tới server:
```text
d|s|pt|ptm+ptb+pts|<FLOORS>
```

Ví dụ: `d|s|pt|ptm+ptb+pts|1,2,3` — server trả về channel s|16 (pta) và s|17 (ptm). Mã sàn: 1-HOSE, 2-HNX, 3-UPCOM.

* * *

## Huỷ đăng ký (Unsubscribe)

Để huỷ đăng ký, bạn dùng action `u` thay vì `s`. Cú pháp giống hoàn toàn lệnh subscribe. Format chung của message unsubscribe gửi tới server:
```text
d|u|<objectType>|<properties>|<object list>
```

### Ví dụ

Huỷ theo mã — message gửi tới server:
```text
d|u|tk|bp+bi+tm+mp+op+fe|TCB,VCB
```

Huỷ theo sàn — message gửi tới server:
```text
d|u|ro|bp+bi+tm+mp+op+fe|1,2
```

Huỷ theo chỉ số — message gửi tới server:
```text
d|u|si|rt|1,2
```

Huỷ giao dịch thỏa thuận — message gửi tới server:
```text
d|u|pt|ptm+ptb+pts|1,2,3
```

Bạn có thể unsubscribe một phần mã. Ví dụ đang subscribe FPT,TCB,VCB mà muốn bỏ TCB → gửi `d|u|tk|bp+bi+tm+mp+op+fe|TCB`. Hai mã còn lại (FPT, VCB) vẫn tiếp tục nhận dữ liệu.

* * *

## Lấy dữ liệu snapshot (Request)

Ngoài subscribe (nhận realtime liên tục), bạn có thể gửi lệnh **request** để lấy snapshot hiện tại một lần duy nhất mà không cần subscribe. Dùng action `r`. Format message request gửi tới server (lưu ý phần `properties` để trống — 2 dấu pipe liên tiếp `||`):
```text
d|r|<objectType>||<object list>
```

### Ví dụ

Request snapshot theo mã — message gửi tới server:
```text
d|r|tk||TCB,VCB
```

Server trả về channel `s|38` (Tickers snapshot) chứa toàn bộ thông tin hiện tại của các mã bạn yêu cầu. Request snapshot theo sàn — message gửi tới server:
```text
d|r|ro||2
```

Server trả về snapshot toàn bộ mã trong sàn VN30.

Request chỉ trả về 1 lần (one-shot). Nếu bạn cần dữ liệu liên tục, hãy dùng subscribe. Request hữu ích khi khởi tạo UI hoặc đồng bộ lại state sau reconnect.

* * *

## Lịch sử khớp trong ngày — tmh (Ticker Match History)

Ngoài các channel cơ bản (bi, op, fe, bp, mp, tm), bạn có thể subscribe thêm `tmh` để nhận lịch sử khớp lệnh trong ngày (tick-by-tick). Ví dụ subscribe có thêm tmh — message gửi tới server:
```text
d|s|tk|bp+bi+tm+tmh+mp+op+fe|TCB,FPT
```

Khi subscribe `tmh`, server trả về channel `s|22` (TickerMatchHis) chứa lịch sử khớp lệnh trong ngày cho mỗi mã.

### Channel 22 — Ticker Match History (tmh)
```text
s|22|{"symbol":"TCB","time":"14:29:30","matchPrice":"24550","matchQtty":"5000","change":200.0}
```

Channel 22 — Ticker Match History (tmh)

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `symbol` | string |  | Mã chứng khoán. |
| `time` | string |  | Thời gian khớp (HH:mm:ss). |
| `matchPrice` | string |  | Giá khớp. |
| `matchQtty` | string |  | Khối lượng khớp. |
| `change` | number |  | Thay đổi so với tham chiếu. |

Khi mới subscribe, server sẽ push toàn bộ lịch sử khớp lệnh trong ngày (backfill). Sau đó tiếp tục push realtime mỗi khi có khớp mới.

* * *

## Heartbeat — Giữ kết nối

Client PHẢI gửi heartbeat text frame mỗi **2 giây**. Nếu server không nhận heartbeat trong **15 giây** → ngắt kết nối. Message heartbeat gửi tới server:
```text
d|p|||
```

⚠️ Heartbeat phải là TEXT frame, KHÔNG phải binary/ping frame. Đây là nguyên nhân #1 gây disconnect liên tục mà developer khó debug.

* * *

## Cấu trúc Message

Server gửi 2 loại message, phân biệt qua prefix:

| Prefix | Loại | Mô tả |
|---|---|---|
| `d\|` | Control | Auth response, timeout config, heartbeat pong, subscription ack |
| `s\|` | Data | Subscription data (orderbook, trade, index...) |

Các control message thường gặp từ server:

| Message | Mô tả |
|---|---|
| `d\|0\|{...}` | Phản hồi xác thực (auth response). |
| `d\|33\|15` | Cấu hình timeout heartbeat (15 giây). |
| `d\|34\|1` | Xác nhận subscribe thành công. Xuất hiện sau mỗi lệnh subscribe. |
| `d\|p\|\|\|` | Heartbeat pong từ server. |

Format data message mà server trả về:
```text
s|<CHANNEL_ID>|<JSON_PAYLOAD>
```

Ví dụ thực tế của một data message từ server:
```text
s|6|{"symbol":"TCB","matchPrice":"24550","matchQtty":"5000","change":200.0,"changePercent":0.82,"totalVolume":"9745500","totalValue":"240774655000"}
```

* * *

## Channel ID & Data Schema

### Channel 1 — Bid Info (Sổ lệnh mua — Top 3)
```text
s|1|{"symbol":"TCB","bidPrice01":"24550","bidPrice02":"24500","bidPrice03":"24450","bidQtty01":"137200","bidQtty02":"354000","bidQtty03":"292900"}
```

Channel 1 — Bid Info (bi)

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `symbol` | string |  | Mã chứng khoán. |
| `bidPrice01` | string |  | Giá đặt mua 1 (tốt nhất). |
| `bidPrice02` | string |  | Giá đặt mua 2. |
| `bidPrice03` | string |  | Giá đặt mua 3. |
| `bidQtty01` | string |  | Khối lượng đặt 1. |
| `bidQtty02` | string |  | Khối lượng đặt 2. |
| `bidQtty03` | string |  | Khối lượng đặt 3. |

### Channel 2 — Offer Info (Sổ lệnh bán — Top 3)
```text
s|2|{"symbol":"TCB","offerPrice01":"24600","offerPrice02":"24650","offerPrice03":"24700","offerQtty01":"294000","offerQtty02":"163400","offerQtty03":"743600"}
```

Channel 2 — Offer Info (op)

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `symbol` | string |  | Mã chứng khoán. |
| `offerPrice01` | string |  | Giá đặt bán 1 (tốt nhất). |
| `offerPrice02` | string |  | Giá đặt bán 2. |
| `offerPrice03` | string |  | Giá đặt bán 3. |
| `offerQtty01` | string |  | Khối lượng đặt 1. |
| `offerQtty02` | string |  | Khối lượng đặt 2. |
| `offerQtty03` | string |  | Khối lượng đặt 3. |

### Channel 3 — Foreign Exchange (Khối ngoại)
```text
s|3|{"symbol":"HPG","buyForeignQtty":"112400","sellForeignQtty":"17380","room":"1773708397"}
```

Channel 3 — Foreign Exchange (fe)

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `symbol` | string |  | Mã chứng khoán. |
| `buyForeignQtty` | string |  | Khối lượng khối ngoại mua. |
| `sellForeignQtty` | string |  | Khối lượng khối ngoại bán. |
| `room` | string |  | Room khối ngoại còn lại. |

### Channel 4 — Base Price (Giá trần/sàn/tham chiếu)
```text
s|4|{"symbol":"VPD","ceilPrice":25000,"floorPrice":24100,"refPrice":24300}
```

Channel 4 — Base Price (bp)

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `symbol` | string |  | Mã chứng khoán. |
| `ceilPrice` | number |  | Giá trần. |
| `floorPrice` | number |  | Giá sàn. |
| `refPrice` | number |  | Giá tham chiếu. |

### Channel 5 — Matched Price (Thông tin phiên)
```text
s|5|{"symbol":"VPD","high":25000,"low":24100,"avg":24300.0,"open":24600}
```

Channel 5 — Matched Price (mp)

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `symbol` | string |  | Mã chứng khoán. |
| `high` | number |  | Giá cao nhất phiên. |
| `low` | number |  | Giá thấp nhất phiên. |
| `avg` | number |  | Giá trung bình phiên. |
| `open` | number |  | Giá mở cửa. |

### Channel 6 — Ticker Match (Giao dịch khớp)
```text
s|6|{"symbol":"TCB","matchPrice":"24550","matchQtty":"5000","change":200.0,"changePercent":0.8213552361396304,"totalVolume":"9745500","totalValue":"240774655000"}
```

Channel 6 — Ticker Match (tm)

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `symbol` | string |  | Mã chứng khoán. |
| `matchPrice` | string |  | Giá khớp. |
| `matchQtty` | string |  | Khối lượng khớp. |
| `change` | number |  | Thay đổi so với tham chiếu (float). |
| `changePercent` | number |  | Phần trăm thay đổi (float). |
| `totalVolume` | string |  | Tổng khối lượng khớp trong phiên. |
| `totalValue` | string |  | Tổng giá trị giao dịch trong phiên (VND). |

### Channel 8 — Stock Index (Chỉ số)
```text
s|8|{"indexNumber":5,"index":91.43,"change":1.75,"changePercent":1.96,"volume":5.5936E7,"value":7.287094199E11,"increase":246,"decrease":58,"notChange":63,"session":"5","ceilIncrease":19,"floorDecrease":8}
```

Channel 8 — Stock Index (rt)

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `indexNumber` | number |  | Mã chỉ số (1-VNINDEX, 2-VN30...). |
| `index` | number |  | Giá trị chỉ số. |
| `change` | number |  | Thay đổi. |
| `changePercent` | number |  | Phần trăm thay đổi. |
| `volume` | number |  | Khối lượng. |
| `value` | number |  | Giá trị. |
| `increase` | number |  | Số mã tăng. |
| `decrease` | number |  | Số mã giảm. |
| `notChange` | number |  | Số mã không đổi. |
| `session` | string |  | Phiên. |
| `ceilIncrease` | number |  | Số mã trần. |
| `floorDecrease` | number |  | Số mã sàn. |

### Channel 16 — PT Advertisement (Chào mua/bán thỏa thuận)
```text
s|16|{"symbol":"VIC124003","price":1.00528E8,"vol":1000.0,"time":"20250808-04:10:33.917","status":1,"color":5,"orderId":"92025080800181048","side":"B"}
```

Channel 16 — PT Advertisement (pta)

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `symbol` | string |  | Mã chứng khoán. |
| `price` | number |  | Giá. |
| `vol` | number |  | Khối lượng. |
| `time` | string |  | Thời gian. |
| `status` | number |  | Trạng thái. |
| `color` | number |  | Màu. |
| `orderId` | string |  | Mã lệnh. |
| `side` | string |  | Chiều: B (mua), S (bán). |

### Channel 17 — PT Match (Khớp thỏa thuận)
```text
s|17|{"symbol":"VND","price":23500.0,"vol":200000.0,"val":4.7E9,"time":"10:56:50","color":4,"accumulatedValue":4.7E9}
```

Channel 17 — PT Match (ptm)

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `symbol` | string |  | Mã chứng khoán. |
| `price` | number |  | Giá. |
| `vol` | number |  | Khối lượng. |
| `val` | number |  | Giá trị. |
| `time` | string |  | Thời gian. |
| `color` | number |  | Màu. |
| `accumulatedValue` | number |  | Giá trị tích luỹ. |

### So sánh Channel ID: Cổ phiếu vs Phái sinh

| Dữ liệu | Cổ phiếu (`/stream/normal`) | Phái sinh (`/stream/derivative`) |
|---|---|---|
| Bid info | `s\|1` | `s\|23` |
| Offer info | `s\|2` | `s\|24` |
| Foreign exchange | `s\|3` | — |
| Base price | `s\|4` | — |
| Matched / day summary | `s\|5` | `s\|27` |
| Ticker match | `s\|6` | `s\|21` |
| Stock index | `s\|8` | — |

⚠️ Channel ID hoàn toàn khác giữa 2 endpoint, và data type cũng khác (cổ phiếu trả string cho giá/khối lượng, phái sinh trả number). KHÔNG dùng chung parser cho cổ phiếu và phái sinh.

* * *

## Sequence Diagram — Luồng hoàn chỉnh

Luồng kết nối WebSocket bảng giá cơ sở

* * *

## Xử lý lỗi & Reconnect

### Nguyên nhân disconnect

| Nguyên nhân | Triệu chứng | Giải pháp |
|---|---|---|
| No heartbeat >15s | Close 1000 | Check heartbeat task |
| Library sends RFC ping | Error 1002 | Disable auto-ping |
| Token expired | `d\|0\|{"error":...}` | Refresh token, reconnect |
| Server maintenance | Connection refuse | Exponential backoff retry |
| Outside trading hours | Connect OK, no data | Normal — wait for session open |

### Chiến lược reconnect (khuyến nghị)

Dùng exponential backoff: `delay = min(2^attempt, 30)` giây. Tối đa 10 lần thử, sau đó dừng lại và alert.

| Lần thử | Delay |
|---|---|
| 1 | 1s |
| 2 | 2s |
| 3 | 4s |
| 4 | 8s |
| 5 | 16s |
| 6+ | 30s |

### Ngoài giờ giao dịch

Phiên cơ sở: 9:00–11:30 (sáng) và 13:00–14:45 (chiều), có phiên ATC đến ~14:45–15:00 tuỳ sàn. Ngoài giờ thì bạn vẫn connect bình thường, heartbeat vẫn cần gửi, nhưng sẽ không có data message nào. Khi phiên sau mở, data tự chảy lại — không cần reconnect.

* * *

## Code hoàn chỉnh

PythonNode.js

Sao chép
```bash
"""Minimal WebSocket cash price-board client for TCBS — Python 3.10+"""

import asyncio
import base64
import json

# pip install websockets>=12.0
from websockets.asyncio.client import connect

WS_URL = "wss://openapi.tcbs.com.vn/ws/thesis/v1/stream/normal"
TOKEN = "YOUR_OPENAPI_TOKEN_HERE"
SYMBOLS = "FPT,VNM,HPG"

async def main():
    # 1. Connect — MUST disable auto-ping
    async with connect(WS_URL, ping_interval=None, ping_timeout=None) as ws:

        # 2. Auth — base64 encode token
        encoded_token = base64.b64encode(TOKEN.encode()).decode()
        await ws.send(f"d|a|||{encoded_token}")

        # 3. Wait for auth response: d|0|{"success":true,...}
        auth_response = await asyncio.wait_for(ws.recv(), timeout=5.0)
        print(f"Auth response: {auth_response}")
        if '"success":true' not in auth_response:
            print("Auth failed!")
            return

        # 4. Subscribe by symbol
        await ws.send(f"d|s|tk|bp+bi+tm+mp+op+fe|{SYMBOLS}")
        print(f"Subscribed to {SYMBOLS}")

        # 5. Start heartbeat background task
        async def heartbeat():
            while True:
                await ws.send("d|p|||")
                await asyncio.sleep(2)

        asyncio.create_task(heartbeat())

        # 6. Receive & parse messages
        while True:
            raw = await ws.recv()

            # Skip control messages
            if raw.startswith("d|"):
                continue

            # Parse data: s|[channel]|[json]
            if raw.startswith("s|"):
                parts = raw.split("|", 2)
                if len(parts) == 3:
                    channel = parts[1]
                    payload = json.loads(parts[2])

                    if channel == "6":
                        print(f"[TRADE] {payload['symbol']} "
                              f"Price={payload['matchPrice']} "
                              f"Qty={payload['matchQtty']}")
                    elif channel == "1":
                        print(f"[BID] {payload['symbol']} "
                              f"Best={payload['bidPrice01']} "
                              f"Qty={payload['bidQtty01']}")
                    elif channel == "2":
                        print(f"[OFFER] {payload['symbol']} "
                              f"Best={payload['offerPrice01']}")
                    elif channel == "4":
                        print(f"[BASE] {payload['symbol']} "
                              f"Ref={payload['refPrice']}")

if __name__ == "__main__":
    asyncio.run(main())
```

* * *

## FAQ — Câu hỏi thường gặp

Q

Tại sao bị disconnect sau 15-20 giây?

A

99% là do library tự gửi RFC ping frame. Phải disable auto-ping và tự gửi `d|p|||` mỗi 2s.

Q

matchPrice là chuỗi (string) hay số (number)?

A

Bảng giá cơ sở trả **string** cho hầu hết trường giá và khối lượng (bi, op, fe, tm). Riêng bp, mp, rt trả **number**. Khuyến nghị: cast rõ ràng khi parse.

Q

Muốn nhận toàn bộ một sàn thay vì từng mã thì làm sao?

A

Dùng lệnh `ro` — ví dụ `d|s|ro|bp+bi+tm+mp+op+fe|1,2` để nhận toàn bộ VN-INDEX và VN30-INDEX.

Q

Chỉ số (VN-INDEX...) lấy ở channel nào?

A

Subscribe bằng `d|s|si|rt|1,2` và đọc channel `s|8` (rt / stock index).

Q

Connect ngoài giờ giao dịch có được không?

A

Được. Connection sống bình thường (vẫn cần heartbeat), nhưng không có data cho đến khi phiên mở (9:00).

Q

Token expire thì sao?

A

Token hiệu lực tối đa 8 giờ. Server ngắt connection khi token hết hạn. Client cần detect disconnect → refresh token → reconnect.
