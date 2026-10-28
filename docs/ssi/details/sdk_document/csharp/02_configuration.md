<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/csharp/configuration
Tieu de goc: Cấu hình
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/csharp/configuration>

# Cấu hình

Tham chiếu đầy đủ các tham số Config của .NET SDK

## Config

Lớp `Config` (`sealed class`) là trung tâm cấu hình SDK. Tạo đối tượng `Config` với thông tin xác thực:
```text
using SsiSdk;

var config = new Config("YOUR_CLIENT_ID")
{
    ApiKey = "YOUR_API_KEY",
    ApiSecret = "YOUR_API_SECRET",
    PrivateKey = "YOUR_PRIVATE_KEY",
};
```

`Config` có 2 constructor: `Config()` (rỗng, gán property sau) và `Config(string clientId)` (gán sẵn `ClientId`).

## Tất cả tham số cấu hình

| Tham số | Kiểu | Mặc định | Mô tả |
|---|---|---|---|
| `ClientId` | `string` | `""` | Client ID xác thực |
| `ApiKey` | `string` | `""` | API key từ SSI |
| `ApiSecret` | `string` | `""` | API secret từ SSI |
| `PrivateKey` | `string` | `""` | Private key cho ký lệnh giao dịch |
| `ApiUrl` | `string` | `"https://api.ssi.com.vn"` | URL REST API |
| `StreamingUrl` | `string` | `"wss://stream.ssi.com.vn/ws/v3"` | URL WebSocket streaming |
| `TimeoutSeconds` | `int` | `60` | Timeout request (giây) |
| `MaxRetries` | `int` | `5` | Số lần retry tối đa |
| `RetryDelay` | `double` | `2.0` | Delay cơ sở giữa các lần retry (exponential backoff, giây) |
| `RateLimitPerSecond` | `int` | `10` | Giới hạn request/giây (0 = không giới hạn) |
| `LogLevel` | `string` | `"INFO"` | Mức log: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `Proxy` | `string?` | `null` | Proxy URL |

## Cấu hình nâng cao

### Debug logging
```text
var config = new Config("YOUR_CLIENT_ID")
{
    ApiKey = "YOUR_API_KEY",
    ApiSecret = "YOUR_API_SECRET",
    LogLevel = "DEBUG",
};
```

### Tuỳ chỉnh retry & rate limit
```text
var config = new Config("YOUR_CLIENT_ID")
{
    ApiKey = "YOUR_API_KEY",
    ApiSecret = "YOUR_API_SECRET",
    MaxRetries = 3,
    RetryDelay = 1.0,
    RateLimitPerSecond = 5,
};
```

### Proxy
```text
var config = new Config("YOUR_CLIENT_ID")
{
    ApiKey = "YOUR_API_KEY",
    ApiSecret = "YOUR_API_SECRET",
    Proxy = "http://proxy.example.com:8080",
};
```

## Khuyến nghị

  * Giữ thông tin khóa (`ApiKey`, `ApiSecret`, `PrivateKey`) trong biến môi trường hoặc secret manager (Azure Key Vault, AWS Secrets Manager, ...) — không hardcode hoặc commit vào Git.
  * Thiếu `ApiKey`/`ApiSecret` sẽ làm luồng xác thực thất bại (`AuthenticationException`).
  * Thiếu `PrivateKey` sẽ ảnh hưởng các nghiệp vụ ký lệnh giao dịch.
  * Cấu hình `RateLimitPerSecond` phù hợp với chính sách hệ thống.
  * Chỉ bật `LogLevel = "DEBUG"` trong môi trường phát triển.
  * Đặt `TimeoutSeconds`, `MaxRetries`, `RetryDelay` phù hợp với tải thực tế.
