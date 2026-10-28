<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/python/utilities
Tieu de goc: Models
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/python/utilities>

# Models

Các model dữ liệu trả về trong Python SDK

Tất cả model import từ `ssi_sdk.models`:
```python
from ssi_sdk.models import Account, OHLCData, PlaceOrderResponse, TradeMessage
```

## Authentication

### Token

| Trường | Kiểu | Mô tả |
|---|---|---|
| `access_token` | `str` | Token truy cập |
| `token_type` | `str` | Loại token (mặc định `"Bearer"`) |
| `expires_at` | `int` | Thời điểm hết hạn (timestamp) |
| `refresh_token` | `str` | Token làm mới |
| `refresh_token_expires_at` | `int` | Thời điểm refresh token hết hạn |

## Account

### Account

| Trường | Kiểu | Mô tả |
|---|---|---|
| `account_no` | `str` | Số tài khoản |
| `account_type` | `AccountType` | Loại tài khoản |

## Market Data

### OHLCData

| Trường | Kiểu | Mô tả |
|---|---|---|
| `symbol` | `str` | Mã chứng khoán |
| `trading_date` | `str` | Ngày giao dịch |
| `open_price` | `float \| int` | Giá mở cửa |
| `high_price` | `float \| int` | Giá cao nhất |
| `low_price` | `float \| int` | Giá thấp nhất |
| `close_price` | `float \| int` | Giá đóng cửa |
| `volume` | `int` | Khối lượng |
| `value` | `float \| int` | Giá trị giao dịch |

### MarketIndexes

| Trường | Kiểu | Mô tả |
|---|---|---|
| `index` | `str` | Mã chỉ số |
| `index_name` | `str` | Tên chỉ số |
| `board` | `Board \| None` | Sàn |

### MarketIndexSummary

| Trường | Kiểu | Mô tả |
|---|---|---|
| `index` | `str` | Mã chỉ số |
| `board` | `str` | Sàn |
| `trading_date` | `str` | Ngày giao dịch |
| `index_value` | `float` | Giá trị chỉ số |
| `index_change` | `float` | Thay đổi |
| `index_change_percent` | `float` | Thay đổi (%) |
| `total_trade` | `int` | Tổng KL giao dịch |
| `total_trade_value` | `float` | Tổng giá trị giao dịch |
| `total_advance_stock` | `int` | Số mã tăng |
| `total_decline_stock` | `int` | Số mã giảm |
| `total_steady_stock` | `int` | Số mã đứng |
| `total_match` | `int` | Tổng khối lượng khớp |
| `total_match_value` | `float` | Tổng giá trị khớp |
| `total_deal` | `int` | Tổng khối lượng thoả thuận |
| `total_deal_value` | `float` | Tổng giá trị thoả thuận |
| `total_ceiling_stock` | `int` | Số CP trần |
| `total_floor_stock` | `int` | Số CP sàn |
| `total_prop_buy` | `int` | Tổng KL mua tự doanh |
| `total_prop_buy_value` | `float` | Tổng GT mua tự doanh |
| `total_prop_sell` | `int` | Tổng KL bán tự doanh |
| `total_prop_sell_value` | `float` | Tổng GT bán tự doanh |

### SecuritiesInfo

| Trường | Kiểu | Mô tả |
|---|---|---|
| `symbol` | `str` | Mã chứng khoán |
| `board` | `Board \| None` | Sàn |
| `index` | `str \| None` | Chỉ số |
| `symbol_name_vi` | `str \| None` | Tên tiếng Việt |
| `symbol_name_en` | `str \| None` | Tên tiếng Anh |
| `lot_size` | `int \| None` | Lô giao dịch |
| `listed_shares` | `int \| None` | Số CP niêm yết |
| `icb_code` | `str \| None` | Mã ngành ICB |
| `icb_name` | `str \| None` | Tên ngành ICB |
| `maturity_date` | `str \| None` | Ngày đáo hạn |
| `first_trading_date` | `str \| None` | Ngày GD đầu tiên |
| `last_trading_date` | `str \| None` | Ngày GD cuối cùng |
| `cw_underlying_symbol` | `str \| None` | Mã CK cơ sở CW |
| `cw_exercise_price` | `float \| None` | Giá thực hiện CW |
| `cw_execution_ratio` | `float \| None` | Tỷ lệ thực hiện CW |
| `i_index` | `float \| None` | Chỉ số I |
| `i_nav` | `float \| None` | Giá trị iNAV |

### SecuritiesSummary

| Trường | Kiểu | Mô tả |
|---|---|---|
| `symbol` | `str` | Mã chứng khoán |
| `trading_date` | `str` | Ngày giao dịch |
| `price_change` | `float` | Thay đổi giá |
| `price_change_percent` | `float` | Thay đổi giá (%) |
| `open_price` | `float` | Giá mở cửa |
| `high_price` | `float` | Giá cao nhất |
| `low_price` | `float` | Giá thấp nhất |
| `close_price` | `float` | Giá đóng cửa |
| `total_match` | `int` | Tổng KL khớp |
| `total_match_value` | `float` | Tổng giá trị khớp |
| `average_price` | `float` | Giá trung bình |
| `total_buy` | `int` | Tổng KL mua |
| `total_trade_buy` | `float` | Tổng GT mua |
| `total_sell` | `int` | Tổng KL bán |
| `total_trade_sell` | `float` | Tổng GT bán |

## Portfolio

### EquityAccountBalance

| Trường | Kiểu | Mô tả |
|---|---|---|
| `account_no` | `str` | Số tài khoản |
| `account_balance` | `float` | Số dư tài khoản |
| `total_debt` | `float` | Tổng nợ |
| `interest_loan` | `float` | Lãi vay |
| `overdue_fee_loan` | `float` | Phí vay quá hạn |
| `withdrawable` | `float` | Tiền rút được |
| `on_hold_cash` | `float` | Tiền tạm giữ |
| `sell_unmatched` | `float` | Tiền bán chờ khớp |
| `sell_t0` | `float` | Tiền bán T0 |
| `sell_t1` | `float` | Tiền bán T1 |
| `sell_t2` | `float` | Tiền bán T2 |
| `buy_unmatched` | `float` | Tiền mua chờ khớp |
| `buy_t0` | `float` | Tiền mua T0 |
| `buy_t1` | `float` | Tiền mua T1 |
| `buy_t2` | `float` | Tiền mua T2 |
| `advance_cash_t0` | `float` | Ứng tiền T0 |
| `advance_cash_t1` | `float` | Ứng tiền T1 |
| `hold_subscription` | `float` | Tiền giữ đăng ký |

### DerivativeAccountBalance

| Trường | Kiểu | Mô tả |
|---|---|---|
| `account_no` | `str` | Số tài khoản |
| `account_balance` | `float` | Số dư tài khoản |
| `fee` | `float` | Phí |
| `commission` | `float` | Hoa hồng |
| `interest` | `float` | Lãi |
| `ext_interest` | `float` | Lãi ngoài |
| `loan` | `float` | Vay |
| `delivery_amount` | `float` | Giá trị giao nhận |
| `floating_pl` | `float` | Lãi/lỗ chưa thực hiện |
| `trading_pl` | `float` | Lãi/lỗ giao dịch |
| `total_pl` | `float` | Tổng lãi/lỗ |
| `withdrawable` | `float` | Tiền rút được |
| `cash_ssi` | `float` | Tiền mặt SSI |
| `valid_non_cash_ssi` | `float` | Tài sản phi tiền mặt hợp lệ SSI |
| `cash_withdrawable_ssi` | `float` | Tiền rút được SSI |
| `cash_vsdc` | `float` | Tiền mặt VSDC |
| `valid_non_cash_vsdc` | `float` | Tài sản phi tiền mặt hợp lệ VSDC |
| `cash_withdrawable_vsdc` | `float` | Tiền rút được VSDC |

### EquityPosition

| Trường | Kiểu | Mô tả |
|---|---|---|
| `account_no` | `str` | Số tài khoản |
| `symbol` | `str` | Mã chứng khoán |
| `quantity` | `int` | Tổng số lượng |
| `sellable_quantity` | `int` | Số lượng bán được |
| `cost_price` | `float` | Giá vốn |
| `buying_quantity` | `int` | SL đang mua |
| `selling_quantity` | `int` | SL đang bán |
| `mortgage_quantity` | `int` | SL cầm cố |
| `block_quantity` | `int` | Khối lượng phong toả |
| `dividend_quantity` | `int` | Khối lượng cổ tức |
| `bought_quantity` | `int` | Khối lượng đã mua |
| `sold_quantity` | `int` | Khối lượng đã bán |
| `t1_sell_quantity` | `int` | KL bán T1 |
| `t2_sell_quantity` | `int` | KL bán T2 |
| `restricted_quantity` | `int` | Khối lượng hạn chế |

### DerivativePosition

| Trường | Kiểu | Mô tả |
|---|---|---|
| `account_no` | `str` | Số tài khoản |
| `symbol` | `str` | Mã hợp đồng |
| `long` / `short` / `net` | `int` | Vị thế mua / bán / ròng |
| `bid_avg_price` / `ask_avg_price` | `float` | Giá TB mua / bán |
| `floating_pl` / `trading_pl` | `float` | Lãi/lỗ |
| `trade_price` | `float` | Giá giao dịch |

### Order

| Trường | Kiểu | Mô tả |
|---|---|---|
| `account_no` | `str` | Số tài khoản |
| `client_request_id` | `str` | ID yêu cầu client |
| `order_id` | `str` | ID lệnh |
| `symbol` | `str` | Mã chứng khoán |
| `side` | `OrderSide` | Mua/Bán |
| `order_type` | `OrderType` | Loại lệnh |
| `price` / `avg_price` | `float` | Giá đặt / Giá TB khớp |
| `quantity` | `int` | SL đặt |
| `os_quantity` | `int` | SL chờ |
| `filled_quantity` | `int` | SL đã khớp |
| `cancel_quantity` | `int` | SL đã huỷ |
| `status` | `OrderStatus` | Trạng thái lệnh |
| `input_time` / `modify_time` | `str` | Thời gian đặt / sửa |
| `message` | `str` | Thông báo |

## Trading Responses

### PlaceOrderResponse

`order_id`, `client_request_id`, `status`

### ModifyOrderResponse

`client_modify_id`, `order_id`, `client_request_id`, `status`

### CancelOrderResponse

`client_cancel_id`, `order_id`, `client_request_id`, `status`

### MaxBuySellResponse

`account_no`, `symbol`, `max_buy_quantity`, `max_sell_quantity`, `margin_ratio`, `purchase_power`

## Conditional Orders (FCO)

### FCOPlaceResponse

Kết quả đặt lệnh điều kiện — `fco_id`

### FCOCancelResponse

Kết quả huỷ lệnh điều kiện — `fco_id`

### FCOListResponse

Danh sách lệnh điều kiện (phân trang).

| Trường | Kiểu | Mô tả |
|---|---|---|
| `page_index` | `int` | Trang hiện tại |
| `page_size` | `int` | Kích thước trang |
| `items_count` | `int` | Tổng số bản ghi |
| `pages_count` | `int` | Tổng số trang |
| `fco_list` | `list[FCOInfo]` | Danh sách lệnh FCO |

### FCOInfo

Thông tin chi tiết một lệnh điều kiện.

| Trường | Kiểu | Mô tả |
|---|---|---|
| `fco_id` | `str` | Mã lệnh FCO |
| `client_id` | `str` | Username / Client ID |
| `account_no` | `str` | Số tài khoản |
| `quantity` | `int` | Khối lượng đặt |
| `price` | `str` | Giá đặt |
| `price_slip` | `str` | Độ trượt giá |
| `symbol` | `str` | Mã chứng khoán |
| `type` | `FCOType \| None` | Loại lệnh điều kiện |
| `from_date` | `str` | Ngày bắt đầu hiệu lực |
| `to_date` | `str` | Ngày kết thúc hiệu lực |
| `matched_quantity` | `int` | Khối lượng đã khớp |
| `is_place_order` | `bool` | Đã đẩy lệnh vào sổ hay chưa |
| `status` | `FCOStatus \| None` | Trạng thái lệnh FCO |
| `detail` | `str` | Chi tiết trạng thái |
| `params` | `FCOParams \| None` | Tham số kích hoạt lệnh FCO |

### FCOParams

Tham số kích hoạt của lệnh điều kiện.

| Trường | Kiểu | Mô tả |
|---|---|---|
| `stop_price` | `float \| None` | Giá dừng / giá kích hoạt |
| `side` | `OrderSide \| None` | Chiều lệnh (Mua/Bán) |
| `active_price` | `float \| None` | Giá kích hoạt (Trailing Stop) |
| `trailing_amount` | `float \| None` | Khoảng bám sát (Trailing Amount) |
| `tp_active_price` | `float \| None` | Giá kích hoạt chốt lời (Take Profit) |
| `sl_active_price` | `float \| None` | Giá kích hoạt cắt lỗ (Stop Loss) |
| `tp_price` | `str \| None` | Giá chốt lời |
| `sl_price` | `str \| None` | Giá cắt lỗ |
| `tp_slip` | `float \| None` | Trượt giá chốt lời |
| `sl_slip` | `float \| None` | Trượt giá cắt lỗ |
| `operator` | `FCOOperator \| None` | Toán tử so sánh kích hoạt |

### FCOOrderBookResponse

Nhật ký khớp lệnh FCO (phân trang).

| Trường | Kiểu | Mô tả |
|---|---|---|
| `page_index` | `int` | Trang hiện tại |
| `page_size` | `int` | Kích thước trang |
| `items_count` | `int` | Tổng số bản ghi |
| `pages_count` | `int` | Tổng số trang |
| `order_book` | `list[FCOOrder]` | Danh sách nhật ký lệnh FCO |

### FCOOrder

Nhật ký giao dịch / thực thi của lệnh FCO.

| Trường | Kiểu | Mô tả |
|---|---|---|
| `fco_id` | `str` | Mã lệnh FCO gốc |
| `account_no` | `str` | Số tài khoản |
| `quantity` | `float` | Khối lượng |
| `price` | `str` | Giá đặt |
| `symbol` | `str` | Mã chứng khoán |
| `side` | `OrderSide \| None` | Chiều lệnh |
| `order_type` | `OrderType \| None` | Loại lệnh con |
| `is_main_order` | `bool` | Là lệnh chính |
| `is_attached_order` | `bool` | Là lệnh kèm theo |
| `created_time` / `updated_time` | `str` | Thời gian tạo / cập nhật |
| `unique_id` | `str` | ID duy nhất |
| `order_id` | `str` | Mã lệnh trên sàn |
| `matched_quantity` | `float` | Khối lượng đã khớp |
| `os_quantity` | `float` | Khối lượng chờ khớp |
| `avg_price` | `float` | Giá khớp trung bình |
| `status` | `OrderStatus \| None` | Trạng thái lệnh con |
| `detail` | `str` | Chi tiết |

## Streaming Messages

### TradeMessage

`type`, `trading_time`, `symbol`, `price`, `quantity`, `side`, `total_volume`

### IntervalMessage

| Trường | Kiểu | Mô tả |
|---|---|---|
| `type` | `DataType` | Loại dữ liệu |
| `interval_time` | `str` | Thời gian interval |
| `trading_time` | `str` | Thời gian giao dịch |
| `symbol` | `str` | Mã chứng khoán |
| `open` | `float \| int` | Giá mở |
| `high` | `float \| int` | Giá cao |
| `low` | `float \| int` | Giá thấp |
| `close` | `float \| int` | Giá đóng |
| `volume` | `int` | Khối lượng |

### QuoteMessage

`type`, `trading_time`, `symbol`, `bid_prices`, `bid_volumes`, `ask_prices`, `ask_volumes`

### ForeignRoomMessage

`type`, `trading_time`, `symbol`, `total_room`, `current_room`, `buy_quantity`, `buy_value`, `sell_quantity`, `sell_value`

### PutMessage

`type`, `trading_time`, `symbol`, `price`, `quantity`, `total_quantity`, `total_value`

### OddLotMessage

`type`, `trading_time`, `symbol`, `price`, `quantity`, `bid_prices`, `bid_volumes`, `ask_prices`, `ask_volumes`

### MarketStatusMessage

`market`, `status`, `trading_date`

### OrderStatusMessage

`type`, `account_no`, `client_request_id`, `order_id`, `symbol`, `side`, `order_type`, `price`, `quantity`, `os_quantity`, `filled_quantity`, `cancel_quantity`, `status`, `input_time`, `modify_time`, `message`

### PortfolioMessage

`type`, `account_no`, `total_asset`, `cash_balance`, `stock_value`

### FCOOrderUpdateMessage

Cập nhật trạng thái lệnh điều kiện FCO (streaming, nhận qua `on_trading` khi `event_type == "fcoEvent"`).

| Trường | Kiểu | Mô tả |
|---|---|---|
| `fco_id` | `str` | Mã lệnh FCO |
| `process_status` | `FCOStatus \| None` | Trạng thái xử lý lệnh FCO (`INIT`, `WAIT`, `WC`, `TER`, ...) |
| `matched_quantity` | `int` | Khối lượng đã khớp |
| `is_place_order` | `bool` | Đã đẩy lệnh vào sổ hay chưa |
| `symbol` | `str` | Mã chứng khoán |
| `quantity` | `int` | Khối lượng đặt |
| `price` | `str` | Giá đặt |
| `account_no` | `str` | Số tài khoản |
| `updated_time` | `str` | Thời gian cập nhật (`YYYY/MM/DD HH:MM:SS`) |
| `status` | `str` | Mã trạng thái |
| `message` | `str` | Thông báo chi tiết / lý do kích hoạt, ngắt kết nối |
| `username` | `str` | Username đặt lệnh |
| `event_type` | `str` | Loại sự kiện (`"fcoEvent"`) |
| `type` | `FCOType \| None` | Loại lệnh điều kiện (`GTD`, `STOP`, ...) |

### HeartbeatMessage

`method`, `channel`, `status`, `message`

## Wrapper Types

### AccountBalance

| Trường | Kiểu | Mô tả |
|---|---|---|
| `equity` | `EquityAccountBalance \| None` | Số dư cơ sở |
| `derivative` | `DerivativeAccountBalance \| None` | Số dư phái sinh |

### Position

| Trường | Kiểu | Mô tả |
|---|---|---|
| `equity` | `list[EquityPosition] \| None` | Vị thế cơ sở |
| `derivative` | `AllDerivativePosition \| None` | Vị thế phái sinh |

### PPMMR

| Trường | Kiểu | Mô tả |
|---|---|---|
| `equity` | `EquityPPMMR \| None` | PPMMR cơ sở |
| `derivative` | `DerivativePPMMR \| None` | PPMMR phái sinh |

### OrderBook

| Trường | Kiểu | Mô tả |
|---|---|---|
| `orders` | `list[Order]` | Danh sách lệnh |
| `total_orders` | `int` | Tổng số lệnh |
