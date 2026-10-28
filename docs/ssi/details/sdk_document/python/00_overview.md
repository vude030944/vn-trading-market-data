<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/python/overview
Tieu de goc: Tổng quan
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/python/overview>

# Tổng quan

Tổng quan Python SDK của SSI FastConnect — REST API và WebSocket streaming

Python SDK cho nền tảng giao dịch chứng khoán SSI. Hỗ trợ REST API và WebSocket streaming, cả đồng bộ (sync) và bất đồng bộ (async).

**Yêu cầu:** Python 3.10+

## Cài đặt
```bash
pip install ssi-sdk
```

## Kiến trúc Client

SDK sử dụng kiến trúc **modular** gồm 4 client chuyên biệt:

| Client | Async | Mô tả | Yêu cầu |
|---|---|---|---|
| `Auth` | `AsyncAuth` | Xác thực & quản lý token | `Config` |
| `Data` | `AsyncData` | Dữ liệu thị trường (OHLC, chỉ số, chứng khoán) | `Auth` (không cần OTP) |
| `Trading` | `AsyncTrading` | Giao dịch + danh mục + tài khoản | `Auth` (cần OTP) |
| `Stream` | `AsyncStream` | Streaming realtime qua WebSocket | `Auth` (cần OTP) |

**Luồng khởi tạo:**
```text
Config → Auth → authenticate(otp=...) → Data / Trading / Stream
```

`Auth` là client gốc — quản lý REST client và token. Các client `Data`, `Trading`, `Stream` đều nhận `Auth` làm tham số và chia sẻ chung HTTP connection.

**Services được cung cấp bởi mỗi client:**

| Client | Service | Truy cập | Mô tả |
|---|---|---|---|
| `Auth` | `TokenManager` | `auth.token_manager` | Xác thực, OTP, refresh token |
| `Data` | `MarketDataService` | `data.market_data` | OHLC, chỉ số, chứng khoán, securities summary |
| `Trading` | `TradingService` | `trading.trading` | Đặt/sửa/huỷ lệnh, sức mua/bán, lệnh điều kiện (FCO) |
| `Trading` | `AccountService` | `trading.account` | Thông tin tài khoản |
| `Trading` | `PortfolioService` | `trading.portfolio` | Số dư, vị thế, sổ lệnh, PPMMR |
| `Stream` | `StreamingService` | `stream.streaming` | Subscribe/unsubscribe realtime data |

## Ví dụ nhanh

### Async (khuyến nghị)
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

        # Dữ liệu thị trường
        async with AsyncData(auth) as data:
            ohlc = await data.market_data.get_ohlc_1minute("SSI")
            print(ohlc)

        # Giao dịch & danh mục
        async with AsyncTrading(auth) as trading:
            accounts = await trading.account.get_account_info()
            print(accounts)

        # Streaming
        async with AsyncStream(auth) as stream:
            await stream.streaming.connect()
            stream.streaming.on_data = lambda msg: print(msg)
            await stream.streaming.subscribe_symbol_trade(["SSI"])
            await stream.streaming.wait()

asyncio.run(main())
```

### Sync
```python
from ssi_sdk import Auth, Data, Trading, Config

config = Config(
    client_id="YOUR_CLIENT_ID",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
    private_key="YOUR_PRIVATE_KEY",
)

with Auth(config) as auth:
    auth.authenticate(otp="222222")

    with Trading(auth) as trading:
        accounts = trading.account.get_account_info()
        print(accounts)
```

### Chỉ dùng dữ liệu thị trường (không cần OTP)
```python
from ssi_sdk import Auth, Data, Config

with Auth(config) as auth:
    auth.authenticate()  # Không cần OTP cho market data

    with Data(auth) as data:
        ohlc = data.market_data.get_ohlc_1minute("SSI")
```

## Mapping nhanh theo use case

| Use case | Client đề xuất | Yêu cầu xác thực |
|---|---|---|
| Dữ liệu thị trường (OHLC, chỉ số, chứng khoán) | `Data` / `AsyncData` | Không cần OTP |
| Đặt/sửa/hủy lệnh, xem tài khoản, danh mục | `Trading` / `AsyncTrading` | Cần OTP |
| Streaming WebSocket realtime | `Stream` / `AsyncStream` | Cần OTP |

## Điều hướng tài liệu

  * **Cài đặt và cấu hình** : môi trường, package, `Config`.
  * **Client classes** : `Auth`, `Data`, `Trading`, `Stream` — cách khởi tạo và sử dụng.
  * **Service classes** : chi tiết các method API cho từng service.
  * **Cấu hình** : tham số `Config` đầy đủ.
  * **Xử lý lỗi** : hệ thống exception và cách xử lý.
  * **Enums** : các hằng số `OrderSide`, `OrderType`, `Board`, ...
  * **Models** : các model dữ liệu trả về.
