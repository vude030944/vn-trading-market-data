<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/go/client-classes
Tieu de goc: Client Classes
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/go/client-classes>

# Client Classes

Auth, Data, Trading, Stream — khởi tạo và sử dụng

SDK cung cấp 4 client chuyên biệt. Go sử dụng goroutines cho concurrency — không cần biến thể async riêng.

## Auth

Client gốc — quản lý REST client, xác thực, và token. Tất cả client khác nhận `*Auth` làm tham số.
```python
import "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/ssi"

config := ssi.NewConfig("YOUR_CLIENT_ID")
config.APIKey     = "YOUR_API_KEY"
config.APISecret  = "YOUR_API_SECRET"
config.PrivateKey = "YOUR_PRIVATE_KEY"

auth := ssi.NewAuth(config)
defer auth.Close()

token, err := auth.Authenticate("222222")
if err != nil {
    log.Fatal(err)
}
log.Printf("Access token: %s", token.AccessToken)
```

### Các method xác thực
```text
// Yêu cầu gửi OTP
result, err := auth.RequestOTP()

// Xác thực với OTP
token, err := auth.Authenticate("222222")

// Xác thực không cần OTP (chỉ dữ liệu thị trường)
token, err := auth.Authenticate("")

// Làm mới token
token, err := auth.Refresh()
```

### Approve OTP (Smart OTP push-approval)

Tài khoản đã kích hoạt Smart OTP có thể duyệt trực tiếp trên app thay vì nhập mã. Gọi `RequestOTP()` để gửi yêu cầu, lấy `transactionId`, rồi truyền vào `EnsureAuthenticated()` — SDK tự poll cho đến khi user bấm duyệt.
```text
// Bước 1: gửi yêu cầu duyệt, nhận transactionId
result, err := auth.RequestOTP()
transactionID := result["transactionId"].(string)

// Bước 2: SDK tự poll cho đến khi user bấm duyệt trên app Smart OTP
// (otp truyền "" vì đang dùng transactionID)
accessToken, err := auth.EnsureAuthenticated("", transactionID)
```

Trong lúc chờ, server trả HTTP 202 + code `401114` ("Push-approval is pending") — SDK tự xử lý. Nếu hết số lần poll mà vẫn chưa duyệt, `EnsureAuthenticated` trả về lỗi xác thực.

### Trạng thái token
```text
auth.TokenManager.IsTokenExpired()  // true/false
auth.AccessToken()                  // chuỗi access token
```

## Data

Client dữ liệu thị trường. **Không cần OTP** — chỉ cần `auth.Authenticate("")`.
```python
import "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/ssi"

auth := ssi.NewAuth(config)
defer auth.Close()

if _, err := auth.Authenticate(""); err != nil {
    log.Fatal(err)
}

data := ssi.NewData(auth)

ohlc, err := data.MarketData.GetOHLC1Minute("SSI")
indexes, err := data.MarketData.GetIndexes()
info, err := data.MarketData.GetSecuritiesInfo("SSI")
```

**Service:** `data.MarketData` (`MarketDataService`) — OHLC, chỉ số, chứng khoán.

## Trading

Client giao dịch, tài khoản, và danh mục. **Cần OTP**.
```python
import (
    "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/ssi"
    "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/trading"
)

auth := ssi.NewAuth(config)
defer auth.Close()

if _, err := auth.Authenticate("222222"); err != nil {
    log.Fatal(err)
}

t := ssi.NewTrading(auth)

// Tài khoản
accounts, err := t.Account.GetAccountInfo()

// Danh mục
balance, err := t.Portfolio.GetEquityBalance("1234561")
positions, err := t.Portfolio.GetEquityPositions("1234561")
orders, err := t.Portfolio.GetTodayOrders("1234561")

// Giao dịch
result, err := t.Trading.PlaceLimitOrder(
    "1234561", "SSI", trading.OrderSideBuy, 100, 66000,
)
```

**Services:**

  * `t.Account` (`AccountService`) — thông tin tài khoản.
  * `t.Portfolio` (`PortfolioService`) — số dư, vị thế, sổ lệnh, PPMMR.
  * `t.Trading` (`TradingService`) — đặt/sửa/huỷ lệnh, sức mua/bán, lệnh điều kiện (FCO).

## Stream

Client streaming realtime qua WebSocket. **Cần OTP**.
```python
import (
    "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/ssi"
    "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/stream"
)

auth := ssi.NewAuth(config)
defer auth.Close()

if _, err := auth.Authenticate("222222"); err != nil {
    log.Fatal(err)
}

s := ssi.NewStream(auth)
defer s.Disconnect()

// Đăng ký callback
s.Streaming.SetOnData(func(msg interface{}) {
    switch m := msg.(type) {
    case *stream.TradeMessage:
        fmt.Printf("[TRADE] %s | %.0f | %d\n", m.Symbol, m.Price, m.Quantity)
    case *stream.QuoteMessage:
        fmt.Printf("[QUOTE] %s\n", m.Symbol)
    }
})

s.Streaming.SetOnTrading(func(msg interface{}) {
    switch m := msg.(type) {
    case *stream.OrderStatusMessage:
        fmt.Printf("[ORDER] %s %s | %s\n", m.Symbol, m.Side, m.Status)
    case *stream.PortfolioMessage:
        fmt.Printf("[PORTFOLIO] %s\n", m.AccountNo)
    }
})

// Kết nối và subscribe
if err := s.Connect(); err != nil {
    log.Fatal(err)
}

s.Streaming.SubscribeSymbol([]string{"SSI", "HPG"}, nil)
s.Streaming.SubscribeOrderStatus("", nil)

s.Wait(nil)
```

**Service:** `s.Streaming` (`StreamingService`) — subscribe/unsubscribe dữ liệu realtime.

**Callbacks:**

| Method | Callback Signature | Mô tả |
|---|---|---|
| `SetOnData` | `func(interface{})` | Nhận dữ liệu thị trường (dùng type switch để xử lý) |
| `SetOnTrading` | `func(interface{})` | Nhận sự kiện giao dịch (trạng thái lệnh, danh mục) |
| `SetOnHeartbeat` | `func(*stream.HeartbeatMessage)` | Nhận heartbeat |

## Ví dụ đầy đủ
```python
package main

import (
    "fmt"
    "log"
    "time"

    "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/ssi"
    "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/stream"
)

func main() {
    config := ssi.NewConfig("YOUR_CLIENT_ID")
    config.APIKey     = "YOUR_API_KEY"
    config.APISecret  = "YOUR_API_SECRET"
    config.PrivateKey = "YOUR_PRIVATE_KEY"

    auth := ssi.NewAuth(config)
    defer auth.Close()

    if _, err := auth.Authenticate("222222"); err != nil {
        log.Fatal(err)
    }

    // Dữ liệu thị trường
    data := ssi.NewData(auth)
    ohlc, err := data.MarketData.GetOHLC1Minute("SSI")
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println(ohlc)

    // Giao dịch
    t := ssi.NewTrading(auth)
    accounts, err := t.Account.GetAccountInfo()
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println(accounts)

    // Streaming
    s := ssi.NewStream(auth)
    defer s.Disconnect()

    s.Streaming.SetOnData(func(msg interface{}) {
        switch m := msg.(type) {
        case *stream.TradeMessage:
            fmt.Printf("[TRADE] %s | %.0f | %d\n", m.Symbol, m.Price, m.Quantity)
        }
    })

    s.Streaming.SetOnTrading(func(msg interface{}) {
        fmt.Printf("[TRADING] %v\n", msg)
    })

    if err := s.Connect(); err != nil {
        log.Fatal(err)
    }

    s.Streaming.SubscribeSymbol([]string{"SSI", "HPG"}, nil)
    s.Streaming.SubscribeOrderStatus("", nil)

    timeout := 30 * time.Second
    s.Wait(&timeout)
}
```

## Ghi chú

  * Go SDK không có biến thể async riêng — dùng goroutines cho concurrency.
  * Tất cả client dùng chung HTTP connection qua `Auth`.
  * Luôn dùng `defer auth.Close()` và `defer s.Disconnect()` để dọn dẹp.
  * Lỗi thường gặp: `*fc.AuthenticationError` (xác thực), `*fc.WebSocketError` (stream), `*fc.APIError` (lỗi HTTP).
