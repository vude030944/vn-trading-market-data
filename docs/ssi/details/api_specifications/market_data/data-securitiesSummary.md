<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/data-securitiesSummary
Tieu de goc: data-securitiesSummary
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/data-securitiesSummary>

# data-securitiesSummary

Lấy thông tin tổng hợp giao dịch của một mã chứng khoán hoặc chỉ số theo từng ngày giao dịch. Chỉ truyền một trong hai tham số là Symbol hoặc Index.

Server URL`loading...`

GET

``/`api`/`v3`/`data`/`securitiesSummary`

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

Mã chứng khoán. Chỉ truyền một trong hai tham số symbol hoặc index.

- **`index`** — `string`, *optional*

Mã chỉ số cần lấy thông tin tổng hợp giao dịch (ví dụ VNINDEX, VN30, VN100 etc...)

- **`from`** — `string`, *required*

Ngày bắt đầu theo định dạng `YYYY/MM/DD`.

- **`to`** — `string`, *required*

Ngày kết thúc theo định dạng `YYYY/MM/DD`. Bắt buộc phải lớn hơn hoặc bằng `from`.

- **`pageIndex`** — `integer`, *optional*

Chỉ số trang khi phân trang kết quả, bắt đầu từ 1. Nếu không cung cấp thì hệ thống sẽ sử dụng giá trị mặc định là 1. Giá trị này kết hợp với `pageSize` giúp khách hàng truy xuất các phần khác nhau của dữ liệu lịch sử sổ lệnh khi có nhiều bản ghi.

- **`pageSize`** — `integer`, *optional*

Số lượng bản ghi trên mỗi trang khi phân trang kết quả. Nếu không cung cấp thì hệ thống sẽ sử dụng giá trị mặc định là 10. Giá trị này kết hợp với `pageIndex` giúp khách hàng truy xuất các phần khác nhau của dữ liệu lịch sử sổ lệnh khi có nhiều bản ghi.

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
curl -X GET "https://api.ssi.com.vn/api/v3/data/securitiesSummary?from=string&to=string" \
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
      "tradingDate": "string",
      "priceChange": "string",
      "priceChangePercentage": "string",
      "open": "string",
      "high": "string",
      "low": "string",
      "close": "string",
      "average": "string",
      "totalMatch": "string",
      "totalMatchValue": "string",
      "totalBuy": "string",
      "totalTradeBuy": "string",
      "totalSell": "string",
      "totalTradeSell": "string",
      "totalForeignBuy": "string",
      "totalForeignBuyValue": "string",
      "totalForeignSell": "string",
      "totalForeignSellValue": "string",
      "remainForeignRoom": "string",
      "totalForeignRoom": "string",
      "totalDeal": "string",
      "totalDealValue": "string",
      "openInterest": "string",
      "settlementPrice": "string"
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
