<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/fco-order-cancel
Tieu de goc: fco-order-cancel
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/fco-order-cancel>

# fco-order-cancel

Hủy lệnh điều kiện đang hoạt động.

Server URL`loading...`

DELETE

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

- **`fcoId`** — `string | null`, *required*

ID của lệnh điều kiện cần hủy.

- **`code`** — `string | null`, *optional*

Mã xác thực OTP hoặc mã PIN dùng để xác thực giao dịch.

- **`deviceId`** — `string`, *optional*

Định danh thiết bị thực hiện gửi yêu cầu. Thông thường dùng MAC address hoặc IMEI của thiết bị.

- **`userAgent`** — `string | null`, *optional*

Thông tin về trình duyệt hoặc ứng dụng gửi yêu cầu.

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
curl -X DELETE "https://api.ssi.com.vn/api/v3/trading/fco/order" \
  -H "Content-Type: application/json" \
  -H "X-Signature: sha256=abc123..." \
  -H "Content-Type: application/json" \
  -d '{    "fcoId": "string"  }'
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
