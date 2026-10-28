<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/nodejs/service-classes
Tieu de goc: API Services
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/nodejs/service-classes>

# API Services

Chi tiết các method API cho mỗi service trong Node.js SDK

## 1\. Xác thực (Auth)

Truy cập trực tiếp trên `auth`.

### Xác thực với OTP
```javascript
const token = await auth.authenticate('222222');
console.log(`Access token: ${token.accessToken}`);
```

### Yêu cầu gửi OTP
```text
await auth.requestOtp();
```

### Làm mới token
```javascript
const token = await auth.refresh();
```

### Đảm bảo xác thực
```text
await auth.ensureAuthenticated('222222');
```

### Trạng thái token
```javascript
const token = auth.getToken();
auth.setToken(token);
```

* * *

## 2\. Tài khoản (AccountService)

Truy cập qua `trading.account`.

### Lấy danh sách tài khoản
```javascript
const accounts = await trading.account.getAccountInfo();

for (const acc of accounts) {
  console.log(`${acc.accountNo} (${acc.accountType})`);
}
```

**Trả về:** `Account[]` — mỗi `Account` có `accountNo: string`, `accountType: string`.

* * *

## 3\. Dữ liệu thị trường (MarketDataService)

Truy cập qua `data.marketData`. Không cần OTP.

### 3.1. Dữ liệu OHLC (nến)

**Trong ngày:**

| Method | Khung thời gian |
|---|---|
| `getOhlc1Minute(symbol)` | 1 phút |
| `getOhlc3Minute(symbol)` | 3 phút |
| `getOhlc5Minute(symbol)` | 5 phút |
| `getOhlc15Minute(symbol)` | 15 phút |
| `getOhlc1Hour(symbol)` | 1 giờ |
```javascript
const ohlc = await data.marketData.getOhlc1Minute('SSI');
for (const candle of ohlc) {
  console.log(`${candle.tradingDate}: O=${candle.openPrice} H=${candle.highPrice} L=${candle.lowPrice} C=${candle.closePrice} V=${candle.volume}`);
}
```

**Lịch sử (với khoảng ngày + phân trang):**

| Method | Khung thời gian |
|---|---|
| `getOhlc1MinuteHistorical(symbol, from, to, page?, size?)` | 1 phút |
| `getOhlc3MinuteHistorical(...)` | 3 phút |
| `getOhlc5MinuteHistorical(...)` | 5 phút |
| `getOhlc15MinuteHistorical(...)` | 15 phút |
| `getOhlc1HourHistorical(...)` | 1 giờ |
| `getOhlc1DayHistorical(...)` | 1 ngày |
| `getOhlc1WeekHistorical(...)` | 1 tuần |
| `getOhlc1MonthHistorical(...)` | 1 tháng |
```javascript
const ohlc = await data.marketData.getOhlc1DayHistorical(
  'SSI', '2026/03/27', '2026/04/22', 1, 100,
);
```

**Tham số lịch sử:**

| Tham số | Kiểu | Mặc định | Mô tả |
|---|---|---|---|
| `symbol` | `string` | _(bắt buộc)_ | Mã chứng khoán |
| `from` | `string` | _(bắt buộc)_ | Ngày bắt đầu (yyyy/MM/dd) |
| `to` | `string` | _(bắt buộc)_ | Ngày kết thúc (yyyy/MM/dd) |
| `page` | `number` | `1` | Số trang |
| `size` | `number` | `1000` | Số bản ghi mỗi trang |

**Trả về:** `OHLCData[]`

### 3.2. Chỉ số thị trường
```python
// Tất cả chỉ số
const indexes = await data.marketData.getIndexes();

// Theo sàn
import { Board } from '@ssi.developer/ssi-sdk';
const indexes = await data.marketData.getIndexesByBoard(Board.HOSE);

for (const idx of indexes) {
  console.log(`${idx.index} - ${idx.indexName}`);
}
```

**Trả về:** `MarketIndexes[]`

### 3.3. Tổng hợp chỉ số (Index Summary)
```javascript
// Tổng hợp hiện tại
const summary = await data.marketData.getIndexSummary('VNINDEX');

// Tổng hợp lịch sử
const summary = await data.marketData.getIndexSummaryHistorical('VNINDEX', '2026/01/15');

// Tổng hợp theo sàn
const summary = await data.marketData.getBoardSummary(Board.HOSE);

// Tổng hợp theo sàn lịch sử
const summary = await data.marketData.getBoardSummaryHistorical(Board.HOSE, '2026/01/15');
```

**Trả về:** `MarketIndexSummary`

### 3.4. Thông tin chứng khoán
```javascript
// Một mã
const info = await data.marketData.getSecuritiesInfo('SSI');

// Theo chỉ số
const securities = await data.marketData.getSecuritiesInfoByIndex('VN30');

// Theo sàn
const securities = await data.marketData.getSecuritiesInfoByBoard(Board.HOSE);
```

**Trả về:** `SecuritiesInfo`

### 3.5. Tổng hợp chứng khoán (Securities Summary)
```javascript
// Tổng hợp hiện tại
const summary = await data.marketData.getSecuritiesSummary('SSI');

// Tổng hợp lịch sử
const summary = await data.marketData.getSecuritiesSummaryHistorical(
  'SSI', '2026/03/01', '2026/03/31',
);

// Theo chỉ số
const summary = await data.marketData.getSecuritiesSummaryByIndex('VN30');

// Theo chỉ số lịch sử
const summary = await data.marketData.getSecuritiesSummaryByIndexHistorical(
  'VN30', '2026/03/01', '2026/03/31',
);
```

**Trả về:** `SecuritiesSummary[]`

* * *

## 4\. Danh mục (PortfolioService)

Truy cập qua `trading.portfolio`.

### 4.1. Số dư tài khoản
```javascript
// Số dư cổ phiếu
const balance = await trading.portfolio.getEquityBalance('1234561');

// Số dư phái sinh
const derBalance = await trading.portfolio.getDerivativeBalance('1234568');
```

### 4.2. Vị thế
```javascript
// Vị thế cổ phiếu
const positions = await trading.portfolio.getEquityPositions('1234561');
for (const pos of positions) {
  console.log(`${pos.symbol}: ${pos.quantity} cổ | Giá vốn: ${pos.costPrice}`);
}

// Tất cả vị thế phái sinh
const derPositions = await trading.portfolio.getDerivativePositions('1234568');

// Chỉ vị thế đang mở
const openPos = await trading.portfolio.getOpenDerivativePositions('1234568');

// Chỉ vị thế đã đóng
const closedPos = await trading.portfolio.getClosedDerivativePositions('1234568');
```

### 4.3. Sổ lệnh
```javascript
// Lệnh trong ngày
const orders = await trading.portfolio.getTodayOrders('1234561');
for (const order of orders) {
  console.log(`${order.orderId}: ${order.symbol} ${order.side} ${order.quantity}@${order.price} - ${order.status}`);
}

// Lệnh lịch sử
const orders = await trading.portfolio.getHistoricalOrders('1234561', '2026/01/01', '2026/01/31');
```

### 4.4. PPMMR
```javascript
// PPMMR cổ phiếu
const ppmmr = await trading.portfolio.getEquityPpmmr('1234561');

// PPMMR phái sinh
const derPPMMR = await trading.portfolio.getDerivativePpmmr('1234568');
```

### Tổng quan method Portfolio

| Nhóm | Method | Trả về |
|---|---|---|
| **Số dư** | `getEquityBalance(accountNo)` | `EquityAccountBalance` |
|  | `getDerivativeBalance(accountNo)` | `DerivativeAccountBalance` |
| **Vị thế** | `getEquityPositions(accountNo)` | `EquityPosition[]` |
|  | `getDerivativePositions(accountNo)` | `AllDerivativePosition` |
|  | `getOpenDerivativePositions(accountNo)` | `DerivativePosition[]` |
|  | `getClosedDerivativePositions(accountNo)` | `DerivativePosition[]` |
| **Sổ lệnh** | `getTodayOrders(accountNo)` | `Order[]` |
|  | `getHistoricalOrders(accountNo, from, to)` | `Order[]` |
| **PPMMR** | `getEquityPpmmr(accountNo)` | `EquityPPMMR` |
|  | `getDerivativePpmmr(accountNo)` | `DerivativePPMMR` |

* * *

## 5\. Giao dịch (TradingService)

Truy cập qua `trading.trading`.

### 5.1. Đặt lệnh
```python
import { OrderSide, OrderType } from '@ssi.developer/ssi-sdk';

// Lệnh giới hạn (LO)
const result = await trading.trading.placeLimitOrder('1234561', 'SSI', OrderSide.BUY, 100, 66000);

// Lệnh thị trường (MTL)
const result = await trading.trading.placeMarketOrder('1234561', 'SSI', OrderSide.BUY, 100);

// Lệnh ATO (mở cửa)
const result = await trading.trading.placeAtoOrder('1234561', 'SSI', OrderSide.BUY, 100);

// Lệnh ATC (đóng cửa)
const result = await trading.trading.placeAtcOrder('1234561', 'SSI', OrderSide.SELL, 100);

// Loại lệnh tuỳ chỉnh
const result = await trading.trading.placeOrder(
  '1234561', 'SSI', OrderSide.BUY, 100, 66000, OrderType.LO,
);

console.log(`Order ID: ${result.orderId}, Status: ${result.status}`);
```

### 5.2. Sửa lệnh

Chỉ có thể sửa **giá** hoặc **khối lượng** (không sửa cả hai cùng lúc).
```javascript
// Sửa giá theo clientRequestId
const result = await trading.trading.modifyOrderPrice('1234561', 'REQ123', 68000);

// Sửa giá theo orderId
const result = await trading.trading.modifyOrderPriceById('1234561', 'ORD123', 68000);

// Sửa khối lượng theo clientRequestId
const result = await trading.trading.modifyOrderQuantity('1234561', 'REQ123', 200);

// Sửa khối lượng theo orderId
const result = await trading.trading.modifyOrderQuantityById('1234561', 'ORD123', 200);
```

### 5.3. Huỷ lệnh
```javascript
// Huỷ theo clientRequestId
const result = await trading.trading.cancelOrder('1234561', 'REQ123');

// Huỷ theo orderId
const result = await trading.trading.cancelOrderById('1234561', 'ORD123');
```

### 5.4. Sức mua/bán tối đa
```javascript
// Với giá cụ thể
const maxBS = await trading.trading.getMaxBuySell('1234561', 'SSI', 66000);
console.log(`Max mua: ${maxBS.maxBuyQuantity}, Max bán: ${maxBS.maxSellQuantity}`);

// Theo giá thị trường
const maxBS = await trading.trading.getMaxBuySellAtMarketPrice('1234561', 'SSI');
```

### 5.5. Lệnh điều kiện (Flexible Conditional Orders - FCO)

SDK hỗ trợ 7 loại lệnh điều kiện linh hoạt FCO (GTD, Stop, Stop Limit, Trailing Stop, Trailing Stop Limit, OCO, Bull Bear), tra cứu danh sách lệnh FCO, nhật ký sổ lệnh FCO và hủy lệnh FCO.
```python
import { FCOOperator, OrderSide, OrderType, fromBeginningOfDay, fromEndOfDay } from '@ssi.developer/ssi-sdk';

const fromDate = fromBeginningOfDay(); // "YYYY/MM/DD 00:00:00"
const toDate = fromEndOfDay();         // "YYYY/MM/DD 23:59:59"

// Lệnh GTD (Good Till Date)
const gtd = await trading.trading.placeFcoGtd(
  '1234561', 'SSI', OrderSide.BUY, 100, 25000, 500, fromDate, toDate,
);
console.log(`FCO ID: ${gtd.fcoId}`);

// Lệnh Stop Market
const stop = await trading.trading.placeFcoStop(
  '1234561', 'SSI', OrderSide.SELL, 100, 24000, FCOOperator.LESSER_OR_EQUAL, fromDate, toDate,
);

// Lệnh Stop Limit
const stopLimit = await trading.trading.placeFcoStopLimit(
  '1234561', 'SSI', OrderSide.BUY, 100, 25500, 500, 25000, FCOOperator.GREATER_OR_EQUAL, fromDate, toDate,
);

// Lệnh Trailing Stop
const trailing = await trading.trading.placeFcoTrailingStop(
  '1234561', 'SSI', OrderSide.BUY, 100, 26000, 1000, fromDate, toDate,
);

// Lệnh OCO (One-Cancels-the-Other)
const oco = await trading.trading.placeFcoOco(
  '1234561', 'SSI', OrderSide.SELL, 100, 30000, 24000, OrderType.MTL, OrderType.MTL, 500, 500, fromDate, toDate,
);

// Tra cứu danh sách lệnh FCO theo tài khoản
const fcoList = await trading.trading.getFcoByAccountNo('1234561', 1, 10);
console.log(`FCO items: ${fcoList.fcoList.length}`);

// Huỷ lệnh FCO
await trading.trading.cancelFco(gtd.fcoId);
```

| Method | Mô tả |
|---|---|
| `placeFcoGtd(accountNo, symbol, side, quantity, price, priceSlip, fromDate, toDate)` | Đặt lệnh GTD (Good Till Date) |
| `placeFcoStop(accountNo, symbol, side, quantity, stopPrice, operator, fromDate, toDate)` | Đặt lệnh Stop Market |
| `placeFcoStopLimit(accountNo, symbol, side, quantity, price, priceSlip, stopPrice, operator, fromDate, toDate)` | Đặt lệnh Stop Limit |
| `placeFcoTrailingStop(accountNo, symbol, side, quantity, activePrice, trailingAmount, fromDate, toDate)` | Đặt lệnh Trailing Stop Market |
| `placeFcoTrailingStopLimit(accountNo, symbol, side, quantity, activePrice, trailingAmount, priceSlip, fromDate, toDate)` | Đặt lệnh Trailing Stop Limit |
| `placeFcoOco(accountNo, symbol, side, quantity, tpActivePrice, slActivePrice, tpPrice, slPrice, tpSlip, slSlip, fromDate, toDate)` | Đặt lệnh OCO (One Cancels the Other) |
| `placeFcoBullBear(accountNo, symbol, side, quantity, price, priceSlip, tpActivePrice, slActivePrice, tpPrice, slPrice, tpSlip, slSlip, fromDate, toDate)` | Đặt lệnh Bull Bear |
| `cancelFco(fcoId)` | Hủy lệnh FCO theo `fcoId` |
| `getFcoByAccountNo(accountNo, pageIndex?, pageSize?)` | Tra cứu danh sách FCO theo tài khoản |
| `getFcoBySymbol(accountNo, symbol, pageIndex?, pageSize?)` | Tra cứu FCO lọc theo mã chứng khoán |
| `getFcoByStatus(accountNo, processStatus, pageIndex?, pageSize?)` | Tra cứu FCO lọc theo trạng thái |
| `getFcoByDate(accountNo, fromDate, toDate, pageIndex?, pageSize?)` | Tra cứu FCO lọc theo khoảng ngày |
| `getFcoById(accountNo, fcoId)` | Lấy thông tin 1 lệnh FCO theo ID |
| `getFcoOrderBook(fcoId, pageIndex?, pageSize?)` | Lấy lịch sử thực thi (Order Book) của FCO |

### Tổng quan method Trading

| Nhóm | Method | Trả về |
|---|---|---|
| **Đặt lệnh** | `placeOrder(accountNo, symbol, side, qty, price, orderType)` | `PlaceOrderResponse` |
|  | `placeLimitOrder(accountNo, symbol, side, qty, price)` | `PlaceOrderResponse` |
|  | `placeMarketOrder(accountNo, symbol, side, qty)` | `PlaceOrderResponse` |
|  | `placeAtoOrder(accountNo, symbol, side, qty)` | `PlaceOrderResponse` |
|  | `placeAtcOrder(accountNo, symbol, side, qty)` | `PlaceOrderResponse` |
| **Sửa lệnh** | `modifyOrderPrice(accountNo, clientRequestId, price)` | `ModifyOrderResponse` |
|  | `modifyOrderPriceById(accountNo, orderId, price)` | `ModifyOrderResponse` |
|  | `modifyOrderQuantity(accountNo, clientRequestId, qty)` | `ModifyOrderResponse` |
|  | `modifyOrderQuantityById(accountNo, orderId, qty)` | `ModifyOrderResponse` |
| **Huỷ lệnh** | `cancelOrder(accountNo, clientRequestId)` | `CancelOrderResponse` |
|  | `cancelOrderById(accountNo, orderId)` | `CancelOrderResponse` |
| **Sức mua/bán** | `getMaxBuySell(accountNo, symbol, price)` | `MaxBuySellResponse` |
|  | `getMaxBuySellAtMarketPrice(accountNo, symbol)` | `MaxBuySellResponse` |
| **Lệnh điều kiện** | `placeFcoGtd(...)` | `FCOPlaceResponse` |
|  | `placeFcoStop(...)` / `placeFcoStopLimit(...)` | `FCOPlaceResponse` |
|  | `placeFcoTrailingStop(...)` / `placeFcoTrailingStopLimit(...)` | `FCOPlaceResponse` |
|  | `placeFcoOco(...)` / `placeFcoBullBear(...)` | `FCOPlaceResponse` |
|  | `cancelFco(fcoId)` | `FCOCancelResponse` |
|  | `getFcoByAccountNo(...)` / `getFcoBySymbol(...)` / `getFcoByStatus(...)` / `getFcoByDate(...)` | `FCOListResponse` |
|  | `getFcoById(accountNo, fcoId)` | `FCOInfo \| null` |
|  | `getFcoOrderBook(fcoId, pageIndex?, pageSize?)` | `FCOOrderBookResponse` |

* * *

## 6\. Streaming Realtime (StreamingService)

Truy cập qua `stream.streaming`. Gọi `await stream.streaming.connect()` trước.

### 6.1. Kết nối
```javascript
const stream = new Stream(auth);

await stream.streaming.connect();

// Chờ vô thời hạn
await stream.streaming.wait();
```

### 6.2. Thiết lập Callbacks
```javascript
stream.streaming.onData = (msg) => {
  console.log('[DATA]', msg);
};

stream.streaming.onTrading = (msg) => {
  console.log('[TRADING]', msg);
};

stream.streaming.onHeartbeat = (msg) => {
  console.log('[HEARTBEAT]', msg);
};
```

### 6.3. Subscribe dữ liệu thị trường
```python
import { Board, Timeframe } from '@ssi.developer/ssi-sdk';

// Tất cả kênh (trade + quote + room) cho mã
stream.streaming.subscribeSymbol(['SSI', 'HPG', 'VIC']);

// Kênh riêng lẻ
stream.streaming.subscribeSymbolTrade(['SSI', 'HPG']);
stream.streaming.subscribeSymbolQuote(['SSI', 'HPG']);
stream.streaming.subscribeSymbolRoom(['SSI', 'HPG']);
stream.streaming.subscribeSymbolPutThrough(['SSI']);
stream.streaming.subscribeSymbolOddLot(['SSI']);

// OHLCV theo timeframe
stream.streaming.subscribeSymbolOhlcv(['SSI'], Timeframe.MINUTE_1);

// Theo sàn
stream.streaming.subscribeBoard([Board.HOSE, Board.HNX]);

// Theo chỉ số
stream.streaming.subscribeIndex(['VNINDEX', 'VN30']);
```

### 6.4. Unsubscribe
```text
stream.streaming.unsubscribeSymbol(['SSI', 'HPG']);
stream.streaming.unsubscribeSymbolTrade(['SSI']);
stream.streaming.unsubscribeSymbolQuote(['SSI']);
stream.streaming.unsubscribeSymbolRoom(['SSI']);
stream.streaming.unsubscribeSymbolPutThrough(['SSI']);
stream.streaming.unsubscribeSymbolOddLot(['SSI']);
stream.streaming.unsubscribeSymbolOhlcv(['SSI'], Timeframe.MINUTE_1);
stream.streaming.unsubscribeBoard([Board.HOSE]);
stream.streaming.unsubscribeIndex(['VNINDEX']);
```

### 6.5. Subscribe sự kiện giao dịch
```text
// Trạng thái lệnh (thường + FCO) — tất cả tài khoản
stream.streaming.subscribeOrderStatus();

// Cho tài khoản cụ thể
stream.streaming.subscribeOrderStatus('1234561');

// Alias cho subscribeOrderStatus — cùng kênh, dùng khi chỉ quan tâm lệnh điều kiện FCO
stream.streaming.subscribeFcoOrderStatus('1234561');

// Danh mục — tất cả tài khoản
stream.streaming.subscribePortfolio();

// Cho tài khoản cụ thể
stream.streaming.subscribePortfolio('1234561');
```

Kênh `order.*` trả về cả `OrderStatusMessage` (lệnh thường) lẫn `FCOOrderUpdateMessage` (lệnh điều kiện FCO) qua callback `onTrading` — phân biệt bằng trường `type` (`orderEvent` vs `fcoOrderEvent`).

### 6.6. Heartbeat
```text
stream.streaming.ping();
```

### Tổng quan method Streaming

| Nhóm | Method | Mô tả |
|---|---|---|
| **Kết nối** | `connect()` | Kết nối WebSocket |
|  | `disconnect()` | Ngắt kết nối |
|  | `wait()` | Chờ dữ liệu |
| **Heartbeat** | `ping(onResponse?, intervalMs?)` | Ping server (tuỳ chọn lặp) |
| **Symbol** | `subscribeSymbol(symbols, onResponse?)` | Trade + Quote + Room |
|  | `subscribeSymbolTrade(symbols, onResponse?)` | Chỉ Trade |
|  | `subscribeSymbolQuote(symbols, onResponse?)` | Chỉ Quote |
|  | `subscribeSymbolRoom(symbols, onResponse?)` | Chỉ Room ngoại |
|  | `subscribeSymbolPutThrough(symbols, onResponse?)` | Chỉ thoả thuận |
|  | `subscribeSymbolOddLot(symbols, onResponse?)` | Chỉ lô lẻ |
|  | `subscribeSymbolOhlcv(symbols, interval, onResponse?)` | OHLCV theo timeframe |
| **Sàn/Chỉ số** | `subscribeBoard(boards, onResponse?)` | Theo sàn |
|  | `subscribeIndex(indices, onResponse?)` | Theo chỉ số |
| **Giao dịch** | `subscribeOrderStatus(accountNo?, onResponse?)` | Trạng thái lệnh (thường + FCO) |
|  | `subscribeFcoOrderStatus(accountNo?, onResponse?)` | Alias cho `subscribeOrderStatus` |
|  | `subscribePortfolio(accountNo?, onResponse?)` | Thay đổi danh mục |
| **Unsubscribe** | `unsubscribeSymbol(symbols)` | Huỷ tất cả kênh |
|  | `unsubscribeSymbolTrade(symbols)` | Huỷ trade |
|  | `unsubscribeSymbolQuote(symbols)` | Huỷ quote |
|  | `unsubscribeSymbolRoom(symbols)` | Huỷ room |
|  | `unsubscribeSymbolPutThrough(symbols)` | Huỷ thoả thuận |
|  | `unsubscribeSymbolOddLot(symbols)` | Huỷ lô lẻ |
|  | `unsubscribeSymbolOhlcv(symbols, interval)` | Huỷ OHLCV |
|  | `unsubscribeBoard(boards)` | Huỷ sàn |
|  | `unsubscribeIndex(indices)` | Huỷ chỉ số |
