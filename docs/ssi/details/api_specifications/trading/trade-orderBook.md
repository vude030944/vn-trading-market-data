<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/trade-orderBook
Tieu de goc: trade-orderBook
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/trade-orderBook>

# trade-orderBook

Lấy lịch sử sổ lệnh theo tài khoản và bộ lọc.

Server URL`loading...`

GET

``/`api`/`v3`/`trading`/`orderBook`

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

Ngôn ngữ phản hồi mong muốn. Nếu không có header này, hệ thống sẽ mặc định là en

### Query Parameters

- **`accountNo`** — `string`, *required*

Tài khoản giao dịch cần lấy lịch sử sổ lệnh.

- **`from`** — `string`, *required*

Thời gian bắt đầu để lọc lịch sử sổ lệnh, định dạng ISO 8601 (ví dụ 2024-01-01T00:00:00Z).

- **`to`** — `string`, *required*

Thời gian kết thúc để lọc lịch sử sổ lệnh, định dạng ISO 8601 (ví dụ 2024-01-01T00:00:00Z).

- **`symbol`** — `string`, *optional*

Mã chứng khoán cần lọc lịch sử sổ lệnh.

- **`orderStatus`** — `string`, *optional*

Trạng thái lệnh cần lọc. Tham khảo danh sách trạng thái tại phụ lục Trạng thái lệnh & luồng trạng thái.

- **`pageSize`** — `integer`, *optional*

Số lượng bản ghi trên mỗi trang khi phân trang kết quả. Nếu không cung cấp thì hệ thống sẽ sử dụng giá trị mặc định (ví dụ 20). Giá trị này giúp khách hàng kiểm soát lượng dữ liệu trả về trong mỗi phản hồi, đặc biệt khi lịch sử sổ lệnh có nhiều bản ghi.

- **`pageIndex`** — `integer`, *optional*

Chỉ số trang khi phân trang kết quả, bắt đầu từ 1. Nếu không cung cấp thì hệ thống sẽ sử dụng giá trị mặc định là 1. Giá trị này kết hợp với `pageSize` giúp khách hàng truy xuất các phần khác nhau của dữ liệu lịch sử sổ lệnh khi có nhiều bản ghi.

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
curl -X GET "https://api.ssi.com.vn/api/v3/trading/orderBook?accountNo=string&from=string&to=string" \
  -H "Content-Type: application/json"
```

200400

Success
```json
{
  "data": {
    "accountNo": "string",
    "totalRecord": 0,
    "orderList": [
      {
        "clientRequestId": "string",
        "orderId": "string",
        "symbol": "string",
        "side": "B",
        "orderType": "LO",
        "quantity": "string",
        "price": "string",
        "filledQty": "string",
        "cancelQty": "string",
        "avgPrice": "string",
        "inputTime": "string",
        "modifiedTime": "string",
        "orderStatus": "PD",
        "message": "string"
      }
    ]
  }
}
```

Yêu cầu không hợp lệ.
```json
{
  "code": "400",
  "msg": "Invalid request"
}
```
