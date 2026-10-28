<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/nodejs/utilities
Tieu de goc: Models
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/nodejs/utilities>

# Models

Các interface TypeScript và message streaming trong Node.js SDK

Tất cả model là TypeScript interface. Import từ package chính.

## Cấu trúc Module
```text
@ssi.developer/ssi-sdk
├── Auth, Data, Trading, Stream  (client classes)
├── Config                        (cấu hình)
├── models/
│   ├── auth        → Token
│   ├── account     → Account
│   ├── marketData  → OHLCData, MarketIndexes, MarketIndexSummary, SecuritiesInfo, SecuritiesSummary
│   ├── trading     → PlaceOrderResponse, ModifyOrderResponse, CancelOrderResponse, MaxBuySellResponse
│   ├── portfolio   → EquityAccountBalance, DerivativeAccountBalance, EquityPosition, DerivativePosition, Order
│   ├── streaming   → DataMessage, TradingMessage, HeartbeatMessage, FCOOrderUpdateMessage
│   └── fco         → FCOInfo, FCOParams, FCOListResponse, FCOOrder, FCOOrderBookResponse, FCOPlaceResponse, FCOCancelResponse
├── enums/          → OrderSide, OrderType, Board, Timeframe, FCOType, FCOOperator, FCOStatus, ...
└── exceptions      → SSIError, APIError, AuthenticationError, ...
```

## Xác thực

### Token

| Field | Kiểu | Mô tả |
|---|---|---|
| `accessToken` | `string` | Access token |
| `tokenType` | `string` | Loại token (mặc định `"Bearer"`) |
| `expiresAt` | `number` | Timestamp hết hạn |
| `refreshToken` | `string` | Refresh token |
| `refreshTokenExpiresAt` | `number` | Timestamp hết hạn refresh token |

## Tài khoản

### Account

| Field | Kiểu | Mô tả |
|---|---|---|
| `accountNo` | `string` | Số tài khoản |
| `accountType` | `string` | Loại tài khoản |

## Dữ liệu thị trường

### OHLCData

| Field | Kiểu | Mô tả |
|---|---|---|
| `symbol` | `string` | Mã chứng khoán |
| `tradingDate` | `string` | Ngày giao dịch |
| `openPrice` | `number` | Giá mở |
| `highPrice` | `number` | Giá cao |
| `lowPrice` | `number` | Giá thấp |
| `closePrice` | `number` | Giá đóng |
| `volume` | `number` | Khối lượng |
| `value` | `number` | Giá trị giao dịch |

### MarketIndexes

| Field | Kiểu | Mô tả |
|---|---|---|
| `index` | `string` | Mã chỉ số |
| `indexName` | `string` | Tên chỉ số |
| `board` | `string` | Sàn |

### MarketIndexSummary

| Field | Kiểu | Mô tả |
|---|---|---|
| `tradingDate` | `string` | Ngày giao dịch |
| `indexValue` | `number` | Giá trị chỉ số |
| `indexChange` | `number` | Thay đổi |
| `indexChangePercent` | `number` | Thay đổi (%) |
| `totalTrade` | `number` | Tổng khối lượng giao dịch |
| `totalTradeValue` | `number` | Tổng giá trị giao dịch |
| `totalAdvanceStock` | `number` | Số CP tăng |
| `totalDeclineStock` | `number` | Số CP giảm |
| `totalSteadyStock` | `number` | Số CP không đổi |
| `totalMatch` | `number` | Tổng khối lượng khớp |
| `totalMatchValue` | `number` | Tổng giá trị khớp |
| `totalDeal` | `number` | Tổng khối lượng thoả thuận |
| `totalDealValue` | `number` | Tổng giá trị thoả thuận |
| `totalCeilingStock` | `number` | Số CP trần |
| `totalFloorStock` | `number` | Số CP sàn |
| `totalPropBuy` | `number` | Tổng KL mua tự doanh |
| `totalPropBuyValue` | `number` | Tổng GT mua tự doanh |
| `totalPropSell` | `number` | Tổng KL bán tự doanh |
| `totalPropSellValue` | `number` | Tổng GT bán tự doanh |

### SecuritiesInfo

| Field | Kiểu | Mô tả |
|---|---|---|
| `symbol` | `string` | Mã chứng khoán |
| `board` | `string` | Sàn |
| `index` | `string` | Chỉ số |
| `symbolNameVi` | `string` | Tên tiếng Việt |
| `symbolNameEn` | `string` | Tên tiếng Anh |
| `lotSize` | `number` | Lô giao dịch |
| `listedShares` | `number` | Số CP niêm yết |
| `icbCode` | `string` | Mã ICB |
| `icbName` | `string` | Tên ICB |
| `maturityDate` | `string` | Ngày đáo hạn |
| `firstTradingDate` | `string` | Ngày GD đầu tiên |
| `lastTradingDate` | `string` | Ngày GD cuối cùng |
| `cwUnderlyingSymbol` | `string` | Mã CK cơ sở CW |
| `cwExercisePrice` | `number` | Giá thực hiện CW |
| `cwExecutionRatio` | `number` | Tỷ lệ thực hiện CW |
| `iIndex` | `number` | Chỉ số I |
| `iNav` | `number` | Giá trị iNAV |

### SecuritiesSummary

| Field | Kiểu | Mô tả |
|---|---|---|
| `symbol` | `string` | Mã chứng khoán |
| `tradingDate` | `string` | Ngày giao dịch |
| `priceChange` | `number` | Thay đổi giá |
| `priceChangePercent` | `number` | Thay đổi giá (%) |
| `openPrice` | `number` | Giá mở |
| `highPrice` | `number` | Giá cao |
| `lowPrice` | `number` | Giá thấp |
| `closePrice` | `number` | Giá đóng |
| `totalMatch` | `number` | Tổng khối lượng khớp |
| `totalMatchValue` | `number` | Tổng giá trị khớp |
| `averagePrice` | `number` | Giá trung bình |
| `totalBuy` | `number` | Tổng KL mua |
| `totalTradeBuy` | `number` | Tổng GT mua |
| `totalSell` | `number` | Tổng KL bán |
| `totalTradeSell` | `number` | Tổng GT bán |

## Danh mục

### EquityAccountBalance

| Field | Kiểu | Mô tả |
|---|---|---|
| `accountNo` | `string` | Số tài khoản |
| `accountBalance` | `number` | Số dư tài khoản |
| `totalDebt` | `number` | Tổng nợ |
| `interestLoan` | `number` | Lãi vay |
| `overdueFeeLoan` | `number` | Phí quá hạn |
| `withdrawable` | `number` | Tiền rút được |
| `onHoldCash` | `number` | Tiền giữ |
| `sellUnmatched` | `number` | Bán chưa khớp |
| `sellT0` | `number` | Tiền bán T+0 |
| `sellT1` | `number` | Tiền bán T+1 |
| `sellT2` | `number` | Tiền bán T+2 |
| `buyUnmatched` | `number` | Mua chưa khớp |
| `buyT0` | `number` | Tiền mua T+0 |
| `buyT1` | `number` | Tiền mua T+1 |
| `buyT2` | `number` | Tiền mua T+2 |
| `advanceCashT0` | `number` | Ứng trước T+0 |
| `advanceCashT1` | `number` | Ứng trước T+1 |
| `holdSubscription` | `number` | Giữ đăng ký mua |

### DerivativeAccountBalance

| Field | Kiểu | Mô tả |
|---|---|---|
| `accountNo` | `string` | Số tài khoản |
| `accountBalance` | `number` | Số dư tài khoản |
| `fee` | `number` | Phí |
| `commission` | `number` | Hoa hồng |
| `interest` | `number` | Lãi |
| `extInterest` | `number` | Lãi mở rộng |
| `loan` | `number` | Khoản vay |
| `deliveryAmount` | `number` | Giá trị giao hàng |
| `floatingPl` | `number` | Lãi/lỗ chưa thực hiện |
| `tradingPl` | `number` | Lãi/lỗ giao dịch |
| `totalPl` | `number` | Tổng lãi/lỗ |
| `withdrawable` | `number` | Có thể rút |
| `cashSsi` | `number` | Tiền tại SSI |
| `validNonCashSsi` | `number` | Tài sản phi tiền mặt hợp lệ tại SSI |
| `cashWithdrawableSsi` | `number` | Tiền có thể rút tại SSI |
| `cashVsdc` | `number` | Tiền tại VSDC |
| `validNonCashVsdc` | `number` | Tài sản phi tiền mặt hợp lệ tại VSDC |
| `cashWithdrawableVsdc` | `number` | Tiền có thể rút tại VSDC |

### EquityPosition

| Field | Kiểu | Mô tả |
|---|---|---|
| `accountNo` | `string` | Số tài khoản |
| `symbol` | `string` | Mã chứng khoán |
| `quantity` | `number` | Tổng khối lượng |
| `sellableQuantity` | `number` | Khối lượng bán được |
| `costPrice` | `number` | Giá vốn |
| `buyingQuantity` | `number` | Khối lượng đang mua |
| `sellingQuantity` | `number` | Khối lượng đang bán |
| `mortgageQuantity` | `number` | Khối lượng cầm cố |
| `blockQuantity` | `number` | Khối lượng phong toả |
| `dividendQuantity` | `number` | Khối lượng cổ tức |
| `boughtQuantity` | `number` | Khối lượng đã mua |
| `soldQuantity` | `number` | Khối lượng đã bán |
| `t1SellQuantity` | `number` | Khối lượng bán T+1 |
| `t2SellQuantity` | `number` | Khối lượng bán T+2 |
| `restrictedQuantity` | `number` | Khối lượng hạn chế |

### DerivativePosition

| Field | Kiểu | Mô tả |
|---|---|---|
| `accountNo` | `string` | Số tài khoản |
| `symbol` | `string` | Mã hợp đồng |
| `long` / `short` / `net` | `number` | Vị thế Long / Short / Net |
| `bidAvgPrice` / `askAvgPrice` | `number` | Giá TB mua / bán |
| `floatingPl` / `tradingPl` | `number` | Lãi/lỗ |
| `tradePrice` | `number` | Giá giao dịch |

### Order

| Field | Kiểu | Mô tả |
|---|---|---|
| `accountNo` | `string` | Số tài khoản |
| `clientRequestId` | `string` | Client request ID |
| `orderId` | `string` | Order ID |
| `symbol` | `string` | Mã chứng khoán |
| `side` | `string` | Mua/Bán |
| `orderType` | `string` | Loại lệnh |
| `price` / `avgPrice` | `number` | Giá đặt / Giá khớp TB |
| `quantity` | `number` | Khối lượng đặt |
| `osQuantity` | `number` | Khối lượng chờ |
| `filledQuantity` | `number` | Khối lượng khớp |
| `cancelQuantity` | `number` | Khối lượng huỷ |
| `status` | `string` | Trạng thái lệnh |
| `inputTime` / `modifyTime` | `string` | Thời gian đặt / sửa |
| `message` | `string` | Thông báo |

## Response giao dịch

### PlaceOrderResponse

`orderId`, `clientRequestId`, `status`

### ModifyOrderResponse

`clientModifyId`, `orderId`, `clientRequestId`, `status`

### CancelOrderResponse

`clientCancelId`, `orderId`, `clientRequestId`, `status`

### MaxBuySellResponse

`accountNo`, `symbol`, `maxBuyQuantity`, `maxSellQuantity`, `marginRatio`, `purchasePower`

## Lệnh điều kiện (FCO)

### FCOPlaceResponse

Kết quả đặt lệnh điều kiện — `fcoId`

### FCOCancelResponse

Kết quả huỷ lệnh điều kiện — `fcoId`

### FCOListResponse

Danh sách lệnh điều kiện (phân trang).

| Field | Kiểu | Mô tả |
|---|---|---|
| `pageIndex` | `number` | Trang hiện tại |
| `pageSize` | `number` | Kích thước trang |
| `itemsCount` | `number` | Tổng số bản ghi |
| `pagesCount` | `number` | Tổng số trang |
| `fcoList` | `FCOInfo[]` | Danh sách lệnh FCO |

### FCOInfo

Thông tin chi tiết một lệnh điều kiện.

| Field | Kiểu | Mô tả |
|---|---|---|
| `fcoId` | `string` | Mã lệnh FCO |
| `clientId` | `string` | Username / Client ID |
| `accountNo` | `string` | Số tài khoản |
| `quantity` | `number` | Khối lượng đặt |
| `price` | `string` | Giá đặt |
| `priceSlip` | `string` | Độ trượt giá |
| `symbol` | `string` | Mã chứng khoán |
| `type` | `FCOType?` | Loại lệnh điều kiện |
| `fromDate` | `string` | Ngày bắt đầu hiệu lực |
| `toDate` | `string` | Ngày kết thúc hiệu lực |
| `matchedQuantity` | `number` | Khối lượng đã khớp |
| `isPlaceOrder` | `boolean` | Đã đẩy lệnh vào sổ hay chưa |
| `status` | `FCOStatus?` | Trạng thái lệnh FCO |
| `detail` | `string` | Chi tiết trạng thái |
| `params` | `FCOParams?` | Tham số kích hoạt lệnh FCO |

### FCOParams

Tham số kích hoạt của lệnh điều kiện.

| Field | Kiểu | Mô tả |
|---|---|---|
| `stopPrice` | `number?` | Giá dừng / giá kích hoạt |
| `side` | `OrderSide?` | Chiều lệnh (Mua/Bán) |
| `activePrice` | `number?` | Giá kích hoạt (Trailing Stop) |
| `trailingAmount` | `number?` | Khoảng bám sát (Trailing Amount) |
| `tpActivePrice` | `number?` | Giá kích hoạt chốt lời (Take Profit) |
| `slActivePrice` | `number?` | Giá kích hoạt cắt lỗ (Stop Loss) |
| `tpPrice` | `string?` | Giá chốt lời |
| `slPrice` | `string?` | Giá cắt lỗ |
| `tpSlip` | `number?` | Trượt giá chốt lời |
| `slSlip` | `number?` | Trượt giá cắt lỗ |
| `operator` | `FCOOperator?` | Toán tử so sánh kích hoạt |

### FCOOrderBookResponse

Nhật ký khớp lệnh FCO (phân trang).

| Field | Kiểu | Mô tả |
|---|---|---|
| `pageIndex` | `number` | Trang hiện tại |
| `pageSize` | `number` | Kích thước trang |
| `itemsCount` | `number` | Tổng số bản ghi |
| `pagesCount` | `number` | Tổng số trang |
| `orderBook` | `FCOOrder[]` | Danh sách nhật ký lệnh FCO |

### FCOOrder

Nhật ký giao dịch / thực thi của lệnh FCO.

| Field | Kiểu | Mô tả |
|---|---|---|
| `fcoId` | `string` | Mã lệnh FCO gốc |
| `accountNo` | `string` | Số tài khoản |
| `quantity` | `number` | Khối lượng |
| `price` | `string` | Giá đặt |
| `symbol` | `string` | Mã chứng khoán |
| `side` | `OrderSide?` | Chiều lệnh |
| `orderType` | `OrderType?` | Loại lệnh con |
| `isMainOrder` | `boolean` | Là lệnh chính |
| `isAttachedOrder` | `boolean` | Là lệnh kèm theo |
| `createdTime` / `updatedTime` | `string` | Thời gian tạo / cập nhật |
| `uniqueId` | `string` | ID duy nhất |
| `orderId` | `string` | Mã lệnh trên sàn |
| `matchedQuantity` | `number` | Khối lượng đã khớp |
| `osQuantity` | `number` | Khối lượng chờ khớp |
| `avgPrice` | `number` | Giá khớp trung bình |
| `status` | `OrderStatus?` | Trạng thái lệnh con |
| `detail` | `string` | Chi tiết |

## Message Streaming

### DataMessage

Dữ liệu thị trường nhận qua callback `onData`. Phân biệt loại bằng trường `type`:

  * `trade` — dữ liệu khớp lệnh
  * `quote` — dữ liệu mua/bán
  * `room` — room ngoại
  * `market` — trạng thái thị trường
  * `put` — thoả thuận
  * `oddlot` — lô lẻ

### TradingMessage

Sự kiện giao dịch nhận qua callback `onTrading`. Phân biệt loại bằng trường `type`:

  * `orderEvent` — cập nhật trạng thái lệnh thường (`OrderStatusMessage`)
  * `orderMatchEvent` — sự kiện khớp lệnh
  * `clientPortfolioEvent` — thay đổi danh mục (`PortfolioMessage`)
  * `fcoOrderEvent` — cập nhật trạng thái lệnh điều kiện FCO (`FCOOrderUpdateMessage`)

### FCOOrderUpdateMessage

Cập nhật trạng thái lệnh điều kiện FCO (streaming, nhận qua `onTrading`).

| Field | Kiểu | Mô tả |
|---|---|---|
| `type` | `"fcoOrderEvent"` | Loại message |
| `fcoId` | `string` | Mã lệnh FCO |
| `processStatus` | `FCOStatus?` | Trạng thái xử lý lệnh FCO (`INIT`, `WAIT`, `WC`, `TER`, ...) |
| `matchedQuantity` | `number` | Khối lượng đã khớp |
| `isPlaceOrder` | `boolean` | Đã đẩy lệnh vào sổ hay chưa |
| `symbol` | `string` | Mã chứng khoán |
| `quantity` | `number` | Khối lượng đặt |
| `price` | `string` | Giá đặt |
| `accountNo` | `string` | Số tài khoản |
| `updatedTime` | `string` | Thời gian cập nhật |
| `status` | `string` | Mã trạng thái |
| `message` | `string` | Thông báo chi tiết / lý do kích hoạt, ngắt kết nối |
| `username` | `string` | Username đặt lệnh |
| `eventType` | `string` | Loại sự kiện (ví dụ `"fcoEvent"`) |
| `fcoType` | `FCOType?` | Loại lệnh điều kiện (`GTD`, `STOP`, ...) |

### HeartbeatMessage

`method`, `channel`, `status`, `message`

### IntervalMessage

| Field | Kiểu | Mô tả |
|---|---|---|
| `type` | `string` | Loại message |
| `intervalTime` | `string` | Thời gian interval |
| `tradingTime` | `string` | Thời gian giao dịch |
| `symbol` | `string` | Mã chứng khoán |
| `open` | `number` | Giá mở |
| `high` | `number` | Giá cao |
| `low` | `number` | Giá thấp |
| `close` | `number` | Giá đóng |
| `volume` | `number` | Khối lượng |
