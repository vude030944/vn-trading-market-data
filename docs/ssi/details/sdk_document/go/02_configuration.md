<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/go/configuration
Tieu de goc: Cấu hình
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/go/configuration>

# Cấu hình

Tham chiếu đầy đủ tham số Config cho Go SDK

## Config

`Config` là đối tượng cấu hình trung tâm của SDK. Tạo instance `Config` với thông tin xác thực:
```python
import "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/ssi"

config := ssi.NewConfig("YOUR_CLIENT_ID")
config.APIKey     = "YOUR_API_KEY"
config.APISecret  = "YOUR_API_SECRET"
config.PrivateKey = "YOUR_PRIVATE_KEY"
```

## Tất cả tham số cấu hình

| Tham số | Kiểu | Mặc định | Mô tả |
|---|---|---|---|
| `ClientID` | `string` | _(bắt buộc)_ | Client ID xác thực |
| `APIKey` | `string` | `""` | API key từ SSI |
| `APISecret` | `string` | `""` | API secret từ SSI |
| `PrivateKey` | `string` | `""` | Private key để ký lệnh giao dịch |
| `APIURL` | `string` | `"https://api.ssi.com.vn"` | URL REST API |
| `StreamingURL` | `string` | `"wss://stream.ssi.com.vn/ws/v3"` | URL WebSocket streaming |
| `Timeout` | `int` | `60` | Timeout request (giây) |
| `MaxRetries` | `int` | `5` | Số lần retry tối đa |
| `RetryDelay` | `float64` | `2.0` | Delay cơ sở giữa các lần retry (exponential backoff, giây) |
| `RateLimitPerSecond` | `int` | `10` | Giới hạn request/giây (0 = không giới hạn) |
| `LogLevel` | `string` | `"INFO"` | Mức log: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `Proxy` | `string` | `""` | Proxy URL |

## Cấu hình nâng cao

### Debug logging
```text
config := ssi.NewConfig("YOUR_CLIENT_ID")
config.APIKey    = "YOUR_API_KEY"
config.APISecret = "YOUR_API_SECRET"
config.LogLevel  = "DEBUG"
```

### Tuỳ chỉnh retry & rate limit
```text
config := ssi.NewConfig("YOUR_CLIENT_ID")
config.APIKey             = "YOUR_API_KEY"
config.APISecret          = "YOUR_API_SECRET"
config.MaxRetries         = 3
config.RetryDelay         = 1.0
config.RateLimitPerSecond = 5
```

### Proxy
```text
config.Proxy = "http://proxy.example.com:8080"
```

## Khuyến nghị

  * Lưu credentials (`APIKey`, `APISecret`, `PrivateKey`) trong biến môi trường hoặc secret manager.
  * Thiếu `APIKey`/`APISecret` sẽ gây lỗi xác thực.
  * Thiếu `PrivateKey` sẽ ảnh hưởng đến thao tác ký lệnh.
  * Đặt `RateLimitPerSecond` theo chính sách nền tảng.
  * Chỉ bật `LogLevel = "DEBUG"` trong môi trường phát triển.
  * Điều chỉnh `Timeout`, `MaxRetries`, và `RetryDelay` theo workload thực tế.
