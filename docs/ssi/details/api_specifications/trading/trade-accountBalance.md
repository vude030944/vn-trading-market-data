<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/trade-accountBalance
Tieu de goc: trade-accountBalance
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/trade-accountBalance>

# trade-accountBalance

Lấy số dư tài khoản giao dịch.

Server URL`loading...`

GET

``/`api`/`v3`/`trading`/`accountBalance`

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

Tài khoản giao dịch cần lấy số dư. Bắt buộc truyền thông tin tiểu khoản.

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
curl -X GET "https://api.ssi.com.vn/api/v3/trading/accountBalance?accountNo=string" \
  -H "Content-Type: application/json"
```

200400

Success
```json
{
  "equity": {
    "accountNo": "string",
    "accountBalance": "string",
    "totalDebt": "string",
    "interestLoan": "string",
    "overdueFeeLoan": "string",
    "withdrawable": "string",
    "onHoldCash": "string",
    "sellUnmatched": "string",
    "sellT0": "string",
    "sellT1": "string",
    "sellT2": "string",
    "buyUnmatched": "string",
    "buyT0": "string",
    "buyT1": "string",
    "buyT2": "string",
    "advancedCashT0": "string",
    "advancedCashT1": "string",
    "holdSubscription": "string",
    "dividend": "string"
  },
  "derivative": {
    "accountNo": "string",
    "accountBalance": "string",
    "fee": "string",
    "commission": "string",
    "interest": "string",
    "extInterest": "string",
    "loan": "string",
    "deliveryAmount": "string",
    "floatingPL": "string",
    "tradingPL": "string",
    "totalPL": "string",
    "withdrawable": "string",
    "cashSSI": "string",
    "validNonCashSSI": "string",
    "withdrawableSSI": "string",
    "cashVSDC": "string",
    "validNonCashVSDC": "string",
    "withdrawableVSDC": "string"
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
