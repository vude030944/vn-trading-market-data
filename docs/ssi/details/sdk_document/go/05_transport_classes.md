<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/go/transport-classes
Tieu de goc: Enums & Hằng số
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/go/transport-classes>

# Enums & Hằng số

Các kiểu enum và hằng số trong Go SDK

Enum được tổ chức theo package:
```python
import (
    "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/trading"
    "github.com/SSI-Securities-Inc/ssi-sdk-go/v3/market"
)
```

## OrderSide

Package: `trading`

| Giá trị | Code | Mô tả |
|---|---|---|
| `OrderSideBuy` | `"B"` | Mua |
| `OrderSideSell` | `"S"` | Bán |

## OrderType

Package: `trading`

| Giá trị | Code | Mô tả |
|---|---|---|
| `OrderTypeLO` | `"LO"` | Lệnh giới hạn |
| `OrderTypeMTL` | `"MTL"` | Market To Limit |
| `OrderTypeMP` | `"MP"` | Lệnh thị trường |
| `OrderTypeATO` | `"ATO"` | Lệnh mở cửa |
| `OrderTypeATC` | `"ATC"` | Lệnh đóng cửa |
| `OrderTypeMOK` | `"MOK"` | Match Or Kill |
| `OrderTypeMAK` | `"MAK"` | Match And Kill |
| `OrderTypePLO` | `"PLO"` | Lệnh sau giờ nghỉ trưa |

## OrderStatus

Package: `trading`

| Giá trị | Code | Mô tả |
|---|---|---|
| `OrderStatusPending` | `"PD"` | Chờ xử lý |
| `OrderStatusPendingApproval` | `"WA"` | Chờ phê duyệt |
| `OrderStatusReady` | `"RS"` | Sẵn sàng |
| `OrderStatusSent` | `"SD"` | Đã gửi |
| `OrderStatusQueued` | `"QU"` | Đã vào hàng đợi |
| `OrderStatusFilled` | `"FF"` | Khớp toàn bộ |
| `OrderStatusPartialFilled` | `"PF"` | Khớp một phần |
| `OrderStatusPartialCancelled` | `"FFPC"` | Khớp một phần + huỷ phần còn lại |
| `OrderStatusPendingModify` | `"WM"` | Chờ sửa |
| `OrderStatusPendingCancel` | `"WC"` | Chờ huỷ |
| `OrderStatusCancelled` | `"CL"` | Đã huỷ |
| `OrderStatusRejected` | `"RJ"` | Bị từ chối |
| `OrderStatusExpired` | `"EX"` | Hết hạn |
| `OrderStatusPreSession` | `"IAV"` | Trước phiên |

## Board

Package: `market`

| Giá trị | Code | Mô tả |
|---|---|---|
| `BoardHOSE` | `"HOSE"` | Sàn HOSE |
| `BoardHNX` | `"HNX"` | Sàn HNX |
| `BoardUPCOM` | `"UPCOM"` | Sàn UPCOM |

## Timeframe

Package: `market`

| Giá trị | Code | Mô tả |
|---|---|---|
| `TimeframeMinute1` | `"1m"` | 1 phút |
| `TimeframeMinute3` | `"3m"` | 3 phút |
| `TimeframeMinute5` | `"5m"` | 5 phút |
| `TimeframeMinute15` | `"15m"` | 15 phút |
| `TimeframeHour1` | `"1h"` | 1 giờ |
| `TimeframeDay1` | `"1d"` | 1 ngày |
| `TimeframeWeek1` | `"1w"` | 1 tuần |
| `TimeframeMonth1` | `"1M"` | 1 tháng |

## FCOType

Loại lệnh điều kiện (Flexible Conditional Order).

Package: `trading`

| Giá trị | Code | Mô tả |
|---|---|---|
| `FCOTypeGTD` | `"gtd"` | Lệnh có hiệu lực đến ngày (Good Till Date) |
| `FCOTypeStop` | `"stop"` | Lệnh dừng thị trường (Stop Market) |
| `FCOTypeStopLimit` | `"stop_limit"` | Lệnh dừng giới hạn (Stop Limit) |
| `FCOTypeTrailingStop` | `"trailing_stop"` | Lệnh xu hướng (Trailing Stop Market) |
| `FCOTypeTrailingStopLimit` | `"trailing_stop_limit"` | Lệnh xu hướng giới hạn (Trailing Stop Limit) |
| `FCOTypeOCO` | `"oco"` | Lệnh huỷ lệnh còn lại (One Cancels the Other) |
| `FCOTypeBullBear` | `"bullbear"` | Lệnh Bull Bear |

## FCOOperator

Toán tử so sánh dùng để kích hoạt lệnh Stop / Stop Limit.

Package: `trading`

| Giá trị | Code | Mô tả |
|---|---|---|
| `FCOOperatorGreater` | `"greater"` | Lớn hơn (`>`) |
| `FCOOperatorGreaterOrEqual` | `"greater_or_equal"` | Lớn hơn hoặc bằng (`>=`) |
| `FCOOperatorLesser` | `"lesser"` | Nhỏ hơn (`<`) |
| `FCOOperatorLesserOrEqual` | `"lesser_or_equal"` | Nhỏ hơn hoặc bằng (`<=`) |
| `FCOOperatorEqual` | `"equal"` | Bằng (`=`) |

## FCOStatus

Trạng thái xử lý của lệnh điều kiện.

Package: `trading`

| Giá trị | Code | Mô tả |
|---|---|---|
| `FCOStatusInit` | `"INIT"` | Mới khởi tạo |
| `FCOStatusWait` | `"WAIT"` | Chờ kích hoạt |
| `FCOStatusTri` | `"TRI"` | Đã kích hoạt |
| `FCOStatusTrit` | `"TRIT"` | Đã kích hoạt thành công |
| `FCOStatusTer` | `"TER"` | Đã kết thúc |
| `FCOStatusFis` | `"FIS"` | Hoàn tất |
| `FCOStatusWc` | `"WC"` | Chờ huỷ |
| `FCOStatusExp` | `"EXP"` | Hết hạn |
| `FCOStatusErr` | `"ERR"` | Lỗi |

## Tổng hợp Package

| Package | Import | Chứa |
|---|---|---|
| `trading` | `.../ssi-sdk-go/v3/trading` | `OrderSide`, `OrderType`, `OrderStatus`, `FCOType`, `FCOOperator`, `FCOStatus` |
| `market` | `.../ssi-sdk-go/v3/market` | `Board`, `Timeframe` |
