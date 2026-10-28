<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/go/service-classes
Tieu de goc: API Services
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/go/service-classes>

# API Services

Chi tiết các method API cho mỗi service trong Go SDK

## 1\. Xác thực (TokenManager)

Truy cập qua `auth.TokenManager` hoặc trực tiếp trên `auth` (được uỷ quyền).

### Xác thực với OTP
```text
token, err := auth.Authenticate("222222")
if err != nil {
    log.Fatal(err)
}
log.Printf("Access token: %s", token.AccessToken)
```

### Yêu cầu gửi OTP
```text
result, err := auth.RequestOTP()
```

### Làm mới token
```text
token, err := auth.Refresh()
```

### Kiểm tra trạng thái token
```text
if auth.TokenManager.IsTokenExpired() {
    auth.Refresh()
}

accessToken := auth.AccessToken()
```

* * *

## 2\. Tài khoản (AccountService)

Truy cập qua `t.Account`.

### Lấy danh sách tài khoản
```text
accounts, err := t.Account.GetAccountInfo()

for _, acc := range accounts {
    fmt.Printf("%s (%s)\n", acc.AccountNo, acc.AccountType)
}
```

**Trả về:** `[]Account` — mỗi `Account` có `AccountNo string`, `AccountType string`.

* * *

## 3\. Dữ liệu thị trường (MarketDataService)

Truy cập qua `data.MarketData`. Không cần OTP.

### 3.1. Dữ liệu OHLC (nến)

**Trong ngày:**

| Method | Khung thời gian |
|---|---|
| `GetOHLC1Minute(symbol)` | 1 phút |
| `GetOHLC3Minute(symbol)` | 3 phút |
| `GetOHLC5Minute(symbol)` | 5 phút |
| `GetOHLC15Minute(symbol)` | 15 phút |
| `GetOHLC1Hour(symbol)` | 1 giờ |
```text
ohlc, err := data.MarketData.GetOHLC1Minute("SSI")
if err != nil {
    log.Fatal(err)
}
for _, candle := range ohlc {
    fmt.Printf("%s: O=%.0f H=%.0f L=%.0f C=%.0f V=%d\n",
        candle.TradingDate, candle.OpenPrice, candle.HighPrice,
        candle.LowPrice, candle.ClosePrice, candle.Volume)
}
```

**Lịch sử (với khoảng ngày + phân trang):**

| Method | Khung thời gian |
|---|---|
| `GetOHLC1MinuteHistorical(symbol, fromDate, toDate, page, size)` | 1 phút |
| `GetOHLC3MinuteHistorical(...)` | 3 phút |
| `GetOHLC5MinuteHistorical(...)` | 5 phút |
| `GetOHLC15MinuteHistorical(...)` | 15 phút |
| `GetOHLC1HourHistorical(...)` | 1 giờ |
| `GetOHLC1DayHistorical(...)` | 1 ngày |
| `GetOHLC1WeekHistorical(...)` | 1 tuần |
| `GetOHLC1MonthHistorical(...)` | 1 tháng |
```text
ohlc, err := data.MarketData.GetOHLC1DayHistorical(
    "SSI", "2026/03/27", "2026/04/22", 1, 100,
)
```

**Tham số lịch sử:**

| Tham số | Kiểu | Mặc định | Mô tả |
|---|---|---|---|
| `symbol` | `string` | _(bắt buộc)_ | Mã chứng khoán |
| `fromDate` | `string` | _(bắt buộc)_ | Ngày bắt đầu (yyyy/MM/dd) |
| `toDate` | `string` | _(bắt buộc)_ | Ngày kết thúc (yyyy/MM/dd) |
| `page` | `int` | `1` | Số trang |
| `size` | `int` | `1000` | Số bản ghi mỗi trang |

**Trả về:** `[]OHLCData`

### 3.1b. Download OHLC

Tải dữ liệu OHLC dạng raw (trả về `map[string]interface{}`):

| Method | Mô tả |
|---|---|
| `DownloadOHLC1Minute(symbol)` | Dữ liệu raw 1 phút |
| `DownloadOHLC1Day(symbol)` | Dữ liệu raw ngày |
```text
// Download dữ liệu OHLC (trả về raw map)
rawData, err := data.MarketData.DownloadOHLC1Minute("SSI")
rawData, err := data.MarketData.DownloadOHLC1Day("SSI")
```

### 3.2. Chỉ số thị trường
```python
// Tất cả chỉ số
indexes, err := data.MarketData.GetIndexes()

// Theo sàn
import "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/market"
indexes, err := data.MarketData.GetIndexesByBoard(market.BoardHOSE)

for _, idx := range indexes {
    fmt.Printf("%s - %s\n", idx.Index, idx.IndexName)
}
```

**Trả về:** `[]MarketIndexes`

### 3.3. Tổng hợp chỉ số (Index Summary)
```text
// Tổng hợp hiện tại
summary, err := data.MarketData.GetIndexSummary("VNINDEX")

// Tổng hợp lịch sử
summary, err := data.MarketData.GetIndexSummaryHistorical("VNINDEX", "2026/01/15")

// Tổng hợp theo sàn
summary, err := data.MarketData.GetBoardSummary(market.BoardHOSE)

// Tổng hợp theo sàn lịch sử
summary, err := data.MarketData.GetBoardSummaryHistorical(market.BoardHOSE, "2026/01/15")
```

**Trả về:** `MarketIndexSummary`

### 3.4. Thông tin chứng khoán
```text
// Một mã
info, err := data.MarketData.GetSecuritiesInfo("SSI")

// Theo chỉ số
securities, err := data.MarketData.GetSecuritiesInfoByIndex("VN30")

// Theo sàn
securities, err := data.MarketData.GetSecuritiesInfoByBoard(market.BoardHOSE)
```

**Trả về:** `SecuritiesInfo`

### 3.5. Tổng hợp chứng khoán (Securities Summary)
```text
// Tổng hợp hiện tại
summary, err := data.MarketData.GetSecuritiesSummary("SSI")

// Tổng hợp lịch sử
summary, err := data.MarketData.GetSecuritiesSummaryHistorical(
    "SSI", "2026/03/01", "2026/03/31",
)

// Theo chỉ số
summary, err := data.MarketData.GetSecuritiesSummaryByIndex("VN30")

// Theo chỉ số lịch sử
summary, err := data.MarketData.GetSecuritiesSummaryByIndexHistorical(
    "VN30", "2026/03/01", "2026/03/31",
)
```

**Trả về:** `[]SecuritiesSummary`

* * *

## 4\. Danh mục (PortfolioService)

Truy cập qua `t.Portfolio`.

### 4.1. Số dư tài khoản
```text
// Số dư cổ phiếu
balance, err := t.Portfolio.GetEquityBalance("1234561")

// Số dư phái sinh
derBalance, err := t.Portfolio.GetDerivativeBalance("1234568")
```

### 4.2. Vị thế
```text
// Vị thế cổ phiếu
positions, err := t.Portfolio.GetEquityPositions("1234561")
for _, pos := range positions {
    fmt.Printf("%s: %d cổ | Giá vốn: %.0f\n", pos.Symbol, pos.Quantity, pos.CostPrice)
}

// Tất cả vị thế phái sinh
derPositions, err := t.Portfolio.GetDerivativePositions("1234568")

// Chỉ vị thế đang mở
openPos, err := t.Portfolio.GetOpenDerivativePositions("1234568")

// Chỉ vị thế đã đóng
closedPos, err := t.Portfolio.GetClosedDerivativePositions("1234568")
```

### 4.3. Sổ lệnh
```text
// Lệnh trong ngày
orders, err := t.Portfolio.GetTodayOrders("1234561")
for _, order := range orders {
    fmt.Printf("%s: %s %s %d@%.0f - %s\n",
        order.OrderID, order.Symbol, order.Side, order.Quantity, order.Price, order.Status)
}

// Lệnh lịch sử
orders, err := t.Portfolio.GetHistoricalOrders("1234561", "2026/01/01", "2026/01/31")
```

### 4.4. PPMMR
```text
// PPMMR cổ phiếu
ppmmr, err := t.Portfolio.GetEquityPPMMR("1234561")

// PPMMR phái sinh
derPPMMR, err := t.Portfolio.GetDerivativePPMMR("1234568")
```

### Tổng quan method Portfolio

| Nhóm | Method | Trả về |
|---|---|---|
| **Số dư** | `GetEquityBalance(accountNo)` | `EquityAccountBalance` |
|  | `GetDerivativeBalance(accountNo)` | `DerivativeAccountBalance` |
| **Vị thế** | `GetEquityPositions(accountNo)` | `[]EquityPosition` |
|  | `GetDerivativePositions(accountNo)` | `[]AllDerivativePosition` |
|  | `GetOpenDerivativePositions(accountNo)` | `[]DerivativePosition` |
|  | `GetClosedDerivativePositions(accountNo)` | `[]DerivativePosition` |
| **Sổ lệnh** | `GetTodayOrders(accountNo)` | `[]Order` |
|  | `GetHistoricalOrders(accountNo, fromDate, toDate)` | `[]Order` |
| **PPMMR** | `GetEquityPPMMR(accountNo)` | `EquityPPMMR` |
|  | `GetDerivativePPMMR(accountNo)` | `DerivativePPMMR` |

* * *

## 5\. Giao dịch (TradingService)

Truy cập qua `t.Trading`.

### 5.1. Đặt lệnh
```python
import "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/trading"

// Lệnh giới hạn (LO)
result, err := t.Trading.PlaceLimitOrder("1234561", "SSI", trading.OrderSideBuy, 100, 66000)

// Lệnh thị trường (MTL)
result, err := t.Trading.PlaceMarketOrder("1234561", "SSI", trading.OrderSideBuy, 100)

// Lệnh ATO (mở cửa)
result, err := t.Trading.PlaceATOOrder("1234561", "SSI", trading.OrderSideBuy, 100)

// Lệnh ATC (đóng cửa)
result, err := t.Trading.PlaceATCOrder("1234561", "SSI", trading.OrderSideSell, 100)

// Loại lệnh tuỳ chỉnh
result, err := t.Trading.PlaceOrder(
    "1234561", "SSI", trading.OrderSideBuy, 100, 66000, trading.OrderTypeLO,
)

fmt.Printf("Order ID: %s, Status: %s\n", result.OrderID, result.Status)
```

### 5.2. Sửa lệnh

Chỉ có thể sửa **giá** hoặc **khối lượng** (không sửa cả hai cùng lúc).
```text
// Sửa giá theo client_request_id
result, err := t.Trading.ModifyOrderPrice("1234561", "REQ123", 68000)

// Sửa giá theo order_id
result, err := t.Trading.ModifyOrderPriceByOrderID("1234561", "ORD123", 68000)

// Sửa khối lượng theo client_request_id
result, err := t.Trading.ModifyOrderQuantity("1234561", "REQ123", 200)

// Sửa khối lượng theo order_id
result, err := t.Trading.ModifyOrderQuantityByOrderID("1234561", "ORD123", 200)
```

### 5.3. Huỷ lệnh
```text
// Huỷ theo client_request_id
result, err := t.Trading.CancelOrder("1234561", "REQ123")

// Huỷ theo order_id
result, err := t.Trading.CancelOrderByOrderID("1234561", "ORD123")
```

### 5.4. Sức mua/bán tối đa
```text
// Với giá cụ thể
price := 66000.0
maxBS, err := t.Trading.GetMaxBuySell("1234561", "SSI", &price)
fmt.Printf("Max mua: %d, Max bán: %d\n", maxBS.MaxBuyQuantity, maxBS.MaxSellQuantity)

// Theo giá thị trường
maxBS, err := t.Trading.GetMaxBuySellAtMarketPrice("1234561", "SSI")
```

### Tổng quan method Trading

| Nhóm | Method | Trả về |
|---|---|---|
| **Đặt lệnh** | `PlaceOrder(accountNo, symbol, side, qty, price, orderType)` | `PlaceOrderResponse` |
|  | `PlaceLimitOrder(accountNo, symbol, side, qty, price)` | `PlaceOrderResponse` |
|  | `PlaceMarketOrder(accountNo, symbol, side, qty)` | `PlaceOrderResponse` |
|  | `PlaceATOOrder(accountNo, symbol, side, qty)` | `PlaceOrderResponse` |
|  | `PlaceATCOrder(accountNo, symbol, side, qty)` | `PlaceOrderResponse` |
| **Sửa lệnh** | `ModifyOrderPrice(accountNo, clientRequestID, price)` | `ModifyOrderResponse` |
|  | `ModifyOrderPriceByOrderID(accountNo, orderID, price)` | `ModifyOrderResponse` |
|  | `ModifyOrderQuantity(accountNo, clientRequestID, qty)` | `ModifyOrderResponse` |
|  | `ModifyOrderQuantityByOrderID(accountNo, orderID, qty)` | `ModifyOrderResponse` |
| **Huỷ lệnh** | `CancelOrder(accountNo, clientRequestID)` | `CancelOrderResponse` |
|  | `CancelOrderByOrderID(accountNo, orderID)` | `CancelOrderResponse` |
| **Sức mua/bán** | `GetMaxBuySell(accountNo, symbol, price)` | `MaxBuySellResponse` |
|  | `GetMaxBuySellAtMarketPrice(accountNo, symbol)` | `MaxBuySellResponse` |
| **Lệnh điều kiện** | `PlaceFcoGtd(accountNo, symbol, side, qty, price, priceSlip, fromDate, toDate)` | `FCOPlaceResponse` |
|  | `PlaceFcoStop(accountNo, symbol, side, qty, stopPrice, operator, fromDate, toDate)` | `FCOPlaceResponse` |
|  | `PlaceFcoStopLimit(accountNo, symbol, side, qty, price, priceSlip, stopPrice, operator, fromDate, toDate)` | `FCOPlaceResponse` |
|  | `PlaceFcoTrailingStop(accountNo, symbol, side, qty, activePrice, trailingAmount, fromDate, toDate)` | `FCOPlaceResponse` |
|  | `PlaceFcoTrailingStopLimit(accountNo, symbol, side, qty, activePrice, trailingAmount, priceSlip, fromDate, toDate)` | `FCOPlaceResponse` |
|  | `PlaceFcoOco(accountNo, symbol, side, qty, tpActivePrice, slActivePrice, tpPrice, slPrice, tpSlip, slSlip, fromDate, toDate)` | `FCOPlaceResponse` |
|  | `PlaceFcoBullBear(accountNo, symbol, side, qty, price, priceSlip, tpActivePrice, slActivePrice, tpPrice, slPrice, tpSlip, slSlip, fromDate, toDate)` | `FCOPlaceResponse` |
|  | `CancelFco(fcoID)` | `FCOCancelResponse` |
|  | `GetFcoByAccountNo(accountNo, pageIndex, pageSize)` | `FCOListResponse` |
|  | `GetFcoBySymbol(accountNo, symbol, pageIndex, pageSize)` | `FCOListResponse` |
|  | `GetFcoByStatus(accountNo, status, pageIndex, pageSize)` | `FCOListResponse` |
|  | `GetFcoByDate(accountNo, fromDate, toDate, pageIndex, pageSize)` | `FCOListResponse` |
|  | `GetFcoById(accountNo, fcoID)` | `*FCOInfo` |
|  | `GetFcoOrderBook(fcoID, pageIndex, pageSize)` | `FCOOrderBookResponse` |

### 5.5. Lệnh điều kiện (Flexible Conditional Orders - FCO)

SDK hỗ trợ 7 loại lệnh điều kiện linh hoạt FCO, tra cứu danh sách lệnh FCO, nhật ký sổ lệnh FCO và hủy lệnh FCO:
```python
import (
    "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/internal/util"
    "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/trading"
)

accountNo := "1234561"
fromDate := util.BeginningOfDay() // "YYYY/MM/DD 00:00:00"
toDate := util.EndOfDay()         // "YYYY/MM/DD 23:59:59"

// 1. Đặt lệnh GTD (Good Till Date)
gtd, err := t.Trading.PlaceFcoGtd(
    accountNo, "SSI", trading.OrderSideBuy, 100, 25000, 500, fromDate, toDate,
)

// 2. Đặt lệnh Stop Market
stop, err := t.Trading.PlaceFcoStop(
    accountNo, "SSI", trading.OrderSideSell, 100, 24000, trading.FCOOperatorLesserOrEqual, fromDate, toDate,
)

// 3. Đặt lệnh Stop Limit
stopLimit, err := t.Trading.PlaceFcoStopLimit(
    accountNo, "SSI", trading.OrderSideBuy, 100, 25500, 500, 25000, trading.FCOOperatorGreaterOrEqual, fromDate, toDate,
)

// 4. Đặt lệnh Trailing Stop
trailing, err := t.Trading.PlaceFcoTrailingStop(
    accountNo, "SSI", trading.OrderSideBuy, 100, 26000, 1000, fromDate, toDate,
)

// 5. Đặt lệnh Trailing Stop Limit
trailingLimit, err := t.Trading.PlaceFcoTrailingStopLimit(
    accountNo, "SSI", trading.OrderSideBuy, 100, 26000, 1000, 500, fromDate, toDate,
)

// 6. Đặt lệnh OCO (One-Cancels-the-Other)
oco, err := t.Trading.PlaceFcoOco(
    accountNo, "SSI", trading.OrderSideSell, 100, 30000, 24000, trading.OrderTypeMTL, trading.OrderTypeMTL, 500, 500, fromDate, toDate,
)

// 7. Đặt lệnh Bull Bear
bullBear, err := t.Trading.PlaceFcoBullBear(
    accountNo, "SSI", trading.OrderSideBuy, 1000, 100.5, 10, 30, 20, 30, 10, 0.1, 0, fromDate, toDate,
)

// Hủy lệnh FCO
cancelRes, err := t.Trading.CancelFco(gtd.FCOID)
```

**Trả về:** `FCOPlaceResponse` (`FCOID`) khi đặt lệnh, `FCOCancelResponse` (`FCOID`) khi huỷ lệnh.
```text
// Tra cứu danh sách lệnh FCO theo tài khoản
fcoList, err := t.Trading.GetFcoByAccountNo(accountNo, 1, 10)

// Tra cứu theo mã chứng khoán
fcoList, err := t.Trading.GetFcoBySymbol(accountNo, "SSI", 1, 10)

// Tra cứu theo trạng thái xử lý
fcoList, err := t.Trading.GetFcoByStatus(accountNo, trading.FCOStatusTrit, 1, 10)

// Tra cứu theo khoảng ngày
fcoList, err := t.Trading.GetFcoByDate(accountNo, "2026/07/01", "2026/07/21", 1, 10)

// Lấy một lệnh FCO cụ thể theo ID
fcoInfo, err := t.Trading.GetFcoById(accountNo, "fco-id-here")

// Lấy nhật ký khớp lệnh (order book) của lệnh FCO
orderBook, err := t.Trading.GetFcoOrderBook("fco-id-here", 1, 10)
```

> **Lưu ý:** Các method tra cứu danh sách hỗ trợ tham số `pageIndex`/`pageSize` để phân trang.

* * *

## 6\. Streaming Realtime (StreamingService)

Truy cập qua `s.Streaming`. Gọi `s.Connect()` trước.

### 6.1. Kết nối
```text
s := ssi.NewStream(auth)
defer s.Disconnect()

if err := s.Connect(); err != nil {
    log.Fatal(err)
}

// Chờ vô thời hạn
s.Wait(nil)

// Chờ với timeout
timeout := 30 * time.Second
s.Wait(&timeout)
```

### 6.2. Thiết lập Callbacks
```python
import "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/stream"

s.Streaming.SetOnData(func(msg interface{}) {
    switch m := msg.(type) {
    case *stream.TradeMessage:
        fmt.Printf("[TRADE] %s | Giá: %.0f | KL: %d\n", m.Symbol, m.Price, m.Quantity)
    case *stream.QuoteMessage:
        fmt.Printf("[QUOTE] %s | Mua: %v | Bán: %v\n", m.Symbol, m.BidPrices, m.AskPrices)
    case *stream.ForeignRoomMessage:
        fmt.Printf("[ROOM] %s | KL Mua: %d | KL Bán: %d\n", m.Symbol, m.BuyQuantity, m.SellQuantity)
    case *stream.MarketStatusMessage:
        fmt.Printf("[MARKET] %s | Trạng thái: %s\n", m.Market, m.Status)
    case *stream.PutMessage:
        fmt.Printf("[PUT] %s | %.0f x %d\n", m.Symbol, m.Price, m.Quantity)
    case *stream.OddLotMessage:
        fmt.Printf("[ODDLOT] %s | %.0f x %d\n", m.Symbol, m.Price, m.Quantity)
    case *stream.IntervalMessage:
        fmt.Printf("[OHLCV] %s | O=%.0f H=%.0f L=%.0f C=%.0f V=%d\n",
            m.Symbol, m.Open, m.High, m.Low, m.Close, m.Volume)
    }
})

s.Streaming.SetOnTrading(func(msg interface{}) {
    switch m := msg.(type) {
    case *stream.OrderStatusMessage:
        fmt.Printf("[ORDER] %s %s | Trạng thái: %s\n", m.Symbol, m.Side, m.Status)
    case *stream.FCOOrderUpdateMessage:
        fmt.Printf("[FCO ORDER] %s | ProcessStatus: %s\n", m.Symbol, m.ProcessStatus)
    case *stream.PortfolioMessage:
        fmt.Printf("[PORTFOLIO] %s | Tổng: %.0f\n", m.AccountNo, m.TotalAsset)
    }
})

s.Streaming.SetOnHeartbeat(func(msg *stream.HeartbeatMessage) {
    fmt.Printf("[HEARTBEAT] %v\n", msg)
})
```

### 6.3. Subscribe dữ liệu thị trường
```python
import "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/market"

// Tất cả kênh (trade + quote + room) cho mã
s.Streaming.SubscribeSymbol([]string{"SSI", "HPG", "VIC"}, nil)

// Kênh riêng lẻ
s.Streaming.SubscribeSymbolTrade([]string{"SSI", "HPG"}, nil)
s.Streaming.SubscribeSymbolQuote([]string{"SSI", "HPG"}, nil)
s.Streaming.SubscribeSymbolRoom([]string{"SSI", "HPG"}, nil)
s.Streaming.SubscribeSymbolPutThrough([]string{"SSI"}, nil)
s.Streaming.SubscribeSymbolOddLot([]string{"SSI"}, nil)

// OHLCV theo timeframe
import "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/market"
s.Streaming.SubscribeSymbolOhlcv([]string{"SSI"}, market.TimeframeMinute1, nil)

// Theo sàn
s.Streaming.SubscribeBoard([]market.Board{market.BoardHOSE, market.BoardHNX}, nil)

// Theo chỉ số
s.Streaming.SubscribeIndex([]string{"VNINDEX", "VN30"}, nil)
```

### 6.4. Unsubscribe
```text
s.Streaming.UnsubscribeSymbol([]string{"SSI", "HPG"})
s.Streaming.UnsubscribeSymbolTrade([]string{"SSI"})
s.Streaming.UnsubscribeSymbolQuote([]string{"SSI"})
s.Streaming.UnsubscribeSymbolRoom([]string{"SSI"})
s.Streaming.UnsubscribeSymbolPutThrough([]string{"SSI"})
s.Streaming.UnsubscribeSymbolOddLot([]string{"SSI"})
s.Streaming.UnsubscribeSymbolOhlcv([]string{"SSI"}, market.TimeframeMinute1)
s.Streaming.UnsubscribeBoard([]market.Board{market.BoardHOSE})
s.Streaming.UnsubscribeIndex([]string{"VNINDEX"})
```

### 6.5. Subscribe sự kiện giao dịch
```text
// Trạng thái lệnh — tất cả tài khoản
s.Streaming.SubscribeOrderStatus("", nil)

// Cho tài khoản cụ thể
s.Streaming.SubscribeOrderStatus("1234561", nil)

// Lệnh điều kiện (FCO) — hiện là alias của SubscribeOrderStatus
s.Streaming.SubscribeFcoOrderStatus("1234561", nil)

// Danh mục — tất cả tài khoản
s.Streaming.SubscribePortfolio("", nil)

// Cho tài khoản cụ thể
s.Streaming.SubscribePortfolio("1234561", nil)
```

### 6.6. Heartbeat
```text
// Ping một lần (không callback, không lặp)
s.Streaming.Ping(nil, nil)

// Ping lặp lại theo interval
interval := 30 * time.Second
s.Streaming.Ping(nil, &interval)

// Dừng ping loop tự động
s.Streaming.StopPingLoop()
```

### 6.7. Trạng thái kết nối
```text
if s.Streaming.IsConnected() {
    fmt.Println("WebSocket connected")
}
```

### Loại message qua `SetOnData`

| Topic | Message Type | Mô tả |
|---|---|---|
| `trade.*` | `*stream.TradeMessage` | Dữ liệu khớp lệnh |
| `quote.*` | `*stream.QuoteMessage` | Dữ liệu mua/bán |
| `room.*` | `*stream.ForeignRoomMessage` | Room ngoại |
| `market.*` | `*stream.MarketStatusMessage` | Trạng thái thị trường |
| `put.*` | `*stream.PutMessage` | Thoả thuận |
| `oddlot.*` | `*stream.OddLotMessage` | Lô lẻ |
| `trade.*.<timeframe>` | `*stream.IntervalMessage` | Dữ liệu OHLCV theo interval |

### Loại message qua `SetOnTrading`

| Topic | Message Type | Mô tả |
|---|---|---|
| `order.*` | `*stream.OrderStatusMessage` | Cập nhật trạng thái lệnh thường |
|  | `*stream.FCOOrderUpdateMessage` | Cập nhật trạng thái lệnh điều kiện (khi `EventType == "fcoEvent"`) |
| `portfolio.*` | `*stream.PortfolioMessage` | Thay đổi danh mục |

### Tổng quan method Streaming

| Nhóm | Method | Mô tả |
|---|---|---|
| **Kết nối** | `Connect()` | Kết nối WebSocket |
|  | `Disconnect()` | Ngắt kết nối |
|  | `Wait(timeout *time.Duration)` | Chờ dữ liệu |
|  | `IsConnected()` | Kiểm tra trạng thái kết nối |
| **Heartbeat** | `Ping(onResponse, interval *time.Duration)` | Ping server (một lần nếu `interval` là `nil`) |
|  | `StopPingLoop()` | Dừng ping loop tự động |
| **Symbol** | `SubscribeSymbol(symbols, callback)` | Trade + Quote + Room |
|  | `SubscribeSymbolTrade(symbols, callback)` | Chỉ Trade |
|  | `SubscribeSymbolQuote(symbols, callback)` | Chỉ Quote |
|  | `SubscribeSymbolRoom(symbols, callback)` | Chỉ Room ngoại |
|  | `SubscribeSymbolPutThrough(symbols, callback)` | Chỉ thoả thuận |
|  | `SubscribeSymbolOddLot(symbols, callback)` | Chỉ lô lẻ |
|  | `SubscribeSymbolOhlcv(symbols, interval, callback)` | OHLCV theo timeframe |
| **Sàn/Chỉ số** | `SubscribeBoard(boards, callback)` | Theo sàn |
|  | `SubscribeIndex(indices, callback)` | Theo chỉ số |
| **Giao dịch** | `SubscribeOrderStatus(accountNo, callback)` | Trạng thái lệnh |
|  | `SubscribeFcoOrderStatus(accountNo, callback)` | Trạng thái lệnh điều kiện (FCO) |
|  | `SubscribePortfolio(accountNo, callback)` | Thay đổi danh mục |
| **Unsubscribe** | `UnsubscribeSymbol(symbols)` | Huỷ tất cả kênh |
|  | `UnsubscribeSymbolTrade(symbols)` | Huỷ trade |
|  | `UnsubscribeSymbolQuote(symbols)` | Huỷ quote |
|  | `UnsubscribeSymbolRoom(symbols)` | Huỷ room |
|  | `UnsubscribeSymbolPutThrough(symbols)` | Huỷ thoả thuận |
|  | `UnsubscribeSymbolOddLot(symbols)` | Huỷ lô lẻ |
|  | `UnsubscribeSymbolOhlcv(symbols, interval)` | Huỷ OHLCV |
|  | `UnsubscribeBoard(boards)` | Huỷ sàn |
|  | `UnsubscribeIndex(indices)` | Huỷ chỉ số |
