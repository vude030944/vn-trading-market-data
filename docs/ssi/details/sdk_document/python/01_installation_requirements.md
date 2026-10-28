<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/python/installation-requirements
Tieu de goc: Cài đặt và cấu hình
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/python/installation-requirements>

# Cài đặt và cấu hình

Hướng dẫn cài đặt và cấu hình Python SDK

## Yêu cầu môi trường

  * Python `>=3.10`
  * Kết nối mạng đến REST API và WebSocket endpoint
  * `client_id`, `api_key`, `api_secret` từ SSI
  * `private_key` cho ký lệnh giao dịch
  * OTP khi xác thực cho các luồng Trading/Stream

## Cài đặt
```bash
pip install ssi-sdk
```

## Cấu hình

Tạo đối tượng `Config` với thông tin xác thực:
```python
from ssi_sdk import Config

config = Config(
    client_id="YOUR_CLIENT_ID",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
    private_key="YOUR_PRIVATE_KEY",
)
```

Hoặc truyền config bằng keyword arguments trực tiếp cho `Auth`:
```python
from ssi_sdk import Auth

auth = Auth(
    client_id="YOUR_CLIENT_ID",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
    private_key="YOUR_PRIVATE_KEY",
    timeout=60,
    log_level="DEBUG",
)
```

## Luồng khởi tạo
```text
Config → Auth → authenticate(otp=...) → Data / Trading / Stream
```

  1. Tạo `Config` với credential.
  2. Khởi tạo `Auth` / `AsyncAuth` với `Config`.
  3. Gọi `auth.authenticate(otp=...)` — không cần OTP nếu chỉ dùng market data.
  4. Khởi tạo client cần thiết (`Data`, `Trading`, `Stream`) với `auth`.
  5. Với `Stream`, gọi `stream.streaming.connect()` trước khi subscribe.

## Ví dụ khởi tạo theo use case

### Chỉ dữ liệu thị trường (không cần OTP)
```python
from ssi_sdk import Auth, Data, Config

config = Config(
    client_id="YOUR_CLIENT_ID",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
)

with Auth(config) as auth:
    auth.authenticate()  # Không cần OTP

    with Data(auth) as data:
        ohlc = data.market_data.get_ohlc_1minute("SSI")
        print(ohlc)
```

### Giao dịch (cần OTP)
```python
from ssi_sdk import Auth, Trading, Config

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

### Streaming realtime (cần OTP)
```python
from ssi_sdk import Auth, Stream, Config

config = Config(
    client_id="YOUR_CLIENT_ID",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
    private_key="YOUR_PRIVATE_KEY",
)

with Auth(config) as auth:
    auth.authenticate(otp="222222")

    with Stream(auth) as stream:
        stream.streaming.connect()
        stream.streaming.on_data = lambda msg: print(msg)
        stream.streaming.subscribe_symbol_trade(["SSI"])
        stream.streaming.wait()
```

## Gợi ý

  * Xác thực trước khi gọi API cần token.
  * Với streaming, gọi `connect()` sau khi xác thực thành công.
  * Bật `log_level="DEBUG"` khi cần điều tra lỗi.
  * Giữ thông tin khóa (`api_key`, `api_secret`, `private_key`) trong secret manager.
