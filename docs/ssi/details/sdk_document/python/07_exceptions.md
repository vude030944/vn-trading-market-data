<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/python/exceptions
Tieu de goc: Xử lý lỗi
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/python/exceptions>

# Xử lý lỗi

Hệ thống exception và cách xử lý lỗi trong Python SDK

SDK sử dụng hệ thống exception phân cấp:

## Danh sách exception

| Exception | Mô tả |
|---|---|
| `SSIError` | Base exception — có `message`, `code`, `status_code`, `response_body`, `headers` |
| `AuthenticationError` | Xác thực thất bại (sai credentials, token hết hạn) |
| `APIError` | API trả về lỗi — có thêm `status_code`, `response_body` |
| `WebSocketError` | Lỗi kết nối hoặc giao tiếp WebSocket |
| `ValidationError` | Lỗi validate input |
| `RateLimitError` | Vượt quá giới hạn request — có thêm `retry_after` |

## Chuỗi kế thừa
```text
Exception → SSIError → AuthenticationError
Exception → SSIError → APIError
Exception → SSIError → WebSocketError
Exception → SSIError → ValidationError
Exception → SSIError → RateLimitError
```

## Sử dụng cơ bản
```python
from ssi_sdk import SSIError

try:
    auth.authenticate(otp="wrong_otp")
except SSIError as e:
    print(f"Lỗi: {e.message} (code: {e.code})")
```

## Xử lý chi tiết theo loại lỗi
```python
from ssi_sdk.exceptions import APIError, AuthenticationError, RateLimitError
from ssi_sdk.enums import OrderSide

try:
    result = trading.trading.place_limit_order(
        account_no="1234561",
        symbol="SSI",
        side=OrderSide.BUY,
        quantity=100,
        price=68000,
    )
except AuthenticationError:
    print("Cần xác thực lại")
except RateLimitError as e:
    print(f"Rate limited, retry sau {e.retry_after}s")
except APIError as e:
    print(f"API error {e.status_code}: {e.message}")
```

## Gợi ý xử lý

  * Bắt `SSIError` ở lớp ngoài cùng để gom lỗi chung.
  * Bắt `AuthenticationError` khi cần refresh token hoặc yêu cầu OTP mới.
  * Bắt `RateLimitError` và tôn trọng `retry_after` để backoff.
  * Bắt `APIError` để xử lý lỗi nghiệp vụ từ server.
  * Bắt `WebSocketError` khi xử lý streaming.
  * Bắt `ValidationError` khi cần xác thực input trước khi gọi API.
