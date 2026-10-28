<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/overview
Tieu de goc: Giới thiệu SSI SDK
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/overview>

# Giới thiệu SSI SDK

Tích hợp FastConnect nhanh hơn bằng bộ SDK chính thức.

## Khi nào nên dùng SDK?

SDK giúp đội ngũ triển khai **FastConnect** nhanh hơn khi cần chuẩn hoá xác thực, gọi API, WebSocket streaming, và quản lý retry theo cùng một mẫu tích hợp. Thay vì tự xử lý token management, ký request, rate limiting, và error recovery, SDK lo các phần này để bạn tập trung vào logic nghiệp vụ.

## Kiến trúc Client

Tất cả SDK dùng chung kiến trúc **modular client** :
```text
Config → Auth → authenticate(otp) → Data / Trading / Stream
```

| Client | Mô tả | Cần OTP |
|---|---|---|
| **Auth** | Xác thực & quản lý token. Entry point cho tất cả client khác. | - |
| **Data** | Dữ liệu thị trường — OHLC, chỉ số, thông tin & tổng hợp chứng khoán. | Không |
| **Trading** | Đặt/sửa/huỷ lệnh, thông tin tài khoản, danh mục, PPMMR. | Có |
| **Stream** | Streaming WebSocket realtime — dữ liệu thị trường & sự kiện giao dịch. | Có |

## Bộ SDK hiện có

| SDK | Runtime | Cài đặt | Mã nguồn |
|---|---|---|---|
| **[Python SDK](./python)** | Python 3.10+ | `pip install ssi-sdk` | [GitHub](https://github.com/SSI-Securities-Inc/ssi-sdk-python) |
| **[Go SDK](./go)** | Go 1.22+ | `go get github.com/SSI-Securities-Inc/ssi-sdk-go/v3` | [GitHub](https://github.com/SSI-Securities-Inc/ssi-sdk-go) |
| **[Node.js SDK](./nodejs)** | Node.js 18+ | `npm install @ssi.developer/ssi-sdk` | [GitHub](https://github.com/SSI-Securities-Inc/ssi-sdk-node) |
| **[.NET SDK](./csharp)** | .NET 8.0+ | `dotnet add package SSIDeveloper.FastConnect.Sdk` | [GitHub](https://github.com/SSI-Securities-Inc/ssi-sdk-dotnet) |

### Python

Hỗ trợ cả **sync** và **async** (`Auth`/`AsyncAuth`, `Data`/`AsyncData`, v.v.). Phù hợp cho data pipeline, automation, và Jupyter notebook.
```python
from ssi_sdk import Auth, Data, Config

config = Config(
    client_id="YOUR_CLIENT_ID",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
)

with Auth(config) as auth:
    auth.authenticate()

    with Data(auth) as data:
        ohlc = data.market_data.get_ohlc_1minute("SSI")
        print(ohlc)
```

### Go

Dùng goroutines cho concurrency — không cần biến thể async riêng. Phù hợp cho dịch vụ hiệu năng cao và realtime.
```python
import "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/ssi"

config := ssi.NewConfig("YOUR_CLIENT_ID")
config.APIKey    = "YOUR_API_KEY"
config.APISecret = "YOUR_API_SECRET"

auth := ssi.NewAuth(config)
defer auth.Close()

if _, err := auth.Authenticate(""); err != nil {
    log.Fatal(err)
}

data := ssi.NewData(auth)
ohlc, err := data.MarketData.GetOHLC1Minute("SSI")
```

### Node.js

Hỗ trợ cả CommonJS và ES Module (dual CJS/ESM). Tất cả method là `async`/`await`. Phù hợp cho web backend, microservice, và serverless.
```python
import { Auth, Data, Config } from '@ssi.developer/ssi-sdk';

const config = new Config({
  clientId: 'YOUR_CLIENT_ID',
  apiKey: 'YOUR_API_KEY',
  apiSecret: 'YOUR_API_SECRET',
});

const auth = new Auth(config);
await auth.authenticate();

const data = new Data(auth);
const ohlc = await data.marketData.getOhlc1Minute('SSI');
console.log(ohlc);
```

### .NET

Dùng `async`/`await` xuyên suốt trên nền .NET 8. Enum nghiệp vụ (`OrderSide`, `Board`, ...) là static class chứa hằng số `string`. Phù hợp cho hệ thống backend .NET, dịch vụ nội bộ doanh nghiệp.
```text
using SsiSdk;

var config = new Config("YOUR_CLIENT_ID")
{
    ApiKey = "YOUR_API_KEY",
    ApiSecret = "YOUR_API_SECRET",
};

using var auth = new AuthClient(config);
await auth.AuthenticateAsync();

var data = new DataClient(auth);
var ohlc = await data.MarketData.GetOhlc1MinuteAsync("SSI");
Console.WriteLine(ohlc);
```

## So sánh tính năng

| Tính năng | Python | Go | Node.js | .NET |
|---|---|---|---|---|
| REST API | Có | Có | Có | Có |
| WebSocket Streaming | Có | Có | Có | Có |
| Async support | `async`/`await` | goroutines | `async`/`await` | `async`/`await` |
| Dọn dẹp tài nguyên | `with` / `async with` | `defer` | manual `disconnect()` | `using`/`IDisposable` |
| Xử lý lỗi | Exception hierarchy | Type switch trên `error` | `instanceof` trên Error class | Exception hierarchy |
| Rate limiting | Tích hợp sẵn | Tích hợp sẵn | Tích hợp sẵn | Tích hợp sẵn |
| Auto retry | Tích hợp sẵn | Tích hợp sẵn | Tích hợp sẵn | Tích hợp sẵn |
| Token auto-refresh | Tích hợp sẵn | Tích hợp sẵn | Tích hợp sẵn | Tích hợp sẵn |

## Quy trình tích hợp khuyến nghị

  1. **Cài đặt** SDK phù hợp với ngôn ngữ hệ thống.
  2. **Cấu hình** credentials (`client_id`, `api_key`, `api_secret`, `private_key`).
  3. **Xác thực** — OTP không bắt buộc cho dữ liệu thị trường, bắt buộc cho giao dịch & streaming.
  4. **Khởi tạo** client cần dùng (`Data`, `Trading`, hoặc `Stream`).
  5. **Gọi API** hoặc **subscribe** các luồng dữ liệu realtime.

## Trường hợp sử dụng

| Trường hợp | Client | OTP |
|---|---|---|
| Dữ liệu thị trường (OHLC, chỉ số, chứng khoán) | `Data` | Không |
| Đặt/sửa/huỷ lệnh | `Trading` | Có |
| Thông tin tài khoản & danh mục | `Trading` | Có |
| Streaming WebSocket realtime | `Stream` | Có |
