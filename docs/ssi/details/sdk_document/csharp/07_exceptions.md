<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/csharp/exceptions
Tieu de goc: Xử lý lỗi
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/csharp/exceptions>

# Xử lý lỗi

Hệ thống exception và cách xử lý lỗi trong .NET SDK

SDK sử dụng hệ thống exception phân cấp, tất cả kế thừa từ `System.Exception`:

## Danh sách exception

| Exception | Mô tả |
|---|---|
| `SsiException` | Exception cơ sở — có `Code`, `StatusCode`, `ResponseBody` |
| `AuthenticationException` | Xác thực thất bại (sai credentials, token hết hạn) |
| `ApiException` | API trả về lỗi — có `Code`, `StatusCode`, `ResponseBody` |
| `WebSocketException` | Lỗi kết nối hoặc giao tiếp WebSocket |
| `ValidationException` | Lỗi validate input |
| `RateLimitException` | Vượt quá giới hạn request — có thêm `RetryAfter` (mã lỗi cố định `"RATE_LIMITED"`) |

## Chuỗi kế thừa
```text
Exception → SsiException → AuthenticationException
Exception → SsiException → ApiException
Exception → SsiException → WebSocketException
Exception → SsiException → ValidationException
Exception → SsiException → RateLimitException
```

## Thuộc tính exception cơ sở
```text
public class SsiException : Exception
{
    public string Code { get; }
    public int StatusCode { get; }
    public Dictionary<string, JsonElement>? ResponseBody { get; }
}
```

`RateLimitException` bổ sung thêm:
```text
public double? RetryAfter { get; }
```

## Sử dụng cơ bản
```text
using SsiSdk;

try
{
    await auth.AuthenticateAsync("wrong_otp");
}
catch (SsiException ex)
{
    Console.WriteLine($"Lỗi: {ex.Message} (code: {ex.Code})");
}
```

## Xử lý chi tiết theo loại lỗi
```text
using SsiSdk;

try
{
    var result = await trading.Trading.PlaceLimitOrderAsync(
        "1234561", "SSI", OrderSide.Buy, 100, 68000);
}
catch (AuthenticationException)
{
    Console.WriteLine("Cần xác thực lại");
}
catch (RateLimitException ex)
{
    Console.WriteLine($"Rate limited, retry sau {ex.RetryAfter}s");
}
catch (ApiException ex)
{
    Console.WriteLine($"API error {ex.StatusCode}: {ex.Message}");
}
catch (ValidationException ex)
{
    Console.WriteLine($"Validation: {ex.Message}");
}
catch (WebSocketException ex)
{
    Console.WriteLine($"WebSocket: {ex.Message}");
}
catch (SsiException ex)
{
    Console.WriteLine($"SDK error: {ex.Message}");
}
```

## Gợi ý xử lý

  * Bắt exception cụ thể trước, `SsiException` sau cùng làm fallback (theo thứ tự `catch` từ đặc thù đến tổng quát).
  * Bắt `AuthenticationException` khi cần refresh token hoặc yêu cầu OTP mới.
  * Bắt `RateLimitException` và tôn trọng `RetryAfter` để backoff.
  * Bắt `ApiException` để xử lý lỗi nghiệp vụ từ server (`StatusCode`, `ResponseBody`).
  * Bắt `WebSocketException` khi xử lý streaming.
  * Bắt `ValidationException` khi input không hợp lệ trước khi gọi API (SDK tự validate qua lớp `Validate` nội bộ).
