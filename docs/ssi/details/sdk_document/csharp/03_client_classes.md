<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/csharp/client-classes
Tieu de goc: Client Classes
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/csharp/client-classes>

# Client Classes

AuthClient, DataClient, TradingClient, StreamClient — khởi tạo và sử dụng

SDK cung cấp 4 client chuyên biệt. Tất cả method API đều là `async` và trả về `Task`/`Task<T>`.

## AuthClient

Client gốc — quản lý REST client, xác thực, và token. Implement `IDisposable`. Tất cả client khác nhận `AuthClient` làm tham số.
```text
using SsiSdk;

var config = new Config("YOUR_CLIENT_ID")
{
    ApiKey = "YOUR_API_KEY",
    ApiSecret = "YOUR_API_SECRET",
    PrivateKey = "YOUR_PRIVATE_KEY",
};

using var auth = new AuthClient(config);

var token = await auth.AuthenticateAsync("222222");
Console.WriteLine($"Access token: {token.AccessToken}");
```

### Các method xác thực
```text
// Yêu cầu gửi OTP
await auth.RequestOtpAsync();

// Xác thực với OTP
var token = await auth.AuthenticateAsync("222222");

// Xác thực không cần OTP (chỉ dữ liệu thị trường)
var token = await auth.AuthenticateAsync();

// Làm mới token
var token = await auth.RefreshAsync();

// Đảm bảo xác thực (tự refresh nếu hết hạn)
var accessToken = await auth.EnsureAuthenticatedAsync("222222");
```

### Approve OTP (Smart OTP push-approval)

Tài khoản đã kích hoạt Smart OTP có thể duyệt trực tiếp trên app thay vì nhập mã. Gọi `RequestOtpAsync()` để gửi yêu cầu, lấy `transactionId`, rồi truyền vào `EnsureAuthenticatedAsync()` — SDK tự poll cho đến khi user bấm duyệt.
```text
// Bước 1: gửi yêu cầu duyệt, nhận transactionId
var otpResult = await auth.RequestOtpAsync();
var transactionId = otpResult.GetProperty("transactionId").GetString();

// Bước 2: SDK tự poll cho đến khi user bấm duyệt trên app Smart OTP
var accessToken = await auth.EnsureAuthenticatedAsync(transactionId: transactionId);
```

Trong lúc chờ, server trả HTTP 202 + code `401114` ("Push-approval is pending") — SDK tự xử lý. Nếu hết số lần poll mà vẫn chưa duyệt, `EnsureAuthenticatedAsync` throw `AuthenticationException`.

### Trạng thái token
```text
auth.AccessToken;                    // access token hiện tại (string)
auth.TokenManager.Token;             // đối tượng Token đầy đủ
auth.TokenManager.IsTokenExpired;    // true/false
auth.TokenManager.SetToken(token);   // thiết lập token (cache)
```

## DataClient

Client dữ liệu thị trường. **Không cần OTP** — chỉ cần `auth.AuthenticateAsync()`.
```text
using SsiSdk;

using var auth = new AuthClient(config);
await auth.AuthenticateAsync();

var data = new DataClient(auth);

var ohlc = await data.MarketData.GetOhlc1MinuteAsync("SSI");
var indexes = await data.MarketData.GetIndexesAsync();
var info = await data.MarketData.GetSecuritiesInfoAsync("SSI");
```

**Service:** `data.MarketData` (`MarketDataService`) — OHLC, chỉ số, chứng khoán.

## TradingClient

Client giao dịch, tài khoản, và danh mục. **Cần OTP**.
```text
using SsiSdk;

using var auth = new AuthClient(config);
await auth.AuthenticateAsync("222222");

var trading = new TradingClient(auth);

// Tài khoản
var accounts = await trading.Account.GetAccountInfoAsync();

// Danh mục
var balance = await trading.Portfolio.GetEquityBalanceAsync("1234561");
var positions = await trading.Portfolio.GetEquityPositionsAsync("1234561");
var orders = await trading.Portfolio.GetTodayOrdersAsync("1234561");

// Giao dịch
var result = await trading.Trading.PlaceLimitOrderAsync(
    "1234561", "SSI", OrderSide.Buy, 100, 66000);
```

**Services:**

  * `trading.Account` (`AccountService`) — thông tin tài khoản.
  * `trading.Portfolio` (`PortfolioService`) — số dư, vị thế, sổ lệnh, PPMMR.
  * `trading.Trading` (`TradingService`) — đặt/sửa/huỷ lệnh, sức mua/bán, lệnh điều kiện (FCO).

## StreamClient

Client streaming realtime qua WebSocket. Implement `IDisposable`. **Cần OTP**.
```text
using SsiSdk;
using SsiSdk.Models;

using var auth = new AuthClient(config);
await auth.AuthenticateAsync("222222");

using var stream = new StreamClient(auth);

// Đăng ký callback
stream.Streaming.SetOnData(msg =>
{
    switch (msg)
    {
        case TradeMessage trade:
            Console.WriteLine($"[TRADE] {trade.Symbol} | {trade.Price} | {trade.Quantity}");
            break;
        case QuoteMessage quote:
            Console.WriteLine($"[QUOTE] {quote.Symbol}");
            break;
    }
});

stream.Streaming.SetOnTrading(msg =>
{
    if (msg is OrderStatusMessage order)
        Console.WriteLine($"[ORDER] {order.Symbol} {order.Side} | {order.Status}");
});

// Kết nối và subscribe
await stream.ConnectAsync();

await stream.Streaming.SubscribeSymbolAsync(["SSI", "HPG"]);
await stream.Streaming.SubscribeOrderStatusAsync();

await stream.WaitAsync();
```

**Service:** `stream.Streaming` (`StreamingService`) — subscribe/unsubscribe dữ liệu realtime.

**Callbacks:**

| Method | Callback | Mô tả |
|---|---|---|
| `SetOnData` | `Action<object>?` | Nhận dữ liệu thị trường (dùng pattern matching để xử lý) |
| `SetOnTrading` | `Action<object>?` | Nhận sự kiện giao dịch (trạng thái lệnh, danh mục) |
| `SetOnHeartbeat` | `Action<HeartbeatMessage>?` | Nhận heartbeat |

**Trạng thái kết nối & dọn dẹp:**
```text
stream.IsConnected;         // true/false
stream.Streaming.StopPingLoop();
stream.Disconnect();        // gọi khi không dùng using
```

## Ví dụ đầy đủ
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

// Dữ liệu thị trường
var data = new DataClient(auth);
var ohlc = await data.MarketData.GetOhlc1MinuteAsync("SSI");
Console.WriteLine(ohlc);

// Giao dịch
var trading = new TradingClient(auth);
var accounts = await trading.Account.GetAccountInfoAsync();
Console.WriteLine(accounts);

// Streaming
using var stream = new StreamClient(auth);

stream.Streaming.SetOnData(msg =>
{
    if (msg is TradeMessage trade)
        Console.WriteLine($"[TRADE] {trade.Symbol} | {trade.Price} | {trade.Quantity}");
});

await stream.ConnectAsync();
await stream.Streaming.SubscribeSymbolAsync(["SSI", "HPG"]);
await stream.Streaming.SubscribeOrderStatusAsync();

await stream.WaitAsync(TimeSpan.FromSeconds(30));
```

## Ghi chú

  * Tất cả method API đều là `async` — dùng `await`.
  * `AuthClient` và `StreamClient` implement `IDisposable` — luôn dùng `using`/`using var`.
  * Tất cả client dùng chung HTTP connection qua `AuthClient`.
  * Lỗi thường gặp: `AuthenticationException` (xác thực), `WebSocketException` (stream), `ApiException` (lỗi HTTP).
