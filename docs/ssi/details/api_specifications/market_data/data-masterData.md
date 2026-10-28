<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/data-masterData
Tieu de goc: data-masterData
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/data-masterData>

# data-masterData

Truy vấn thông tin giá trần, giá sàn, giá tham chiếu của chứng khoán theo ngày giao dịch.

Server URL`loading...`

GET

``/`api`/`v3`/`data`/`masterdata`

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

- **`from`** — `string`, *optional*

Ngày bắt đầu theo định dạng `YYYY/MM/DD`. Không truyền thì trả dữ liệu ngày mới nhất.

- **`to`** — `string`, *optional*

Ngày kết thúc theo định dạng `YYYY/MM/DD`. Không truyền thì trả dữ liệu ngày mới nhất.

- **`pageIndex`** — `integer`, *optional*

Chỉ số trang khi phân trang kết quả, bắt đầu từ 1. Nếu không cung cấp thì hệ thống sẽ sử dụng giá trị mặc định là 1.

- **`pageSize`** — `integer`, *optional*

Số lượng bản ghi trên mỗi trang khi phân trang kết quả. Nếu không cung cấp thì hệ thống sẽ sử dụng giá trị mặc định là 10.

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
curl -X GET "https://api.ssi.com.vn/api/v3/data/masterdata" \
  -H "Content-Type: application/json"
```

200400

Success
```json
{
  "pageSize": 0,
  "pageIndex": 0,
  "pagesCount": 0,
  "itemsCount": 0,
  "data": [
    {
      "symbol": "string",
      "exchange": "string",
      "tradingDate": "string",
      "ceiling": "string",
      "floor": "string",
      "refPrice": "string"
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
