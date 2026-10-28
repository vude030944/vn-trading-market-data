<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/python/configuration
Tieu de goc: Cấu hình
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/python/configuration>

# Cấu hình

Tham chiếu đầy đủ các tham số Config của Python SDK

## Config

Lớp `Config` là trung tâm cấu hình SDK. Tạo đối tượng `Config` với thông tin xác thực:
```python
from ssi_sdk import Config

config = Config(
    client_id="YOUR_CLIENT_ID",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
    private_key="YOUR_PRIVATE_KEY",
)
```

## Tất cả tham số cấu hình

| Tham số | Kiểu | Mặc định | Mô tả |
|---|---|---|---|
| `client_id` | `str` | `""` | Client ID xác thực |
| `api_key` | `str` | `""` | API key từ SSI |
| `api_secret` | `str` | `""` | API secret từ SSI |
| `private_key` | `str` | `""` | Private key cho ký lệnh giao dịch |
| `api_url` | `str` | `"https://api.ssi.com.vn"` | URL REST API |
| `streaming_url` | `str` | `"wss://stream.ssi.com.vn/ws/v3"` | URL WebSocket streaming |
| `timeout` | `int` | `60` | Timeout request (giây) |
| `max_retries` | `int` | `5` | Số lần retry tối đa |
| `retry_delay` | `float` | `2.0` | Delay cơ sở giữa các lần retry (exponential backoff, giây) |
| `rate_limit_per_second` | `int` | `10` | Giới hạn request/giây (0 = không giới hạn) |
| `proxy` | `str \| None` | `None` | Proxy URL |
| `log_level` | `str` | `"INFO"` | Mức log: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |

## Cấu hình nâng cao

### Debug logging
```text
config = Config(
    client_id="YOUR_CLIENT_ID",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
    log_level="DEBUG",
)
```

### Tuỳ chỉnh retry & rate limit
```text
config = Config(
    client_id="YOUR_CLIENT_ID",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
    max_retries=3,
    retry_delay=1.0,
    rate_limit_per_second=5,
)
```

## Khuyến nghị

  * Giữ thông tin khóa (`api_key`, `api_secret`, `private_key`) trong secret manager.
  * Thiếu `api_key`/`api_secret` sẽ làm luồng xác thực thất bại.
  * Thiếu `private_key` sẽ ảnh hưởng các nghiệp vụ ký lệnh giao dịch.
  * Cấu hình `rate_limit_per_second` phù hợp với chính sách hệ thống.
  * Chỉ bật `log_level="DEBUG"` trong môi trường phát triển.
  * Đặt `timeout`, `max_retries`, `retry_delay` phù hợp với tải thực tế.
