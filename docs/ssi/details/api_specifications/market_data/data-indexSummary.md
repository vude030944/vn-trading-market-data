<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/data-indexSummary
Tieu de goc: data-indexSummary
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/data-indexSummary>

# data-indexSummary

Lấy thông tin tổng hợp của một chỉ số theo ngày giao dịch.

Server URL`loading...`

GET

``/`api`/`v3`/`data`/`indexSummary`

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

Mã sàn của chỉ số. Giá trị có thể là `HOSE`, `HNX`, hoặc `UPCOM`. Bắt buộc cung cấp chính xác một trong hai tham số `board` hoặc `index`.

- **`index`** — `string`, *optional*

Mã chỉ số cần lấy thông tin tổng hợp (ví dụ VNINDEX, VN30, HNX30). Bắt buộc cung cấp chính xác một trong hai tham số `board` hoặc `index`.

- **`tradingDate`** — `string`, *optional*

Ngày giao dịch theo định dạng `YYYY/MM/DD`.

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
curl -X GET "https://api.ssi.com.vn/api/v3/data/indexSummary" \
  -H "Content-Type: application/json"
```

200400

Success
```json
[
  {
    "tradingDate": "string",
    "totalTrade": "string",
    "totalTradeValue": "string",
    "totalMatch": "string",
    "totalMatchValue": "string",
    "totalDeal": "string",
    "totalDealValue": "string",
    "indexChange": "string",
    "indexChangePercentage": "string",
    "indexValue": "string",
    "totalAdvanceStock": "string",
    "totalCeilingStock": "string",
    "totalDeclineStock": "string",
    "totalFloorStock": "string",
    "totalNoChangeStock": "string",
    "totalPropBuy": "string",
    "totalPropBuyValue": "string",
    "totalPropSell": "string",
    "totalPropSellValue": "string"
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
