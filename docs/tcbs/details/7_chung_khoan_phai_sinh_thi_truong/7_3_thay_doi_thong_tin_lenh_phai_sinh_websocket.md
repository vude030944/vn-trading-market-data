<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/derivative/ws-order-matching
Tieu de goc: 7.3. Thay đổi thông tin lệnh phái sinh (WebSocket)
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/ws-order-matching>

# 7.3. Thay đổi thông tin lệnh phái sinh (WebSocket)

Nhận thông báo real-time mỗi khi lệnh phái sinh của bạn thay đổi trạng thái — lệnh thường, lệnh điều kiện, và vị thế mở. Server đẩy cập nhật qua WebSocket ngay lập tức, bạn không cần polling. Mỗi loại lệnh có topic riêng để subscribe.

Endpoint: `/ws/nesoi`. Heartbeat là `ping|1` mỗi 2 giây (timeout 45s). Format dữ liệu: `message_proto|TOPIC|{JSON}`.

## Demo tương tác

Địa chỉ WSS

`WSSwss://openapi.tcbs.com.vn/ws/nesoi`

Payload kết nối / xác thực
```json
{
  "note": "Real auth: authenticate|base64({jwt:token})",
  "format": "authenticate|BASE64_JWT_PAYLOAD"
}
```

Kênh / Chủ đề

  * `DE_ORDER`Sổ lệnh thường phái sinh.
  * `DE_CONDITIONAL_ORDER`Sổ lệnh điều kiện phái sinh.
  * `DE_OPEN_POSITION`Vị thế mở và lãi/lỗ.

Đã ngắt

Kết nốiXóa

// Nhấn Kết nối để bắt đầu luồng mô phỏng…

Demo trên chỉ mang tính minh họa. Wire format thực tế là text frame dạng message_proto|TOPIC|{JSON}. Xem chi tiết bên dưới.

* * *

## Kết nối

WSS`/ws/nesoi`

Địa chỉ đầy đủ của WebSocket endpoint:
```text
wss://openapi.tcbs.com.vn/ws/nesoi
```

BẮT BUỘC: Bạn phải disable auto-ping (RFC 6455 ping frame) của WebSocket library. Server TCBS chỉ chấp nhận heartbeat dạng text frame ping|1.

| Ngôn ngữ | Thư viện | Disable auto-ping |
|---|---|---|
| Python | `websockets` | `connect(url, ping_interval=None, ping_timeout=None)` |
| JavaScript | `ws` | Default off — do NOT rely on library ping |

* * *

## Xác thực (Authentication)

Sau khi kết nối thành công, bạn gửi message xác thực theo format sau: **Client gửi đi** — authenticate message:
```text
authenticate|BASE64_PAYLOAD
```

Trong đó `BASE64_PAYLOAD` là base64 encode của chuỗi JSON chứa token OpenAPI của bạn:
```json
{"jwt":"YOUR_OPENAPI_TOKEN"}
```

**Ví dụ cụ thể:**

Token OpenAPI`igwfUq9M2IqWVhrFrYybEYKWxAxDbYzxz1RzOkp0L0S95lrMtrJDbMgFwy86r8Ir`

Base64({"jwt":"<token>"})`eyJqd3QiOiJpZ3dmVXE5TTJJcVdWaHJGcll5YkVZS1d4QXhEYll6eHoxUnpPa3AwTDBTOTVsck10ckpEYk1nRnd5ODZyOElyIn0=`

Client gửi server`authenticate|eyJqd3QiOiJpZ3dmVXE5TTJJcVdWaHJGcll5YkVZS1d4QXhEYll6eHoxUnpPa3AwTDBTOTVsck10ckpEYk1nRnd5ODZyOElyIn0=`

**Server trả về** — đầu tiên là timeout config:
```text
pingTimeout|45
```

Con số 45 nghĩa là nếu client không gửi heartbeat trong 45 giây, server sẽ ngắt kết nối. **Server trả về** — xác thực thành công:
```text
authenticate|{"success":true,"error":null}
```

Bạn PHẢI đợi nhận response auth thành công trước khi gửi subscribe. Không gửi subscribe ngay sau authenticate.

* * *

## Đăng ký kênh (Subscribe)

Sau khi auth thành công, bạn đăng ký từng topic riêng lẻ. Có 3 topic khả dụng:

| Topic | Base64 | Mô tả |
|---|---|---|
| `DE_ORDER` | `eyJ0b3BpYyI6IkRFX09SREVSIn0=` | Sổ lệnh thường |
| `DE_CONDITIONAL_ORDER` | `eyJ0b3BpYyI6IkRFX0NPTkRJVElPTkFMX09SREVSIn0=` | Sổ lệnh điều kiện |
| `DE_OPEN_POSITION` | `eyJ0b3BpYyI6IkRFX09QRU5fUE9TSVRJT04ifQ==` | Vị thế mở |

**Client gửi đi** — subscribe cho từng topic:

Subscribe theo topic

DE_ORDER`subscribe|eyJ0b3BpYyI6IkRFX09SREVSIn0=`

DE_CONDITIONAL_ORDER`subscribe|eyJ0b3BpYyI6IkRFX0NPTkRJVElPTkFMX09SREVSIn0=`

DE_OPEN_POSITION`subscribe|eyJ0b3BpYyI6IkRFX09QRU5fUE9TSVRJT04ifQ==`

* * *

## Heartbeat — Giữ kết nối

Client PHẢI gửi heartbeat text frame mỗi **2 giây**. Nếu server không nhận heartbeat trong **45 giây** (giá trị `pingTimeout`) thì sẽ tự động ngắt kết nối. **Client gửi đi** — heartbeat frame:
```text
ping|1
```

Heartbeat phải là TEXT frame, KHÔNG phải binary/ping frame theo RFC 6455. Tần suất: 1 message mỗi 2 giây.

* * *

## Cấu trúc Message

Server đẩy về cho bạn 2 loại message — control (điều khiển) và data (dữ liệu lệnh):

| Prefix | Loại | Mô tả |
|---|---|---|
| `pingTimeout\|N` | Control | Timeout config (N seconds) |
| `authenticate\|{...}` | Control | Auth response |
| `message_proto\|TOPIC\|{...}` | Data | Order/position update payload |

**Server trả về** — data message có format như sau:
```text
message_proto|<TOPIC>|{JSON_PAYLOAD}
```

**Ví dụ thực tế** — server đẩy về khi lệnh của bạn thay đổi trạng thái:
```text
message_proto|DE_ORDER|{"subAccount":"738764A","orderNo":"41","pkOrderNo":"7861546","orderTime":"14:34:10","accountCode":"738764A","side":"B","symbol":"VN30F2110","volume":1,"showPrice":"MTL","status":"P","orderStatus":"2","channel":"D","group":"FU","isCancel":"1","isAmend":"1"}
```

* * *

## Data Schema

### DE_ORDER — Sổ lệnh thường

DE_ORDER — Lệnh phái sinh thường

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `subAccount` | string |  | Số tài khoản phái sinh. |
| `orderNo` | string |  | Số hiệu lệnh. |
| `pkOrderNo` | string |  | Primary key lệnh. |
| `orderTime` | string |  | Thời gian đặt lệnh. |
| `accountCode` | string |  | Mã tài khoản. |
| `side` | string |  | Chiều lệnh: B = Mua, S = Bán. |
| `symbol` | string |  | Mã hợp đồng. |
| `volume` | int64 |  | Khối lượng đặt lệnh. |
| `showPrice` | string |  | Giá đặt (hoặc MTL = Market). |
| `matchVolume` | int64 |  | Khối lượng đã khớp. |
| `matchPriceBQ` | number |  | Giá khớp bình quân. |
| `status` | string |  | Trạng thái lệnh (xem bảng tổ hợp dưới). |
| `orderStatus` | string |  | Mã trạng thái lệnh. |
| `channel` | string |  | Kênh đặt lệnh. |
| `group` | string |  | Nhóm lệnh PS (FU = Futures). |
| `cancelTime` | string |  | Thời gian huỷ lệnh. |
| `isCancel` | string |  | Có thể huỷ (0 = Không, 1 = Có). |
| `isAmend` | string |  | Có thể sửa (0 = Không, 1 = Có). |
| `info` | string |  | Chi tiết từ chối (nếu bị reject). |
| `maxPrice` | int64 |  | Không dùng, luôn là 0. |
| `matchValue` | number |  | Giá trị khớp. |
| `quote` | string |  | Trạng thái: C=Hoàn tất, G=Chờ, Y=Khớp 1 phần. |
| `autoType` | string |  | Loại lệnh tự động (Arbitrage, SL/TP, hoặc rỗng). |
| `product` | string |  | Với ABI = mã HĐ đối ứng; với SL/TP = chỉ số SL/TP. |
| `orderType` | string |  | Loại lệnh (N = Normal). |
| `source` | string |  | SYS = hệ thống, USER = người dùng. |
| `traderCode` | string |  | Mã kênh đặt lệnh. |

### Bảng tổ hợp trạng thái DE_ORDER

| status | quote | Mô tả |
|---|---|---|
| `P` | `G` | Chờ khớp trên gateway — có thể huỷ |
| `P` | `Y` | Lệnh đã vào sổ |
| `P` |  | Thông tin lệnh có sửa đổi |
| `PM` | `G` | Lệnh đã khớp |
| `PC` | `Y` | Lệnh chờ xác nhận sửa |
| `PC` | `G` | Đã confirm sửa |
| `PMW` |  | Lệnh khớp 1 phần yêu cầu huỷ |
| `PW` | `Y` | Đặt lệnh huỷ — chờ huỷ |
| `PWX` |  | Lệnh huỷ được confirm bởi sở |
| `PMWX` |  | Lệnh khớp 1 phần huỷ đã xác nhận |

* * *

### DE_CONDITIONAL_ORDER — Sổ lệnh điều kiện

DE_CONDITIONAL_ORDER — Lệnh điều kiện phái sinh

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `sub_account` | string |  | Số tài khoản PS. |
| `order_no` | string |  | Số hiệu lệnh. |
| `group_order` | string |  | Nhóm lệnh. |
| `pk_order_no` | string |  | Primary key lệnh. |
| `account_code` | string |  | Mã tài khoản. |
| `side` | string |  | B = Mua, S = Bán. |
| `symbol` | string |  | Mã hợp đồng. |
| `volume` | int64 |  | Khối lượng lệnh. |
| `show_price` | string |  | Giá đặt. |
| `condition` | string |  | Điều kiện kích hoạt. |
| `result` | string |  | 0 = Huỷ, 1 = Kích hoạt. |
| `active_time` | string |  | Thời gian kích hoạt. |
| `send_time` | string |  | Thời gian đặt lệnh. |
| `cancel_time` | string |  | Thời gian huỷ. |
| `group` | string |  | Nhóm PS (FU). |
| `channel` | string |  | Kênh đặt lệnh. |
| `so_price` | number |  | Giá stop. |
| `order_type` | string |  | Loại lệnh. |
| `from_time` | string |  | Có giá trị từ ngày. |
| `exp_time` | string |  | Đến ngày. |
| `status` | string |  | 1 = Kích hoạt, 2 = Đã huỷ, 3 = Từ chối. |
| `details` | string |  | Số hiệu lệnh đã kích hoạt. |
| `message` | string |  | Thông báo. |
| `notes` | string |  | Loại chiến lược (SL/TP, Stop order, Arbitrage). |
| `call_back_point` | string |  | Biên trượt (trailing stop). |
| `trailing_price` | string |  | Giá trailing. |
| `trigger_condition` | string |  | Điều kiện kích hoạt trailing. |

### DE_OPEN_POSITION — Vị thế mở

DE_OPEN_POSITION — Vị thế mở phái sinh

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `sub_account` | string |  | Số tài khoản PS. |
| `symbol` | string |  | Mã hợp đồng. |
| `side` | string |  | L = Long, S = Short. |
| `account` | string |  | Số tài khoản (duplicate). |
| `last_price` | number |  | Giá hiện tại. |
| `avg_remain` | number |  | Giá trung bình phần còn lại. |
| `im_value` | number |  | Giá trị ký quỹ ban đầu. |
| `net` | number |  | Số vị thế đang nắm giữ. |
| `stoploss` | number |  | Giá stop loss. |
| `takeprofit` | number |  | Giá take profit. |
| `pc_remain` | number |  | % lãi/lỗ vị thế mở. |
| `vm_remain` | number |  | Giá trị VM chưa đóng. |
| `duedate` | string |  | Ngày đáo hạn. |
| `netoffvol` | int64 |  | Số cần net-off. |
| `trigger_type` | string |  | Giá kích hoạt trailing. |
| `call_back_point` | number |  | Biên trượt trailing. |
| `trailing_price` | number |  | Giá lệnh trailing. |

* * *

## Sequence Diagram

Luồng kết nối WebSocket thay đổi thông tin lệnh phái sinh

* * *

## Xử lý lỗi & Reconnect

| Nguyên nhân | Triệu chứng | Giải pháp |
|---|---|---|
| No heartbeat >45s | Connection closed | Ensure ping\|1 every 2s |
| Library sends RFC ping | Unexpected disconnect | Disable auto-ping |
| Token expired | Auth fails | Refresh token, reconnect |
| Server maintenance | Connection refused | Exponential backoff retry |

**Chiến lược reconnect:** Dùng exponential backoff với công thức `delay = min(2^attempt, 30)` giây. Tối đa thử 10 lần, sau đó bạn nên alert để xử lý thủ công.

* * *

## Code hoàn chỉnh

PythonNode.js

Sao chép
```python
"""WebSocket client for TCBS derivative order updates — Python 3.10+"""

import asyncio
import base64
import json

from websockets.asyncio.client import connect

WS_URL = "wss://openapi.tcbs.com.vn/ws/nesoi"
TOKEN = "YOUR_OPENAPI_TOKEN_HERE"

TOPICS = ["DE_ORDER", "DE_CONDITIONAL_ORDER", "DE_OPEN_POSITION"]

async def main():
    async with connect(WS_URL, ping_interval=None, ping_timeout=None) as ws:

        # 1. Authenticate
        jwt_payload = json.dumps({"jwt": TOKEN})
        encoded = base64.b64encode(jwt_payload.encode()).decode()
        await ws.send(f"authenticate|{encoded}")

        # 2. Wait for auth response
        while True:
            msg = await asyncio.wait_for(ws.recv(), timeout=10.0)
            print(f"< {msg}")
            if msg.startswith("authenticate|"):
                payload = msg.split("|", 1)[1]
                result = json.loads(payload)
                if result.get("success"):
                    break
                else:
                    raise Exception(f"Auth failed: {result}")

        # 3. Subscribe to all topics
        for topic in TOPICS:
            sub_payload = base64.b64encode(json.dumps({"topic": topic}).encode()).decode()
            await ws.send(f"subscribe|{sub_payload}")
            print(f"Subscribed to {topic}")

        # 4. Heartbeat task
        async def heartbeat():
            while True:
                await ws.send("ping|1")
                await asyncio.sleep(2)

        asyncio.create_task(heartbeat())

        # 5. Receive updates
        while True:
            raw = await ws.recv()
            if raw.startswith("message_proto|"):
                parts = raw.split("|", 2)
                topic = parts[1]
                data = json.loads(parts[2])

                if topic == "DE_ORDER":
                    print(f"[ORDER] {data.get('symbol')} "
                          f"Side={data.get('side')} "
                          f"Status={data.get('status')} "
                          f"Vol={data.get('volume')}")
                elif topic == "DE_OPEN_POSITION":
                    print(f"[POSITION] {data.get('symbol')} "
                          f"Net={data.get('net')} "
                          f"PnL%={data.get('pcRemain')}")
                elif topic == "DE_CONDITIONAL_ORDER":
                    print(f"[COND] {data.get('symbol')} "
                          f"Status={data.get('status')} "
                          f"Type={data.get('notes')}")

if __name__ == "__main__":
    asyncio.run(main())
```

* * *

## FAQ

Q

Endpoint Nesoi khác gì so với Aither (cổ phiếu)?

A

Nesoi dành riêng cho phái sinh, hỗ trợ 3 topic (`DE_ORDER`, `DE_CONDITIONAL_ORDER`, `DE_OPEN_POSITION`). Aither chỉ có 1 topic (`STOCK_ORDER`). Timeout của Nesoi là 45s (vs 7s của Aither).

Q

Trường `status` và `quote` kết hợp như thế nào?

A

`status` cho biết trạng thái luồng (`P`=Pending, `PM`=Matched, `PC`=Cancel, `PW`=Waiting cancel...), `quote` cho biết trạng thái chi tiết (`G`=Gateway/chờ, `Y`=Đã gửi sổ). Xem bảng tổ hợp ở trên.

Q

`DE_OPEN_POSITION` push khi nào?

A

Mỗi khi vị thế của bạn thay đổi (lệnh khớp, net-off) hoặc khi giá thị trường thay đổi đáng kể (cập nhật lãi/lỗ realtime).

Q

Có cần subscribe tất cả 3 topic không?

A

Không bắt buộc. Bạn chỉ cần subscribe topic nào mình quan tâm. Ví dụ chỉ theo dõi lệnh thường thì subscribe `DE_ORDER` là đủ.
