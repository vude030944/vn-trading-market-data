<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/trade-order-place
Tieu de goc: trade-order-place
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/trade-order-place>

# trade-order-place

Đặt lệnh mới.

Server URL`loading...`

POST

``/`api`/`v3`/`trading`/`order`

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

Ngôn ngữ phản hồi mong muốn. Nếu không có header này, hệ thống sẽ mặc định là en

- **`X-Signature`** — `string`, *required*

Chữ ký RSA + SHA256 để xác thực tính toàn vẹn của request. Input bao gồm SecretKey + JSON body.

### Request Body

`application/json`

TypeScript Definitions

Use the request body type in TypeScript.

Copy

- **`body`** — `object`, *required*

- **`clientRequestId`** — `string | null`, *optional*

Định danh lệnh do client tạo ra, dùng để đối chiếu trong các phản hồi sau này. Trường này không bắt buộc nhưng nếu có thì nên đảm bảo tính duy nhất để tránh nhầm lẫn khi xử lý phản hồi. Khi để trống thì hệ thống sẽ tự sinh định danh lệnh cho khách hàng và trả về response & streaming.

- **`accountNo`** — `string`, *required*

Số tài khoản giao dịch.

- **`symbol`** — `string`, *required*

Mã chứng khoán.

- **`side`** — `string`, *required*

Chiều mua hoặc bán của lệnh giao dịch. (B- Buy/Mua, S- Sell/Bán)

- **`orderType`** — `string`, *required*

Loại lệnh giao dịch. (LO - Limit Order/Lệnh giới hạn, ATO - At The Open/Lệnh mở cửa, ATC - At The Close/Lệnh đóng cửa, MP - Market Price/Giá thị trường)

- **`quantity`** — `number`, *required*

Khối lượng đặt lệnh.

- **`price`** — `string`, *required*

Giá đặt lệnh. Bắt buộc khi orderType là LO (Lệnh giới hạn); không bắt buộc với các loại lệnh khác (ATO, ATC, MP).

- **`deviceId`** — `string`, *required*

Định danh thiết bị thực hiện gửi yêu cầu đặt lệnh. Thông thường dùng MAC address hoặc IMEI của thiết bị.

- **`userAgent`** — `string`, *optional*

Thông tin về trình duyệt hoặc ứng dụng gửi yêu cầu.

- **`ipAddress`** — `string`, *optional*

Địa chỉ IP của thiết bị gửi yêu cầu.

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
curl -X POST "https://api.ssi.com.vn/api/v3/trading/order" \
  -H "Content-Type: application/json" \
  -H "X-Signature: sha256=abc123..." \
  -H "Content-Type: application/json" \
  -d '{    "accountNo": "string",    "symbol": "string",    "side": "B",    "orderType": "LO",    "quantity": 0.1,    "price": "string",    "deviceId": "string"  }'
```

200400

Success
```json
{
  "clientRequestId": "string",
  "orderId": "string",
  "orderStatus": "string",
  "clientModifyId": "string",
  "clientCancelId": "string"
}
```

Yêu cầu không hợp lệ.
```json
{
  "code": "400",
  "msg": "Invalid request"
}
```
