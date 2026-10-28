<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/ws-order-matching
Tieu de goc: 5.9. Thay đổi thông tin lệnh cơ sở (WebSocket)
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/ws-order-matching>

# 5.9. Thay đổi thông tin lệnh cơ sở (WebSocket)

Nhận thông báo real-time mỗi khi lệnh cổ phiếu cơ sở của bạn thay đổi trạng thái — đặt, khớp, huỷ, hoặc sửa. Server tự động push thông tin qua WebSocket ngay khi có cập nhật, không cần bạn polling. Mỗi message chứa đầy đủ thông tin lệnh ở trạng thái mới nhất.

Endpoint này (`/ws/aither`) dùng riêng cho lệnh cổ phiếu cơ sở. Heartbeat là `ping|1`, format dữ liệu là `message_proto|TOPIC|{JSON}` — khác với bảng giá dùng pipe-delimited.

## Demo tương tác

Địa chỉ WSS

`WSSwss://openapi.tcbs.com.vn/ws/aither`

Payload kết nối / xác thực
```json
{
  "note": "Real auth: authenticate|base64({jwt:token})",
  "format": "authenticate|BASE64_JWT_PAYLOAD"
}
```

Kênh / Chủ đề

  * `STOCK_ORDER`Cập nhật trạng thái lệnh cổ phiếu cơ sở.

Đã ngắt

Kết nốiXóa

// Nhấn Kết nối để bắt đầu luồng mô phỏng…

Demo trên chỉ mang tính minh họa. Wire format thực tế là text frame dạng message_proto|STOCK_ORDER|{JSON}. Xem chi tiết bên dưới.

* * *

## Kết nối

WSS`/ws/aither`

Địa chỉ WebSocket đầy đủ mà bạn cần kết nối tới:
```text
wss://openapi.tcbs.com.vn/ws/aither
```

BẮT BUỘC: Bạn phải disable auto-ping (RFC 6455 ping frame) của WebSocket library. Server TCBS chỉ chấp nhận heartbeat dạng text frame ping|1. Nếu library tự gửi binary ping, server có thể ngắt kết nối.

| Ngôn ngữ | Thư viện | Disable auto-ping |
|---|---|---|
| Python | `websockets` | `connect(url, ping_interval=None, ping_timeout=None)` |
| JavaScript | `ws` | Default off — do NOT rely on library ping |

* * *

## Xác thực (Authentication)

Sau khi kết nối WebSocket thành công, bạn cần gửi một text frame xác thực theo format sau:
```text
authenticate|BASE64_PAYLOAD
```

Phần `BASE64_PAYLOAD` là base64 encode của một chuỗi JSON chứa token OpenAPI của bạn:
```json
{"jwt":"YOUR_OPENAPI_TOKEN"}
```

Ví dụ cụ thể — giả sử token OpenAPI của bạn là:

Token OpenAPI`igwfUq9M2IqWVhrFrYybEYKWxAxDbYzxz1RzOkp0L0S95lrMtrJDbMgFwy86r8Ir`

Base64({"jwt":"<token>"})`eyJqd3QiOiJpZ3dmVXE5TTJJcVdWaHJGcll5YkVZS1d4QXhEYll6eHoxUnpPa3AwTDBTOTVsck10ckpEYk1nRnd5ODZyOElyIn0=`

Message gửi server`authenticate|eyJqd3QiOiJpZ3dmVXE5TTJJcVdWaHJGcll5YkVZS1d4QXhEYll6eHoxUnpPa3AwTDBTOTVsck10ckpEYk1nRnd5ODZyOElyIn0=`

Sau khi nhận được message xác thực, server sẽ trả về hai message. Đầu tiên là timeout config cho biết khoảng thời gian heartbeat tối đa:
```text
pingTimeout|7
```

Con số 7 nghĩa là nếu client không gửi ping trong 7 giây, server sẽ ngắt kết nối. Tiếp theo, server trả về kết quả xác thực:
```text
authenticate|{"success":true,"error":null}
```

Bạn PHẢI đợi nhận response auth thành công trước khi gửi subscribe. Nếu gửi subscribe ngay lập tức, server có thể reject.

* * *

## Đăng ký kênh (Subscribe)

Sau khi auth thành công, bạn gửi message subscribe để đăng ký nghe topic `STOCK_ORDER`. Message client gửi lên:
```text
subscribe|eyJ0b3BpYyI6IlNUT0NLX09SREVSIn0=
```

Phần base64 payload khi decode ra sẽ là:
```json
{"topic":"STOCK_ORDER"}
```

Kể từ lúc này, mỗi khi lệnh của bạn có thay đổi trạng thái, server sẽ tự động push data về cho bạn qua kết nối này.

* * *

## Heartbeat — Giữ kết nối

Để giữ kết nối sống, client PHẢI gửi heartbeat text frame mỗi **2 giây**. Nếu server không nhận được heartbeat nào trong **7 giây** (giá trị `pingTimeout` server đã gửi lúc auth) thì sẽ tự động ngắt kết nối. Message heartbeat mà client gửi lên:
```text
ping|1
```

Heartbeat phải là TEXT frame, KHÔNG phải binary/ping frame. Tần suất: 1 message mỗi 2 giây.

* * *

## Cấu trúc Message

Server gửi về cho bạn 2 loại message chính:

| Prefix | Loại | Mô tả |
|---|---|---|
| `pingTimeout\|N` | Control | Timeout config (N seconds) |
| `authenticate\|{...}` | Control | Auth response |
| `message_proto\|TOPIC\|{...}` | Data | Order update payload |

Với data message (cập nhật lệnh), format mà server trả về sẽ là:
```text
message_proto|STOCK_ORDER|{JSON_PAYLOAD}
```

Ví dụ thực tế — đây là một message server push về khi lệnh mua LUT được tiếp nhận:
```text
message_proto|STOCK_ORDER|{"object":"order","accountNo":"0001201435","orderId":"9202412270000098858","execType":"NB","orderQtty":100.0,"symbol":"LUT","priceType":"LO","txTime":"12:04:39","orStatus":"8","limitPrice":500.0,"remainQtty":100.0,"via":"O"}
```

* * *

## Data Schema — STOCK_ORDER

STOCK_ORDER — Thông tin lệnh cơ sở

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `object` | string |  | Loại object (luôn là order). |
| `accountNo` | string |  | Số tiểu khoản. |
| `orderId` | string |  | Số hiệu lệnh. |
| `execType` | string |  | Loại lệnh (NB = mua, NS = bán). |
| `orderQtty` | number |  | Khối lượng đặt. |
| `symbol` | string |  | Mã chứng khoán. |
| `priceType` | string |  | Loại giá (LO, MP, ATO, ATC). |
| `txTime` | string |  | Giờ đặt lệnh (HH:mm:ss). |
| `txDate` | string |  | Ngày đặt lệnh (ISO 8601). |
| `expDate` | string |  | Ngày hết hạn. |
| `timeType` | string |  | T = trong ngày, G = nhiều ngày. |
| `orStatus` | string |  | Trạng thái lệnh (xem bảng dưới). |
| `limitPrice` | number |  | Giá đặt lệnh. |
| `remainQtty` | number |  | Số lượng còn lại. |
| `via` | string |  | Kênh giao dịch (O=Online, M=Call center, T=Call margin). |
| `quotePrice` | number |  | Giá quote. |
| `tradePlace` | string |  | Sàn giao dịch (001=HOSE, 002=HNX, 005=UPCOM, 000=BOND). |
| `matchType` | string |  | Loại khớp (N=bình thường, P=thoả thuận). |
| `isDisposal` | string |  | Là lệnh bán xử lý (Y/N). |
| `isCancel` | string |  | Cho phép huỷ (Y/N). |
| `isAmend` | string |  | Cho phép sửa (Y/N). |
| `userName` | string |  | User đặt lệnh (6868=Online, 8686=Lệnh điều kiện/iCopy). |
| `orsOrderId` | string |  | Số hiệu lệnh ORS. |
| `secType` | string |  | Loại CK (001=CP thường, 002=CP ưu đãi, 006=Trái phiếu, 011=Chứng quyền). |
| `isFOOrder` | string |  | Lệnh từ FO (Y) hay BO (N). |
| `odTimeStamp` | string |  | Thời gian sinh lệnh (yyyy-MM-dd HH:mm:ss.SSSSSS). |

### Bảng trạng thái lệnh (orStatus)

| Mã | Mô tả |
|---|---|
| `0` | Từ chối |
| `2` | Đã gửi |
| `3` | Đã huỷ |
| `4` | Đã khớp (một phần) |
| `5` | Hết hiệu lực |
| `8` | Chờ gửi |
| `10` | Đã sửa |
| `11` | Đang gửi |
| `12` | Khớp hết |
| `A` | Đang sửa |
| `C` | Đang huỷ |
| `S` | Hoàn tất |

* * *

## Sequence Diagram

Luồng kết nối WebSocket thay đổi thông tin lệnh cơ sở

* * *

## Xử lý lỗi & Reconnect

| Nguyên nhân | Triệu chứng | Giải pháp |
|---|---|---|
| No heartbeat >7s | Connection closed | Ensure ping\|1 every 2s |
| Library sends RFC ping | Unexpected disconnect | Disable auto-ping |
| Token expired | Auth fails | Refresh token, reconnect |
| Server maintenance | Connection refused | Exponential backoff retry |

**Chiến lược reconnect:** Bạn nên dùng exponential backoff với công thức `delay = min(2^attempt, 30)` giây. Tối đa thử 10 lần, sau đó nên alert để kiểm tra thủ công.

* * *

## Code hoàn chỉnh

PythonNode.js

Sao chép
```python
"""WebSocket client for TCBS cash order updates — Python 3.10+"""

import asyncio
import base64
import json

from websockets.asyncio.client import connect

WS_URL = "wss://openapi.tcbs.com.vn/ws/aither"
TOKEN = "YOUR_OPENAPI_TOKEN_HERE"

async def main():
    async with connect(WS_URL, ping_interval=None, ping_timeout=None) as ws:

        # 1. Authenticate
        jwt_payload = json.dumps({"jwt": TOKEN})
        encoded = base64.b64encode(jwt_payload.encode()).decode()
        await ws.send(f"authenticate|{encoded}")

        # 2. Wait for auth response
        while True:
            msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
            print(f"< {msg}")
            if msg.startswith("authenticate|"):
                payload = msg.split("|", 1)[1]
                result = json.loads(payload)
                if result.get("success"):
                    break
                else:
                    raise Exception(f"Auth failed: {result}")

        # 3. Subscribe to STOCK_ORDER
        sub_payload = base64.b64encode(json.dumps({"topic": "STOCK_ORDER"}).encode()).decode()
        await ws.send(f"subscribe|{sub_payload}")
        print("Subscribed to STOCK_ORDER")

        # 4. Heartbeat task
        async def heartbeat():
            while True:
                await ws.send("ping|1")
                await asyncio.sleep(2)

        asyncio.create_task(heartbeat())

        # 5. Receive order updates
        while True:
            raw = await ws.recv()
            if raw.startswith("message_proto|STOCK_ORDER|"):
                order_json = raw.split("|", 2)[2]
                order = json.loads(order_json)
                print(f"[ORDER] {order['symbol']} "
                      f"Status={order['orStatus']} "
                      f"Qty={order['orderQtty']} "
                      f"Remain={order.get('remainQtty')}")

if __name__ == "__main__":
    asyncio.run(main())
```

* * *

## FAQ

Q

Topic `STOCK_ORDER` gửi data khi nào?

A

Mỗi khi lệnh của bạn thay đổi trạng thái: đặt, gửi sàn, khớp, khớp một phần, huỷ, sửa, từ chối, hết hiệu lực.

Q

Format authenticate khác gì so với bảng giá (`d|a|||`)?

A

Endpoint Aither dùng format `authenticate|base64({'jwt':'token'})` — base64 encode toàn bộ JSON object chứa JWT. Bảng giá (Thesis/Ouranos) dùng `d|a|||base64(token_raw)`.

Q

Heartbeat dùng format nào?

A

Gửi `ping|1` (text frame) mỗi 2 giây. Timeout mặc định là 7 giây (từ server config `pingTimeout|7`).

Q

Có cần truyền accountNo khi subscribe không?

A

Không. Subscribe chỉ cần topic name. Server tự xác định account từ JWT token đã xác thực.
