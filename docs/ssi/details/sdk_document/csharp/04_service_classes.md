<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/csharp/service-classes
Tieu de goc: API Services
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/csharp/service-classes>

# API Services

Chi tiết các method API cho từng service trong .NET SDK

## 1\. Xác thực (TokenManager)

Truy cập qua `auth.TokenManager` hoặc trực tiếp trên `auth` (uỷ quyền).

### Xác thực với OTP
```text
var token = await auth.AuthenticateAsync("222222");
Console.WriteLine($"Access token: {token.AccessToken}");
Console.WriteLine($"Expires at: {token.ExpiresAt}");
```

### Yêu cầu gửi OTP
```text
var result = await auth.RequestOtpAsync();
```

### Làm mới token
```text
var token = await auth.RefreshAsync();
```

### Tự động đảm bảo xác thực
```text
var accessToken = await auth.EnsureAuthenticatedAsync("222222");
```

* * *

## 2\. Tài khoản (AccountService)

Truy cập qua `trading.Account`.

### Lấy danh sách tài khoản
```text
var accounts = await trading.Account.GetAccountInfoAsync();

foreach (var acc in accounts)
{
    Console.WriteLine($"{acc.AccountNo} - {acc.AccountType}");
}
```

**Trả về:** `List<Account>` — mỗi `Account` có `AccountNo: string`, `AccountType: string`.

* * *

## 3\. Dữ liệu thị trường (MarketDataService)

Truy cập qua `data.MarketData`. Không cần OTP.

### 3.1. Dữ liệu OHLC (nến)

**Trong ngày:**

| Method | Timeframe |
|---|---|
| `GetOhlc1MinuteAsync(symbol)` | 1 phút |
| `GetOhlc3MinuteAsync(symbol)` | 3 phút |
| `GetOhlc5MinuteAsync(symbol)` | 5 phút |
| `GetOhlc15MinuteAsync(symbol)` | 15 phút |
| `GetOhlc1HourAsync(symbol)` | 1 giờ |
```text
var ohlc = await data.MarketData.GetOhlc1MinuteAsync("SSI");
foreach (var candle in ohlc)
{
    Console.WriteLine($"{candle.TradingDate}: O={candle.OpenPrice} H={candle.HighPrice} L={candle.LowPrice} C={candle.ClosePrice} V={candle.Volume}");
}
```

**Lịch sử (truyền khoảng ngày + phân trang):**

| Method | Timeframe |
|---|---|
| `GetOhlc1MinuteHistoricalAsync(symbol, fromDate, toDate, page, size)` | 1 phút |
| `GetOhlc3MinuteHistoricalAsync(...)` | 3 phút |
| `GetOhlc5MinuteHistoricalAsync(...)` | 5 phút |
| `GetOhlc15MinuteHistoricalAsync(...)` | 15 phút |
| `GetOhlc1HourHistoricalAsync(...)` | 1 giờ |
| `GetOhlc1DayHistoricalAsync(...)` | 1 ngày |
| `GetOhlc1WeekHistoricalAsync(...)` | 1 tuần |
| `GetOhlc1MonthHistoricalAsync(...)` | 1 tháng |
```text
var ohlc = await data.MarketData.GetOhlc1DayHistoricalAsync(
    symbol: "SSI",
    fromDate: "2026/03/27",
    toDate: "2026/04/22",
    page: 1,
    size: 100);
```

**Tham số historical:**

| Tham số | Kiểu | Mặc định | Mô tả |
|---|---|---|---|
| `symbol` | `string` | _(bắt buộc)_ | Mã chứng khoán |
| `fromDate` | `string` | _(bắt buộc)_ | Ngày bắt đầu |
| `toDate` | `string` | _(bắt buộc)_ | Ngày kết thúc |
| `page` | `int` | `1` | Trang |
| `size` | `int` | `1000` | Số bản ghi/trang |

**Trả về:** `List<OhlcData>`

### 3.1b. Download OHLC

Tải dữ liệu OHLC dạng raw (trả về `DownloadData` chứa `List<Dictionary<string, object>>`):
```text
var raw = await data.MarketData.DownloadOhlc1MinuteAsync("SSI");
var rawDay = await data.MarketData.DownloadOhlc1DayAsync("SSI");
```

### 3.2. Danh sách chỉ số thị trường
```text
// Tất cả chỉ số
var indexes = await data.MarketData.GetIndexesAsync();

// Theo sàn
var indexesByBoard = await data.MarketData.GetIndexesByBoardAsync(Board.HOSE);

foreach (var idx in indexes)
{
    Console.WriteLine($"{idx.Index} - {idx.IndexName}");
}
```

**Trả về:** `List<MarketIndexes>`

### 3.3. Tổng hợp chỉ số (Index Summary)
```text
// Summary hiện tại
var summary = await data.MarketData.GetIndexSummaryAsync("VNINDEX");

// Summary lịch sử
var summaryHist = await data.MarketData.GetIndexSummaryHistoricalAsync("VNINDEX", "2026/01/15");

// Summary theo sàn
var boardSummary = await data.MarketData.GetBoardSummaryAsync(Board.HOSE);

// Summary sàn lịch sử
var boardSummaryHist = await data.MarketData.GetBoardSummaryHistoricalAsync(Board.HOSE, "2026/01/15");
```

**Trả về:** `MarketIndexSummary?`

### 3.4. Thông tin chứng khoán
```text
// 1 mã
var info = await data.MarketData.GetSecuritiesInfoAsync("SSI");

// Theo chỉ số
var byIndex = await data.MarketData.GetSecuritiesInfoByIndexAsync("VN30");

// Theo sàn
var byBoard = await data.MarketData.GetSecuritiesInfoByBoardAsync(Board.HOSE);
```

**Trả về:** `SecuritiesInfo?` / `List<SecuritiesInfo>`

### 3.5. Tổng hợp chứng khoán (Securities Summary)
```text
// Summary hiện tại
var summary = await data.MarketData.GetSecuritiesSummaryAsync("SSI");

// Summary lịch sử
var summaryHist = await data.MarketData.GetSecuritiesSummaryHistoricalAsync(
    symbol: "SSI", fromDate: "2026/03/01", toDate: "2026/03/31");

// Summary theo chỉ số
var byIndex = await data.MarketData.GetSecuritiesSummaryByIndexAsync("VN30");

// Summary theo chỉ số lịch sử
var byIndexHist = await data.MarketData.GetSecuritiesSummaryByIndexHistoricalAsync(
    index: "VN30", fromDate: "2026/03/01", toDate: "2026/03/31");
```

**Trả về:** `List<SecuritiesSummary>`

* * *

## 4\. Danh mục đầu tư (PortfolioService)

Truy cập qua `trading.Portfolio`.

### 4.1. Số dư tài khoản
```text
// Số dư cơ sở
var equityBalance = await trading.Portfolio.GetEquityBalanceAsync("1234561");
Console.WriteLine($"Available cash: {equityBalance?.AccountBalance}");

// Số dư phái sinh
var derivativeBalance = await trading.Portfolio.GetDerivativeBalanceAsync("1234568");
Console.WriteLine($"Withdrawable: {derivativeBalance?.Withdrawable}");
```

### 4.2. Vị thế (Positions)
```text
// Vị thế cơ sở
var positions = await trading.Portfolio.GetEquityPositionsAsync("1234561");
foreach (var pos in positions)
{
    Console.WriteLine($"{pos.Symbol}: {pos.Quantity} cp | Giá vốn: {pos.CostPrice}");
}

// Tất cả vị thế phái sinh (chia Open/Closed)
var allDerivative = await trading.Portfolio.GetDerivativePositionsAsync("1234568");

// Chỉ vị thế mở phái sinh
var openPos = await trading.Portfolio.GetOpenDerivativePositionsAsync("1234568");

// Chỉ vị thế đóng phái sinh
var closedPos = await trading.Portfolio.GetClosedDerivativePositionsAsync("1234568");
```

### 4.3. Sổ lệnh (Order Book)
```text
// Lệnh trong ngày
var todayOrders = await trading.Portfolio.GetTodayOrdersAsync("1234561");
foreach (var order in todayOrders)
{
    Console.WriteLine($"{order.OrderId}: {order.Symbol} {order.Side} {order.Quantity}@{order.Price} - {order.Status}");
}

// Lệnh lịch sử
var historicalOrders = await trading.Portfolio.GetHistoricalOrdersAsync(
    "1234561", fromDate: "2026/01/01", toDate: "2026/01/31");
```

### 4.4. PPMMR
```text
// PPMMR cơ sở
var equityPpmmr = await trading.Portfolio.GetEquityPpmmrAsync("1234561");
Console.WriteLine($"Purchasing power: {equityPpmmr?.PurchasingPower}");

// PPMMR phái sinh
var derivativePpmmr = await trading.Portfolio.GetDerivativePpmmrAsync("1234568");
```

### Tổng quan method Portfolio

| Nhóm | Method | Trả về |
|---|---|---|
| **Số dư** | `GetEquityBalanceAsync(accountNo)` | `EquityAccountBalance?` |
|  | `GetDerivativeBalanceAsync(accountNo)` | `DerivativeAccountBalance?` |
| **Vị thế** | `GetEquityPositionsAsync(accountNo)` | `List<EquityPosition>` |
|  | `GetDerivativePositionsAsync(accountNo)` | `AllDerivativePosition` |
|  | `GetOpenDerivativePositionsAsync(accountNo)` | `List<DerivativePosition>` |
|  | `GetClosedDerivativePositionsAsync(accountNo)` | `List<DerivativePosition>` |
| **Sổ lệnh** | `GetTodayOrdersAsync(accountNo)` | `List<Order>` |
|  | `GetHistoricalOrdersAsync(accountNo, fromDate, toDate)` | `List<Order>` |
| **PPMMR** | `GetEquityPpmmrAsync(accountNo)` | `EquityPPMMR?` |
|  | `GetDerivativePpmmrAsync(accountNo)` | `DerivativePPMMR?` |

* * *

## 5\. Giao dịch (TradingService)

Truy cập qua `trading.Trading`.

### 5.1. Đặt lệnh
```text
// Lệnh giới hạn (LO)
var result = await trading.Trading.PlaceLimitOrderAsync(
    accountNo: "1234561", symbol: "SSI", side: OrderSide.Buy, quantity: 100, price: 66000);
Console.WriteLine($"Order ID: {result.OrderId}, Status: {result.Status}");

// Lệnh thị trường (MTL)
var market = await trading.Trading.PlaceMarketOrderAsync(
    "1234561", "SSI", OrderSide.Buy, 100);

// Lệnh ATO (mở cửa)
var ato = await trading.Trading.PlaceAtoOrderAsync(
    "1234561", "SSI", OrderSide.Buy, 100);

// Lệnh ATC (đóng cửa)
var atc = await trading.Trading.PlaceAtcOrderAsync(
    "1234561", "SSI", OrderSide.Sell, 100);

// Lệnh tuỳ chỉnh (chỉ định OrderType)
var custom = await trading.Trading.PlaceOrderAsync(
    "1234561", "SSI", OrderSide.Buy, 100, 66000, OrderType.LO);
```

### 5.2. Sửa lệnh

Chỉ sửa **giá** hoặc **khối lượng** (không đồng thời).
```text
// Sửa giá theo ClientRequestId
var r1 = await trading.Trading.ModifyOrderPriceAsync("1234561", "REQ123", 68000);

// Sửa giá theo OrderId
var r2 = await trading.Trading.ModifyOrderPriceByOrderIdAsync("1234561", "ORD123", 68000);

// Sửa khối lượng theo ClientRequestId
var r3 = await trading.Trading.ModifyOrderQuantityAsync("1234561", "REQ123", 200);

// Sửa khối lượng theo OrderId
var r4 = await trading.Trading.ModifyOrderQuantityByOrderIdAsync("1234561", "ORD123", 200);
```

### 5.3. Huỷ lệnh
```text
// Huỷ theo ClientRequestId
var c1 = await trading.Trading.CancelOrderAsync("1234561", "REQ123");

// Huỷ theo OrderId
var c2 = await trading.Trading.CancelOrderByOrderIdAsync("1234561", "ORD123");
```

### 5.4. Sức mua/bán tối đa
```text
// Với giá cụ thể
var maxBS = await trading.Trading.GetMaxBuySellAsync("1234561", "SSI", 66000);
Console.WriteLine($"Max buy: {maxBS.MaxBuyQuantity}");
Console.WriteLine($"Max sell: {maxBS.MaxSellQuantity}");

// Với giá thị trường
var maxBSMarket = await trading.Trading.GetMaxBuySellAtMarketPriceAsync("1234561", "SSI");
```

### Tổng quan method Trading

| Nhóm | Method | Trả về |
|---|---|---|
| **Đặt lệnh** | `PlaceOrderAsync(accountNo, symbol, side, quantity, price, orderType)` | `PlaceOrderResponse` |
|  | `PlaceLimitOrderAsync(accountNo, symbol, side, quantity, price)` | `PlaceOrderResponse` |
|  | `PlaceMarketOrderAsync(accountNo, symbol, side, quantity)` | `PlaceOrderResponse` |
|  | `PlaceAtoOrderAsync(accountNo, symbol, side, quantity)` | `PlaceOrderResponse` |
|  | `PlaceAtcOrderAsync(accountNo, symbol, side, quantity)` | `PlaceOrderResponse` |
| **Sửa lệnh** | `ModifyOrderPriceAsync(accountNo, clientRequestId, price)` | `ModifyOrderResponse` |
|  | `ModifyOrderPriceByOrderIdAsync(accountNo, orderId, price)` | `ModifyOrderResponse` |
|  | `ModifyOrderQuantityAsync(accountNo, clientRequestId, quantity)` | `ModifyOrderResponse` |
|  | `ModifyOrderQuantityByOrderIdAsync(accountNo, orderId, quantity)` | `ModifyOrderResponse` |
| **Huỷ lệnh** | `CancelOrderAsync(accountNo, clientRequestId)` | `CancelOrderResponse` |
|  | `CancelOrderByOrderIdAsync(accountNo, orderId)` | `CancelOrderResponse` |
| **Sức mua/bán** | `GetMaxBuySellAsync(accountNo, symbol, price)` | `MaxBuySellResponse` |
|  | `GetMaxBuySellAtMarketPriceAsync(accountNo, symbol)` | `MaxBuySellResponse` |
| **Lệnh điều kiện** | `PlaceFcoGtdAsync(accountNo, symbol, side, quantity, price, priceSlip, fromDate, toDate)` | `FCOPlaceResponse` |
|  | `PlaceFcoStopAsync(accountNo, symbol, side, quantity, stopPrice, operatorType, fromDate, toDate)` | `FCOPlaceResponse` |
|  | `PlaceFcoStopLimitAsync(accountNo, symbol, side, quantity, price, priceSlip, stopPrice, operatorType, fromDate, toDate)` | `FCOPlaceResponse` |
|  | `PlaceFcoTrailingStopAsync(accountNo, symbol, side, quantity, activePrice, trailingAmount, fromDate, toDate)` | `FCOPlaceResponse` |
|  | `PlaceFcoTrailingStopLimitAsync(accountNo, symbol, side, quantity, activePrice, trailingAmount, priceSlip, fromDate, toDate)` | `FCOPlaceResponse` |
|  | `PlaceFcoOcoAsync(accountNo, symbol, side, quantity, tpActivePrice, slActivePrice, tpPrice, slPrice, tpSlip, slSlip, fromDate, toDate)` | `FCOPlaceResponse` |
|  | `PlaceFcoBullBearAsync(accountNo, symbol, side, quantity, price, priceSlip, tpActivePrice, slActivePrice, tpPrice, slPrice, tpSlip, slSlip, fromDate, toDate)` | `FCOPlaceResponse` |
|  | `CancelFcoAsync(fcoId)` | `FCOCancelResponse` |
|  | `GetFcoByAccountNoAsync(accountNo, pageIndex, pageSize)` | `FCOListResponse` |
|  | `GetFcoBySymbolAsync(accountNo, symbol, pageIndex, pageSize)` | `FCOListResponse` |
|  | `GetFcoByStatusAsync(accountNo, processStatus, pageIndex, pageSize)` | `FCOListResponse` |
|  | `GetFcoByDateAsync(accountNo, fromDate, toDate, pageIndex, pageSize)` | `FCOListResponse` |
|  | `GetFcoByIdAsync(accountNo, fcoId)` | `FCOInfo?` |
|  | `GetFcoOrderBookAsync(fcoId, pageIndex, pageSize)` | `FCOOrderBookResponse` |

### 5.5. Lệnh điều kiện (FCO)

Hỗ trợ các loại lệnh điều kiện linh hoạt (Flexible Conditional Order): GTD, Stop, Stop Limit, Trailing Stop, Trailing Stop Limit, OCO và Bull Bear. Lệnh gửi đi cũng được ký số tự động như lệnh thường.
```text
using SsiSdk;

string accountNo = "1234561";
string fromDate = "2026/07/21 00:00:00";
string toDate = "2026/07/28 23:00:00";

// Lệnh GTD (Good Till Date)
var gtd = await trading.Trading.PlaceFcoGtdAsync(
    accountNo, "SSI", OrderSide.Buy, 100, 25000, 0.5, fromDate, toDate);

// Lệnh Stop (dừng thị trường)
var stop = await trading.Trading.PlaceFcoStopAsync(
    accountNo, "SSI", OrderSide.Sell, 100, 24000, FCOOperator.LesserOrEqual, fromDate, toDate);

// Lệnh Stop Limit (dừng giới hạn)
var stopLimit = await trading.Trading.PlaceFcoStopLimitAsync(
    accountNo, "SSI", OrderSide.Buy, 100, 25500, 0.5, 25000, FCOOperator.GreaterOrEqual, fromDate, toDate);

// Lệnh Trailing Stop (bám sát xu hướng)
var trailing = await trading.Trading.PlaceFcoTrailingStopAsync(
    accountNo, "SSI", OrderSide.Buy, 100, 26000, 1000, fromDate, toDate);

// Lệnh Trailing Stop Limit
var trailingLimit = await trading.Trading.PlaceFcoTrailingStopLimitAsync(
    accountNo, "SSI", OrderSide.Buy, 100, 26000, 1000, 0.5, fromDate, toDate);

// Lệnh OCO (huỷ lệnh kia khi 1 trong 2 khớp)
var oco = await trading.Trading.PlaceFcoOcoAsync(
    accountNo, "SSI", OrderSide.Sell, 100, 30000, 24000, OrderType.MTL, OrderType.MTL, 0.5, 0.5, fromDate, toDate);

// Lệnh Bull Bear
var bullBear = await trading.Trading.PlaceFcoBullBearAsync(
    accountNo, "SSI", OrderSide.Buy, 1000, 100.5, 0.5, 30, 20, 30, 10, 0.1, 0, fromDate, toDate);

// Huỷ lệnh điều kiện
var cancelRes = await trading.Trading.CancelFcoAsync(gtd.FCOID);
```

**Trả về:** `FCOPlaceResponse` (`FCOID`) khi đặt lệnh, `FCOCancelResponse` (`FCOID`) khi huỷ lệnh.
```text
// Lấy toàn bộ lệnh FCO theo tài khoản
var fcos = await trading.Trading.GetFcoByAccountNoAsync("1234561");

// Lấy FCO theo mã chứng khoán
var fcosBySymbol = await trading.Trading.GetFcoBySymbolAsync("1234561", "SSI");

// Lấy FCO theo trạng thái xử lý
var fcosByStatus = await trading.Trading.GetFcoByStatusAsync("1234561", FCOStatus.Trit);

// Lấy FCO theo khoảng thời gian
var fcosByDate = await trading.Trading.GetFcoByDateAsync("1234561", "2026/07/01", "2026/07/21");

// Lấy một lệnh FCO cụ thể bằng ID
var fcoInfo = await trading.Trading.GetFcoByIdAsync("1234561", "fco-id-here");

// Lấy nhật ký khớp lệnh (order book) của lệnh FCO
var orderBook = await trading.Trading.GetFcoOrderBookAsync("fco-id-here");
```

> **Lưu ý:** Các method truy vấn danh sách hỗ trợ tham số tuỳ chọn `pageIndex` (mặc định `1`) và `pageSize` (mặc định `10`) để phân trang.

* * *

## 6\. Streaming realtime (StreamingService)

Truy cập qua `stream.Streaming`. Cần gọi `stream.ConnectAsync()` trước.

### 6.1. Kết nối
```text
using var stream = new StreamClient(auth);

await stream.ConnectAsync();       // Kết nối WebSocket

// Chờ vô thời hạn
await stream.WaitAsync();

// Chờ với timeout
await stream.WaitAsync(TimeSpan.FromSeconds(30));

stream.Disconnect();                // Ngắt kết nối thủ công (nếu không dùng using)
```

### 6.2. Thiết lập callback
```text
using SsiSdk.Models;

stream.Streaming.SetOnData(msg =>
{
    switch (msg)
    {
        case TradeMessage t: Console.WriteLine($"Trade: {t.Symbol} {t.Price}"); break;
        case QuoteMessage q: Console.WriteLine($"Quote: {q.Symbol}"); break;
    }
});

stream.Streaming.SetOnTrading(msg =>
{
    if (msg is OrderStatusMessage order)
        Console.WriteLine($"Order: {order.Symbol} {order.Status}");
});

stream.Streaming.SetOnHeartbeat(hb => Console.WriteLine($"Heartbeat: {hb.Status}"));
```

### 6.3. Subscribe dữ liệu thị trường
```text
// Từng kênh riêng
await stream.Streaming.SubscribeSymbolTradeAsync(["SSI", "HPG"]);
await stream.Streaming.SubscribeSymbolQuoteAsync(["SSI", "HPG"]);
await stream.Streaming.SubscribeSymbolRoomAsync(["SSI", "HPG"]);
await stream.Streaming.SubscribeSymbolPutThroughAsync(["SSI"]);
await stream.Streaming.SubscribeSymbolOddLotAsync(["SSI"]);

// Tất cả kênh (trade + quote + room) cho mã
await stream.Streaming.SubscribeSymbolAsync(["SSI", "HPG", "VIC"]);

// OHLCV theo interval
await stream.Streaming.SubscribeSymbolOhlcvAsync(["SSI"], Timeframe.Minute1);

// Theo sàn
await stream.Streaming.SubscribeBoardAsync([Board.HOSE, Board.HNX]);

// Theo chỉ số
await stream.Streaming.SubscribeIndexAsync(["VNINDEX", "VN30"]);
```

### 6.4. Unsubscribe
```text
await stream.Streaming.UnsubscribeSymbolTradeAsync(["SSI"]);
await stream.Streaming.UnsubscribeSymbolQuoteAsync(["SSI"]);
await stream.Streaming.UnsubscribeSymbolRoomAsync(["SSI"]);
await stream.Streaming.UnsubscribeSymbolPutThroughAsync(["SSI"]);
await stream.Streaming.UnsubscribeSymbolOddLotAsync(["SSI"]);
await stream.Streaming.UnsubscribeSymbolAsync(["SSI", "HPG"]);

// Huỷ OHLCV
await stream.Streaming.UnsubscribeSymbolOhlcvAsync(["SSI"], Timeframe.Minute1);

await stream.Streaming.UnsubscribeBoardAsync([Board.HOSE]);
await stream.Streaming.UnsubscribeIndexAsync(["VNINDEX"]);
```

### 6.5. Subscribe giao dịch
```text
// Trạng thái lệnh (tất cả tài khoản, mặc định "*")
await stream.Streaming.SubscribeOrderStatusAsync();

// Cho tài khoản cụ thể
await stream.Streaming.SubscribeOrderStatusAsync("1234561");

// Portfolio
await stream.Streaming.SubscribePortfolioAsync();
await stream.Streaming.SubscribePortfolioAsync("1234561");
```

### 6.6. Heartbeat
```text
// Ping một lần
await stream.Streaming.PingAsync();

// Ping tự động theo interval (giây)
await stream.Streaming.PingAsync(intervalSeconds: 30);

// Dừng ping loop tự động
stream.Streaming.StopPingLoop();
```

### Message types nhận qua `SetOnData`

| Topic | Message Type | Mô tả |
|---|---|---|
| `trade.*` | `TradeMessage` | Dữ liệu khớp lệnh |
| `trade.*.<timeframe>` | `IntervalMessage` | Dữ liệu OHLCV theo interval |
| `quote.*` | `QuoteMessage` | Dữ liệu giá (bid/ask) |
| `room.*` | `ForeignRoomMessage` | Room nước ngoài |
| `market.*` | `MarketStatusMessage` | Trạng thái thị trường |
| `put.*` | `PutMessage` | Thoả thuận |
| `oddlot.*` | `OddLotMessage` | Lô lẻ |

### Message types nhận qua `SetOnTrading`

| Topic | Message Type | Mô tả |
|---|---|---|
| `order.*` | `OrderStatusMessage` hoặc `FCOOrderUpdateMessage` (khi `eventType == "fcoEvent"`) | Trạng thái lệnh |
| `portfolio.*` | `PortfolioMessage` | Thay đổi danh mục |
| `fco_order.*` / `fco.*` | `FCOOrderUpdateMessage` | Trạng thái lệnh điều kiện (FCO) |

### Tổng quan method Streaming

| Nhóm | Method | Mô tả |
|---|---|---|
| **Kết nối** | `ConnectAsync()` | Kết nối WebSocket |
|  | `Disconnect()` | Ngắt kết nối |
|  | `WaitAsync(timeout?)` | Chờ nhận dữ liệu |
|  | `IsConnected` | Kiểm tra trạng thái kết nối |
| **Heartbeat** | `PingAsync(intervalSeconds?)` | Ping server (tuỳ chọn lặp) |
|  | `StopPingLoop()` | Dừng ping loop tự động |
| **Subscribe mã** | `SubscribeSymbolAsync(symbols)` | Trade + Quote + Room |
|  | `SubscribeSymbolTradeAsync(symbols)` | Chỉ trade |
|  | `SubscribeSymbolQuoteAsync(symbols)` | Chỉ quote |
|  | `SubscribeSymbolRoomAsync(symbols)` | Chỉ foreign room |
|  | `SubscribeSymbolPutThroughAsync(symbols)` | Chỉ thoả thuận |
|  | `SubscribeSymbolOddLotAsync(symbols)` | Chỉ lô lẻ |
|  | `SubscribeSymbolOhlcvAsync(symbols, interval)` | OHLCV theo timeframe |
| **Subscribe sàn/chỉ số** | `SubscribeBoardAsync(boards)` | Theo sàn |
|  | `SubscribeIndexAsync(indices)` | Theo chỉ số |
| **Subscribe giao dịch** | `SubscribeOrderStatusAsync(accountNo = "*")` | Trạng thái lệnh (bao gồm cả sự kiện FCO) |
|  | `SubscribeFcoOrderStatusAsync(accountNo = "*")` | Alias của `SubscribeOrderStatusAsync` |
|  | `SubscribePortfolioAsync(accountNo = "*")` | Portfolio changes |
| **Unsubscribe** | `UnsubscribeSymbolAsync(symbols)` | Huỷ tất cả kênh cho mã |
|  | `UnsubscribeSymbolTradeAsync(symbols)` | Huỷ trade |
|  | `UnsubscribeSymbolQuoteAsync(symbols)` | Huỷ quote |
|  | `UnsubscribeSymbolRoomAsync(symbols)` | Huỷ foreign room |
|  | `UnsubscribeSymbolPutThroughAsync(symbols)` | Huỷ thoả thuận |
|  | `UnsubscribeSymbolOddLotAsync(symbols)` | Huỷ lô lẻ |
|  | `UnsubscribeSymbolOhlcvAsync(symbols, interval)` | Huỷ OHLCV |
|  | `UnsubscribeBoardAsync(boards)` | Huỷ sàn |
|  | `UnsubscribeIndexAsync(indices)` | Huỷ chỉ số |
