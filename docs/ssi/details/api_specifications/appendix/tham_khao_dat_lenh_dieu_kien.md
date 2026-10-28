<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/appendix/fco-reference
Tieu de goc: Tham khảo đặt lệnh điều kiện
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/appendix/fco-reference>

# Tham khảo đặt lệnh điều kiện

Hướng dẫn chi tiết về cách đặt lệnh điều kiện (FCO) qua FastConnect API, bao gồm các loại lệnh, tham số và ví dụ.

# Tham khảo đặt lệnh điều kiện

## Tổng quan

Lệnh điều kiện (FCO - FastConnect Conditional Order) cho phép đặt lệnh tự động khi thỏa mãn các điều kiện được thiết lập trước. Hệ thống hỗ trợ 7 loại lệnh điều kiện, mỗi loại có bộ tham số riêng phù hợp với chiến lược giao dịch khác nhau.

Tất cả lệnh điều kiện được gửi qua endpoint `POST /api/v3/trading/fco/order` với field `type` xác định loại lệnh.

## Tham số chung

Các tham số sau áp dụng cho **tất cả** loại lệnh điều kiện:

| Tham số | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `accountNo` | string | **Có** | Tài khoản đặt lệnh (cơ sở hoặc phái sinh). |
| `symbol` | string | **Có** | Mã chứng khoán hoặc mã hợp đồng phái sinh. |
| `side` | string | **Có** | Chiều mua hoặc bán: `B` (Buy) hoặc `S` (Sell). |
| `type` | string | **Có** | Loại lệnh điều kiện (xem bảng bên dưới). |
| `quantity` | integer | **Có** | Khối lượng muốn đặt lệnh. |
| `deviceId` | string | **Có** | Định danh thiết bị (MAC address hoặc IMEI). |
| `price` | string | Không | Giá đặt lệnh. Hỗ trợ giá số hoặc loại lệnh đặc biệt (`MP`, `MOK`, `MTL`). |
| `priceSlip` | number | Không | Khoảng trượt giá (price slippage) cho phép. |
| `from` | string | Không | Ngày bắt đầu hiệu lực, định dạng `YYYY/MM/DD hh:mm:ss`. Mặc định là thời điểm tạo lệnh. |
| `to` | string | Không | Ngày kết thúc hiệu lực, định dạng `YYYY/MM/DD hh:mm:ss`. Mặc định 24h, tối đa 31 ngày. |
| `code` | string | Không | Mã xác thực OTP hoặc PIN (cần điền nếu token chưa xác thực kèm OTP). |
| `userAgent` | string | Không | Thông tin trình duyệt hoặc ứng dụng gửi yêu cầu. |
| `clientRequestId` | string | Không | Định danh lệnh do client tạo, dùng để đối chiếu response và streaming. |
| `ipAddress` | string | Không | Địa chỉ IP của thiết bị gửi yêu cầu. |

## Các loại lệnh điều kiện và tham số

### 1\. Stop Limit (`stop_limit`)

Tương tự lệnh Stop, tuy nhiên lệnh được đẩy lên sở với mức giá limit KH đã đặt.

**Tham số riêng:**

| Tham số | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `price` | string | **Có** | Giá limit để đẩy lệnh lên sở. |
| `stopPrice` | number | **Có** | Giá dừng (stop price). Khi giá thị trường đạt đến mức này, lệnh sẽ được kích hoạt. |
| `operator` | string | **Có** | Toán tử so sánh giá: `greater_or_equal`, `lesser_or_equal`, `greater`, `lesser`, `equal`. |

**Ví dụ request body:**
```json
{
  "symbol": "SSI",
  "side": "S",
  "type": "stop_limit",
  "price": "30500",
  "priceSlip": 0,
  "quantity": 1000,
  "accountNo": "0001234",
  "from": "2025/07/10 08:00:00",
  "to": "2025/07/15 23:59:59",
  "stopPrice": 30500,
  "operator": "greater_or_equal",
  "code": "",
  "userAgent": "agent fctrading app",
  "deviceId": "0A:B1:92:D3:5S:8G"
}
```

* * *

### 2\. Stop (`stop`)

Lệnh dừng. Lệnh sẽ được kích hoạt khi thỏa mãn điều kiện về giá. Lệnh được đẩy lên sở với giá thị trường.

**Tham số riêng:**

| Tham số | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `stopPrice` | number | **Có** | Giá dừng (stop price). Khi giá thị trường đạt đến mức này, lệnh sẽ được kích hoạt. |
| `operator` | string | **Có** | Toán tử so sánh giá: `greater_or_equal`, `lesser_or_equal`, `greater`, `lesser`, `equal`. |

**Ví dụ request body:**
```json
{
  "symbol": "SSI",
  "side": "S",
  "type": "stop",
  "price": "30500",
  "priceSlip": 0,
  "quantity": 1000,
  "accountNo": "0001234",
  "from": "2025/07/10 08:00:00",
  "to": "2025/07/15 23:59:59",
  "stopPrice": 30500,
  "operator": "greater_or_equal",
  "code": "",
  "userAgent": "agent fctrading app",
  "deviceId": "0A:B1:92:D3:5S:8G"
}
```

* * *

### 3\. Good Till Date (`gtd`)

Lệnh có hiệu lực nhiều ngày. Lệnh được trigger mỗi ngày cho đến khi gặp một trong các điều kiện sau thì dừng:

  * Khớp hết khối lượng lệnh gốc
  * Người dùng hủy lệnh
  * Sau ngày hết hiệu lực

**Tham số riêng:**

Không có tham số riêng ngoài các tham số chung. Tuy nhiên `from` và `to` cần được thiết lập để xác định khoảng thời gian hiệu lực.

**Ví dụ request body:**
```json
{
  "symbol": "SSI",
  "side": "S",
  "type": "gtd",
  "price": "30500",
  "priceSlip": 0,
  "quantity": 1000,
  "accountNo": "0001234",
  "from": "2025/07/10 08:00:00",
  "to": "2025/07/15 23:59:59",
  "code": "",
  "userAgent": "agent fctrading app",
  "deviceId": "0A:B1:92:D3:5S:8G"
}
```

* * *

### 4\. Bull Bear (`bullbear`)

Lệnh chốt lãi, cắt lỗ (chưa có vị thế): Cho phép KH đính kèm lệnh chốt lãi (Take Profit) và cắt lỗ (Stop Loss) với một lệnh chính.

Khi lệnh chính khớp, hệ thống sẽ sinh ra 1 lệnh OCO có chiều ngược với chiều của lệnh chính.

**Tham số riêng:**

| Tham số | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `tpActivePrice` | number | **Có** | Giá kích hoạt lệnh chốt lời (Take Profit). |
| `tpPrice` | string | **Có** | Giá chốt lời. Hỗ trợ giá số hoặc `MP`, `MOK`, `MTL`. |
| `tpSlip` | number | **Có** | Biên trượt giá chốt lời. |
| `slActivePrice` | number | **Có** | Giá kích hoạt lệnh dừng lỗ (Stop Loss). |
| `slPrice` | string | **Có** | Giá dừng lỗ. Hỗ trợ giá số hoặc `MP`, `MOK`, `MTL`. |
| `slSlip` | number | **Có** | Biên trượt giá dừng lỗ. |

**Ví dụ request body (phái sinh):**
```json
{
  "symbol": "41I1F7000",
  "side": "B",
  "type": "bullbear",
  "price": "MTL",
  "priceSlip": 0.50,
  "quantity": 1,
  "accountNo": "0D01234",
  "from": "2025/07/10 08:00:00",
  "to": "2025/07/15 23:59:59",
  "stopPrice": 0,
  "activePrice": 0.0,
  "trailingAmount": 0,
  "tpActivePrice": 1555,
  "slActivePrice": 1540,
  "tpPrice": "1556",
  "slPrice": "1541",
  "tpSlip": 1,
  "slSlip": 1,
  "operator": "",
  "code": "",
  "userAgent": "agent fctrading app",
  "deviceId": "0A:B1:92:D3:5S:8G"
}
```

* * *

### 5\. OCO - One Cancels Other (`oco`)

Lệnh cặp dùng cho việc đặt lệnh chốt lãi, cắt lỗ cho vị thế đã có sẵn trong danh mục.

Khi điều kiện kích hoạt của một lệnh (a) thỏa mãn thì hệ thống sẽ kiểm tra:

  * Nếu lệnh còn lại (b) đã được kích hoạt thì hủy lệnh con của lệnh đó
  * Đẩy lệnh thỏa mãn điều kiện kích hoạt đi sau khi hủy lệnh thành công. KL của lệnh = KL khớp còn lại của lệnh con lệnh (b)

**Tham số riêng:**

| Tham số | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `tpActivePrice` | number | **Có** | Giá kích hoạt lệnh chốt lời (Take Profit). |
| `tpPrice` | string | **Có** | Giá chốt lời. Hỗ trợ giá số hoặc `MP`, `MTL`, `MOK`, `MAK`. |
| `tpSlip` | number | **Có** | Biên trượt giá chốt lời. |
| `slActivePrice` | number | **Có** | Giá kích hoạt lệnh dừng lỗ (Stop Loss). |
| `slPrice` | string | **Có** | Giá dừng lỗ. Hỗ trợ giá số hoặc `MP`, `MTL`, `MOK`, `MAK`. |
| `slSlip` | number | **Có** | Biên trượt giá dừng lỗ. |

**Ví dụ request body:**
```json
{
  "symbol": "SSI",
  "side": "S",
  "type": "oco",
  "price": "MP",
  "priceSlip": 0.0,
  "quantity": 1000,
  "accountNo": "0001234",
  "from": "2025/07/10 08:00:00",
  "to": "2025/07/15 23:59:59",
  "stopPrice": 0,
  "activePrice": 0.0,
  "trailingAmount": 0,
  "tpActivePrice": 30500,
  "slActivePrice": 20000,
  "tpPrice": "30500",
  "slPrice": "30500",
  "tpSlip": 100,
  "slSlip": 100,
  "operator": "",
  "code": "",
  "userAgent": "agent fctrading app",
  "deviceId": "0A:B1:92:D3:5S:8G"
}
```

* * *

### 6\. Trailing Stop (`trailing_stop`)

Lệnh Stop với mức giá stop dịch chuyển theo xu hướng của thị trường. Mức giá đẩy lệnh là giá thị trường.

**Tham số riêng:**

| Tham số | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `activePrice` | number | **Có** | Giá kích hoạt ban đầu của lệnh điều kiện. |
| `trailingAmount` | number | **Có** | Khoảng giá trailing (khoảng cách giữa giá thị trường và giá stop). |

**Ví dụ request body:**
```json
{
  "symbol": "SSI",
  "side": "S",
  "type": "trailing_stop",
  "price": "MP",
  "priceSlip": 0.0,
  "quantity": 1000,
  "accountNo": "0001234",
  "from": "2025/07/10 08:00:00",
  "to": "2025/07/15 23:59:59",
  "activePrice": 28000,
  "trailingAmount": 1000,
  "code": "",
  "userAgent": "agent fctrading app",
  "deviceId": "0A:B1:92:D3:5S:8G"
}
```

* * *

### 7\. Trailing Stop Limit (`trailing_stop_limit`)

Lệnh Stop với mức giá stop dịch chuyển theo xu hướng của thị trường. Mức giá đẩy lệnh đi là mức giá được tính toán từ giá stop.

**Tham số riêng:**

| Tham số | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `price` | string | **Có** | Giá limit để đẩy lệnh lên sở. |
| `activePrice` | number | **Có** | Giá kích hoạt ban đầu của lệnh điều kiện. |
| `trailingAmount` | number | **Có** | Khoảng giá trailing (khoảng cách giữa giá thị trường và giá stop). |

**Ví dụ request body:**
```json
{
  "symbol": "SSI",
  "side": "S",
  "type": "trailing_stop_limit",
  "price": "MP",
  "priceSlip": 0.0,
  "quantity": 1000,
  "accountNo": "0001234",
  "from": "2025/07/10 08:00:00",
  "to": "2025/07/15 23:59:59",
  "activePrice": 28000,
  "trailingAmount": 1000,
  "userAgent": "agent fctrading app",
  "deviceId": "0A:B1:92:D3:5S:8G"
}
```

## Bảng tóm tắt loại lệnh

| # | Loại lệnh | `type` | Tham số riêng |
|---|---|---|---|
| 1 | Stop Limit | `stop_limit` | `price`, `stopPrice`, `operator` |
| 2 | Stop | `stop` | `stopPrice`, `operator` |
| 3 | Good Till Date | `gtd` | (không có) |
| 4 | Bull Bear | `bullbear` | `tpActivePrice`, `tpPrice`, `tpSlip`, `slActivePrice`, `slPrice`, `slSlip` |
| 5 | OCO | `oco` | `tpActivePrice`, `tpPrice`, `tpSlip`, `slActivePrice`, `slPrice`, `slSlip` |
| 6 | Trailing Stop | `trailing_stop` | `activePrice`, `trailingAmount` |
| 7 | Trailing Stop Limit | `trailing_stop_limit` | `price`, `activePrice`, `trailingAmount` |

## Giá trị operator

Toán tử `operator` dùng cho lệnh `stop`, `stop_limit` để xác định điều kiện kích hoạt:

| Giá trị | Mô tả |
|---|---|
| `greater_or_equal` | Giá thị trường ≥ giá stop |
| `lesser_or_equal` | Giá thị trường ≤ giá stop |
| `greater` | Giá thị trường > giá stop |
| `lesser` | Giá thị trường < giá stop |
| `equal` | Giá thị trường = giá stop |

## Loại giá đặc biệt

Một số loại lệnh hỗ trợ giá đặc biệt thay vì giá số cụ thể:

| Giá trị | Mô tả |
|---|---|
| `MP` | Market Price - giá thị trường |
| `MOK` | Match or Kill - khớp hoặc hủy |
| `MTL` | Match then Limit - khớp rồi chuyển thành lệnh giới hạn |
| `MAK` | Match and Kill - khớp và hủy phần còn lại |
