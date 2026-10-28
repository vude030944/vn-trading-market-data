<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/csharp/overview
Tieu de goc: Tổng quan
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/csharp/overview>

# Tổng quan

Tổng quan về SSI FastConnect .NET SDK — REST API và WebSocket streaming

.NET SDK cho nền tảng giao dịch chứng khoán SSI. Hỗ trợ REST API và WebSocket streaming, dùng `async`/`await` xuyên suốt.

**Yêu cầu:** .NET 8.0+

**Mã nguồn:** [github.com/SSI-Securities-Inc/ssi-sdk-dotnet](https://github.com/SSI-Securities-Inc/ssi-sdk-dotnet)

**Package:** [`SSIDeveloper.FastConnect.Sdk`](https://www.nuget.org/packages/SSIDeveloper.FastConnect.Sdk) (NuGet)

## Cài đặt
```bash
dotnet add package SSIDeveloper.FastConnect.Sdk
```

## Kiến trúc Client

SDK sử dụng kiến trúc **modular** với 4 client chuyên biệt:

| Client | Mô tả | Yêu cầu |
|---|---|---|
| `AuthClient` | Xác thực & quản lý token | `Config` |
| `DataClient` | Dữ liệu thị trường (OHLC, chỉ số, chứng khoán) | `AuthClient` (không cần OTP) |
| `TradingClient` | Giao dịch + danh mục + tài khoản | `AuthClient` (cần OTP) |
| `StreamClient` | Streaming realtime qua WebSocket | `AuthClient` (cần OTP) |

**Luồng khởi tạo:**
```text
Config → AuthClient → AuthenticateAsync(otp) → DataClient / TradingClient / StreamClient
```

`AuthClient` là client gốc — quản lý REST client và token, implement `IDisposable`. `DataClient`, `TradingClient`, và `StreamClient` đều nhận `AuthClient` làm tham số và dùng chung HTTP connection. Tất cả method API đều là `async` và trả về `Task`/`Task<T>`.

**Service của mỗi client:**

| Client | Service | Truy cập | Mô tả |
|---|---|---|---|
| `AuthClient` | `TokenManager` | `auth.TokenManager` | Xác thực, OTP, làm mới token |
| `DataClient` | `MarketDataService` | `data.MarketData` | OHLC, chỉ số, chứng khoán |
| `TradingClient` | `TradingService` | `trading.Trading` | Đặt/sửa/huỷ lệnh, sức mua/bán, lệnh điều kiện (FCO) |
| `TradingClient` | `AccountService` | `trading.Account` | Thông tin tài khoản |
| `TradingClient` | `PortfolioService` | `trading.Portfolio` | Số dư, vị thế, sổ lệnh, PPMMR |
| `StreamClient` | `StreamingService` | `stream.Streaming` | Subscribe/unsubscribe dữ liệu realtime |

## Bắt đầu nhanh

### Chỉ lấy dữ liệu thị trường (không cần OTP)
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

### Giao dịch (cần OTP)
```text
using SsiSdk;

var config = new Config("YOUR_CLIENT_ID")
{
    ApiKey = "YOUR_API_KEY",
    ApiSecret = "YOUR_API_SECRET",
    PrivateKey = "YOUR_PRIVATE_KEY",
};

using var auth = new AuthClient(config);
await auth.AuthenticateAsync("222222");

var trading = new TradingClient(auth);

var accounts = await trading.Account.GetAccountInfoAsync();
Console.WriteLine(accounts);

var result = await trading.Trading.PlaceLimitOrderAsync("1234561", "SSI", OrderSide.Buy, 100, 66000);
Console.WriteLine($"Order ID: {result.OrderId}, Status: {result.Status}");
```

### Streaming realtime (cần OTP)
```text
using SsiSdk;
using SsiSdk.Models;

var config = new Config("YOUR_CLIENT_ID")
{
    ApiKey = "YOUR_API_KEY",
    ApiSecret = "YOUR_API_SECRET",
    PrivateKey = "YOUR_PRIVATE_KEY",
};

using var auth = new AuthClient(config);
await auth.AuthenticateAsync("222222");

using var stream = new StreamClient(auth);

stream.Streaming.SetOnData(msg =>
{
    if (msg is TradeMessage trade)
        Console.WriteLine($"[TRADE] {trade.Symbol} | {trade.Price} | {trade.Quantity}");
});

await stream.ConnectAsync();
await stream.Streaming.SubscribeSymbolTradeAsync(["SSI"]);
await stream.WaitAsync();
```

## Trường hợp sử dụng

| Trường hợp | Client | Xác thực |
|---|---|---|
| Dữ liệu thị trường (OHLC, chỉ số, chứng khoán) | `DataClient` | Không cần OTP |
| Đặt/sửa/huỷ lệnh, tài khoản, danh mục | `TradingClient` | Cần OTP |
| Streaming WebSocket realtime | `StreamClient` | Cần OTP |

## Điều hướng tài liệu

  * **Cài đặt & Cấu hình**: môi trường, package NuGet, `Config`.
  * **Client Classes** : `AuthClient`, `DataClient`, `TradingClient`, `StreamClient` — khởi tạo và sử dụng.
  * **API Services** : chi tiết các method API.
  * **Cấu hình** : tham chiếu đầy đủ `Config`.
  * **Xử lý lỗi** : các loại exception và cách xử lý.
  * **Enums** : hằng số như `OrderSide`, `OrderType`, `Board`, ...
  * **Models** : các model dữ liệu và message streaming.
