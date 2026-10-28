<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/data-indexList
Tieu de goc: data-indexList
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/data-indexList>

# data-indexList

Lấy danh sách các chỉ số thị trường.

Server URL`loading...`

GET

``/`api`/`v3`/`data`/`indexList`

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

Định dạng nội dung request body, sử dụng "application/json".

- **`User-Agent`** — `string`, *optional*

Thông tin client gửi request.

- **`Accept-Language`** — `string`, *optional*

Ngôn ngữ phản hồi mong muốn. Nếu không có header này, hệ thống sẽ mặc định là en

### Query Parameters

- **`board`** — `string`, *optional*

Mã sàn cần lấy danh sách các chỉ số. Giá trị có thể là `HOSE`, `HNX`, hoặc `UPCOM`. Nếu không cung cấp thì hệ thống sẽ trả về danh sách các chỉ số của tất cả các sàn.

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
curl -X GET "https://api.ssi.com.vn/api/v3/data/indexList" \
  -H "Content-Type: application/json"
```

200400

Success
```json
[
  {
    "index": "string",
    "indexName": "string",
    "board": "HOSE"
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
