<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/nodejs/configuration
Tieu de goc: Cấu hình
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/nodejs/configuration>

# Cấu hình

Tham chiếu đầy đủ tham số Config cho Node.js SDK

## Config

`Config` là đối tượng cấu hình trung tâm của SDK. Tạo instance với thông tin xác thực:
```python
import { Config } from '@ssi.developer/ssi-sdk';

const config = new Config({
  clientId: 'YOUR_CLIENT_ID',
  apiKey: 'YOUR_API_KEY',
  apiSecret: 'YOUR_API_SECRET',
  privateKey: 'YOUR_PRIVATE_KEY',
});
```

## Tất cả tham số cấu hình

| Tham số | Kiểu | Mặc định | Mô tả |
|---|---|---|---|
| `clientId` | `string` | `""` | Client ID cho portfolio operations |
| `apiKey` | `string` | `""` | API key từ SSI |
| `apiSecret` | `string` | `""` | API secret từ SSI |
| `privateKey` | `string` | `""` | Private key RSA để ký lệnh giao dịch (XML format, base64-encoded) |
| `apiUrl` | `string` | `"https://api.ssi.com.vn"` | URL REST API |
| `streamingUrl` | `string` | `"wss://stream.ssi.com.vn/ws/v3"` | URL WebSocket streaming |
| `timeout` | `number` | `60000` | Timeout request (ms) |
| `maxRetries` | `number` | `5` | Số lần retry tối đa |
| `retryDelay` | `number` | `2000` | Delay cơ sở giữa các lần retry (exponential backoff, ms) |
| `rateLimitPerSecond` | `number` | `10` | Giới hạn request/giây (0 = không giới hạn) |
| `proxy` | `string` | `undefined` | Proxy URL (HTTP hoặc SOCKS5) |
| `logLevel` | `string` | `"INFO"` | Mức log: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |

## Cấu hình nâng cao

### Debug logging
```javascript
const config = new Config({
  clientId: 'YOUR_CLIENT_ID',
  apiKey: 'YOUR_API_KEY',
  apiSecret: 'YOUR_API_SECRET',
  logLevel: 'DEBUG',
});
```

### Tuỳ chỉnh retry & rate limit
```javascript
const config = new Config({
  clientId: 'YOUR_CLIENT_ID',
  apiKey: 'YOUR_API_KEY',
  apiSecret: 'YOUR_API_SECRET',
  maxRetries: 3,
  retryDelay: 1000,
  rateLimitPerSecond: 5,
});
```

### Proxy
```javascript
const config = new Config({
  clientId: 'YOUR_CLIENT_ID',
  apiKey: 'YOUR_API_KEY',
  apiSecret: 'YOUR_API_SECRET',
  proxy: 'http://proxy.example.com:8080',
});
```

## Khuyến nghị

  * Lưu credentials (`apiKey`, `apiSecret`, `privateKey`) trong biến môi trường hoặc secret manager.
  * Thiếu `apiKey`/`apiSecret` sẽ gây lỗi xác thực.
  * Thiếu `privateKey` sẽ ảnh hưởng đến thao tác ký lệnh.
  * Đặt `rateLimitPerSecond` theo chính sách nền tảng.
  * Chỉ bật `logLevel: 'DEBUG'` trong môi trường phát triển.
  * Điều chỉnh `timeout`, `maxRetries`, và `retryDelay` theo workload thực tế.
