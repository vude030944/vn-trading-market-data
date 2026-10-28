<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/fco-list
Tieu de goc: fco-list
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/fco-list>

# fco-list

Lấy danh sách các lệnh điều kiện đã tạo theo bộ lọc.

Server URL`loading...`

GET

``/`api`/`v3`/`trading`/`fco`/`list`

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

- **`fcoId`** — `string`, *optional*

ID của lệnh điều kiện cần truy vấn.

- **`accountNo`** — `string`, *required*

Tài khoản đặt lệnh.

- **`type`** — `string`, *optional*

Loại lệnh điều kiện cần lọc.

- **`processStatus`** — `string`, *optional*

Trạng thái lệnh điều kiện cần lọc. Hỗ trợ lọc nhiều trạng thái cùng lúc, phân cách bằng dấu phẩy.

- **`symbol`** — `string`, *optional*

Mã chứng khoán hoặc mã hợp đồng phái sinh cần lọc.

- **`side`** — `string`, *optional*

Chiều mua hoặc bán của lệnh.

- **`from`** — `string`, *optional*

Ngày bắt đầu lọc, định dạng `YYYY/MM/DD`.

- **`to`** — `string`, *optional*

Ngày kết thúc lọc, định dạng `YYYY/MM/DD`.

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
curl -X GET "https://api.ssi.com.vn/api/v3/trading/fco/list?accountNo=string" \
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
  "fcoList": [
    {
      "fcoId": "string",
      "username": "string",
      "accountNo": "string",
      "quantity": 0.1,
      "price": "string",
      "priceSlip": "string",
      "symbol": "string",
      "type": "stop_limit",
      "orderType": "string",
      "from": "string",
      "to": "string",
      "matchedQuantity": 0.1,
      "isPlaceOrder": true,
      "status": "INIT",
      "detail": "string",
      "params": {
        "stopPrice": 0.1,
        "side": "string",
        "activePrice": 0.1,
        "trailingAmount": 0.1,
        "tpActivePrice": 0.1,
        "slActivePrice": 0.1,
        "tpPrice": "string",
        "slPrice": "string",
        "tpSlip": 0.1,
        "slSlip": 0.1,
        "operator": "string"
      }
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
