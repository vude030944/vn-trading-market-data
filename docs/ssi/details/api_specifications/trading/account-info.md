<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/account-info
Tieu de goc: account-info
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/account-info>

# account-info

Lấy danh sách tài khoản giao dịch của khách hàng. Tài khoản có thể một trong ba loại CASH (thường); MARGIN (ký quỹ); DERIVATIVE (phái sinh). * DERIVATIVE (phái sinh)

Server URL`loading...`

GET

``/`api`/`v3`/`account`/`info`

Send

Authorization

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
curl -X GET "https://api.ssi.com.vn/api/v3/account/info" \
  -H "Content-Type: application/json"
```

200400

Success
```json
[
  {
    "accountNo": "string",
    "accountType": "CASH"
  }
]
```

Yêu cầu không hợp lệ.
```json
{
  "code": "400",
  "msg": "Invalid request"
}
```
