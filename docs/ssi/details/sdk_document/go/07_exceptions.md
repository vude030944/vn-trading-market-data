<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/go/exceptions
Tieu de goc: Xử lý lỗi
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/go/exceptions>

# Xử lý lỗi

Các loại error và cách xử lý trong Go SDK

SDK sử dụng hệ thống error phân cấp. Tất cả error type đều implement interface `error`.

## Danh sách Error

| Error Type | Mô tả |
|---|---|
| `*fc.SSIError` | Error cơ sở — có `Message`, `Code` |
| `*fc.AuthenticationError` | Xác thực thất bại (sai credentials, token hết hạn) |
| `*fc.APIError` | API trả về lỗi — có thêm `StatusCode`, `ResponseBody` |
| `*fc.WebSocketError` | Lỗi kết nối hoặc giao tiếp WebSocket |
| `*fc.ValidationError` | Lỗi validate input |
| `*fc.RateLimitError` | Vượt quá giới hạn request — có thêm `RetryAfter` |

## Import
```python
import fc "github.com/SSI-Securities-Inc/ssi-sdk-go/v3"
```

## Sử dụng cơ bản
```text
token, err := auth.Authenticate("wrong_otp")
if err != nil {
    log.Printf("Error: %v", err)
}
```

## Xử lý lỗi chi tiết
```python
import fc "github.com/SSI-Securities-Inc/ssi-sdk-go/v3"

result, err := t.Trading.PlaceLimitOrder("1234561", "SSI", trading.OrderSideBuy, 100, 68000)
if err != nil {
    switch e := err.(type) {
    case *fc.AuthenticationError:
        log.Println("Cần xác thực lại")
    case *fc.RateLimitError:
        log.Printf("Rate limited, retry sau %.0fs", *e.RetryAfter)
    case *fc.APIError:
        log.Printf("API error %d: %s", e.StatusCode, e.Message)
    case *fc.ValidationError:
        log.Printf("Validation: %s", e.Message)
    case *fc.WebSocketError:
        log.Printf("WebSocket: %s", e.Message)
    default:
        log.Printf("Unknown error: %v", err)
    }
}
```

## Hướng dẫn xử lý

  * Dùng type switch (`switch e := err.(type)`) để xử lý từng loại error.
  * Bắt `*fc.AuthenticationError` khi cần làm mới token hoặc lấy OTP mới.
  * Bắt `*fc.RateLimitError` và tuân thủ `RetryAfter` để backoff.
  * Bắt `*fc.APIError` để xử lý lỗi nghiệp vụ từ server.
  * Bắt `*fc.WebSocketError` khi xử lý kết nối streaming.
  * Bắt `*fc.ValidationError` để kiểm tra input trước khi gọi API.
  * Dùng `*fc.SSIError` làm fallback cho tất cả lỗi SDK.
