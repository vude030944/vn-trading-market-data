<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/python/transport-classes
Tieu de goc: Enums & Hằng số
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/python/transport-classes>

# Enums & Hằng số

Các enum và hằng số trong Python SDK

Tất cả enum import từ `ssi_sdk.enums`:
```python
from ssi_sdk.enums import OrderSide, OrderType, OrderStatus, Board, AccountType, Timeframe
```

## OrderSide

| Giá trị | Value | Mô tả |
|---|---|---|
| `BUY` | `"B"` | Mua |
| `SELL` | `"S"` | Bán |

## OrderType

| Giá trị | Value | Mô tả |
|---|---|---|
| `LO` | `"LO"` | Lệnh giới hạn (Limit Order) |
| `MTL` | `"MTL"` | Market To Limit |
| `MP` | `"MP"` | Market Price |
| `ATO` | `"ATO"` | Lệnh mở cửa (At The Open) |
| `ATC` | `"ATC"` | Lệnh đóng cửa (At The Close) |
| `MOK` | `"MOK"` | Match Or Kill |
| `MAK` | `"MAK"` | Match And Kill |
| `PLO` | `"PLO"` | Post Lunch Order |

## OrderStatus

| Giá trị | Value | Mô tả |
|---|---|---|
| `PENDING` | `"PD"` | Đang chờ |
| `PENDING_APPROVAL` | `"WA"` | Chờ duyệt |
| `READY` | `"RS"` | Sẵn sàng |
| `SENT` | `"SD"` | Đã gửi |
| `QUEUED` | `"QU"` | Đã xếp hàng |
| `FILLED` | `"FF"` | Khớp toàn bộ |
| `PARTIAL_FILLED` | `"PF"` | Khớp một phần |
| `PARTIAL_CANCELLED` | `"FFPC"` | Khớp một phần + huỷ phần còn lại |
| `PENDING_MODIFY` | `"WM"` | Chờ sửa |
| `PENDING_CANCEL` | `"WC"` | Chờ huỷ |
| `CANCELLED` | `"CL"` | Đã huỷ |
| `REJECTED` | `"RJ"` | Bị từ chối |
| `EXPIRED` | `"EX"` | Hết hạn |
| `PRE_SESSION` | `"IAV"` | Phiên trước |

## Board

| Giá trị | Value | Mô tả |
|---|---|---|
| `HOSE` | `"HOSE"` | Sàn HOSE |
| `HNX` | `"HNX"` | Sàn HNX |
| `UPCOM` | `"UPCOM"` | Sàn UPCOM |

## AccountType

| Giá trị | Value | Mô tả |
|---|---|---|
| `EQUITY` | `"Cash"` | Tài khoản cơ sở |
| `EQUITY_MARGIN` | `"Margin"` | Tài khoản ký quỹ |
| `DERIVATIVE` | `"Derivative"` | Tài khoản phái sinh |

## Timeframe

| Giá trị | Value | Mô tả |
|---|---|---|
| `MINUTE_1` | `"1m"` | 1 phút |
| `MINUTE_3` | `"3m"` | 3 phút |
| `MINUTE_5` | `"5m"` | 5 phút |
| `MINUTE_15` | `"15m"` | 15 phút |
| `HOUR_1` | `"1h"` | 1 giờ |
| `DAY_1` | `"1d"` | 1 ngày |
| `WEEK_1` | `"1w"` | 1 tuần |
| `MONTH_1` | `"1M"` | 1 tháng |

## FCOType

Loại lệnh điều kiện (Flexible Conditional Order).

| Giá trị | Value | Mô tả |
|---|---|---|
| `GTD` | `"gtd"` | Lệnh có hiệu lực đến ngày (Good Till Date) |
| `STOP` | `"stop"` | Lệnh dừng thị trường (Stop Market) |
| `STOP_LIMIT` | `"stop_limit"` | Lệnh dừng giới hạn (Stop Limit) |
| `TRAILING_STOP` | `"trailing_stop"` | Lệnh xu hướng (Trailing Stop Market) |
| `TRAILING_STOP_LIMIT` | `"trailing_stop_limit"` | Lệnh xu hướng giới hạn (Trailing Stop Limit) |
| `OCO` | `"oco"` | Lệnh huỷ lệnh còn lại (One Cancels the Other) |
| `BULL_BEAR` | `"bullbear"` | Lệnh Bull Bear |

## FCOOperator

Toán tử so sánh dùng để kích hoạt lệnh Stop / Stop Limit.

| Giá trị | Value | Mô tả |
|---|---|---|
| `GREATER` | `"greater"` | Lớn hơn (`>`) |
| `GREATER_OR_EQUAL` | `"greater_or_equal"` | Lớn hơn hoặc bằng (`>=`) |
| `LESSER` | `"lesser"` | Nhỏ hơn (`<`) |
| `LESSER_OR_EQUAL` | `"lesser_or_equal"` | Nhỏ hơn hoặc bằng (`<=`) |
| `EQUAL` | `"equal"` | Bằng (`=`) |

## FCOStatus

Trạng thái xử lý của lệnh điều kiện.

| Giá trị | Value | Mô tả |
|---|---|---|
| `INIT` | `"INIT"` | Mới khởi tạo |
| `WAIT` | `"WAIT"` | Chờ kích hoạt |
| `TRI` | `"TRI"` | Đã kích hoạt |
| `TRIT` | `"TRIT"` | Đã kích hoạt thành công |
| `TER` | `"TER"` | Đã kết thúc |
| `FIS` | `"FIS"` | Hoàn tất |
| `WC` | `"WC"` | Chờ huỷ |
| `EXP` | `"EXP"` | Hết hạn |
| `ERR` | `"ERR"` | Lỗi |
