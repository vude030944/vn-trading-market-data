<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/tutorials/websocket-data
Tieu de goc: 10. WebSocket Market Data
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/tutorials/websocket-data>

# 10\. WebSocket Market Data

Nhận giá khớp, bảng giá, room nước ngoài tức thời qua WebSocket

## Mục tiêu

Nhận tick data real-time (giá khớp, bảng giá, room nước ngoài) qua WebSocket. Không cần OTP cho market data.

## Luồng xử lý
```text
Client ↔ Streaming API ↔ Market Data Event
```

  1. Mở kết nối WebSocket bằng token hợp lệ (không cần OTP)
  2. Subscribe stream theo symbol (`subscribe_symbol`) và index (`subscribe_index`)
  3. Server push event khi có giao dịch mới hoặc bảng giá thay đổi
  4. Callback `on_data` phân loại message: `TradeMessage`, `QuoteMessage`, `ForeignRoomMessage`
  5. Khi mất kết nối, SDK có cơ chế reconnect

## Các loại Message

| Type | Mô tả |
|---|---|
| `TradeMessage` | Giá khớp, khối lượng, chiều mua/bán |
| `QuoteMessage` | Bảng giá bid/ask |
| `ForeignRoomMessage` | Room nước ngoài còn lại |
| `HeartbeatMessage` | Keepalive từ server |

## Sample Code — Sync

python/sample_10_websocket_data.py
```python
from ssi_sdk import Auth, Stream, Config
from auth_helper import ensure_auth
from ssi_sdk.models.streaming import (
    TradeMessage, QuoteMessage, ForeignRoomMessage, HeartbeatMessage,
)

config = Config(
    client_id="<your_client_id>",
    api_key="<your_api_key>",
    api_secret="<your_api_secret>",
    private_key="<your_private_key>",
)

# Callback xử lý dữ liệu
def on_market_data(msg):
    if isinstance(msg, TradeMessage):
        print(f"  [TRADE] {msg.symbol} | Giá: {msg.price} | KL: {msg.quantity}")
    elif isinstance(msg, QuoteMessage):
        print(f"  [QUOTE] {msg.symbol} | Bid: {msg.bid_prices[:3]} | Ask: {msg.ask_prices[:3]}")
    elif isinstance(msg, ForeignRoomMessage):
        print(f"  [ROOM]  {msg.symbol} | Room: {msg.current_room}/{msg.total_room}")

def on_heartbeat(msg: HeartbeatMessage):
    print(f"  [HEARTBEAT] {msg.status}")

with Auth(config) as auth:
    ensure_auth(auth)  # Không cần OTP

    with Stream(auth) as stream:
        stream.streaming.connect()
        stream.streaming.on_data = on_market_data
        stream.streaming.on_heartbeat = on_heartbeat

        # Subscribe theo symbol và index
        stream.streaming.subscribe_symbol(["SSI", "HPG", "VNM"])
        stream.streaming.subscribe_index(["VNINDEX", "HNX-INDEX"])

        # Lắng nghe 5 phút
        try:
            stream.streaming.wait(timeout=300)
        except KeyboardInterrupt:
            print("Ngắt kết nối...")
```

## Sample Code — Async

python/sample_10_websocket_data_async.py
```python
import asyncio
from ssi_sdk import AsyncAuth, AsyncStream, Config
from auth_helper import ensure_auth_async
from ssi_sdk.models.streaming import TradeMessage, QuoteMessage, ForeignRoomMessage

config = Config(...)

def on_market_data(msg):
    if isinstance(msg, TradeMessage):
        print(f"  [TRADE] {msg.symbol} | {msg.price} x {msg.quantity}")
    elif isinstance(msg, QuoteMessage):
        print(f"  [QUOTE] {msg.symbol}")

async def main():
    async with AsyncAuth(config) as auth:
        await ensure_auth_async(auth)
        async with AsyncStream(auth) as stream:
            await stream.streaming.connect()
            stream.streaming.on_data = on_market_data

            await stream.streaming.subscribe_symbol(["SSI", "HPG", "VNM"])
            await stream.streaming.subscribe_index(["VNINDEX"])

            try:
                await stream.streaming.wait(timeout=300)
            except KeyboardInterrupt:
                print("Disconnecting...")

asyncio.run(main())
```

## Lưu ý

  * **Không cần OTP** cho market data streaming.
  * SDK tự xử lý reconnect khi mất kết nối.
  * Sử dụng `wait(timeout=...)` để giới hạn thời gian lắng nghe.
  * Có thể subscribe nhiều symbol và index cùng lúc.
