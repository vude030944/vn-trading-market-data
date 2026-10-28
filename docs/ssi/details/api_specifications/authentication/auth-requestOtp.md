<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/auth-requestOtp
Tieu de goc: auth-requestOtp
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/auth-requestOtp>

# auth-requestOtp

Gửi yêu cầu OTP phục vụ xác thực giao dịch. Với tài khoản 2FA loại SMS/Email, OTP sẽ được gửi về email/số điện thoại đã đăng ký. Với tài khoản 2FA loại SmartOTP, khách hàng nhận yêu cầu phê duyệt trên ứng dụng iBoard và có thể dùng `transactionId` trả về để gọi `auth/token`.

Server URL`loading...`

POST

``/`api`/`v3`/`auth`/`requestOtp`

Send

Body

### Request Body

`application/json`

TypeScript Definitions

Use the request body type in TypeScript.

Copy

- **`body`** — `object`, *required*

- **`apiKey`** — `string`, *required*

API key do SSI/FastConnect cấp.

- **`apiSecret`** — `string`, *required*

API secret tương ứng với `apiKey`.

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
curl -X POST "https://api.ssi.com.vn/api/v3/auth/requestOtp" \
  -H "Content-Type: application/json" \
  -d '{    "apiKey": "string",    "apiSecret": "string"  }'
```

200400

Thành công.
```json
{
  "message": "Thành công",
  "transactionId": "f306c510-0647-417b-9210-bb5b7e155e77"
}
```

Request không hợp lệ.
```json
{
  "code": 400,
  "msg": "apiKey is required"
}
```
