<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/auth-refresh
Tieu de goc: auth-refresh
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/auth-refresh>

# auth-refresh

Làm mới access token bằng refresh token còn hiệu lực.

Server URL`loading...`

POST

``/`api`/`v3`/`auth`/`refresh`

Send

Body

### Request Body

`application/json`

TypeScript Definitions

Use the request body type in TypeScript.

Copy

- **`body`** — `object`, *required*

- **`refreshToken`** — `string`, *required*

Refresh token còn hiệu lực để cấp mới access token.

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
curl -X POST "https://api.ssi.com.vn/api/v3/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{    "refreshToken": "string"  }'
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
