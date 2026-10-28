<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/nodejs/transport-classes
Tieu de goc: Enums & Hằng số
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/nodejs/transport-classes>

# Enums & Hằng số

Các kiểu enum và hằng số trong Node.js SDK

Tất cả enum được export từ package chính:
```python
import { OrderSide, OrderType, OrderStatus, Board, Timeframe, AccountType, DataType, FCOType, FCOOperator, FCOStatus } from '@ssi.developer/ssi-sdk';
```

## OrderSide

| Giá trị | Code | Mô tả |
|---|---|---|
| `OrderSide.BUY` | `"B"` | Mua |
| `OrderSide.SELL` | `"S"` | Bán |

## OrderType

| Giá trị | Code | Mô tả |
|---|---|---|
| `OrderType.ATO` | `"ATO"` | Lệnh mở cửa |
| `OrderType.ATC` | `"ATC"` | Lệnh đóng cửa |
| `OrderType.LO` | `"LO"` | Lệnh giới hạn |
| `OrderType.MTL` | `"MTL"` | Market To Limit |
| `OrderType.MP` | `"MP"` | Lệnh thị trường |
| `OrderType.MOK` | `"MOK"` | Match Or Kill |
| `OrderType.MAK` | `"MAK"` | Match And Kill |
| `OrderType.PLO` | `"PLO"` | Lệnh sau giờ nghỉ trưa |

## OrderStatus

| Giá trị | Code | Mô tả |
|---|---|---|
| `OrderStatus.PENDING` | `"PD"` | Chờ xử lý |
| `OrderStatus.PENDING_APPROVAL` | `"WA"` | Chờ phê duyệt |
| `OrderStatus.READY` | `"RS"` | Sẵn sàng |
| `OrderStatus.SENT` | `"SD"` | Đã gửi |
| `OrderStatus.QUEUED` | `"QU"` | Đã vào hàng đợi |
| `OrderStatus.FILLED` | `"FF"` | Khớp toàn bộ |
| `OrderStatus.PARTIAL_FILLED` | `"PF"` | Khớp một phần |
| `OrderStatus.PARTIAL_CANCELLED` | `"FFPC"` | Khớp một phần + huỷ phần còn lại |
| `OrderStatus.PENDING_MODIFY` | `"WM"` | Chờ sửa |
| `OrderStatus.PENDING_CANCEL` | `"WC"` | Chờ huỷ |
| `OrderStatus.CANCELLED` | `"CL"` | Đã huỷ |
| `OrderStatus.REJECTED` | `"RJ"` | Bị từ chối |
| `OrderStatus.EXPIRED` | `"EX"` | Hết hạn |
| `OrderStatus.PRE_SESSION` | `"IAV"` | Trước phiên |

## Board

| Giá trị | Code | Mô tả |
|---|---|---|
| `Board.HOSE` | `"HOSE"` | Sàn HOSE |
| `Board.HNX` | `"HNX"` | Sàn HNX |
| `Board.UPCOM` | `"UPCOM"` | Sàn UPCOM |

## Timeframe

| Giá trị | Code | Mô tả |
|---|---|---|
| `Timeframe.MINUTE_1` | `"1m"` | 1 phút |
| `Timeframe.MINUTE_3` | `"3m"` | 3 phút |
| `Timeframe.MINUTE_5` | `"5m"` | 5 phút |
| `Timeframe.MINUTE_15` | `"15m"` | 15 phút |
| `Timeframe.HOUR_1` | `"1h"` | 1 giờ |
| `Timeframe.DAY_1` | `"1d"` | 1 ngày |
| `Timeframe.WEEK_1` | `"1w"` | 1 tuần |
| `Timeframe.MONTH_1` | `"1M"` | 1 tháng |

## FCOType

Loại lệnh điều kiện (Flexible Conditional Order).

| Giá trị | Code | Mô tả |
|---|---|---|
| `FCOType.GTD` | `"gtd"` | Lệnh có hiệu lực đến ngày (Good Till Date) |
| `FCOType.STOP` | `"stop"` | Lệnh dừng thị trường (Stop Market) |
| `FCOType.STOP_LIMIT` | `"stop_limit"` | Lệnh dừng giới hạn (Stop Limit) |
| `FCOType.TRAILING_STOP` | `"trailing_stop"` | Lệnh xu hướng (Trailing Stop Market) |
| `FCOType.TRAILING_STOP_LIMIT` | `"trailing_stop_limit"` | Lệnh xu hướng giới hạn (Trailing Stop Limit) |
| `FCOType.OCO` | `"oco"` | Lệnh huỷ lệnh còn lại (One Cancels the Other) |
| `FCOType.BULL_BEAR` | `"bullbear"` | Lệnh Bull Bear |

## FCOOperator

Toán tử so sánh dùng để kích hoạt lệnh Stop / Stop Limit.

| Giá trị | Code | Mô tả |
|---|---|---|
| `FCOOperator.GREATER` | `"greater"` | Lớn hơn (`>`) |
| `FCOOperator.GREATER_OR_EQUAL` | `"greater_or_equal"` | Lớn hơn hoặc bằng (`>=`) |
| `FCOOperator.LESSER` | `"lesser"` | Nhỏ hơn (`<`) |
| `FCOOperator.LESSER_OR_EQUAL` | `"lesser_or_equal"` | Nhỏ hơn hoặc bằng (`<=`) |
| `FCOOperator.EQUAL` | `"equal"` | Bằng (`=`) |

## FCOStatus

Trạng thái xử lý của lệnh điều kiện.

| Giá trị | Code | Mô tả |
|---|---|---|
| `FCOStatus.INIT` | `"INIT"` | Mới khởi tạo |
| `FCOStatus.WAIT` | `"WAIT"` | Chờ kích hoạt |
| `FCOStatus.TRI` | `"TRI"` | Đã kích hoạt |
| `FCOStatus.TRIT` | `"TRIT"` | Đã kích hoạt thành công |
| `FCOStatus.TER` | `"TER"` | Đã kết thúc |
| `FCOStatus.FIS` | `"FIS"` | Hoàn tất |
| `FCOStatus.WC` | `"WC"` | Chờ huỷ |
| `FCOStatus.EXP` | `"EXP"` | Hết hạn |
| `FCOStatus.ERR` | `"ERR"` | Lỗi |

## AccountType

| Giá trị | Code | Mô tả |
|---|---|---|
| `AccountType.EQUITY` | `"Cash"` | Tài khoản tiền mặt |
| `AccountType.EQUITY_MARGIN` | `"Margin"` | Tài khoản ký quỹ |
| `AccountType.DERIVATIVE` | `"Derivative"` | Tài khoản phái sinh |

## DataType

| Giá trị | Code | Mô tả |
|---|---|---|
| `DataType.QUOTE` | `"quote"` | Dữ liệu mua/bán |
| `DataType.TRADE` | `"trade"` | Dữ liệu khớp lệnh |
| `DataType.ODD_LOT` | `"oddlot"` | Lô lẻ |
| `DataType.MARKET` | `"market"` | Trạng thái thị trường |
| `DataType.ROOM` | `"room"` | Room ngoại |
| `DataType.PUT` | `"put"` | Thoả thuận |

## Streaming Enums

### StreamingChannel

| Giá trị | Code | Mô tả |
|---|---|---|
| `StreamingChannel.DATA` | `"DATA"` | Kênh dữ liệu thị trường |
| `StreamingChannel.HEARTBEAT` | `"HEARTBEAT"` | Kênh heartbeat |
| `StreamingChannel.TRADING` | `"TRADING"` | Kênh sự kiện giao dịch |

### StreamingType

| Giá trị | Code | Mô tả |
|---|---|---|
| `StreamingType.ORDER` | `"orderEvent"` | Sự kiện lệnh |
| `StreamingType.ORDER_MATCH` | `"orderMatchEvent"` | Sự kiện khớp lệnh |
| `StreamingType.PORTFOLIO` | `"clientPortfolioEvent"` | Sự kiện danh mục |

## HTTPStatus

Mã HTTP status thường gặp, dùng nội bộ để phân loại lỗi API.

| Giá trị | Code | Mô tả |
|---|---|---|
| `HTTPStatus.OK` | `200` | Thành công |
| `HTTPStatus.NO_CONTENT` | `204` | Thành công, không có nội dung |
| `HTTPStatus.BAD_REQUEST` | `400` | Yêu cầu không hợp lệ |
| `HTTPStatus.UNAUTHORIZED` | `401` | Chưa xác thực |
| `HTTPStatus.FORBIDDEN` | `403` | Không có quyền |
| `HTTPStatus.NOT_FOUND` | `404` | Không tìm thấy |
| `HTTPStatus.UNPROCESSABLE_ENTITY` | `422` | Dữ liệu không xử lý được |
| `HTTPStatus.TOO_MANY_REQUESTS` | `429` | Vượt quá giới hạn request |
| `HTTPStatus.INTERNAL_SERVER_ERROR` | `500` | Lỗi máy chủ nội bộ |
| `HTTPStatus.BAD_GATEWAY` | `502` | Bad Gateway |
| `HTTPStatus.SERVICE_UNAVAILABLE` | `503` | Dịch vụ không khả dụng |
| `HTTPStatus.GATEWAY_TIMEOUT` | `504` | Gateway timeout |
