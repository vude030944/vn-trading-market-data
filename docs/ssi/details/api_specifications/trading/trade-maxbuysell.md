<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/trade-maxbuysell
Tieu de goc: trade-maxbuysell
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/trade-maxbuysell>

# trade-maxbuysell

Lấy khối lượng mua/bán tối đa theo tài khoản, mã và giá.

Server URL`loading...`

GET

``/`api`/`v3`/`trading`/`maxBuySell`

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

Tài khoản giao dịch cần kiểm tra khối lượng mua/bán tối đa.

- **`symbol`** — `string`, *required*

Mã chứng khoán cần kiểm tra khối lượng mua/bán tối đa.

- **`price`** — `string`, *required*

Giá cần kiểm tra khối lượng mua/bán tối đa.

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
curl -X GET "https://api.ssi.com.vn/api/v3/trading/maxBuySell?accountNo=string&symbol=string&price=string" \
  -H "Content-Type: application/json"
```

200400

Success
```json
{
  "data": {
    "accountNo": "string",
    "maxBuyQty": 0.1,
    "marginRatio": "string",
    "maxSellQty": 0.1,
    "purchasingPower": 0.1
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
