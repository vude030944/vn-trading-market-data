<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/data-securitiesByBoard
Tieu de goc: data-securitiesByBoard
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/data-securitiesByBoard>

# data-securitiesByBoard

Lấy danh sách chứng khoán theo điều kiện lọc. Khách chỉ được phép cung cấp một trong ba tham số symbol, board hoặc index để lọc danh sách chứng khoán.

Server URL`loading...`

GET

``/`api`/`v3`/`data`/`securitiesByBoard`

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

- **`symbol`** — `string`, *optional*

Mã chứng khoán cần truy vấn. Chỉ cung cấp một trong ba tham số symbol, board hoặc index.

- **`board`** — `string`, *optional*

Mã sàn cần lấy danh sách chứng khoán. Giá trị có thể là `HOSE`, `HNX`, hoặc `UPCOM`.

- **`index`** — `string`, *optional*

Mã chỉ số cần lấy danh sách chứng khoán.

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
curl -X GET "https://api.ssi.com.vn/api/v3/data/securitiesByBoard" \
  -H "Content-Type: application/json"
```

200400

Success
```json
[
  {
    "symbol": "string",
    "symbolNameVi": "string",
    "symbolNameEn": "string",
    "board": "HOSE",
    "lotSize": "string",
    "maturityDate": "string",
    "firstTradingDate": "string",
    "lastTradingDate": "string",
    "cwUnderlyingSymbol": "string",
    "cwExercisePrice": "string",
    "cwExecutionRatio": "string",
    "listedShare": "string",
    "icbCode": "string",
    "icbName": "string",
    "iIndex": "string",
    "iNav": "string",
    "openInterest": "string",
    "settlementPrice": "string"
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
