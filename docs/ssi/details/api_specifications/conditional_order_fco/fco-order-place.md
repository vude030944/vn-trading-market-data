<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/fco-order-place
Tieu de goc: fco-order-place
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/fco-order-place>

# fco-order-place

Đặt lệnh điều kiện mới. Hỗ trợ các loại lệnh điều kiện bao gồm stop, stop_limit, gtd, bullbear, oco, trailing_stop, trailing_stop_limit.

📄 **Xem thêm:** [Tham khảo đặt lệnh điều kiện](/docs/api-reference/appendix/fco-reference)

Server URL`loading...`

POST

``/`api`/`v3`/`trading`/`fco`/`order`

Send

Authorization

Body

### Authorization

`Bearer `

AuthorizationBearer <token>

Nhập JWT token theo định dạng `Bearer <token>`.

In: `header`

### Header Parameters

- **`Content-Type`** — `string`, *required*

Định dạng nội dung request body. Chủ yếu là application/json.

- **`User-Agent`** — `string`, *optional*

Thông tin client gửi request.

- **`Accept-Language`** — `string`, *optional*

Ngôn ngữ phản hồi mong muốn. Nếu không có header này, hệ thống sẽ mặc định là en.

- **`X-Signature`** — `string`, *required*

Chữ ký RSA + SHA256 để xác thực tính toàn vẹn của request. Input bao gồm SecretKey + JSON body.

### Request Body

`application/json`

TypeScript Definitions

Use the request body type in TypeScript.

Copy

- **`body`** — `object`, *required*

- **`accountNo`** — `string`, *required*

Tài khoản đặt lệnh (tài khoản cơ sở hoặc phái sinh).

- **`deviceId`** — `string`, *required*

Định danh thiết bị thực hiện gửi yêu cầu. Thông thường dùng MAC address hoặc IMEI của thiết bị.

- **`userAgent`** — `string | null`, *optional*

Thông tin về trình duyệt hoặc ứng dụng gửi yêu cầu.

- **`clientRequestId`** — `string | null`, *optional*

Định danh lệnh do client tạo ra, dùng để đối chiếu trong các phản hồi sau này. Trường này không bắt buộc nhưng nếu có thì nên đảm bảo tính duy nhất để tránh nhầm lẫn khi xử lý phản hồi. Khi để trống thì hệ thống sẽ tự sinh định danh lệnh cho khách hàng và trả về response & streaming.

- **`ipAddress`** — `string`, *optional*

Địa chỉ IP của thiết bị gửi yêu cầu.

- **`from`** — `string | null`, *optional*

Ngày bắt đầu hiệu lực của lệnh điều kiện, định dạng `YYYY/MM/DD hh:mm:ss`. Mặc định là thời điểm tạo lệnh.

- **`to`** — `string | null`, *optional*

Ngày kết thúc hiệu lực của lệnh điều kiện, định dạng `YYYY/MM/DD hh:mm:ss`. Mặc định là 24h kể từ thời điểm tạo, tối đa 31 ngày kể từ ngày bắt đầu.

- **`code`** — `string | null`, *optional*

Mã xác thực OTP hoặc mã PIN dùng để xác thực giao dịch (cần điền nếu token chưa được xác thực kèm với OTP)

- **`symbol`** — `string | null`, *required*

Mã chứng khoán hoặc mã hợp đồng phái sinh cần đặt lệnh điều kiện.

- **`side`** — `string | null`, *required*

Chiều mua hoặc bán của lệnh. B (Buy/Mua) hoặc S (Sell/Bán).

- **`type`** — `string | null`, *required*

Loại lệnh điều kiện.

- **`price`** — `string | null`, *required*

Giá đặt lệnh. Hỗ trợ giá số hoặc loại lệnh đặc biệt (MP, MOK, MTL).

- **`quantity`** — `integer`, *required*

Khối lượng muốn đặt lệnh.

- **`priceSlip`** — `number`, *optional*

Khoảng trượt giá (price slippage) cho phép khi thực hiện lệnh.

- **`stopPrice`** — `number`, *optional*

Giá dừng lỗ. Khi giá thị trường đạt đến mức này, lệnh sẽ được kích hoạt.

- **`activePrice`** — `number`, *optional*

Giá kích hoạt ban đầu của lệnh điều kiện.

- **`trailingAmount`** — `number`, *optional*

Khoảng giá trailing. Dùng cho loại lệnh trailing_stop và trailing_stop_limit.

- **`tpActivePrice`** — `number`, *optional*

Giá kích hoạt lệnh chốt lời (Take Profit). Khi giá thị trường đạt đến mức này, lệnh chốt lời sẽ được kích hoạt.

- **`slActivePrice`** — `number`, *optional*

Giá kích hoạt lệnh dừng lỗ (Stop Loss). Khi giá thị trường đạt đến mức này, lệnh dừng lỗ sẽ được kích hoạt.

- **`tpPrice`** — `string | null`, *optional*

Giá chốt lời. Hỗ trợ giá số hoặc loại lệnh đặc biệt (MP, MOK, MTL).

- **`slPrice`** — `string | null`, *optional*

Giá dừng lỗ. Hỗ trợ giá số hoặc loại lệnh đặc biệt (MP, MOK, MTL).

- **`tpSlip`** — `number`, *optional*

Biên trượt giá chốt lời.

- **`slSlip`** — `number`, *optional*

Biên trượt giá dừng lỗ.

- **`operator`** — `string | null`, *optional*

Toán tử so sánh giá để kích hoạt lệnh điều kiện.

### Response Headers

- **`X-RATELIMIT-LIMIT`** — `string`, *optional*

Giới hạn số request trong chu kỳ.

- **`X-RATELIMIT-REMAINING`** — `string`, *optional*

Số request còn lại trong chu kỳ hiện tại.

- **`X-RATELIMIT-RESET`** — `string`, *optional*

Thời điểm reset giới hạn request.

### Response Body

### 200

`application/json`

### 400

`application/json`

cURL

JavaScript

Go

Python

Java

C#
```bash
curl -X POST "https://api.ssi.com.vn/api/v3/trading/fco/order" \
  -H "Content-Type: application/json" \
  -H "X-Signature: sha256=abc123..." \
  -H "Content-Type: application/json" \
  -d '{    "accountNo": "string",    "deviceId": "string",    "symbol": "string",    "side": "B",    "type": "stop_limit",    "price": "string",    "quantity": 0  }'
```

200400

Success
```json
{
  "fcoId": "string"
}
```

Yêu cầu không hợp lệ.
```json
{
  "code": "400",
  "msg": "Invalid request"
}
```
