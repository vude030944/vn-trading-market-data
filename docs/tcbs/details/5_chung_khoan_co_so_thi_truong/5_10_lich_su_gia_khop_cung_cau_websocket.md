<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/ws-history
Tieu de goc: 5.10. Lịch sử giá khớp, cung cầu (WebSocket)
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/ws-history>

# 5.10. Lịch sử giá khớp, cung cầu (WebSocket)

Nhận dữ liệu real-time về lịch sử giá khớp, cung cầu mua/bán, và giao dịch khối ngoại — cập nhật mỗi phút qua WebSocket. Bạn mở một kết nối tới endpoint Ouranos, server sẽ tự đẩy dữ liệu tích luỹ theo từng mã chứng khoán mà bạn đăng ký.

Endpoint: `/ws/ouranos/v1/stream`. Heartbeat là `d|po` mỗi 2 giây. Dữ liệu trả về dạng `CODE|SYMBOL|{JSON}`.

## Demo tương tác

Địa chỉ WSS

`WSSwss://openapi.tcbs.com.vn/ws/ouranos/v1/stream`

Payload kết nối / xác thực
```json
{
  "note": "Real auth: d|a|||base64(token)",
  "format": "d|a|||[BASE64_TOKEN]"
}
```

Kênh / Chủ đề

  * `C001 (Price history)`Lịch sử giá khớp 1 phút: giá, khối lượng, tổng giao dịch.
  * `C002S60 (Supply/demand 60s)`Cung cầu tích luỹ 1 phút: mua/bán chủ động.
  * `C002S900 (Foreign exchange)`Giao dịch khối ngoại tích luỹ 15 phút.

Đã ngắt

Kết nốiXóa

// Nhấn Kết nối để bắt đầu luồng mô phỏng…

Demo trên chỉ mang tính minh họa. Wire format thực tế là text frame dạng CODE|SYMBOL|{JSON} (pipe-delimited). Xem chi tiết bên dưới.

* * *

## Kết nối

WSS`/ws/ouranos/v1/stream`

Địa chỉ WebSocket đầy đủ mà bạn cần kết nối tới:
```text
wss://openapi.tcbs.com.vn/ws/ouranos/v1/stream
```

BẮT BUỘC: Bạn phải disable auto-ping (RFC 6455 ping frame) của WebSocket library. Server TCBS chỉ chấp nhận heartbeat dạng text frame d|po. Nếu library tự gửi binary ping, server sẽ ngắt kết nối.

| Ngôn ngữ | Thư viện | Disable auto-ping |
|---|---|---|
| Python | `websockets` | `connect(url, ping_interval=None, ping_timeout=None)` |
| JavaScript | `ws` | Default off — do NOT rely on library ping |

* * *

## Xác thực (Authentication)

Sau khi kết nối WebSocket thành công, bạn cần gửi auth message ngay. Token OpenAPI phải được **base64 encode trực tiếp** — không wrap trong JSON hay object nào cả. **Format auth message** — client gửi lên server (`xxx` = base64 của token_openapi):
```text
d|a|||xxx
```

**Ví dụ cụ thể** — giả sử bạn có token như sau:

Token OpenAPI`igwfUq9M2IqWVhrFrYybEYKWxAxDbYzxz1RzOkp0L0S95lrMtrJDbMgFwy86r8Ir`

Base64(token)`aWd3ZlVxOU0ySXFXVmhyRnJZeWJFWUtXeEF4RGJZenh6MVJ6T2twMEwwUzk1bHJNdHJKRGJNZ0Z3eTg2cjhJcg==`

Client gửi server`d|a|||aWd3ZlVxOU0ySXFXVmhyRnJZeWJFWUtXeEF4RGJZenh6MVJ6T2twMEwwUzk1bHJNdHJKRGJNZ0Z3eTg2cjhJcg==`

**Auth thành công** — server trả về message sau:
```text
d|0|{"success":true,"error":null}
```

**Auth thất bại** — server trả về lỗi kèm mã code:
```text
d|0|{"success":false,"error":{"code":"211110","message":"Invalid JWT"}}
```

Server cũng gửi kèm bản tin timeout config `d|33|15`. Ý nghĩa: nếu client không gửi heartbeat trong 15 giây, server sẽ ngắt kết nối.
```text
d|33|15
```

Bạn PHẢI đợi nhận response auth thành công (d|0|{success:true...}) trước khi gửi subscribe. Gửi sớm sẽ bị bỏ qua.

* * *

## Đăng ký kênh (Subscribe)

Sau khi auth thành công, bạn đăng ký các channel bằng format sau — client gửi lên server:
```text
d|st|<code1+code2+...>|<ticker1,ticker2,...>
```

**Ví dụ** — đăng ký cả 3 channel cho TCB, POW, VIC. Client gửi:
```text
d|st|C001+C002S60+C002S900|POW,TCB,VIC
```

**Huỷ đăng ký** — dùng `d|ut` thay vì `d|st`. Client gửi:
```text
d|ut|C001+C002S60+C002S900|POW,TCB,VIC
```

**Bảng channel codes** — các mã channel bạn có thể đăng ký:

| Code | Mô tả |
|---|---|
| `C001` | Lịch sử giá khớp (1 phút) |
| `C002S60` | Cung cầu tích luỹ (1 phút) |
| `C002S900` | Giao dịch khối ngoại (15 phút) |

* * *

## Heartbeat — Giữ kết nối

Client PHẢI gửi heartbeat text frame mỗi **2 giây**. Nếu server không nhận được heartbeat trong **15 giây** → tự động ngắt kết nối. Client gửi:
```text
d|po
```

Heartbeat phải là TEXT frame chứa đúng nội dung d|po. KHÔNG dùng binary/ping frame — server sẽ không nhận.

* * *

## Cấu trúc Message

Server gửi về 2 loại message — control message (prefix `d|`) và data message (dữ liệu channel):

| Prefix | Loại | Mô tả |
|---|---|---|
| `d\|` | Control | Auth response, timeout config, heartbeat |
| `CODE\|SYMBOL\|{...}` | Data | Channel data (C001, C002S60, C002S900) |

**Data message format** — server trả về dữ liệu theo cấu trúc pipe-delimited:
```text
<CODE>|<SYMBOL>|{JSON_PAYLOAD}
```

**Ví dụ thực tế** — một frame server push về cho mã TCB:
```text
C001|TCB|{"symbol":"TCB","closePrice":38600.0,"closeVol":1000.0,"change":1100.0,"reference":37500.0,"totalTrading":2.42776E7,"timeSec":"1755144180","action":"SD","unitTimeFrame":"60"}
```

* * *

## Channel ID & Data Schema

### C001 — Lịch sử giá khớp (Price History)

Dữ liệu giá khớp được tổng hợp mỗi 1 phút (unitTimeFrame=60). Mỗi frame bao gồm giá khớp, khối lượng, tổng giao dịch trong ngày, và chỉ báo bên mua/bán chủ động. Server trả về frame như sau:
```text
C001|TCB|{"symbol":"TCB","closePrice":38600.0,"closeVol":1000.0,"change":1100.0,"reference":37500.0,"totalTrading":2.42776E7,"totalTradingValue":9.3340061E11,"timeSec":"1755144180","action":"SD","unitTimeFrame":"60","tradingValue":3.86E7,"buyUpAcc":1.51419E7,"sellDownAcc":8481600.0,"bidPrice":38600.0,"bidVol":34100.0,"askPrice":38650.0,"askVol":89600.0,"prevChange":1100.0}
```

C001 — Lịch sử giá khớp

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `symbol` | string |  | Mã chứng khoán. |
| `closePrice` | number |  | Giá khớp. |
| `closeVol` | number |  | Khối lượng khớp 1 phút. |
| `change` | number |  | Thay đổi giá so với tham chiếu. |
| `reference` | number |  | Giá tham chiếu. |
| `totalTrading` | number |  | Tổng khối lượng giao dịch trong ngày. |
| `totalTradingValue` | number |  | Tổng giá trị giao dịch trong ngày. |
| `timeSec` | string |  | Thời gian (epoch seconds). |
| `action` | string |  | BU = mua chủ động, SD = bán chủ động. |
| `unitTimeFrame` | string |  | Khung thời gian (giây): 60. |
| `tradingValue` | number |  | Giá trị khớp trong 1 phút. |
| `buyUpAcc` | number |  | Khối lượng mua chủ động tích luỹ. |
| `sellDownAcc` | number |  | Khối lượng bán chủ động tích luỹ. |
| `bidPrice` | number |  | Giá đặt mua tốt nhất. |
| `bidVol` | number |  | Khối lượng đặt mua. |
| `askPrice` | number |  | Giá đặt bán tốt nhất. |
| `askVol` | number |  | Khối lượng đặt bán. |
| `prevChange` | number |  | Thay đổi so với giá khớp gần nhất. |

### C002S60 — Cung cầu (Supply/Demand, 1 phút)

Khối lượng mua/bán chủ động tích luỹ mỗi 1 phút. Server trả về frame như sau:
```text
C002S60|TCB|{"symbol":"TCB","timeSec":"1755144120","totalBUVol":200.0,"totalBUVolAcc":1.51419E7,"totalSDVol":49700.0,"totalSDVolAcc":8480600.0,"bsAccRatio":0.6409948,"unitTimeFrame":"60"}
```

C002S60 — Cung cầu 1 phút

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `symbol` | string |  | Mã chứng khoán. |
| `timeSec` | string |  | Thời gian (epoch seconds). |
| `totalBUVol` | number |  | Khối lượng mua chủ động trong 1 phút. |
| `totalBUVolAcc` | number |  | Khối lượng mua chủ động tích luỹ đầu ngày. |
| `totalSDVol` | number |  | Khối lượng bán chủ động trong 1 phút. |
| `totalSDVolAcc` | number |  | Khối lượng bán chủ động tích luỹ đầu ngày. |
| `bsAccRatio` | number |  | Tỷ lệ mua/bán chủ động tích luỹ (0-1). |
| `unitTimeFrame` | string |  | Khung thời gian: 60 (giây). |

### C002S900 — Giao dịch khối ngoại (Foreign Exchange, 15 phút)

Cùng cấu trúc như C002S60 nhưng tích luỹ mỗi 15 phút (unitTimeFrame=900). Server trả về frame như sau:
```text
C002S900|TCB|{"symbol":"TCB","timeSec":"1755144120","totalBUVol":200.0,"totalBUVolAcc":1.51419E7,"totalSDVol":49700.0,"totalSDVolAcc":8480600.0,"bsAccRatio":0.6409948,"unitTimeFrame":"900"}
```

C002S900 — Khối ngoại 15 phút

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `symbol` | string |  | Mã chứng khoán. |
| `timeSec` | string |  | Thời gian (epoch seconds). |
| `totalBUVol` | number |  | Khối lượng mua chủ động. |
| `totalBUVolAcc` | number |  | Mua chủ động tích luỹ đầu ngày. |
| `totalSDVol` | number |  | Khối lượng bán chủ động. |
| `totalSDVolAcc` | number |  | Bán chủ động tích luỹ đầu ngày. |
| `bsAccRatio` | number |  | Tỷ lệ mua/bán chủ động. |
| `unitTimeFrame` | string |  | Khung thời gian: 900 (giây = 15 phút). |

* * *

## Sequence Diagram

Luồng kết nối WebSocket lịch sử giá và cung cầu

* * *

## Xử lý lỗi & Reconnect

| Nguyên nhân | Triệu chứng | Giải pháp |
|---|---|---|
| No heartbeat >15s | Connection closed | Ensure d\|po every 2s |
| Library sends RFC ping | Unexpected disconnect | Disable auto-ping |
| Token expired | Auth response with error | Refresh token, reconnect |
| Server maintenance | Connection refused | Exponential backoff retry |

**Chiến lược reconnect:** Dùng exponential backoff với công thức `delay = min(2^attempt, 30)` giây. Thử tối đa 10 lần, sau đó gửi alert cho hệ thống monitoring.

* * *

## Code hoàn chỉnh

PythonNode.js

Sao chép
```python
"""WebSocket client for TCBS price history & supply/demand — Python 3.10+"""

import asyncio
import base64
import json

from websockets.asyncio.client import connect

WS_URL = "wss://openapi.tcbs.com.vn/ws/ouranos/v1/stream"
TOKEN = "YOUR_OPENAPI_TOKEN_HERE"
SYMBOLS = "TCB,POW,VIC"

async def main():
    async with connect(WS_URL, ping_interval=None, ping_timeout=None) as ws:

        # 1. Auth — base64 encode token directly
        encoded_token = base64.b64encode(TOKEN.encode()).decode()
        await ws.send(f"d|a|||{encoded_token}")

        # 2. Wait for auth response
        while True:
            msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
            print(f"< {msg}")
            if msg.startswith("d|0|"):
                result = json.loads(msg[4:])
                if result.get("success"):
                    break
                else:
                    raise Exception(f"Auth failed: {result}")

        # 3. Subscribe to all channels
        await ws.send(f"d|st|C001+C002S60+C002S900|{SYMBOLS}")
        print(f"Subscribed: C001+C002S60+C002S900 for {SYMBOLS}")

        # 4. Heartbeat task
        async def heartbeat():
            while True:
                await ws.send("d|po")
                await asyncio.sleep(2)

        asyncio.create_task(heartbeat())

        # 5. Receive & parse
        while True:
            raw = await ws.recv()

            # Skip control messages
            if raw.startswith("d|"):
                continue

            # Parse data: CODE|SYMBOL|{json}
            parts = raw.split("|", 2)
            if len(parts) == 3:
                code, symbol, payload_str = parts
                payload = json.loads(payload_str)

                if code == "C001":
                    print(f"[PRICE] {symbol} "
                          f"Close={payload['closePrice']} "
                          f"Vol={payload['closeVol']} "
                          f"Action={payload['action']}")
                elif code == "C002S60":
                    print(f"[SUPPLY] {symbol} "
                          f"BuyVol={payload['totalBUVol']} "
                          f"SellVol={payload['totalSDVol']} "
                          f"Ratio={payload['bsAccRatio']}")
                elif code == "C002S900":
                    print(f"[FOREIGN] {symbol} "
                          f"BuyAcc={payload['totalBUVolAcc']} "
                          f"SellAcc={payload['totalSDVolAcc']}")

if __name__ == "__main__":
    asyncio.run(main())
```

* * *

## FAQ

Q

Có thể subscribe từng channel riêng lẻ không?

A

Có. Ví dụ chỉ lịch sử giá: `d|st|C001|TCB,POW`. Bạn có thể kết hợp bất kỳ channel code nào bằng dấu +.

Q

Heartbeat dùng d|p||| hay d|po?

A

Endpoint Ouranos dùng `d|po`. Endpoint Thesis (bảng giá) dùng `d|p|||`. Mỗi endpoint có format heartbeat riêng.

Q

Data push liên tục hay chỉ khi có thay đổi?

A

Server push mỗi phút (C001 với unitTimeFrame=60) khi có giao dịch khớp. Ngoài giờ giao dịch sẽ không có data.

Q

action=BU/SD nghĩa là gì?

A

BU = Buy Up (mua chủ động — giá khớp tăng), SD = Sell Down (bán chủ động — giá khớp giảm). Cho biết bên nào đang chiếm ưu thế.
