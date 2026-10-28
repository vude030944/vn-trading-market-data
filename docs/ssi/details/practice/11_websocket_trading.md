<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/tutorials/websocket-trading
Tieu de goc: 11. WebSocket Trading
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/tutorials/websocket-trading>

# 11\. WebSocket Trading

Nhận cập nhật trạng thái lệnh và danh mục tài khoản real-time qua WebSocket

## Mục tiêu

Nhận cập nhật tức thời về trạng thái lệnh khớp và danh mục tài khoản qua WebSocket. **Cần OTP** khi authenticate.

## Luồng xử lý
```text
Client ↔ Streaming API ↔ Trading Event
```

  1. Mở kết nối WebSocket bằng token hợp lệ (cần OTP)
  2. Subscribe `subscribe_order_status(account_no)` và `subscribe_portfolio(account_no)`
  3. Server push event khi trạng thái lệnh hoặc danh mục thay đổi
  4. Callback `on_trading` phân loại: `OrderStatusMessage`, `PortfolioMessage`
  5. Khi mất kết nối, SDK có cơ chế reconnect

## Các loại Message

| Type | Mô tả |
|---|---|
| `OrderStatusMessage` | Trạng thái lệnh (symbol, side, orderId, status, filled) |
| `PortfolioMessage` | Danh mục tài khoản (total_asset, cash_balance) |
| `HeartbeatMessage` | Keepalive từ server |

## Sample Code — Sync

python/sample_11_websocket_trading.py
```python
from ssi_sdk import Auth, Stream, Config
from auth_helper import ensure_auth
from ssi_sdk.models.streaming import OrderStatusMessage, PortfolioMessage, HeartbeatMessage

config = Config(
    client_id="<your_client_id>",
    api_key="<your_api_key>",
    api_secret="<your_api_secret>",
    private_key="<your_private_key>",
)
ACCOUNT_NO = "<your_account_no>"

def on_trading_event(msg):
    if isinstance(msg, OrderStatusMessage):
        print(
            f"  [ORDER] {msg.symbol} {msg.side} | ID: {msg.order_id} "
            f"| Status: {msg.status} | Khớp: {msg.filled_quantity}/{msg.quantity}"
        )
    elif isinstance(msg, PortfolioMessage):
        print(f"  [PORTFOLIO] Account: {msg.account_no} | Tổng TS: {msg.total_asset}")

def on_heartbeat(msg: HeartbeatMessage):
    print(f"  [HEARTBEAT] {msg.status}")

with Auth(config) as auth:
    ensure_auth(auth, otp="<your_otp>")  # Cần OTP

    with Stream(auth) as stream:
        stream.streaming.connect()
        stream.streaming.on_trading = on_trading_event
        stream.streaming.on_heartbeat = on_heartbeat

        # Subscribe trạng thái lệnh
        stream.streaming.subscribe_order_status(ACCOUNT_NO)

        # Subscribe danh mục (optional)
        # stream.streaming.subscribe_portfolio(ACCOUNT_NO)

        try:
            stream.streaming.wait(timeout=300)
        except KeyboardInterrupt:
            print("Ngắt kết nối...")
```

## Sample Code — Async

python/sample_11_websocket_trading_async.py
```python
import asyncio
from ssi_sdk import AsyncAuth, AsyncStream, Config
from auth_helper import ensure_auth_async
from ssi_sdk.models.streaming import OrderStatusMessage, PortfolioMessage

config = Config(...)
ACCOUNT_NO = "<your_account_no>"

def on_trading_event(msg):
    if isinstance(msg, OrderStatusMessage):
        print(f"  [ORDER] {msg.symbol} | {msg.status} | {msg.filled_quantity}/{msg.quantity}")
    elif isinstance(msg, PortfolioMessage):
        print(f"  [PORTFOLIO] {msg.account_no} | {msg.total_asset}")

async def main():
    async with AsyncAuth(config) as auth:
        await ensure_auth_async(auth, otp="<your_otp>")
        async with AsyncStream(auth) as stream:
            await stream.streaming.connect()
            stream.streaming.on_trading = on_trading_event

            await stream.streaming.subscribe_order_status(ACCOUNT_NO)

            try:
                await stream.streaming.wait(timeout=300)
            except KeyboardInterrupt:
                pass

asyncio.run(main())
```

## So sánh Polling vs WebSocket

|  | Polling (Sample 8) | WebSocket (Sample 11) |
|---|---|---|
| Latency | Theo chu kỳ poll (3-5s) | Near real-time (<100ms) |
| Traffic | Nhiều request lặp lại | 1 kết nối duy trì |
| Complexity | Đơn giản | Cần xử lý reconnect |
| Use case | Kiểm tra nhanh | Production monitoring |
