<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/go/utilities
Tieu de goc: Models
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/go/utilities>

# Models

Các model dữ liệu và message streaming trong Go SDK

Tất cả model là Go struct. Import từ package tương ứng.

## Cấu trúc Package
```python
ssi-sdk-go/v3/
├── ssi/        → Auth, Data, Trading, Stream (import chính)
├── auth/       → Token
├── account/    → Account
├── market/     → OHLCData, MarketIndexes, MarketIndexSummary, SecuritiesInfo, SecuritiesSummary
├── trading/    → PlaceOrderResponse, ModifyOrderResponse, CancelOrderResponse, MaxBuySellResponse, FCOInfo, FCOListResponse, FCOOrder, ...
├── portfolio/  → EquityAccountBalance, DerivativeAccountBalance, EquityPosition, DerivativePosition, Order
├── stream/     → TradeMessage, QuoteMessage, OrderStatusMessage, PortfolioMessage, FCOOrderUpdateMessage, ...
└── (root)      → SSIError, APIError, AuthenticationError, ...
```

## Xác thực

### Token

| Field | Kiểu | Mô tả |
|---|---|---|
| `AccessToken` | `string` | Access token |
| `TokenType` | `string` | Loại token (mặc định `"Bearer"`) |
| `ExpiresAt` | `int64` | Timestamp hết hạn |
| `RefreshToken` | `string` | Refresh token |
| `RefreshTokenExpiresAt` | `int64` | Timestamp hết hạn refresh token |

## Tài khoản

### Account

| Field | Kiểu | Mô tả |
|---|---|---|
| `AccountNo` | `string` | Số tài khoản |
| `AccountType` | `string` | Loại tài khoản |

## Dữ liệu thị trường

### OHLCData

| Field | Kiểu | Mô tả |
|---|---|---|
| `Symbol` | `string` | Mã chứng khoán |
| `TradingDate` | `string` | Ngày giao dịch |
| `OpenPrice` | `float64` | Giá mở |
| `HighPrice` | `float64` | Giá cao |
| `LowPrice` | `float64` | Giá thấp |
| `ClosePrice` | `float64` | Giá đóng |
| `Volume` | `int` | Khối lượng |
| `Value` | `float64` | Giá trị giao dịch |

### MarketIndexes

| Field | Kiểu | Mô tả |
|---|---|---|
| `Index` | `string` | Mã chỉ số |
| `IndexName` | `string` | Tên chỉ số |
| `Board` | `string` | Sàn |

### MarketIndexSummary

| Field | Kiểu | Mô tả |
|---|---|---|
| `TradingDate` | `string` | Ngày giao dịch |
| `IndexValue` | `float64` | Giá trị chỉ số |
| `IndexChange` | `float64` | Thay đổi |
| `IndexChangePercent` | `float64` | Thay đổi (%) |
| `TotalTrade` | `int` | Tổng khối lượng giao dịch |
| `TotalTradeValue` | `float64` | Tổng giá trị giao dịch |
| `TotalAdvanceStock` | `int` | Số CP tăng |
| `TotalDeclineStock` | `int` | Số CP giảm |
| `TotalSteadyStock` | `int` | Số CP không đổi |
| `TotalMatch` | `int` | Tổng khối lượng khớp |
| `TotalMatchValue` | `float64` | Tổng giá trị khớp |
| `TotalDeal` | `int` | Tổng khối lượng thoả thuận |
| `TotalDealValue` | `float64` | Tổng giá trị thoả thuận |
| `TotalCeilingStock` | `int` | Số CP trần |
| `TotalFloorStock` | `int` | Số CP sàn |
| `TotalPropBuy` | `int` | Tổng KL mua tự doanh |
| `TotalPropBuyValue` | `float64` | Tổng GT mua tự doanh |
| `TotalPropSell` | `int` | Tổng KL bán tự doanh |
| `TotalPropSellValue` | `float64` | Tổng GT bán tự doanh |

> **Lưu ý:** `MarketIndexSummary` không có field `Index`/`Board` riêng — dùng tham số truy vấn của method (`GetIndexSummary(index)` / `GetBoardSummary(board)`) để xác định phạm vi kết quả.

### SecuritiesInfo

| Field | Kiểu | Mô tả |
|---|---|---|
| `Symbol` | `string` | Mã chứng khoán |
| `Board` | `string` | Sàn |
| `Index` | `string` | Chỉ số |
| `SymbolNameVi` | `string` | Tên tiếng Việt |
| `SymbolNameEn` | `string` | Tên tiếng Anh |
| `LotSize` | `int` | Lô giao dịch |
| `ListedShares` | `int` | Số CP niêm yết |
| `ICBCode` | `string` | Mã ICB |
| `ICBName` | `string` | Tên ICB |
| `MaturityDate` | `string` | Ngày đáo hạn |
| `FirstTradingDate` | `string` | Ngày GD đầu tiên |
| `LastTradingDate` | `string` | Ngày GD cuối cùng |
| `CWUnderlyingSymbol` | `string` | Mã CK cơ sở CW |
| `CWExercisePrice` | `float64` | Giá thực hiện CW |
| `CWExecutionRatio` | `float64` | Tỷ lệ thực hiện CW |
| `IIndex` | `float64` | Chỉ số I |
| `INAV` | `float64` | Giá trị iNAV |

### SecuritiesSummary

| Field | Kiểu | Mô tả |
|---|---|---|
| `Symbol` | `string` | Mã chứng khoán |
| `TradingDate` | `string` | Ngày giao dịch |
| `PriceChange` | `float64` | Thay đổi giá |
| `PriceChangePercent` | `float64` | Thay đổi giá (%) |
| `OpenPrice` | `float64` | Giá mở |
| `HighPrice` | `float64` | Giá cao |
| `LowPrice` | `float64` | Giá thấp |
| `ClosePrice` | `float64` | Giá đóng |
| `TotalMatch` | `int` | Tổng khối lượng khớp |
| `TotalMatchValue` | `float64` | Tổng giá trị khớp |
| `AveragePrice` | `float64` | Giá trung bình |
| `TotalBuy` | `int` | Tổng KL mua |
| `TotalTradeBuy` | `float64` | Tổng GT mua |
| `TotalSell` | `int` | Tổng KL bán |
| `TotalTradeSell` | `float64` | Tổng GT bán |

## Danh mục

### EquityAccountBalance

| Field | Kiểu | Mô tả |
|---|---|---|
| `AccountNo` | `string` | Số tài khoản |
| `AccountBalance` | `float64` | Số dư tài khoản (tiền mặt khả dụng) |
| `TotalDebt` | `float64` | Tổng nợ |
| `InterestLoan` | `float64` | Lãi vay |
| `OverdueFeeLoan` | `float64` | Phí quá hạn |
| `Withdrawable` | `float64` | Tiền có thể rút |
| `OnHoldCash` | `float64` | Tiền giữ |
| `SellUnmatched` | `float64` | Bán chưa khớp |
| `SellT0` | `float64` | Tiền bán T+0 |
| `SellT1` | `float64` | Tiền bán T+1 |
| `SellT2` | `float64` | Tiền bán T+2 |
| `BuyUnmatched` | `float64` | Mua chưa khớp |
| `BuyT0` | `float64` | Tiền mua T+0 |
| `BuyT1` | `float64` | Tiền mua T+1 |
| `BuyT2` | `float64` | Tiền mua T+2 |
| `AdvanceCashT0` | `float64` | Ứng trước T+0 |
| `AdvanceCashT1` | `float64` | Ứng trước T+1 |
| `HoldSubscription` | `float64` | Giữ đăng ký mua |

### DerivativeAccountBalance

| Field | Kiểu | Mô tả |
|---|---|---|
| `AccountNo` | `string` | Số tài khoản |
| `AccountBalance` | `float64` | Số dư tài khoản |
| `Fee` | `float64` | Phí |
| `Commission` | `float64` | Hoa hồng |
| `Interest` | `float64` | Lãi |
| `ExtInterest` | `float64` | Lãi mở rộng |
| `Loan` | `float64` | Khoản vay |
| `DeliveryAmount` | `float64` | Giá trị giao hàng |
| `FloatingPL` | `float64` | Lãi/lỗ chưa thực hiện |
| `TradingPL` | `float64` | Lãi/lỗ giao dịch |
| `TotalPL` | `float64` | Tổng lãi/lỗ |
| `Withdrawable` | `float64` | Có thể rút |
| `CashSSI` | `float64` | Tiền tại SSI |
| `ValidNonCashSSI` | `float64` | Tài sản phi tiền mặt hợp lệ tại SSI |
| `CashWithdrawableSSI` | `float64` | Tiền có thể rút tại SSI |
| `CashVSDC` | `float64` | Tiền tại VSDC |
| `ValidNonCashVSDC` | `float64` | Tài sản phi tiền mặt hợp lệ tại VSDC |
| `CashWithdrawableVSDC` | `float64` | Tiền có thể rút tại VSDC |

### EquityPosition

| Field | Kiểu | Mô tả |
|---|---|---|
| `AccountNo` | `string` | Số tài khoản |
| `Symbol` | `string` | Mã chứng khoán |
| `Quantity` | `int` | Tổng khối lượng |
| `SellableQuantity` | `int` | Khối lượng bán được |
| `CostPrice` | `float64` | Giá vốn |
| `BuyingQuantity` | `int` | Khối lượng đang mua |
| `SellingQuantity` | `int` | Khối lượng đang bán |
| `MortgageQuantity` | `int` | Khối lượng cầm cố |
| `BlockQuantity` | `int` | Khối lượng phong toả |
| `DividendQuantity` | `int` | Khối lượng cổ tức |
| `BoughtQuantity` | `int` | Khối lượng đã mua |
| `SoldQuantity` | `int` | Khối lượng đã bán |
| `T1SellQuantity` | `int` | Khối lượng bán T+1 |
| `T2SellQuantity` | `int` | Khối lượng bán T+2 |
| `RestrictedQuantity` | `int` | Khối lượng hạn chế |

### DerivativePosition

| Field | Kiểu | Mô tả |
|---|---|---|
| `AccountNo` | `string` | Số tài khoản |
| `Symbol` | `string` | Mã hợp đồng |
| `Long` / `Short` / `Net` | `int` | Vị thế Long / Short / Net |
| `BidAvgPrice` / `AskAvgPrice` | `float64` | Giá TB mua / bán |
| `FloatingPL` / `TradingPL` | `float64` | Lãi/lỗ |
| `TradePrice` | `float64` | Giá giao dịch |

### Order

| Field | Kiểu | Mô tả |
|---|---|---|
| `AccountNo` | `string` | Số tài khoản |
| `ClientRequestID` | `string` | Client request ID |
| `OrderID` | `string` | Order ID |
| `Symbol` | `string` | Mã chứng khoán |
| `Side` | `string` | Mua/Bán |
| `OrderType` | `string` | Loại lệnh |
| `Price` / `AvgPrice` | `float64` | Giá đặt / Giá khớp TB |
| `Quantity` | `int` | Khối lượng đặt |
| `OsQuantity` | `int` | Khối lượng chờ |
| `FilledQuantity` | `int` | Khối lượng khớp |
| `CancelQuantity` | `int` | Khối lượng huỷ |
| `Status` | `string` | Trạng thái lệnh |
| `InputTime` / `ModifyTime` | `string` | Thời gian đặt / sửa |
| `Message` | `string` | Thông báo |

## Response giao dịch

### PlaceOrderResponse

`OrderID`, `ClientRequestID`, `Status`

### ModifyOrderResponse

`ClientModifyID`, `OrderID`, `ClientRequestID`, `Status`

### CancelOrderResponse

`ClientCancelID`, `OrderID`, `ClientRequestID`, `Status`

### MaxBuySellResponse

`AccountNo`, `Symbol`, `MaxBuyQuantity`, `MaxSellQuantity`, `MarginRatio`, `PurchasePower`

## Lệnh điều kiện (FCO)

### FCOPlaceResponse

Kết quả đặt lệnh điều kiện — `FCOID string`

### FCOCancelResponse

Kết quả huỷ lệnh điều kiện — `FCOID string`

### FCOListResponse

Danh sách lệnh điều kiện (phân trang).

| Field | Kiểu | Mô tả |
|---|---|---|
| `PageIndex` | `int` | Trang hiện tại |
| `PageSize` | `int` | Kích thước trang |
| `ItemsCount` | `int` | Tổng số bản ghi |
| `PagesCount` | `int` | Tổng số trang |
| `FCOList` | `[]*FCOInfo` | Danh sách lệnh FCO |

### FCOInfo

Thông tin chi tiết một lệnh điều kiện.

| Field | Kiểu | Mô tả |
|---|---|---|
| `FCOID` | `string` | Mã lệnh FCO |
| `ClientID` | `string` | Username / Client ID |
| `AccountNo` | `string` | Số tài khoản |
| `Quantity` | `int` | Khối lượng đặt |
| `Price` | `string` | Giá đặt |
| `PriceSlip` | `float64` | Độ trượt giá |
| `Symbol` | `string` | Mã chứng khoán |
| `Type` | `FCOType` | Loại lệnh điều kiện |
| `FromDate` | `string` | Ngày bắt đầu hiệu lực |
| `ToDate` | `string` | Ngày kết thúc hiệu lực |
| `MatchedQuantity` | `int` | Khối lượng đã khớp |
| `IsPlaceOrder` | `bool` | Đã đẩy lệnh vào sổ hay chưa |
| `Status` | `FCOStatus` | Trạng thái lệnh FCO |
| `Detail` | `string` | Chi tiết trạng thái |
| `Params` | `*FCOParams` | Tham số kích hoạt lệnh FCO |

### FCOParams

Tham số kích hoạt của lệnh điều kiện.

| Field | Kiểu | Mô tả |
|---|---|---|
| `StopPrice` | `float64` | Giá dừng / giá kích hoạt |
| `Side` | `OrderSide` | Chiều lệnh (Mua/Bán) |
| `ActivePrice` | `float64` | Giá kích hoạt (Trailing Stop) |
| `TrailingAmount` | `float64` | Khoảng bám sát (Trailing Amount) |
| `TPActivePrice` | `float64` | Giá kích hoạt chốt lời (Take Profit) |
| `SLActivePrice` | `float64` | Giá kích hoạt cắt lỗ (Stop Loss) |
| `TPPrice` | `string` | Giá chốt lời |
| `SLPrice` | `string` | Giá cắt lỗ |
| `TPSlip` | `float64` | Trượt giá chốt lời |
| `SLSlip` | `float64` | Trượt giá cắt lỗ |
| `Operator` | `FCOOperator` | Toán tử so sánh kích hoạt |

### FCOOrderBookResponse

Nhật ký khớp lệnh FCO (phân trang).

| Field | Kiểu | Mô tả |
|---|---|---|
| `PageIndex` | `int` | Trang hiện tại |
| `PageSize` | `int` | Kích thước trang |
| `ItemsCount` | `int` | Tổng số bản ghi |
| `PagesCount` | `int` | Tổng số trang |
| `OrderBook` | `[]*FCOOrder` | Danh sách nhật ký lệnh FCO |

### FCOOrder

Nhật ký giao dịch / thực thi của lệnh FCO.

| Field | Kiểu | Mô tả |
|---|---|---|
| `FCOID` | `string` | Mã lệnh FCO gốc |
| `AccountNo` | `string` | Số tài khoản |
| `Quantity` | `float64` | Khối lượng |
| `Price` | `string` | Giá đặt |
| `Symbol` | `string` | Mã chứng khoán |
| `Side` | `OrderSide` | Chiều lệnh |
| `OrderType` | `OrderType` | Loại lệnh con |
| `IsMainOrder` | `bool` | Là lệnh chính |
| `IsAttachedOrder` | `bool` | Là lệnh kèm theo |
| `CreatedTime` / `UpdatedTime` | `string` | Thời gian tạo / cập nhật |
| `UniqueID` | `string` | ID duy nhất |
| `OrderID` | `string` | Mã lệnh trên sàn |
| `MatchedQuantity` | `float64` | Khối lượng đã khớp |
| `OSQuantity` | `float64` | Khối lượng chờ khớp |
| `AvgPrice` | `float64` | Giá khớp trung bình |
| `Status` | `OrderStatus` | Trạng thái lệnh con |
| `Detail` | `string` | Chi tiết |

## Message Streaming

### TradeMessage

`Type`, `TradingTime`, `Symbol`, `Price`, `Quantity`, `Side`, `TotalVolume`

### QuoteMessage

`Type`, `TradingTime`, `Symbol`, `BidPrices`, `BidVolumes`, `AskPrices`, `AskVolumes`

### ForeignRoomMessage

`Type`, `TradingTime`, `Symbol`, `TotalRoom`, `CurrentRoom`, `BuyQuantity`, `BuyValue`, `SellQuantity`, `SellValue`

### PutMessage

`Type`, `TradingTime`, `Symbol`, `Price`, `Quantity`, `TotalQuantity`, `TotalValue`

### OddLotMessage

`Type`, `TradingTime`, `Symbol`, `Price`, `Quantity`, `BidPrices`, `BidVolumes`, `AskPrices`, `AskVolumes`

### MarketStatusMessage

`Market`, `Status`, `TradingDate`

### OrderStatusMessage

`Type`, `AccountNo`, `ClientRequestID`, `OrderID`, `Symbol`, `Side`, `OrderType`, `Price`, `Quantity`, `OsQuantity`, `FilledQuantity`, `CancelQuantity`, `Status`, `InputTime`, `ModifyTime`, `Message`

### PortfolioMessage

`Type`, `AccountNo`, `TotalAsset`, `CashBalance`, `StockValue`

### FCOOrderUpdateMessage

Cập nhật realtime trạng thái lệnh điều kiện FCO (nhận qua `SetOnTrading`, khi `EventType == "fcoEvent"`).

| Field | Kiểu | Mô tả |
|---|---|---|
| `FCOID` | `string` | Mã lệnh FCO |
| `ProcessStatus` | `FCOStatus` | Trạng thái xử lý lệnh FCO (`INIT`, `WAIT`, `WC`, `TER`, ...) |
| `MatchedQuantity` | `int` | Khối lượng đã khớp |
| `IsPlaceOrder` | `bool` | Đã đẩy lệnh vào sổ hay chưa |
| `Symbol` | `string` | Mã chứng khoán |
| `Quantity` | `int` | Khối lượng đặt |
| `Price` | `string` | Giá đặt |
| `AccountNo` | `string` | Số tài khoản |
| `UpdatedTime` | `string` | Thời gian cập nhật |
| `Status` | `string` | Mã trạng thái |
| `Message` | `string` | Thông báo chi tiết |
| `Username` | `string` | Username đặt lệnh |
| `EventType` | `string` | Loại sự kiện (`"fcoEvent"`) |
| `FCOType` | `FCOType` | Loại lệnh điều kiện (`GTD`, `Stop`, ...) |

### IntervalMessage

| Field | Kiểu | Mô tả |
|---|---|---|
| `Type` | `string` | Loại message |
| `IntervalTime` | `string` | Thời gian interval |
| `TradingTime` | `string` | Thời gian giao dịch |
| `Symbol` | `string` | Mã chứng khoán |
| `Open` | `float64` | Giá mở |
| `High` | `float64` | Giá cao |
| `Low` | `float64` | Giá thấp |
| `Close` | `float64` | Giá đóng |
| `Volume` | `int64` | Khối lượng |

### HeartbeatMessage

`Method`, `Channel`, `Status`, `Message`

## Wrapper Types

### AccountBalance

| Field | Kiểu | Mô tả |
|---|---|---|
| `Equity` | `*EquityAccountBalance` | Số dư tài khoản cổ phiếu |
| `Derivative` | `*DerivativeAccountBalance` | Số dư tài khoản phái sinh |

### Position

| Field | Kiểu | Mô tả |
|---|---|---|
| `Equity` | `[]EquityPosition` | Danh sách vị thế cổ phiếu |
| `Derivative` | `*AllDerivativePosition` | Tất cả vị thế phái sinh |

### PPMMR

| Field | Kiểu | Mô tả |
|---|---|---|
| `Equity` | `*EquityPPMMR` | PPMMR cổ phiếu |
| `Derivative` | `*DerivativePPMMR` | PPMMR phái sinh |
