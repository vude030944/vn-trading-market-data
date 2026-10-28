<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/python/client-classes
Tieu de goc: Client classes
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/python/client-classes>

# Client classes

Auth, Data, Trading, Stream — khởi tạo và sử dụng

SDK cung cấp 4 client chuyên biệt, mỗi client có phiên bản sync và async.

## Auth / AsyncAuth

Client gốc — quản lý REST client, xác thực và token. Tất cả client khác đều nhận `Auth` làm tham số.
```python
from ssi_sdk import Auth, Config

config = Config(
    client_id="YOUR_CLIENT_ID",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
    private_key="YOUR_PRIVATE_KEY",
)

with Auth(config) as auth:
    # Xác thực với OTP
    token = auth.authenticate(otp="222222")
    print(f"Access token: {token.access_token}")
    print(f"Expires at: {token.expires_at}")
```

### Các method xác thực
```text
# Yêu cầu gửi OTP
result = auth.request_otp()

# Xác thực với OTP
token = auth.authenticate(otp="222222")

# Làm mới token
token = auth.refresh()

# Tự động refresh nếu token hết hạn, hoặc yêu cầu OTP nếu cần
access_token = auth.ensure_authenticated(otp="222222")
```

### Approve OTP (Smart OTP push-approval)

Tài khoản đã kích hoạt Smart OTP có thể duyệt trực tiếp trên app thay vì nhập mã. Gọi `request_otp()` để gửi yêu cầu, lấy `transaction_id`, rồi truyền vào `ensure_authenticated()` — SDK tự poll cho đến khi user bấm duyệt.
```text
# Bước 1: gửi yêu cầu duyệt, nhận transaction_id
otp_result = auth.request_otp()
transaction_id = otp_result["transactionId"]

# Bước 2: SDK tự poll cho đến khi user bấm duyệt trên app Smart OTP
access_token = auth.ensure_authenticated(
    transaction_id=transaction_id,
    poll_interval=5,      # giây giữa mỗi lần poll (mặc định 5)
    poll_max_retries=5,   # số lần poll tối đa (mặc định 5)
)
```

Trong lúc chờ, server trả HTTP 202 + code `401114` ("Push-approval is pending") — SDK tự xử lý. Nếu hết `poll_max_retries` mà vẫn chưa duyệt, `ensure_authenticated` raise `AuthenticationError`.

### Kiểm tra trạng thái token
```python
print(auth.token)              # Token object hoặc None
print(auth.access_token)       # Access token string hoặc None
print(auth.is_token_expired)   # True/False
print(auth.has_refresh_token)  # True/False
```

## Data / AsyncData

Client dữ liệu thị trường. **Không cần OTP** — chỉ cần `auth.authenticate()`.
```python
from ssi_sdk import Auth, Data, Config

with Auth(config) as auth:
    auth.authenticate()  # Không cần OTP cho market data

    with Data(auth) as data:
        # Truy cập qua service
        ohlc = data.market_data.get_ohlc_1minute("SSI")
        indices = data.market_data.get_indexes()
        info = data.market_data.get_securities_info("SSI")
```

**Service:** `data.market_data` (`MarketDataService`) — OHLC, chỉ số, chứng khoán, securities summary.

## Trading / AsyncTrading

Client giao dịch, tài khoản và danh mục. **Cần OTP**.
```python
from ssi_sdk import Auth, Trading, Config
from ssi_sdk.enums import OrderSide

with Auth(config) as auth:
    auth.authenticate(otp="222222")

    with Trading(auth) as trading:
        # Tài khoản
        accounts = trading.account.get_account_info()

        # Danh mục
        balance = trading.portfolio.get_equity_balance("1234561")
        positions = trading.portfolio.get_equity_positions("1234561")
        orders = trading.portfolio.get_today_orders("1234561")

        # Giao dịch
        result = trading.trading.place_limit_order(
            account_no="1234561",
            symbol="SSI",
            side=OrderSide.BUY,
            quantity=100,
            price=66000,
        )
```

**Services:**

  * `trading.account` (`AccountService`) — thông tin tài khoản.
  * `trading.portfolio` (`PortfolioService`) — số dư, vị thế, sổ lệnh, PPMMR.
  * `trading.trading` (`TradingService`) — đặt/sửa/huỷ lệnh, sức mua/bán, lệnh điều kiện (FCO).

## Stream / AsyncStream

Client streaming realtime qua WebSocket. **Cần OTP**.
```python
from ssi_sdk import Auth, Stream, Config

with Auth(config) as auth:
    auth.authenticate(otp="222222")

    with Stream(auth) as stream:
        stream.streaming.connect()

        # Đăng ký callback
        stream.streaming.on_data = lambda msg: print(f"Data: {msg}")
        stream.streaming.on_trading = lambda msg: print(f"Trading: {msg}")

        # Subscribe
        stream.streaming.subscribe_symbol(["SSI", "HPG"])
        stream.streaming.subscribe_order_status()

        # Chờ nhận dữ liệu
        stream.streaming.wait()
```

**Service:** `stream.streaming` (`StreamingService`) — subscribe/unsubscribe realtime data.

**Callbacks:**

| Property | Kiểu | Mô tả |
|---|---|---|
| `on_data` | `Callable[[message], Any]` | Nhận market data (tự parse thành typed message) |
| `on_trading` | `Callable[[OrderStatusMessage \| FCOOrderUpdateMessage \| PortfolioMessage], Any]` | Nhận trading events |
| `on_heartbeat` | `Callable[[HeartbeatMessage], Any]` | Nhận heartbeat |

## Async example hoàn chỉnh
```python
import asyncio
from ssi_sdk import AsyncAuth, AsyncData, AsyncTrading, AsyncStream, Config

async def main():
    config = Config(
        client_id="YOUR_CLIENT_ID",
        api_key="YOUR_API_KEY",
        api_secret="YOUR_API_SECRET",
        private_key="YOUR_PRIVATE_KEY",
    )

    async with AsyncAuth(config) as auth:
        await auth.authenticate(otp="222222")

        async with AsyncData(auth) as data:
            ohlc = await data.market_data.get_ohlc_1minute("SSI")
            print(ohlc)

        async with AsyncTrading(auth) as trading:
            accounts = await trading.account.get_account_info()
            print(accounts)

        async with AsyncStream(auth) as stream:
            await stream.streaming.connect()
            stream.streaming.on_data = lambda msg: print(msg)
            await stream.streaming.subscribe_symbol_trade(["SSI"])
            await stream.streaming.wait()

asyncio.run(main())
```

## Ghi chú

  * Nhóm `Async*` dùng `async with` và `await`.
  * Nhóm sync (`Auth`, `Data`, `Trading`, `Stream`) dùng `with` — phù hợp luồng xử lý tuần tự.
  * Tất cả client chia sẻ HTTP connection qua `Auth`.
  * Lỗi thường gặp: `AuthenticationError` (xác thực), `WebSocketError` (stream), `APIError` (HTTP lỗi nghiệp vụ).
