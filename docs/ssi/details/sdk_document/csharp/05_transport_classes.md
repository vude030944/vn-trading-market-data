<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/csharp/transport-classes
Tieu de goc: Enums & Hằng số
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/csharp/transport-classes>

# Enums & Hằng số

Các hằng số dùng như enum trong .NET SDK

SDK biểu diễn các giá trị cố định (order side, order type, board, ...) bằng **static class chứa hằng số`string`** thay vì `enum` chuẩn của C#. Cách này giữ nguyên giá trị string gửi/nhận trực tiếp với API, không cần convert qua lại.
```text
using SsiSdk;

var side = OrderSide.Buy;      // "B"
var board = Board.HOSE;        // "HOSE"
```

Tất cả nằm trong namespace `SsiSdk` — không cần import riêng.

## OrderSide

| Hằng số | Value | Mô tả |
|---|---|---|
| `OrderSide.Buy` | `"B"` | Mua |
| `OrderSide.Sell` | `"S"` | Bán |

## OrderType

| Hằng số | Value | Mô tả |
|---|---|---|
| `OrderType.LO` | `"LO"` | Lệnh giới hạn (Limit Order) |
| `OrderType.MTL` | `"MTL"` | Market To Limit |
| `OrderType.MP` | `"MP"` | Market Price |
| `OrderType.ATO` | `"ATO"` | Lệnh mở cửa (At The Open) |
| `OrderType.ATC` | `"ATC"` | Lệnh đóng cửa (At The Close) |
| `OrderType.MOK` | `"MOK"` | Match Or Kill |
| `OrderType.MAK` | `"MAK"` | Match And Kill |
| `OrderType.PLO` | `"PLO"` | Post Lunch Order |

## OrderStatus

| Hằng số | Value | Mô tả |
|---|---|---|
| `OrderStatus.Pending` | `"PD"` | Đang chờ |
| `OrderStatus.PendingApproval` | `"WA"` | Chờ duyệt |
| `OrderStatus.Ready` | `"RS"` | Sẵn sàng |
| `OrderStatus.Sent` | `"SD"` | Đã gửi |
| `OrderStatus.Queued` | `"QU"` | Đã xếp hàng |
| `OrderStatus.Filled` | `"FF"` | Khớp toàn bộ |
| `OrderStatus.PartialFilled` | `"PF"` | Khớp một phần |
| `OrderStatus.PartialCancelled` | `"FFPC"` | Khớp một phần + huỷ phần còn lại |
| `OrderStatus.PendingModify` | `"WM"` | Chờ sửa |
| `OrderStatus.PendingCancel` | `"WC"` | Chờ huỷ |
| `OrderStatus.Cancelled` | `"CL"` | Đã huỷ |
| `OrderStatus.Rejected` | `"RJ"` | Bị từ chối |
| `OrderStatus.Expired` | `"EX"` | Hết hạn |
| `OrderStatus.PreSession` | `"IAV"` | Phiên trước |

## Board

| Hằng số | Value | Mô tả |
|---|---|---|
| `Board.HOSE` | `"HOSE"` | Sàn HOSE |
| `Board.HNX` | `"HNX"` | Sàn HNX |
| `Board.UPCOM` | `"UPCOM"` | Sàn UPCOM |

## AccountType

| Hằng số | Value | Mô tả |
|---|---|---|
| `AccountType.Equity` | `"Cash"` | Tài khoản cơ sở |
| `AccountType.EquityMargin` | `"Margin"` | Tài khoản ký quỹ |
| `AccountType.Derivative` | `"Derivative"` | Tài khoản phái sinh |

## FCOType

Loại lệnh điều kiện (Flexible Conditional Order).

| Hằng số | Value | Mô tả |
|---|---|---|
| `FCOType.GTD` | `"gtd"` | Lệnh có hiệu lực đến ngày (Good Till Date) |
| `FCOType.Stop` | `"stop"` | Lệnh dừng thị trường (Stop Market) |
| `FCOType.StopLimit` | `"stop_limit"` | Lệnh dừng giới hạn (Stop Limit) |
| `FCOType.TrailingStop` | `"trailing_stop"` | Lệnh xu hướng (Trailing Stop Market) |
| `FCOType.TrailingStopLimit` | `"trailing_stop_limit"` | Lệnh xu hướng giới hạn (Trailing Stop Limit) |
| `FCOType.OCO` | `"oco"` | Lệnh huỷ lệnh còn lại (One Cancels the Other) |
| `FCOType.BullBear` | `"bullbear"` | Lệnh Bull Bear |

## FCOOperator

Toán tử so sánh dùng để kích hoạt lệnh Stop / Stop Limit.

| Hằng số | Value | Mô tả |
|---|---|---|
| `FCOOperator.Greater` | `"greater"` | Lớn hơn (`>`) |
| `FCOOperator.GreaterOrEqual` | `"greater_or_equal"` | Lớn hơn hoặc bằng (`>=`) |
| `FCOOperator.Lesser` | `"lesser"` | Nhỏ hơn (`<`) |
| `FCOOperator.LesserOrEqual` | `"lesser_or_equal"` | Nhỏ hơn hoặc bằng (`<=`) |
| `FCOOperator.Equal` | `"equal"` | Bằng (`=`) |

## FCOStatus

Trạng thái xử lý của lệnh điều kiện.

| Hằng số | Value | Mô tả |
|---|---|---|
| `FCOStatus.Init` | `"INIT"` | Mới khởi tạo |
| `FCOStatus.Wait` | `"WAIT"` | Chờ kích hoạt |
| `FCOStatus.Tri` | `"TRI"` | Đã kích hoạt |
| `FCOStatus.Trit` | `"TRIT"` | Đã kích hoạt thành công |
| `FCOStatus.Ter` | `"TER"` | Đã kết thúc |
| `FCOStatus.Fis` | `"FIS"` | Hoàn tất |
| `FCOStatus.Wc` | `"WC"` | Chờ huỷ |
| `FCOStatus.Exp` | `"EXP"` | Hết hạn |
| `FCOStatus.Err` | `"ERR"` | Lỗi |

## Timeframe

| Hằng số | Value | Mô tả |
|---|---|---|
| `Timeframe.Minute1` | `"1m"` | 1 phút |
| `Timeframe.Minute3` | `"3m"` | 3 phút |
| `Timeframe.Minute5` | `"5m"` | 5 phút |
| `Timeframe.Minute15` | `"15m"` | 15 phút |
| `Timeframe.Hour1` | `"1h"` | 1 giờ |
| `Timeframe.Day1` | `"1d"` | 1 ngày |
| `Timeframe.Week1` | `"1w"` | 1 tuần |
| `Timeframe.Month1` | `"1M"` | 1 tháng |

## DataType

Loại dữ liệu nhận qua `StreamingService.SetOnData` (dựa trên tiền tố topic).

| Hằng số | Value | Mô tả |
|---|---|---|
| `DataType.Trade` | `"trade"` | Khớp lệnh |
| `DataType.Quote` | `"quote"` | Giá mua/bán |
| `DataType.OddLot` | `"oddlot"` | Lô lẻ |
| `DataType.Market` | `"market"` | Trạng thái thị trường |
| `DataType.Room` | `"room"` | Room nước ngoài |
| `DataType.Put` | `"put"` | Thoả thuận |

## StreamingType

Loại sự kiện nhận qua `StreamingService.SetOnTrading`.

| Hằng số | Value | Mô tả |
|---|---|---|
| `StreamingType.Order` | `"orderEvent"` | Cập nhật trạng thái lệnh |
| `StreamingType.OrderMatch` | `"orderMatchEvent"` | Sự kiện khớp lệnh |
| `StreamingType.Portfolio` | `"clientPortfolioEvent"` | Thay đổi danh mục |
| `StreamingType.FCOOrder` | `"fcoOrderEvent"` | Cập nhật trạng thái lệnh điều kiện (FCO) |
