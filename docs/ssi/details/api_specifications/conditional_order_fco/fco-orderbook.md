<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/fco-orderbook
Tieu de goc: fco-orderbook
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/fco-orderbook>

# fco-orderbook

Lấy danh sách các lệnh thực được phát sinh (trigger) bởi một lệnh điều kiện.

Server URL`loading...`

GET

``/`api`/`v3`/`trading`/`fco`/`orderbook`

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

ID của lệnh điều kiện cần truy vấn sổ lệnh phát sinh.

- **`pageIndex`** — `integer`, *optional*

Chỉ số trang khi phân trang kết quả, bắt đầu từ 1. Mặc định là 1.

- **`pageSize`** — `integer`, *optional*

Số lượng bản ghi trên mỗi trang. Mặc định là 10.

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
curl -X GET "https://api.ssi.com.vn/api/v3/trading/fco/orderbook?fcoId=string" \
  -H "Content-Type: application/json"
```

200400

Success
```json
{
  "pageIndex": "string",
  "pageSize": "string",
  "itemsCount": "string",
  "pagesCount": "string",
  "data": [
    {
      "fcoId": "string",
      "accountNo": "string",
      "quantity": 0.1,
      "price": "string",
      "symbol": "string",
      "side": "B",
      "orderType": "string",
      "isMainOrder": true,
      "isAttachedOrder": true,
      "createdTime": "string",
      "updatedTime": "string",
      "uniqueId": "string",
      "orderId": "string",
      "matchedQuantity": 0.1,
      "osQuantity": 0.1,
      "avgPrice": 0.1,
      "status": "RQ",
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
