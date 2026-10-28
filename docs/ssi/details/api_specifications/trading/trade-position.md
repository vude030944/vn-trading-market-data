<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/trade-position
Tieu de goc: trade-position
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/trade-position>

# trade-position

Lấy thông tin vị thế cho tài khoản.

Server URL`loading...`

GET

``/`api`/`v3`/`trading`/`position`

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

- **`clientId`** — `string`, *optional*

Tài khoản 6 số định danh khách hàng tại SSI. Nếu số tài khoản là 003C123888 thì clientId = 123888

- **`accountNo`** — `string`, *required*

Tài khoản giao dịch cần lấy thông tin vị thế, các tài khoản đuôi 1, 6, 8 tương ứng (CASH, MARGIN, DERIVATIVE) sẽ có thông tin vị thế khác nhau.

- **`querySummary`** — `boolean`, *optional*

Nếu true, trả về tóm tắt vị thế phái sinh. Nếu false, trả về chi tiết từng vị thế. Chỉ áp dụng cho tài khoản phái sinh. Mặc định là true.

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
curl -X GET "https://api.ssi.com.vn/api/v3/trading/position?accountNo=string" \
  -H "Content-Type: application/json"
```

200400

Success
```json
{
  "data": {
    "equity": [
      {
        "accountNo": "string",
        "symbol": "string",
        "quantity": "string",
        "blockQuantity": "string",
        "dividendQuantity": "string",
        "buyingQuantity": "string",
        "boughtQuantity": "string",
        "sellingQuantity": "string",
        "soldQuantity": "string",
        "t1SellQuantity": "string",
        "t2SellQuantity": "string",
        "costPrice": "string",
        "mortgageQuantity": "string",
        "sellableQuantity": "string",
        "restrictedQuantity": "string"
      }
    ],
    "derivative": {
      "accountNo": "string",
      "derOpenPositions": [
        {
          "symbol": "string",
          "long": "string",
          "short": "string",
          "net": "string",
          "bidAvgPrice": "string",
          "askAvgPrice": "string",
          "tradePrice": "string",
          "tradingPL": "string",
          "floatingPL": "string"
        }
      ],
      "derClosePositions": [
        {
          "symbol": "string",
          "long": "string",
          "short": "string",
          "net": "string",
          "bidAvgPrice": "string",
          "askAvgPrice": "string",
          "tradePrice": "string",
          "tradingPL": "string",
          "floatingPL": "string"
        }
      ]
    }
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
