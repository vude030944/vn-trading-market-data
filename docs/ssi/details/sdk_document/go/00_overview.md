<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/go/overview
Tieu de goc: Tổng quan
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/go/overview>

# Tổng quan

Tổng quan về SSI FastConnect Go SDK — REST API và WebSocket streaming

Go SDK cho nền tảng giao dịch chứng khoán SSI. Hỗ trợ REST API và WebSocket streaming.

**Yêu cầu:** Go 1.22+

**Mã nguồn:** [github.com/SSI-Securities-Inc/ssi-sdk-go](https://github.com/SSI-Securities-Inc/ssi-sdk-go)

## Cài đặt
```bash
go get github.com/SSI-Securities-Inc/ssi-sdk-go/v3
```

## Kiến trúc Client

SDK sử dụng kiến trúc **module** với 4 client chuyên biệt:

| Client | Mô tả | Yêu cầu |
|---|---|---|
| `Auth` | Xác thực & quản lý token | `Config` |
| `Data` | Dữ liệu thị trường (OHLC, chỉ số, chứng khoán) | `Auth` (không cần OTP) |
| `Trading` | Giao dịch + danh mục + tài khoản | `Auth` (cần OTP) |
| `Stream` | Streaming realtime qua WebSocket | `Auth` (cần OTP) |

**Luồng khởi tạo:**
```text
Config → Auth → Authenticate(otp) → Data / Trading / Stream
```

`Auth` là client gốc — quản lý REST client và token. `Data`, `Trading`, và `Stream` đều nhận `*Auth` làm tham số và dùng chung HTTP connection.

**Service của mỗi client:**

| Client | Service | Truy cập | Mô tả |
|---|---|---|---|
| `Auth` | `TokenManager` | `auth.TokenManager` | Xác thực, OTP, làm mới token |
| `Data` | `MarketDataService` | `data.MarketData` | OHLC, chỉ số, chứng khoán |
| `Trading` | `TradingService` | `t.Trading` | Đặt/sửa/huỷ lệnh, sức mua/bán, lệnh điều kiện (FCO) |
| `Trading` | `AccountService` | `t.Account` | Thông tin tài khoản |
| `Trading` | `PortfolioService` | `t.Portfolio` | Số dư, vị thế, sổ lệnh, PPMMR |
| `Stream` | `StreamingService` | `s.Streaming` | Subscribe/unsubscribe dữ liệu realtime |

## Bắt đầu nhanh

### Chỉ lấy dữ liệu thị trường (không cần OTP)
```python
package main

import (
    "fmt"
    "log"

    "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/ssi"
)

func main() {
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
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println(ohlc)
}
```

### Giao dịch (cần OTP)
```python
package main

import (
    "fmt"
    "log"

    "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/ssi"
    "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/trading"
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

    t := ssi.NewTrading(auth)

    accounts, err := t.Account.GetAccountInfo()
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println(accounts)

    result, err := t.Trading.PlaceLimitOrder("1234561", "SSI", trading.OrderSideBuy, 100, 66000)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println(result)
}
```

### Streaming realtime (cần OTP)
```python
package main

import (
    "fmt"
    "log"

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

    s := ssi.NewStream(auth)
    defer s.Disconnect()

    s.Streaming.SetOnData(func(msg interface{}) {
        switch m := msg.(type) {
        case *stream.TradeMessage:
            fmt.Printf("[TRADE] %s | %.0f | %d\n", m.Symbol, m.Price, m.Quantity)
        }
    })

    if err := s.Connect(); err != nil {
        log.Fatal(err)
    }

    s.Streaming.SubscribeSymbolTrade([]string{"SSI"}, nil)
    s.Wait(nil)
}
```

## Trường hợp sử dụng

| Trường hợp | Client | Xác thực |
|---|---|---|
| Dữ liệu thị trường (OHLC, chỉ số, chứng khoán) | `Data` | Không cần OTP |
| Đặt/sửa/huỷ lệnh, tài khoản, danh mục | `Trading` | Cần OTP |
| Streaming WebSocket realtime | `Stream` | Cần OTP |

## Điều hướng tài liệu

  * **Cài đặt & Cấu hình**: môi trường, packages, `Config`.
  * **Client Classes** : `Auth`, `Data`, `Trading`, `Stream` — khởi tạo và sử dụng.
  * **API Services** : chi tiết các method API.
  * **Cấu hình** : tham chiếu đầy đủ `Config`.
  * **Xử lý lỗi** : các loại error và cách xử lý.
  * **Enums** : hằng số như `OrderSide`, `OrderType`, `Board`, ...
  * **Models** : các model dữ liệu và message streaming.
