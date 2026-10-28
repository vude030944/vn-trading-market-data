<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/csharp/installation-requirements
Tieu de goc: Cài đặt và cấu hình
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/csharp/installation-requirements>

# Cài đặt và cấu hình

Hướng dẫn cài đặt và cấu hình .NET SDK

## Yêu cầu môi trường

  * .NET `>=8.0`
  * Kết nối mạng đến REST API và WebSocket endpoint
  * `ClientId`, `ApiKey`, `ApiSecret` từ SSI
  * `PrivateKey` cho ký lệnh giao dịch
  * OTP khi xác thực cho các luồng Trading/Stream

## Cài đặt
```bash
dotnet add package SSIDeveloper.FastConnect.Sdk
```

Hoặc thêm trực tiếp vào file `.csproj`:
```text
<ItemGroup>
  <PackageReference Include="SSIDeveloper.FastConnect.Sdk" Version="3.0.5" />
</ItemGroup>
```

## Cấu hình

Tạo đối tượng `Config` với thông tin xác thực:
```text
using SsiSdk;

var config = new Config("YOUR_CLIENT_ID")
{
    ApiKey = "YOUR_API_KEY",
    ApiSecret = "YOUR_API_SECRET",
    PrivateKey = "YOUR_PRIVATE_KEY",
};
```

## Luồng khởi tạo
```text
Config → AuthClient → AuthenticateAsync(otp) → DataClient / TradingClient / StreamClient
```

  1. Tạo `Config` với `new Config(clientId)`.
  2. Khởi tạo `AuthClient` với `new AuthClient(config)`.
  3. Gọi `await auth.AuthenticateAsync(otp)` — bỏ trống `otp` nếu chỉ dùng dữ liệu thị trường.
  4. Khởi tạo client cần dùng (`DataClient`, `TradingClient`, `StreamClient`) với `auth`.
  5. Với `StreamClient`, gọi `await stream.ConnectAsync()` trước khi subscribe.
  6. Dùng `using`/`using var` cho `AuthClient` và `StreamClient` (đều implement `IDisposable`) để dọn dẹp tài nguyên.

## Ví dụ khởi tạo theo trường hợp sử dụng

### Chỉ dữ liệu thị trường (không cần OTP)
```text
using SsiSdk;

var config = new Config("YOUR_CLIENT_ID")
{
    ApiKey = "YOUR_API_KEY",
    ApiSecret = "YOUR_API_SECRET",
};

using var auth = new AuthClient(config);
await auth.AuthenticateAsync(); // Không cần OTP

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
```

### Streaming realtime (cần OTP)
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

using var stream = new StreamClient(auth);
await stream.ConnectAsync();
stream.Streaming.SetOnData(msg => Console.WriteLine(msg));
await stream.Streaming.SubscribeSymbolTradeAsync(["SSI"]);
await stream.WaitAsync();
```

## Gợi ý

  * Xác thực trước khi gọi API cần token.
  * Với streaming, gọi `ConnectAsync()` sau khi xác thực thành công.
  * Đặt `LogLevel = "DEBUG"` trong `Config` khi cần điều tra lỗi.
  * Giữ thông tin khóa (`ApiKey`, `ApiSecret`, `PrivateKey`) trong biến môi trường hoặc secret manager (Azure Key Vault, AWS Secrets Manager, ...), không hardcode.
  * Luôn dùng `using`/`using var` cho `AuthClient` và `StreamClient` để giải phóng `HttpClient`/WebSocket đúng cách.
