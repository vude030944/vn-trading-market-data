<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/fco-statusHistory
Tieu de goc: fco-statusHistory
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/fco-statusHistory>

# fco-statusHistory

Lấy lịch sử thay đổi trạng thái của một lệnh điều kiện.

Server URL`loading...`

GET

``/`api`/`v3`/`trading`/`fco`/`statusHistory`

Send

Authorization

Query

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

### Query Parameters

- **`fcoId`** — `string`, *required*

ID của lệnh điều kiện cần truy vấn lịch sử trạng thái.

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
curl -X GET "https://api.ssi.com.vn/api/v3/trading/fco/statusHistory?fcoId=string" \
  -H "Content-Type: application/json"
```

200400

Success
```json
{
  "data": [
    {
      "state": "string",
      "time": "string",
      "code": 0,
      "detail": "string"
    }
  ]
}
```

Yêu cầu không hợp lệ.
```json
{
  "code": "400",
  "msg": "Invalid request"
}
```
