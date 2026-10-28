<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/auth-token
Tieu de goc: auth-token
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/auth-token>

# auth-token

Xác thực apiKey/apiSecret để lấy access token và refresh token (kèm thông tin hết hạn).

Server URL`loading...`

POST

``/`api`/`v3`/`auth`/`token`

Send

Body

### Request Body

`application/json`

TypeScript Definitions

Use the request body type in TypeScript.

Copy

- **`body`** — `object`, *required*

- **`apiKey`** — `string`, *required*

API key do SSI/FastConnect cấp cho ứng dụng.

- **`apiSecret`** — `string`, *required*

API secret tương ứng với `apiKey`.

- **`otp`** — `string | null`, *optional*

Mã OTP (SMS OTP hoặc SmartOTP) cần phải có nếu bạn muốn token cấp ra có quyền thực hiện giao dịch. Trường hợp chỉ sử dụng để truy vấn dữ liệu (data, query trading) thì không cần truyền OTP.

- **`transactionId`** — `string | null`, *optional*

Mã transaction trả về từ API `auth/requestOtp` khi tài khoản dùng 2FA loại SmartOTP và đã kích hoạt luồng phê duyệt qua ứng dụng iBoard.

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
curl -X POST "https://api.ssi.com.vn/api/v3/auth/token" \
  -H "Content-Type: application/json" \
  -d '{    "apiKey": "string",    "apiSecret": "string"  }'
```

200400

Thành công.
```json
{
  "tokenType": "Bearer",
  "accessToken": "string",
  "expiresAt": 1772075293023,
  "refreshToken": "string",
  "refreshExpiresAt": 1772075293023
}
```

Request không hợp lệ.
```json
{
  "code": 400,
  "msg": "apiKey is required"
}
```
