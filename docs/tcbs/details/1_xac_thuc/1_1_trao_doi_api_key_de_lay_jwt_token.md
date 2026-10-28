<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/auth/token
Tieu de goc: 1.1. Trao đổi API Key để lấy JWT Token
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/auth/token>

# 1.1. Trao đổi API Key để lấy JWT Token

POST`/gaia/v1/oauth2/openapi/token`

Trao đổi API Key (tạo trên TCInvest) cùng mã xác thực để lấy JWT token, gắn token này dưới dạng Bearer cho mọi request sau đó.

**Chọn phương thức xác thực:**

TOTP (TCInvest App)default

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Content-Type` | string |  | application/json. |

## Request Body

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `apiKey` | string |  | API Key được gen trên TCInvest. |
| `otp` | string |  | Mã OTP từ ứng dụng TCInvest. |

cURLNode.jsPythonJava

Sao chép

POST /gaia/v1/oauth2/openapi/token
```bash
curl -X POST https://openapi.tcbs.com.vn/gaia/v1/oauth2/openapi/token \
  -H "Content-Type: application/json" \
  -d '{"apiKey":"<API_KEY>","otp":"111111"}'
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `token` | string |  | JWT token dùng cho các request tiếp theo. |

200 OK400 Error

Sao chép
```json
{
  "token": "eyJ4NXQiOiJaaWpkaFpqVmlNamMwWmdfUlMyNTYiLCJhbGciOiJSUzI1NiJ9..."
}
```
