<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/python/service-classes
Tieu de goc: API Services
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/python/service-classes>

# API Services

Chi tiết các method API cho từng service trong Python SDK

## 1\. Xác thực (TokenManager)

Truy cập qua `auth.token_manager` hoặc trực tiếp trên `auth` (delegate).

### Xác thực với OTP
```python
token = auth.authenticate(otp="222222")
print(f"Access token: {token.access_token}")
print(f"Expires at: {token.expires_at}")
```

### Yêu cầu gửi OTP
```text
result = auth.request_otp()
```

### Làm mới token
```text
token = auth.refresh()
```

### Tự động đảm bảo xác thực
```text
access_token = auth.ensure_authenticated(otp="222222")
```

* * *

## 2\. Tài khoản (AccountService)

Truy cập qua `trading.account`.

### Lấy danh sách tài khoản
```python
accounts = trading.account.get_account_info()

for acc in accounts:
    print(f"{acc.account_no} - {acc.account_type}")
```

**Trả về:** `list[Account]` — mỗi `Account` có `account_no: str`, `account_type: AccountType`.

* * *

## 3\. Dữ liệu thị trường (MarketDataService)

Truy cập qua `data.market_data`. Không cần OTP.

### 3.1. Dữ liệu OHLC (nến)

**Trong ngày:**

| Method | Timeframe |
|---|---|
| `get_ohlc_1minute(symbol)` | 1 phút |
| `get_ohlc_3minute(symbol)` | 3 phút |
| `get_ohlc_5minute(symbol)` | 5 phút |
| `get_ohlc_15minute(symbol)` | 15 phút |
| `get_ohlc_1hour(symbol)` | 1 giờ |
```python
ohlc = data.market_data.get_ohlc_1minute("SSI")
for candle in ohlc:
    print(f"{candle.trading_date}: O={candle.open_price} H={candle.high_price} L={candle.low_price} C={candle.close_price} V={candle.volume}")
```

**Lịch sử (truyền khoảng ngày + phân trang):**

| Method | Timeframe |
|---|---|
| `get_ohlc_1minute_historical(symbol, from_date, to_date, page, size)` | 1 phút |
| `get_ohlc_3minute_historical(...)` | 3 phút |
| `get_ohlc_5minute_historical(...)` | 5 phút |
| `get_ohlc_15minute_historical(...)` | 15 phút |
| `get_ohlc_1hour_historical(...)` | 1 giờ |
| `get_ohlc_1day_historical(...)` | 1 ngày |
| `get_ohlc_1week_historical(...)` | 1 tuần |
| `get_ohlc_1month_historical(...)` | 1 tháng |
```text
ohlc = data.market_data.get_ohlc_1day_historical(
    symbol="SSI",
    from_date="2026/03/27 00:00:00",
    to_date="2026/03/27 00:00:00",
    page=1,
    size=100,
)
```

**Tham số historical:**

| Tham số | Kiểu | Mặc định | Mô tả |
|---|---|---|---|
| `symbol` | `str` | _(bắt buộc)_ | Mã chứng khoán |
| `from_date` | `str` | _(bắt buộc)_ | Ngày bắt đầu |
| `to_date` | `str` | _(bắt buộc)_ | Ngày kết thúc |
| `page` | `int` | `1` | Trang |
| `size` | `int` | `1000` | Số bản ghi/trang |

**Trả về:** `list[OHLCData]`

### 3.2. Danh sách chỉ số thị trường
```python
# Tất cả chỉ số
indices = data.market_data.get_indexes()

# Theo sàn
from ssi_sdk.enums import Board
indices = data.market_data.get_indexes_by_board(Board.HOSE)

for idx in indices:
    print(f"{idx.index} - {idx.index_name}")
```

**Trả về:** `list[MarketIndexes]`

### 3.3. Tổng hợp chỉ số (Index Summary)
```text
# Summary hiện tại
summary = data.market_data.get_index_summary("VNINDEX")

# Summary lịch sử
summary = data.market_data.get_index_summary_historical("VNINDEX", "2025/01/15")

# Summary theo sàn
summary = data.market_data.get_board_summary(Board.HOSE)

# Summary sàn lịch sử
summary = data.market_data.get_board_summary_historical(Board.HOSE, "2025/01/15")
```

**Trả về:** `MarketIndexSummary`

### 3.4. Thông tin chứng khoán
```text
# 1 mã
info = data.market_data.get_securities_info("SSI")

# Theo chỉ số
securities = data.market_data.get_securities_info_by_index("VN30")

# Theo sàn
securities = data.market_data.get_securities_info_by_board(Board.HOSE)
```

**Trả về:** `SecuritiesInfo`

### 3.5. Tổng hợp chứng khoán (Securities Summary)
```text
# Summary hiện tại
summary = data.market_data.get_securities_summary("SSI")

# Summary lịch sử
summary = data.market_data.get_securities_summary_historical(
    symbol="SSI",
    from_date="2025/01/01",
    to_date="2025/01/31",
)

# Summary theo chỉ số
summary = data.market_data.get_securities_summary_by_index("VN30")

# Summary theo chỉ số lịch sử
summary = data.market_data.get_securities_summary_by_index_historical(
    index="VN30",
    from_date="2025/01/01",
    to_date="2025/01/31",
)
```

**Trả về:** `list[SecuritiesSummary]`

* * *

## 4\. Danh mục đầu tư (PortfolioService)

Truy cập qua `trading.portfolio`.

### 4.1. Số dư tài khoản
```python
# Số dư cơ sở
equity_balance = trading.portfolio.get_equity_balance("1234561")
print(f"Account balance: {equity_balance.account_balance}")

# Số dư phái sinh
derivative_balance = trading.portfolio.get_derivative_balance("1234568")
print(f"Withdrawable: {derivative_balance.withdrawable}")
```

### 4.2. Vị thế (Positions)
```python
# Vị thế cơ sở
positions = trading.portfolio.get_equity_positions("1234561")
for pos in positions:
    print(f"{pos.symbol}: {pos.quantity} cp | Giá vốn: {pos.cost_price}")

# Vị thế phái sinh (tất cả)
derivative_positions = trading.portfolio.get_derivative_positions("1234568")

# Chỉ vị thế mở phái sinh
open_pos = trading.portfolio.get_open_derivative_positions("1234568")

# Chỉ vị thế đóng phái sinh
closed_pos = trading.portfolio.get_closed_derivative_positions("1234568")
```

### 4.3. Sổ lệnh (Order Book)
```python
# Lệnh trong ngày
today_orders = trading.portfolio.get_today_orders("1234561")
for order in today_orders:
    print(f"{order.order_id}: {order.symbol} {order.side} {order.quantity}@{order.price} - {order.status}")

# Lệnh lịch sử
historical_orders = trading.portfolio.get_historical_orders(
    "1234561",
    from_date="2025/01/01",
    to_date="2025/01/31",
)
```

### 4.4. PPMMR
```python
# PPMMR cơ sở
equity_ppmmr = trading.portfolio.get_equity_ppmmr("1234561")
print(f"Purchasing power: {equity_ppmmr.purchasing_power}")

# PPMMR phái sinh
derivative_ppmmr = trading.portfolio.get_derivative_ppmmr("1234568")
```

### Tổng quan method Portfolio

| Nhóm | Method | Trả về |
|---|---|---|
| **Số dư** | `get_equity_balance(account_no)` | `EquityAccountBalance` |
|  | `get_derivative_balance(account_no)` | `DerivativeAccountBalance` |
| **Vị thế** | `get_equity_positions(account_no)` | `list[EquityPosition]` |
|  | `get_derivative_positions(account_no)` | `list[AllDerivativePosition]` |
|  | `get_open_derivative_positions(account_no)` | `list[DerivativePosition]` |
|  | `get_closed_derivative_positions(account_no)` | `list[DerivativePosition]` |
| **Sổ lệnh** | `get_today_orders(account_no)` | `list[Order]` |
|  | `get_historical_orders(account_no, from_date, to_date)` | `list[Order]` |
| **PPMMR** | `get_equity_ppmmr(account_no)` | `EquityPPMMR` |
|  | `get_derivative_ppmmr(account_no)` | `DerivativePPMMR` |

* * *

## 5\. Giao dịch (TradingService)

Truy cập qua `trading.trading`.

### 5.1. Đặt lệnh
```python
from ssi_sdk.enums import OrderSide, OrderType

# Lệnh giới hạn (LO)
result = trading.trading.place_limit_order(
    account_no="1234561",
    symbol="SSI",
    side=OrderSide.BUY,
    quantity=100,
    price=66000,
)
print(f"Order ID: {result.order_id}, Status: {result.status}")

# Lệnh thị trường (MTL)
result = trading.trading.place_market_order(
    account_no="1234561", symbol="SSI", side=OrderSide.BUY, quantity=100,
)

# Lệnh ATO (mở cửa)
result = trading.trading.place_ato_order(
    account_no="1234561", symbol="SSI", side=OrderSide.BUY, quantity=100,
)

# Lệnh ATC (đóng cửa)
result = trading.trading.place_atc_order(
    account_no="1234561", symbol="SSI", side=OrderSide.SELL, quantity=100,
)

# Lệnh tuỳ chỉnh
result = trading.trading.place_order(
    account_no="1234561", symbol="SSI", side=OrderSide.BUY,
    quantity=100, price=66000, order_type=OrderType.LO,
)
```

### 5.2. Sửa lệnh

Chỉ sửa **giá** hoặc **số lượng** (không đồng thời).
```text
# Sửa giá theo client_request_id
result = trading.trading.modify_order_price(
    account_no="1234561", client_request_id="REQ123", price=68000,
)

# Sửa giá theo order_id
result = trading.trading.modify_order_price_by_order_id(
    account_no="1234561", order_id="ORD123", price=68000,
)

# Sửa số lượng theo client_request_id
result = trading.trading.modify_order_quantity(
    account_no="1234561", client_request_id="REQ123", quantity=200,
)

# Sửa số lượng theo order_id
result = trading.trading.modify_order_quantity_by_order_id(
    account_no="1234561", order_id="ORD123", quantity=200,
)
```

### 5.3. Huỷ lệnh
```text
# Huỷ theo client_request_id
result = trading.trading.cancel_order(
    account_no="1234561", client_request_id="REQ123",
)

# Huỷ theo order_id
result = trading.trading.cancel_order_by_order_id(
    account_no="1234561", order_id="ORD123",
)
```

### 5.4. Sức mua/bán tối đa
```python
# Với giá cụ thể
max_bs = trading.trading.get_max_buy_sell(
    account_no="1234561", symbol="SSI", price=66000,
)
print(f"Max buy: {max_bs.max_buy_quantity}")
print(f"Max sell: {max_bs.max_sell_quantity}")

# Với giá thị trường
max_bs = trading.trading.get_max_buy_sell_at_market_price(
    account_no="1234561", symbol="SSI",
)
```

### Tổng quan method Trading

| Nhóm | Method | Trả về |
|---|---|---|
| **Đặt lệnh** | `place_order(account_no, symbol, side, quantity, price, order_type)` | `PlaceOrderResponse` |
|  | `place_limit_order(account_no, symbol, side, quantity, price)` | `PlaceOrderResponse` |
|  | `place_market_order(account_no, symbol, side, quantity)` | `PlaceOrderResponse` |
|  | `place_ato_order(account_no, symbol, side, quantity)` | `PlaceOrderResponse` |
|  | `place_atc_order(account_no, symbol, side, quantity)` | `PlaceOrderResponse` |
| **Sửa lệnh** | `modify_order_price(account_no, client_request_id, price)` | `ModifyOrderResponse` |
|  | `modify_order_price_by_order_id(account_no, order_id, price)` | `ModifyOrderResponse` |
|  | `modify_order_quantity(account_no, client_request_id, quantity)` | `ModifyOrderResponse` |
|  | `modify_order_quantity_by_order_id(account_no, order_id, quantity)` | `ModifyOrderResponse` |
| **Huỷ lệnh** | `cancel_order(account_no, client_request_id)` | `CancelOrderResponse` |
|  | `cancel_order_by_order_id(account_no, order_id)` | `CancelOrderResponse` |
| **Sức mua/bán** | `get_max_buy_sell(account_no, symbol, price)` | `MaxBuySellResponse` |
|  | `get_max_buy_sell_at_market_price(account_no, symbol)` | `MaxBuySellResponse` |
| **Lệnh điều kiện** | `place_fco_gtd(account_no, symbol, side, quantity, price, price_slip, from_date, to_date)` | `FCOPlaceResponse` |
|  | `place_fco_stop(account_no, symbol, side, quantity, stop_price, operator, from_date, to_date)` | `FCOPlaceResponse` |
|  | `place_fco_stop_limit(account_no, symbol, side, quantity, price, price_slip, stop_price, operator, from_date, to_date)` | `FCOPlaceResponse` |
|  | `place_fco_trailing_stop(account_no, symbol, side, quantity, active_price, trailing_amount, from_date, to_date)` | `FCOPlaceResponse` |
|  | `place_fco_trailing_stop_limit(account_no, symbol, side, quantity, active_price, trailing_amount, price_slip, from_date, to_date)` | `FCOPlaceResponse` |
|  | `place_fco_oco(account_no, symbol, side, quantity, tp_active_price, sl_active_price, tp_price, sl_price, tp_slip, sl_slip, from_date, to_date)` | `FCOPlaceResponse` |
|  | `place_fco_bull_bear(account_no, symbol, side, quantity, price, price_slip, tp_active_price, sl_active_price, tp_price, sl_price, tp_slip, sl_slip, from_date, to_date)` | `FCOPlaceResponse` |
|  | `cancel_fco(fco_id)` | `FCOCancelResponse` |
|  | `get_fco_by_account_no(account_no, page_index, page_size)` | `FCOListResponse` |
|  | `get_fco_by_symbol(account_no, symbol, page_index, page_size)` | `FCOListResponse` |
|  | `get_fco_by_status(account_no, process_status, page_index, page_size)` | `FCOListResponse` |
|  | `get_fco_by_date(account_no, from_date, to_date, page_index, page_size)` | `FCOListResponse` |
|  | `get_fco_by_id(account_no, fco_id)` | `FCOInfo \| None` |
|  | `get_fco_order_book(fco_id, page_index, page_size)` | `FCOOrderBookResponse` |

### 5.5. Giao dịch điều kiện (FCO)

Hỗ trợ các loại lệnh điều kiện linh hoạt (Flexible Conditional Order): GTD, Stop, Stop Limit, Trailing Stop, Trailing Stop Limit, OCO, và Bull Bear. Cả `Trading` (sync) và `AsyncTrading` (async) đều hỗ trợ đầy đủ các method này.
```python
from ssi_sdk.enums import OrderSide, OrderType, FCOOperator

# Lệnh GTD (Good Till Date)
gtd_res = trading.trading.place_fco_gtd(
    account_no="1234561",
    symbol="SSI",
    side=OrderSide.BUY,
    quantity=100,
    price=OrderType.MTL,        # Hoặc giá số cụ thể
    price_slip=0.5,
    from_date="2026/07/21 00:00:00",
    to_date="2026/07/28 23:00:00",
)

# Lệnh Stop (dừng thị trường)
stop_res = trading.trading.place_fco_stop(
    account_no="1234561",
    symbol="SSI",
    side=OrderSide.BUY,
    quantity=100,
    stop_price=20000,
    operator=FCOOperator.GREATER_OR_EQUAL,
    from_date="2026/07/21 00:00:00",
    to_date="2026/07/28 23:00:00",
)

# Lệnh Stop Limit (dừng giới hạn)
stop_limit_res = trading.trading.place_fco_stop_limit(
    account_no="1234561",
    symbol="SSI",
    side=OrderSide.BUY,
    quantity=100,
    stop_price=20000,
    price=20500,
    price_slip=0.5,
    operator=FCOOperator.GREATER_OR_EQUAL,
    from_date="2026/07/21 00:00:00",
    to_date="2026/07/28 23:00:00",
)

# Lệnh Trailing Stop (bám sát xu hướng)
ts_res = trading.trading.place_fco_trailing_stop(
    account_no="1234561",
    symbol="SSI",
    side=OrderSide.BUY,
    quantity=100,
    active_price=20000,
    trailing_amount=1000,
    from_date="2026/07/21 00:00:00",
    to_date="2026/07/28 23:00:00",
)

# Lệnh OCO (huỷ lệnh kia khi 1 trong 2 khớp)
oco_res = trading.trading.place_fco_oco(
    account_no="1234561",
    symbol="SSI",
    side=OrderSide.BUY,
    quantity=100,
    tp_active_price=30000,      # Giá kích hoạt chốt lời
    sl_active_price=20000,      # Giá kích hoạt cắt lỗ
    tp_price=OrderType.MP,
    sl_price=OrderType.MP,
    tp_slip=0.1,
    sl_slip=0,
    from_date="2026/07/21 00:00:00",
    to_date="2026/07/28 23:00:00",
)

# Huỷ lệnh điều kiện
cancel_res = trading.trading.cancel_fco(fco_id="d346f2be-e33b-42f4-afb8-270a70db8216")

# Bất đồng bộ: cú pháp await tương tự trên trading từ AsyncTrading
gtd_res = await trading.trading.place_fco_gtd(
    account_no="1234561", symbol="SSI", side=OrderSide.BUY, quantity=100,
    price=OrderType.MTL, price_slip=0.5,
    from_date="2026/07/21 00:00:00", to_date="2026/07/28 23:00:00",
)
```

**Trả về:** `FCOPlaceResponse` (`fco_id`) khi đặt lệnh, `FCOCancelResponse` (`fco_id`) khi huỷ lệnh.
```text
# Lấy toàn bộ lệnh FCO theo tài khoản
fcos = trading.trading.get_fco_by_account_no(account_no="1234561")

# Lấy FCO theo mã chứng khoán
fcos_symbol = trading.trading.get_fco_by_symbol(account_no="1234561", symbol="SSI")

# Lấy FCO theo trạng thái xử lý
fcos_status = trading.trading.get_fco_by_status(account_no="1234561", process_status="TRIT")

# Lấy FCO theo khoảng thời gian
fcos_date = trading.trading.get_fco_by_date(account_no="1234561", from_date="2026/07/01", to_date="2026/07/21")

# Lấy một lệnh FCO cụ thể bằng ID
fco_info = trading.trading.get_fco_by_id(account_no="1234561", fco_id="fco-id-here")

# Lấy nhật ký khớp lệnh (order book) của lệnh FCO
order_book = trading.trading.get_fco_order_book(fco_id="fco-id-here")
```

> **Lưu ý:** Các method truy vấn danh sách hỗ trợ tham số tuỳ chọn `page_index` và `page_size` để phân trang, và đều gọi được bất đồng bộ với `await`.

* * *

## 6\. Streaming realtime (StreamingService)

Truy cập qua `stream.streaming`. Cần gọi `connect()` trước.

### 6.1. Kết nối
```text
stream.streaming.connect()       # Kết nối WebSocket
stream.streaming.disconnect()    # Ngắt kết nối
stream.streaming.wait(timeout=None)  # Chờ nhận dữ liệu (block)
```

### 6.2. Thiết lập callback
```python
def on_market_data(msg):
    print(f"Market data: {msg}")

def on_trading_data(msg):
    print(f"Trading: {msg}")

def on_heartbeat(msg):
    print(f"Heartbeat: {msg.status}")

stream.streaming.on_data = on_market_data
stream.streaming.on_trading = on_trading_data
stream.streaming.on_heartbeat = on_heartbeat
```

### 6.3. Subscribe dữ liệu thị trường
```python
# Tất cả kênh (trade + quote + room) cho mã
stream.streaming.subscribe_symbol(["SSI", "HPG", "VIC"])

# Từng kênh riêng
stream.streaming.subscribe_symbol_trade(["SSI", "HPG"])
stream.streaming.subscribe_symbol_quote(["SSI", "HPG"])
stream.streaming.subscribe_symbol_room(["SSI", "HPG"])
stream.streaming.subscribe_symbol_put_through(["SSI"])
stream.streaming.subscribe_symbol_odd_lot(["SSI"])

# OHLCV theo interval
from ssi_sdk.enums import Timeframe
stream.streaming.subscribe_symbol_ohlcv(["SSI"], interval=Timeframe.MINUTE_1)

# Theo sàn
from ssi_sdk.enums import Board
stream.streaming.subscribe_board([Board.HOSE, Board.HNX])

# Theo chỉ số
stream.streaming.subscribe_index(["VNINDEX", "VN30"])
```

### 6.4. Unsubscribe
```text
stream.streaming.unsubscribe_symbol(["SSI", "HPG"])
stream.streaming.unsubscribe_symbol_trade(["SSI"])
stream.streaming.unsubscribe_symbol_quote(["SSI"])
stream.streaming.unsubscribe_symbol_room(["SSI"])
stream.streaming.unsubscribe_symbol_put_through(["SSI"])
stream.streaming.unsubscribe_symbol_odd_lot(["SSI"])

# Huỷ OHLCV
stream.streaming.unsubscribe_symbol_ohlcv(["SSI"], interval=Timeframe.MINUTE_1)

stream.streaming.unsubscribe_board([Board.HOSE])
stream.streaming.unsubscribe_index(["VNINDEX"])
```

### 6.5. Subscribe giao dịch
```text
# Trạng thái lệnh (tất cả tài khoản)
stream.streaming.subscribe_order_status()

# Cho tài khoản cụ thể
stream.streaming.subscribe_order_status(account_no="1234561")

# Portfolio
stream.streaming.subscribe_portfolio()
stream.streaming.subscribe_portfolio(account_no="1234561")
```

### 6.6. Heartbeat
```text
# Ping một lần
stream.streaming.ping()

# Ping tự động theo interval (giây)
stream.streaming.ping(interval=30)
```

### Message types nhận qua `on_data`

| Topic | Message Type | Mô tả |
|---|---|---|
| `trade.*` | `TradeMessage` | Dữ liệu khớp lệnh |
| `trade.*.<timeframe>` | `IntervalMessage` | Dữ liệu OHLCV theo interval |
| `quote.*` | `QuoteMessage` | Dữ liệu giá (bid/ask) |
| `room.*` | `ForeignRoomMessage` | Room nước ngoài |
| `market.*` | `MarketStatusMessage` | Trạng thái thị trường |
| `put.*` | `PutMessage` | Thoả thuận |
| `oddlot.*` | `OddLotMessage` | Lô lẻ |

### Message types nhận qua `on_trading`

| Topic | Message Type | Mô tả |
|---|---|---|
| `order.*` | `OrderStatusMessage` | Trạng thái lệnh thường |
|  | `FCOOrderUpdateMessage` | Trạng thái lệnh điều kiện (khi `event_type == "fcoEvent"`) |
| `portfolio.*` | `PortfolioMessage` | Thay đổi danh mục |

### Tổng quan method Streaming

| Nhóm | Method | Mô tả |
|---|---|---|
| **Kết nối** | `connect()` | Kết nối WebSocket |
|  | `disconnect()` | Ngắt kết nối |
|  | `wait(timeout=None)` | Chờ nhận dữ liệu |
| **Heartbeat** | `ping(on_response=None, interval=None)` | Ping server |
| **Subscribe mã** | `subscribe_symbol(symbols)` | Trade + Quote + Room |
|  | `subscribe_symbol_trade(symbols)` | Chỉ trade |
|  | `subscribe_symbol_quote(symbols)` | Chỉ quote |
|  | `subscribe_symbol_room(symbols)` | Chỉ foreign room |
|  | `subscribe_symbol_put_through(symbols)` | Chỉ thoả thuận |
|  | `subscribe_symbol_odd_lot(symbols)` | Chỉ lô lẻ |
|  | `subscribe_symbol_ohlcv(symbols, interval)` | OHLCV theo timeframe |
| **Subscribe sàn/chỉ số** | `subscribe_board(boards)` | Theo sàn |
|  | `subscribe_index(indices)` | Theo chỉ số |
| **Subscribe giao dịch** | `subscribe_order_status(account_no="*")` | Trạng thái lệnh |
|  | `subscribe_portfolio(account_no="*")` | Portfolio changes |
| **Unsubscribe** | `unsubscribe_symbol(symbols)` | Huỷ tất cả kênh cho mã |
|  | `unsubscribe_symbol_trade(symbols)` | Huỷ trade |
|  | `unsubscribe_symbol_quote(symbols)` | Huỷ quote |
|  | `unsubscribe_symbol_room(symbols)` | Huỷ foreign room |
|  | `unsubscribe_symbol_put_through(symbols)` | Huỷ thoả thuận |
|  | `unsubscribe_symbol_odd_lot(symbols)` | Huỷ lô lẻ |
|  | `unsubscribe_symbol_ohlcv(symbols, interval)` | Huỷ OHLCV |
|  | `unsubscribe_board(boards)` | Huỷ sàn |
|  | `unsubscribe_index(indices)` | Huỷ chỉ số |
