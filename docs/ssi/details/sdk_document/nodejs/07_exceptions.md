<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/nodejs/exceptions
Tieu de goc: Xử lý lỗi
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/nodejs/exceptions>

# Xử lý lỗi

Các loại error và cách xử lý trong Node.js SDK

SDK sử dụng hệ thống error phân cấp. Tất cả error đều kế thừa từ `SSIError`, kế thừa từ `Error` chuẩn.

## Danh sách Error

| Error Class | Kế thừa | Mô tả |
|---|---|---|
| `SSIError` | `Error` | Error cơ sở — có `message` |
| `APIError` | `SSIError` | API trả về lỗi — có thêm `code`, `statusCode`, `responseBody` |
| `AuthenticationError` | `APIError` | Xác thực thất bại (sai credentials, token hết hạn) |
| `RateLimitError` | `SSIError` | Vượt quá giới hạn request — có thêm `retryAfter` |
| `WebSocketError` | `SSIError` | Lỗi kết nối hoặc giao tiếp WebSocket |
| `ValidationError` | `SSIError` | Lỗi validate input |
| `ConfigurationError` | `SSIError` | Lỗi cấu hình |

## Import
```python
import {
  SSIError,
  APIError,
  AuthenticationError,
  RateLimitError,
  WebSocketError,
  ValidationError,
  ConfigurationError,
} from '@ssi.developer/ssi-sdk';
```

## Sử dụng cơ bản
```javascript
try {
  const token = await auth.authenticate('wrong_otp');
} catch (error) {
  console.error(`Error: ${error.message}`);
}
```

## Xử lý lỗi chi tiết
```javascript
try {
  const result = await trading.trading.placeLimitOrder(
    '1234561', 'SSI', OrderSide.BUY, 100, 68000,
  );
} catch (error) {
  if (error instanceof AuthenticationError) {
    console.log('Cần xác thực lại');
  } else if (error instanceof RateLimitError) {
    console.log(`Rate limited, retry sau ${error.retryAfter}s`);
  } else if (error instanceof APIError) {
    console.log(`API error ${error.statusCode}: ${error.message}`);
  } else if (error instanceof ValidationError) {
    console.log(`Validation: ${error.message}`);
  } else if (error instanceof WebSocketError) {
    console.log(`WebSocket: ${error.message}`);
  } else if (error instanceof ConfigurationError) {
    console.log(`Config: ${error.message}`);
  } else if (error instanceof SSIError) {
    console.log(`SDK error: ${error.message}`);
  } else {
    console.log(`Unknown error: ${error}`);
  }
}
```

## Thuộc tính Error

### APIError

| Thuộc tính | Kiểu | Mô tả |
|---|---|---|
| `message` | `string` | Thông báo lỗi |
| `code` | `string` | Mã lỗi |
| `statusCode` | `number` | HTTP status code |
| `responseBody` | `string?` | Body response gốc (nếu có) |

### RateLimitError

| Thuộc tính | Kiểu | Mô tả |
|---|---|---|
| `message` | `string` | Thông báo lỗi |
| `retryAfter` | `number?` | Thời gian chờ trước khi retry (giây) |

## Hướng dẫn xử lý

  * Dùng `instanceof` để xử lý từng loại error.
  * Bắt `AuthenticationError` khi cần làm mới token hoặc lấy OTP mới.
  * Bắt `RateLimitError` và tuân thủ `retryAfter` để backoff.
  * Bắt `APIError` để xử lý lỗi nghiệp vụ từ server.
  * Bắt `WebSocketError` khi xử lý kết nối streaming.
  * Bắt `ValidationError` để kiểm tra input trước khi gọi API.
  * Bắt `ConfigurationError` khi cấu hình thiếu hoặc không hợp lệ.
  * Dùng `SSIError` làm fallback cho tất cả lỗi SDK.
