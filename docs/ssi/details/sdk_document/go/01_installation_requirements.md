<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/go/installation-requirements
Tieu de goc: Cài đặt & Thiết lập
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/go/installation-requirements>

# Cài đặt & Thiết lập

Hướng dẫn cài đặt và thiết lập Go SDK

## Yêu cầu môi trường

  * Go `>=1.22`
  * Truy cập mạng tới REST API và WebSocket endpoints
  * `ClientID`, `APIKey`, `APISecret` từ SSI
  * `PrivateKey` để ký lệnh giao dịch
  * OTP cho luồng xác thực Trading/Stream

## Cài đặt
```bash
go get github.com/SSI-Securities-Inc/ssi-sdk-go/v3
```

## Cấu hình

Tạo đối tượng `Config` với thông tin xác thực:
```python
import "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/ssi"

config := ssi.NewConfig("YOUR_CLIENT_ID")
config.APIKey     = "YOUR_API_KEY"
config.APISecret  = "YOUR_API_SECRET"
config.PrivateKey = "YOUR_PRIVATE_KEY"
```

## Luồng khởi tạo
```text
Config → Auth → Authenticate(otp) → Data / Trading / Stream
```

  1. Tạo `Config` với `ssi.NewConfig(clientID)`.
  2. Khởi tạo `Auth` với `ssi.NewAuth(config)`.
  3. Gọi `auth.Authenticate(otp)` — truyền chuỗi rỗng `""` nếu chỉ dùng dữ liệu thị trường.
  4. Khởi tạo client cần dùng (`Data`, `Trading`, `Stream`) với `auth`.
  5. Với `Stream`, gọi `s.Connect()` trước khi subscribe.
  6. Dùng `defer auth.Close()` và `defer s.Disconnect()` để dọn dẹp tài nguyên.

## Ví dụ theo trường hợp sử dụng

### Chỉ lấy dữ liệu thị trường (không cần OTP)
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

### Giao dịch (cần OTP)
```python
import (
    "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/ssi"
    "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/trading"
)

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
```

### Streaming realtime (cần OTP)
```python
import (
    "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/ssi"
    "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/stream"
)

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
    fmt.Println(msg)
})

if err := s.Connect(); err != nil {
    log.Fatal(err)
}

s.Streaming.SubscribeSymbolTrade([]string{"SSI"}, nil)
s.Wait(nil)
```

## Mẹo

  * Xác thực trước khi gọi API có bảo vệ bằng token.
  * Với streaming, gọi `s.Connect()` sau khi xác thực thành công.
  * Dùng `config.LogLevel = "DEBUG"` để gỡ lỗi.
  * Lưu credentials (`APIKey`, `APISecret`, `PrivateKey`) trong biến môi trường hoặc secret manager.
  * Luôn dùng `defer auth.Close()` và `defer s.Disconnect()` để dọn dẹp đúng cách.
