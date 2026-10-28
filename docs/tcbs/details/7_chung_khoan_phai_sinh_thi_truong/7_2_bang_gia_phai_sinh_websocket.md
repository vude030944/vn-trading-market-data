<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/derivative/ws-price-board
Tieu de goc: 7.2. Bảng giá phái sinh (WebSocket)
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/ws-price-board>

# 7.2. Bảng giá phái sinh (WebSocket)

Nhận bảng giá phái sinh (VN30F, VN30F1M, VN30F2M...) theo thời gian thực qua WebSocket. Một kết nối duy nhất — server đẩy giá khớp, sổ lệnh bid/offer top 3, và thông tin phiên (high, low, open, avg) mỗi khi có thay đổi.

Trang này dành cho phái sinh (endpoint `/stream/derivative`). So với cổ phiếu cơ sở: channel ID khác (21/23/24/27), data type là `number` thay vì `string`. Xác thực và heartbeat giống nhau.

## Demo tương tác

Địa chỉ WSS

`WSSwss://openapi.tcbs.com.vn/ws/thesis/v1/stream/derivative`

Payload kết nối / xác thực
```json
{
  "note": "Conceptual only — real auth is pipe-delimited: d|a|||[base64_token]",
  "format": "d|a|||[BASE64_JWT]"
}
```

Kênh / Chủ đề

  * `s|21 (ticker match)`Giao dịch khớp: giá, khối lượng, thay đổi.
  * `s|23 (bid info)`Sổ lệnh mua top 3: giá và khối lượng.
  * `s|24 (offer info)`Sổ lệnh bán top 3: giá và khối lượng.
  * `s|27 (day summary)`Thông tin phiên: cao, thấp, trung bình, mở cửa.

Đã ngắt

Kết nốiXóa

// Nhấn Kết nối để bắt đầu luồng mô phỏng…

⚠️ Demo trên chỉ mang tính minh họa. Protocol thực tế trên wire là TEXT frame phân tách bằng pipe (|), KHÔNG phải JSON. Xem các phần bên dưới để biết chi tiết format thật.

* * *

## Kết nối

WSS`/ws/thesis/v1/stream/derivative`

Địa chỉ WebSocket đầy đủ mà bạn cần connect tới:
```text
wss://openapi.tcbs.com.vn/ws/thesis/v1/stream/derivative
```

⚠️ BẮT BUỘC: Phải disable auto-ping (RFC 6455 ping frame) của WebSocket library. Server TCBS chỉ chấp nhận heartbeat dạng text frame d|p|||. Nếu library tự gửi binary ping → server trả 1002 Protocol Error và ngắt kết nối sau ~15-20 giây.

Dưới đây là cách disable auto-ping cho từng ngôn ngữ/thư viện phổ biến:

| Ngôn ngữ | Thư viện | Disable auto-ping |
|---|---|---|
| Python | `websockets` | `connect(url, ping_interval=None, ping_timeout=None)` |
| JavaScript | `ws` | Default off — do NOT set `perMessageDeflate` |
| Go | `gorilla/websocket` | Do not call `SetPingHandler`; manage ping manually |
| Java | `javax.websocket` | Endpoint config: do not set ping |

* * *

## Xác thực (Authentication)

Sau khi kết nối WebSocket thành công, bạn phải gửi auth message trước khi subscribe bất kỳ kênh nào. Lưu ý: JWT token từ API đăng nhập cần được **base64 encode** trước khi đưa vào message. **Client gửi auth message** theo format sau:
```text
d|a|||<BASE64_ENCODED_TOKEN>
```

**Server trả về khi auth thành công** — bạn sẽ nhận frame xác nhận:
```text
d|0|{"success":true,"error":null}
```

Server cũng gửi thêm một frame cấu hình timeout (15 = số giây heartbeat timeout):
```text
d|33|15
```

**Server trả về khi auth thất bại:**
```text
d|0|{"success":false,"error":{"code":"211110","message":"Invalid JWT"}}
```

⚠️ PHẢI đợi nhận response auth d|0|{...success:true...} trước khi gửi subscribe. Gửi subscribe ngay mà không đợi → có thể bị server reject.

PythonNode.js

Sao chép
```python
import base64

jwt_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
encoded = base64.b64encode(jwt_token.encode()).decode()
auth_message = f"d|a|||{encoded}"

# Send: "d|a|||ZXlKaGJHY2lPaUpTVXpJMU5pSXNJbl..."
await ws.send(auth_message)

# Wait for response
response = await ws.recv()  # d|0|{"success":true,...} = success
```

* * *

## Đăng ký kênh (Subscribe)

Sau khi nhận auth thành công, bạn gửi subscribe message để bắt đầu nhận dữ liệu realtime. Format như sau:
```text
d|s|tk|<CHANNELS>|<SYMBOL>
```

**Ví dụ:** subscribe đầy đủ tất cả kênh cho VN30F front-month — client gửi:
```text
d|s|tk|bp+bi+tm+mp+op+fe|41I1G8000
```

Dưới đây là bảng channel codes và ý nghĩa tương ứng:

| Code | Ý nghĩa | Channel ID |
|---|---|---|
| `bp` | Giá tham chiếu | — |
| `bi` | Sổ lệnh mua | `s\|23` |
| `tm` | Giao dịch khớp | `s\|21` |
| `mp` | Thông tin phiên | `s\|27` |
| `op` | Sổ lệnh bán | `s\|24` |
| `fe` | Ngoại hối | — |

Bạn có thể gửi bp và fe trong subscribe request (cùng format 6 channel code như cổ phiếu cơ sở), nhưng server phái sinh chỉ phát dữ liệu trên channel 21/23/24/27 (tm/bi/op/mp). Các code bp và fe sẽ được chấp nhận nhưng không tạo ra frame nào.

* * *

## Heartbeat — Giữ kết nối

Client PHẢI gửi heartbeat text frame mỗi **2 giây** để giữ kết nối sống. Nếu server không nhận heartbeat trong **15 giây** → tự động ngắt. Frame heartbeat mà client gửi:
```text
d|p|||
```

⚠️ Heartbeat phải là TEXT frame, KHÔNG phải binary/ping frame. Đây là nguyên nhân #1 gây disconnect liên tục mà developer khó debug.

* * *

## Cấu trúc Message

Server gửi về 2 loại message. Bạn phân biệt chúng qua prefix đầu tiên:

| Prefix | Loại | Mô tả |
|---|---|---|
| `d\|` | Control | Auth response, timeout config, heartbeat pong |
| `s\|` | Data | Subscription data (trade, orderbook, summary) |

**Data message** mà server push về có format như sau:
```text
s|<CHANNEL_ID>|<JSON_PAYLOAD>
```

**Ví dụ thực tế** — server gửi một giao dịch khớp trên channel 21:
```text
s|21|{"symbol":"41I1G8000","matchPrice":1870.5,"matchQtty":2,"change":-4.5,"changePercent":-0.24,"totalVolume":15234}
```

**Control messages** — bạn có thể bỏ qua khi parse data. Server gửi các dạng sau:

| Message | Mô tả |
|---|---|
| `d\|0\|{...}` | Kết quả xác thực (thành công / thất bại) |
| `d\|33\|15` | Cấu hình timeout heartbeat (15 giây) |
| `d\|p\|\|\|` | Heartbeat pong từ server |

* * *

## Channel ID & Data Schema

### Channel 21 — Ticker Match (Giao dịch khớp)

Mỗi lệnh khớp, server push 1 message dạng JSON trên channel 21:
```json
{"symbol":"41I1G8000","matchPrice":1870.5,"matchQtty":2,"change":-4.5,"changePercent":-0.24,"totalVolume":15234}
```

Channel 21 — Ticker Match

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `symbol` | string |  | Mã hợp đồng phái sinh. |
| `matchPrice` | number |  | Giá khớp. |
| `matchQtty` | int64 |  | Khối lượng khớp. |
| `change` | number |  | Thay đổi so với giá tham chiếu. |
| `changePercent` | number |  | Phần trăm thay đổi. |
| `totalVolume` | int64 |  | Tổng khối lượng giao dịch trong phiên. |

### Channel 23 — Bid Info (Sổ lệnh mua — Top 3)

Server push sổ lệnh mua top 3 trên channel 23:
```json
{"symbol":"41I1G8000","bidPrice01":1870.5,"bidPrice02":1870.3,"bidPrice03":1870.0,"bidQtty01":15,"bidQtty02":8,"bidQtty03":22}
```

Channel 23 — Bid Info

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `bidPrice01` | number |  | Giá bid tốt nhất (cao nhất). |
| `bidPrice02` | number |  | Giá bid thứ 2. |
| `bidPrice03` | number |  | Giá bid thứ 3. |
| `bidQtty01` | int64 |  | Khối lượng tại mức giá bid 1. |
| `bidQtty02` | int64 |  | Khối lượng tại mức giá bid 2. |
| `bidQtty03` | int64 |  | Khối lượng tại mức giá bid 3. |

### Channel 24 — Offer Info (Sổ lệnh bán — Top 3)

Server push sổ lệnh bán top 3 trên channel 24:
```json
{"symbol":"41I1G8000","offerPrice01":1870.8,"offerPrice02":1871.0,"offerPrice03":1871.5,"offerQtty01":10,"offerQtty02":5,"offerQtty03":30}
```

Channel 24 — Offer Info

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `offerPrice01` | number |  | Giá offer tốt nhất (thấp nhất). |
| `offerPrice02` | number |  | Giá offer thứ 2. |
| `offerPrice03` | number |  | Giá offer thứ 3. |
| `offerQtty01` | int64 |  | Khối lượng tại mức giá offer 1. |
| `offerQtty02` | int64 |  | Khối lượng tại mức giá offer 2. |
| `offerQtty03` | int64 |  | Khối lượng tại mức giá offer 3. |

### Channel 27 — Day Summary (Thông tin phiên)

Server push thông tin tổng hợp phiên trên channel 27:
```json
{"symbol":"41I1G8000","high":1885.0,"low":1862.5,"avg":1873.2,"open":1875.0}
```

Channel 27 — Day Summary

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `high` | number |  | Giá cao nhất phiên. |
| `low` | number |  | Giá thấp nhất phiên. |
| `avg` | number |  | Giá trung bình phiên. |
| `open` | number |  | Giá mở cửa. |

### So sánh Channel ID: Phái sinh vs Cổ phiếu

| Dữ liệu | Cổ phiếu (`/stream/normal`) | Phái sinh (`/stream/derivative`) |
|---|---|---|
| Ticker match | `s\|6` | `s\|21` |
| Bid info | `s\|1` | `s\|23` |
| Offer info | `s\|2` | `s\|24` |
| Day summary | `s\|5` | `s\|27` |
| Base price | `s\|4` | — |
| Foreign exchange | `s\|3` | — |

⚠️ Channel ID hoàn toàn khác giữa 2 endpoint. KHÔNG dùng chung parser cho cổ phiếu và phái sinh.

* * *

## Mã hợp đồng phái sinh (Symbol)

Phái sinh sử dụng mã nội bộ TCBS, KHÔNG phải mã HNX/HSX. Ví dụ: `41I1G8000` = VN30F front-month (tháng gần nhất). Mã này sẽ thay đổi khi rollover sang kỳ hạn mới. **Để lấy danh sách mã active hiện tại** , bạn gọi API sau:

GET`/api/v1/derivatives/contracts`
```text
GET https://openapi.tcbs.com.vn/api/v1/derivatives/contracts
Authorization: Bearer <JWT_TOKEN>
```

**Về rollover:** mã front-month thay đổi vào ngày đáo hạn — thường là thứ Năm tuần thứ 3 của tháng. Sau rollover, mã cũ ngừng push data. Bạn cần re-subscribe với mã mới.

* * *

## Sequence Diagram — Luồng hoàn chỉnh

Luồng kết nối WebSocket phái sinh

* * *

## Xử lý lỗi & Reconnect

### Nguyên nhân disconnect

| Nguyên nhân | Triệu chứng | Giải pháp |
|---|---|---|
| No heartbeat >15s | Close 1000 | Check heartbeat task |
| Library sends RFC ping | Error 1002 | Disable auto-ping |
| Token expired | `d\|0\|{"error":...}` | Refresh token, reconnect |
| Server maintenance | Connection refuse | Exponential backoff retry |
| Outside trading hours | Connect OK, no data | Normal — wait until 8:45 |

### Chiến lược reconnect (khuyến nghị)

Dùng exponential backoff: `delay = min(2^attempt, 30)` giây. Tối đa 10 lần thử, sau đó dừng hẳn và gửi alert cho bạn xử lý thủ công.

| Lần thử | Delay |
|---|---|
| 1 | 1s |
| 2 | 2s |
| 3 | 4s |
| 4 | 8s |
| 5 | 16s |
| 6+ | 30s |

### Token lifecycle

JWT token có `exp` claim — hiệu lực tối đa 8 giờ. Trước khi expire, bạn nên gọi refresh token API. Sau khi expire, server sẽ ngắt connection → bạn cần reconnect với token mới.

### Ngoài giờ giao dịch

Phiên phái sinh chạy 8:45–11:30 và 13:00–14:45 (ngày thường). Ngoài giờ, bạn vẫn connect bình thường, heartbeat vẫn cần gửi, nhưng sẽ không có data message nào. Sáng hôm sau data tự chảy lại mà không cần reconnect.

* * *

## Code hoàn chỉnh

PythonNode.js

Sao chép
```python
"""Minimal WebSocket derivative price-board client for TCBS — Python 3.10+"""

import asyncio
import base64
import json

# pip install websockets>=12.0
from websockets.asyncio.client import connect

WS_URL = "wss://openapi.tcbs.com.vn/ws/thesis/v1/stream/derivative"
TOKEN = "YOUR_JWT_TOKEN_HERE"
SYMBOL = "41I1G8000"  # VN30F front-month

async def main():
    # 1. Connect — MUST disable auto-ping
    async with connect(WS_URL, ping_interval=None, ping_timeout=None) as ws:

        # 2. Auth — base64 encode token
        encoded_token = base64.b64encode(TOKEN.encode()).decode()
        await ws.send(f"d|a|||{encoded_token}")

        # 3. Wait for auth response
        auth_response = await asyncio.wait_for(ws.recv(), timeout=5.0)
        print(f"Auth response: {auth_response}")
        if '"success":true' not in auth_response:
            print("Auth failed!")
            return

        # 4. Subscribe
        await ws.send(f"d|s|tk|bp+bi+tm+mp+op+fe|{SYMBOL}")
        print(f"Subscribed to {SYMBOL}")

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

                    if channel == "21":
                        print(f"[TRADE] Price={payload['matchPrice']} "
                              f"Qty={payload['matchQtty']} "
                              f"Vol={payload.get('totalVolume', 0)}")
                    elif channel == "23":
                        print(f"[BID] Best={payload['bidPrice01']} "
                              f"Qty={payload['bidQtty01']}")
                    elif channel == "24":
                        print(f"[OFFER] Best={payload['offerPrice01']} "
                              f"Qty={payload['offerQtty01']}")
                    elif channel == "27":
                        print(f"[DAY] H={payload['high']} "
                              f"L={payload['low']} O={payload['open']}")

if __name__ == "__main__":
    asyncio.run(main())
```

* * *

## FAQ — Câu hỏi thường gặp

Q

Tại sao bị disconnect sau 15-20 giây?

A

99% là do library tự gửi RFC ping frame. Bạn phải disable auto-ping và tự gửi `d|p|||` mỗi 2s.

Q

Parse theo document cổ phiếu (channel 1, 2, 3...) nhưng không nhận được data?

A

Phái sinh dùng channel ID khác hoàn toàn: 21, 23, 24, 27. Xem bảng mapping ở phần Channel ID phía trên.

Q

matchPrice trả về `'1870.5'` hay `1870.5`?

A

Phái sinh trả **number** (`1870.5`), KHÔNG phải string. Khác với cổ phiếu cơ sở (trả string). Khuyến nghị: bạn nên luôn cast sang float khi parse cho an toàn.

Q

Mã `41I1G8000` là gì? Sao không dùng VN30F2507?

A

Đây là mã nội bộ TCBS cho VN30F front-month. Bạn gọi API `GET /api/v1/derivatives/contracts` để lấy mapping mã hiện tại.

Q

Connect ngoài giờ giao dịch có được không?

A

Được. Connection sống bình thường, nhưng không có data cho đến khi phiên mở lúc 8:45.

Q

Token expire thì sao?

A

Token hiệu lực tối đa 8 giờ. Server ngắt connection khi token hết hạn. Bạn cần detect disconnect → refresh token → reconnect.

Q

Có rate limit không?

A

Hiện chưa có document chính thức. Trong thực tế, 1 connection per token là safe. Mở nhiều connection cùng token có thể bị reject.
