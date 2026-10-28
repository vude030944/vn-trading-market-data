<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/csharp/utilities
Tieu de goc: Models
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/csharp/utilities>

# Models

Các model dữ liệu trả về trong .NET SDK

Tất cả model nằm trong namespace `SsiSdk.Models`, là các `sealed class` với auto-property:
```text
using SsiSdk.Models;
```

## Xác thực

### Token

| Trường | Kiểu | Mô tả |
|---|---|---|
| `AccessToken` | `string` | Token truy cập |
| `TokenType` | `string` | Loại token (mặc định `"Bearer"`) |
| `ExpiresAt` | `long` | Thời điểm hết hạn (timestamp) |
| `RefreshToken` | `string` | Token làm mới |
| `RefreshTokenExpiresAt` | `long` | Thời điểm refresh token hết hạn |

## Account

### Account

| Trường | Kiểu | Mô tả |
|---|---|---|
| `AccountNo` | `string` | Số tài khoản |
| `AccountType` | `string` | Loại tài khoản |

## Market Data

### OhlcData

| Trường | Kiểu | Mô tả |
|---|---|---|
| `Symbol` | `string` | Mã chứng khoán |
| `TradingDate` | `string` | Ngày giao dịch |
| `OpenPrice` | `double` | Giá mở cửa |
| `HighPrice` | `double` | Giá cao nhất |
| `LowPrice` | `double` | Giá thấp nhất |
| `ClosePrice` | `double` | Giá đóng cửa |
| `Volume` | `int` | Khối lượng |
| `Value` | `double` | Giá trị giao dịch |

### MarketIndexes

| Trường | Kiểu | Mô tả |
|---|---|---|
| `Index` | `string` | Mã chỉ số |
| `IndexName` | `string` | Tên chỉ số |
| `Board` | `string?` | Sàn |

### MarketIndexSummary

| Trường | Kiểu | Mô tả |
|---|---|---|
| `Index` | `string` | Mã chỉ số |
| `Board` | `string` | Sàn |
| `TradingDate` | `string` | Ngày giao dịch |
| `IndexValue` | `double` | Giá trị chỉ số |
| `IndexChange` | `double` | Thay đổi |
| `IndexChangePercent` | `double` | Thay đổi (%) |
| `TotalTrade` | `int` | Tổng KL giao dịch |
| `TotalTradeValue` | `double` | Tổng giá trị giao dịch |
| `TotalAdvanceStock` | `int` | Số mã tăng |
| `TotalDeclineStock` | `int` | Số mã giảm |
| `TotalSteadyStock` | `int` | Số mã đứng |
| `TotalMatch` | `int` | Tổng khối lượng khớp |
| `TotalMatchValue` | `double` | Tổng giá trị khớp |
| `TotalDeal` | `int` | Tổng khối lượng thoả thuận |
| `TotalDealValue` | `double` | Tổng giá trị thoả thuận |
| `TotalCeilingStock` | `int` | Số CP trần |
| `TotalFloorStock` | `int` | Số CP sàn |
| `TotalPropBuy` | `int` | Tổng KL mua tự doanh |
| `TotalPropBuyValue` | `double` | Tổng GT mua tự doanh |
| `TotalPropSell` | `int` | Tổng KL bán tự doanh |
| `TotalPropSellValue` | `double` | Tổng GT bán tự doanh |

### SecuritiesInfo

| Trường | Kiểu | Mô tả |
|---|---|---|
| `Symbol` | `string` | Mã chứng khoán |
| `Board` | `string?` | Sàn |
| `Index` | `string` | Chỉ số |
| `SymbolNameVi` | `string` | Tên tiếng Việt |
| `SymbolNameEn` | `string` | Tên tiếng Anh |
| `LotSize` | `int` | Lô giao dịch |
| `ListedShares` | `int` | Số CP niêm yết |
| `IcbCode` | `string?` | Mã ngành ICB |
| `IcbName` | `string?` | Tên ngành ICB |
| `MaturityDate` | `string?` | Ngày đáo hạn |
| `FirstTradingDate` | `string?` | Ngày GD đầu tiên |
| `LastTradingDate` | `string?` | Ngày GD cuối cùng |
| `CwUnderlyingSymbol` | `string?` | Mã CK cơ sở CW |
| `CwExercisePrice` | `double?` | Giá thực hiện CW |
| `CwExecutionRatio` | `double?` | Tỷ lệ thực hiện CW |
| `IIndex` | `double?` | Chỉ số I |
| `INav` | `double?` | Giá trị iNAV |

### SecuritiesSummary

| Trường | Kiểu | Mô tả |
|---|---|---|
| `Symbol` | `string` | Mã chứng khoán |
| `TradingDate` | `string` | Ngày giao dịch |
| `PriceChange` | `double` | Thay đổi giá |
| `PriceChangePercent` | `double` | Thay đổi giá (%) |
| `OpenPrice` | `double` | Giá mở cửa |
| `HighPrice` | `double` | Giá cao nhất |
| `LowPrice` | `double` | Giá thấp nhất |
| `ClosePrice` | `double` | Giá đóng cửa |
| `AveragePrice` | `double` | Giá trung bình |
| `TotalMatch` | `int` | Tổng KL khớp |
| `TotalMatchValue` | `double` | Tổng giá trị khớp |
| `TotalBuy` | `int` | Tổng KL mua |
| `TotalTradeBuy` | `double` | Tổng GT mua |
| `TotalSell` | `int` | Tổng KL bán |
| `TotalTradeSell` | `double` | Tổng GT bán |

### DownloadData

| Trường | Kiểu | Mô tả |
|---|---|---|
| `Data` | `List<Dictionary<string, object>>` | Dữ liệu raw dạng bảng |
| `TotalCount` | `int` | Tổng số bản ghi |

## Portfolio

### EquityAccountBalance

| Trường | Kiểu | Mô tả |
|---|---|---|
| `AccountNo` | `string` | Số tài khoản |
| `AccountBalance` | `double` | Số dư tài khoản (tiền mặt khả dụng) |
| `TotalDebt` | `double` | Tổng nợ |
| `InterestLoan` | `double` | Lãi vay |
| `OverdueFeeLoan` | `double` | Phí vay quá hạn |
| `Withdrawable` | `double` | Tiền có thể rút |
| `OnHoldCash` | `double` | Tiền tạm giữ |
| `SellUnmatched` / `BuyUnmatched` | `double` | Tiền bán/mua chờ khớp |
| `SellT0` / `SellT1` / `SellT2` | `double` | Tiền bán T0/T1/T2 |
| `BuyT0` / `BuyT1` / `BuyT2` | `double` | Tiền mua T0/T1/T2 |
| `AdvanceCashT0` / `AdvanceCashT1` | `double` | Ứng tiền T0/T1 |
| `HoldSubscription` | `double` | Tiền giữ đăng ký |

### DerivativeAccountBalance

| Trường | Kiểu | Mô tả |
|---|---|---|
| `AccountNo` | `string` | Số tài khoản |
| `AccountBalance` | `double` | Số dư tài khoản |
| `Fee` / `Commission` / `Interest` / `ExtInterest` | `double` | Phí / Hoa hồng / Lãi |
| `Loan` | `double` | Vay |
| `DeliveryAmount` | `double` | Giá trị giao nhận |
| `FloatingPL` / `TradingPL` / `TotalPL` | `double` | Lãi/lỗ chưa thực hiện / giao dịch / tổng |
| `Withdrawable` | `double` | Tiền rút được |
| `CashSSI` / `ValidNonCashSSI` / `CashWithdrawableSSI` | `double` | Tiền mặt / tài sản phi tiền mặt hợp lệ / rút được (SSI) |
| `CashVSDC` / `ValidNonCashVSDC` / `CashWithdrawableVSDC` | `double` | Tương tự tại VSDC |

### EquityPosition

| Trường | Kiểu | Mô tả |
|---|---|---|
| `AccountNo` | `string` | Số tài khoản |
| `Symbol` | `string` | Mã chứng khoán |
| `Quantity` | `int` | Tổng số lượng |
| `SellableQuantity` | `int` | Số lượng bán được |
| `CostPrice` | `double` | Giá vốn |
| `BuyingQuantity` / `SellingQuantity` | `int` | SL đang mua / đang bán |
| `BoughtQuantity` / `SoldQuantity` | `int` | Khối lượng đã mua / đã bán |
| `MortgageQuantity` | `int` | SL cầm cố |
| `BlockQuantity` | `int` | Khối lượng phong toả |
| `DividendQuantity` | `int` | Khối lượng cổ tức |
| `T1SellQuantity` / `T2SellQuantity` | `int` | KL bán T1 / T2 |
| `RestrictedQuantity` | `int` | Khối lượng hạn chế |

### DerivativePosition

| Trường | Kiểu | Mô tả |
|---|---|---|
| `AccountNo` | `string` | Số tài khoản |
| `Symbol` | `string` | Mã hợp đồng |
| `Long` / `Short` / `Net` | `int` | Vị thế mua / bán / ròng |
| `BidAvgPrice` / `AskAvgPrice` | `double` | Giá TB mua / bán |
| `TradePrice` | `double` | Giá giao dịch |
| `FloatingPL` / `TradingPL` | `double` | Lãi/lỗ |

### AllDerivativePosition

| Trường | Kiểu | Mô tả |
|---|---|---|
| `OpenPositions` | `List<DerivativePosition>` | Vị thế đang mở |
| `ClosedPositions` | `List<DerivativePosition>` | Vị thế đã đóng |

### Order

| Trường | Kiểu | Mô tả |
|---|---|---|
| `AccountNo` | `string` | Số tài khoản |
| `ClientRequestId` | `string` | ID yêu cầu client |
| `OrderId` | `string` | ID lệnh |
| `Symbol` | `string` | Mã chứng khoán |
| `Side` | `string` | Mua/Bán |
| `OrderType` | `string` | Loại lệnh |
| `Price` / `AvgPrice` | `double` | Giá đặt / Giá TB khớp |
| `Quantity` | `int` | SL đặt |
| `OsQuantity` | `int` | SL chờ |
| `FilledQuantity` | `int` | SL đã khớp |
| `CancelQuantity` | `int` | SL đã huỷ |
| `Status` | `string` | Trạng thái lệnh |
| `InputTime` / `ModifyTime` | `string` | Thời gian đặt / sửa |
| `Message` | `string` | Thông báo |

### EquityPPMMR / DerivativePPMMR

Hai model chứa rất nhiều chỉ số ký quỹ chi tiết (margin ratio, limit, collateral, ...). Các trường thường dùng nhất:

| Trường | Kiểu | Mô tả |
|---|---|---|
| `AccountNo` | `string` | Số tài khoản |
| `PurchasingPower` _(EquityPPMMR)_ | `double` | Sức mua |
| `Withdrawable` | `double` | Tiền/tài sản rút được |
| `MarginRatio` | `double` | Tỷ lệ ký quỹ |
| `TotalEquity` | `double` | Tổng tài sản ròng |
| `AccountBalance` _(DerivativePPMMR)_ | `double` | Số dư tài khoản phái sinh |

## Trading Responses

### PlaceOrderResponse

`OrderId`, `ClientRequestId`, `Status` — đều `string`.

### ModifyOrderResponse

`ClientModifyId`, `OrderId`, `ClientRequestId`, `Status` — đều `string`.

### CancelOrderResponse

`ClientCancelId`, `OrderId`, `ClientRequestId`, `Status` — đều `string`.

### MaxBuySellResponse

| Trường | Kiểu | Mô tả |
|---|---|---|
| `AccountNo` | `string` | Số tài khoản |
| `Symbol` | `string` | Mã chứng khoán |
| `MaxBuyQuantity` | `int` | SL mua tối đa |
| `MaxSellQuantity` | `int` | SL bán tối đa |
| `MarginRatio` | `string` | Tỷ lệ ký quỹ |
| `PurchasePower` | `string` | Sức mua |

## Lệnh điều kiện (FCO)

### FCOPlaceResponse

Kết quả đặt lệnh điều kiện — `FCOID` (`string`).

### FCOCancelResponse

Kết quả huỷ lệnh điều kiện — `FCOID` (`string`).

### FCOListResponse

Danh sách lệnh điều kiện (phân trang).

| Trường | Kiểu | Mô tả |
|---|---|---|
| `PageIndex` | `int` | Trang hiện tại |
| `PageSize` | `int` | Kích thước trang |
| `ItemsCount` | `int` | Tổng số bản ghi |
| `PagesCount` | `int` | Tổng số trang |
| `FCOList` | `List<FCOInfo>` | Danh sách lệnh FCO |

### FCOInfo

Thông tin chi tiết một lệnh điều kiện.

| Trường | Kiểu | Mô tả |
|---|---|---|
| `FCOID` | `string` | Mã lệnh FCO |
| `ClientID` | `string` | Username / Client ID |
| `AccountNo` | `string` | Số tài khoản |
| `Quantity` | `int` | Khối lượng đặt |
| `Price` | `string` | Giá đặt |
| `PriceSlip` | `double` | Độ trượt giá |
| `Symbol` | `string` | Mã chứng khoán |
| `Type` | `string` | Loại lệnh điều kiện (xem `FCOType`) |
| `FromDate` | `string` | Ngày bắt đầu hiệu lực |
| `ToDate` | `string` | Ngày kết thúc hiệu lực |
| `MatchedQuantity` | `int` | Khối lượng đã khớp |
| `IsPlaceOrder` | `bool` | Đã đẩy lệnh vào sổ hay chưa |
| `Status` | `string` | Trạng thái lệnh FCO (xem `FCOStatus`) |
| `Detail` | `string` | Chi tiết trạng thái |
| `Params` | `FCOParams?` | Tham số kích hoạt lệnh FCO |

### FCOParams

Tham số kích hoạt của lệnh điều kiện.

| Trường | Kiểu | Mô tả |
|---|---|---|
| `StopPrice` | `double` | Giá dừng / giá kích hoạt |
| `Side` | `string` | Chiều lệnh (Mua/Bán) |
| `ActivePrice` | `double` | Giá kích hoạt (Trailing Stop) |
| `TrailingAmount` | `double` | Khoảng bám sát (Trailing Amount) |
| `TPActivePrice` | `double` | Giá kích hoạt chốt lời (Take Profit) |
| `SLActivePrice` | `double` | Giá kích hoạt cắt lỗ (Stop Loss) |
| `TPPrice` | `string` | Giá chốt lời |
| `SLPrice` | `string` | Giá cắt lỗ |
| `TPSlip` | `double` | Trượt giá chốt lời |
| `SLSlip` | `double` | Trượt giá cắt lỗ |
| `Operator` | `string` | Toán tử so sánh kích hoạt (xem `FCOOperator`) |

### FCOOrderBookResponse

Nhật ký khớp lệnh FCO (phân trang).

| Trường | Kiểu | Mô tả |
|---|---|---|
| `PageIndex` | `int` | Trang hiện tại |
| `PageSize` | `int` | Kích thước trang |
| `ItemsCount` | `int` | Tổng số bản ghi |
| `PagesCount` | `int` | Tổng số trang |
| `OrderBook` | `List<FCOOrder>` | Danh sách nhật ký lệnh FCO |

### FCOOrder

Nhật ký giao dịch / thực thi của lệnh FCO.

| Trường | Kiểu | Mô tả |
|---|---|---|
| `FCOID` | `string` | Mã lệnh FCO gốc |
| `AccountNo` | `string` | Số tài khoản |
| `Quantity` | `double` | Khối lượng |
| `Price` | `string` | Giá đặt |
| `Symbol` | `string` | Mã chứng khoán |
| `Side` | `string` | Chiều lệnh |
| `OrderType` | `string` | Loại lệnh con |
| `IsMainOrder` | `bool` | Là lệnh chính |
| `IsAttachedOrder` | `bool` | Là lệnh kèm theo |
| `CreatedTime` / `UpdatedTime` | `string` | Thời gian tạo / cập nhật |
| `UniqueID` | `string` | ID duy nhất |
| `OrderID` | `string` | Mã lệnh trên sàn |
| `MatchedQuantity` | `double` | Khối lượng đã khớp |
| `OSQuantity` | `double` | Khối lượng chờ khớp |
| `AvgPrice` | `double` | Giá khớp trung bình |
| `Status` | `string` | Trạng thái lệnh con |
| `Detail` | `string` | Chi tiết |

## Streaming Messages

### TradeMessage

`Type`, `TradingTime`, `Symbol`, `Price`, `Quantity`, `Side`, `TotalVolume`

### IntervalMessage

| Trường | Kiểu | Mô tả |
|---|---|---|
| `Type` | `string` | Loại dữ liệu |
| `IntervalTime` | `string` | Thời gian interval |
| `TradingTime` | `string` | Thời gian giao dịch |
| `Symbol` | `string` | Mã chứng khoán |
| `Open` / `High` / `Low` / `Close` | `double` | Giá OHLC |
| `Volume` | `int` | Khối lượng |

### QuoteMessage

`Type`, `TradingTime`, `Symbol`, `BidPrices: List<double>`, `BidVolumes: List<int>`, `AskPrices: List<double>`, `AskVolumes: List<int>`

### ForeignRoomMessage

`Type`, `TradingTime`, `Symbol`, `TotalRoom`, `CurrentRoom`, `BuyQuantity`, `BuyValue`, `SellQuantity`, `SellValue`

### PutMessage

`Type`, `TradingTime`, `Symbol`, `Price`, `Quantity`, `TotalQuantity`, `TotalValue`

### OddLotMessage

`Type`, `TradingTime`, `Symbol`, `Price`, `Quantity`, `BidPrices`, `BidVolumes`, `AskPrices`, `AskVolumes`

### MarketStatusMessage

`Market`, `Status`, `TradingDate`

### OrderStatusMessage

`Type`, `AccountNo`, `ClientRequestId`, `OrderId`, `Symbol`, `Side`, `OrderType`, `Price`, `Quantity`, `OsQuantity`, `FilledQuantity`, `CancelQuantity`, `Status`, `InputTime`, `ModifyTime`, `Message`

### PortfolioMessage

`Type`, `AccountNo`, `TotalAsset`, `CashBalance`, `StockValue`

### FCOOrderUpdateMessage

Cập nhật trạng thái lệnh điều kiện FCO (streaming, nhận qua `SetOnTrading` khi `EventType == "fcoEvent"`, hoặc qua topic `fco_order.*`/`fco.*`).

| Trường | Kiểu | Mô tả |
|---|---|---|
| `FCOID` | `string` | Mã lệnh FCO |
| `ProcessStatus` | `string` | Trạng thái xử lý lệnh FCO (`INIT`, `WAIT`, `WC`, `TER`, ... — xem `FCOStatus`) |
| `MatchedQuantity` | `int` | Khối lượng đã khớp |
| `IsPlaceOrder` | `bool` | Đã đẩy lệnh vào sổ hay chưa |
| `Symbol` | `string` | Mã chứng khoán |
| `Quantity` | `int` | Khối lượng đặt |
| `Price` | `string` | Giá đặt |
| `AccountNo` | `string` | Số tài khoản |
| `UpdatedTime` | `string` | Thời gian cập nhật |
| `Status` | `string` | Mã trạng thái |
| `Message` | `string` | Thông báo chi tiết / lý do kích hoạt |
| `Username` | `string` | Username đặt lệnh |
| `EventType` | `string` | Loại sự kiện (`"fcoEvent"`) |
| `FCOType` | `string` | Loại lệnh điều kiện (`gtd`, `stop`, ... — xem `FCOType`) |

### HeartbeatMessage

`Method`, `Channel`, `Status`, `Message`
