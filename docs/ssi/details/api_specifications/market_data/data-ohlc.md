<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/data-ohlc
Tieu de goc: data-ohlc
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/data-ohlc>

# data-ohlc

Lấy dữ liệu nến OHLCV theo khoảng thời gian. Thời gian cung cấp 1 năm gần nhất cho dữ liệu intraday, dữ liệu daily cung cấp từ khi mã chứng khoán được giao dịch.

Server URL`loading...`

GET

``/`api`/`v3`/`data`/`ohlc`

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

- **`symbol`** — `string`, *required*

Mã chứng khoán cần lấy dữ liệu OHLCV.

- **`from`** — `string`, *required*

Mốc thời gian bắt đầu. Định dạng `YYYY/MM/DD` cho dữ liệu daily và `YYYY/MM/DD HH:mm:ss` cho dữ liệu intraday.

- **`to`** — `string`, *required*

Mốc thời gian kết thúc. Định dạng `YYYY/MM/DD` cho dữ liệu daily và `YYYY/MM/DD HH:mm:ss` cho dữ liệu intraday.

- **`timeFrame`** — `string`, *optional*

Khung thời gian của dữ liệu OHLCV. Giá trị có thể là `1m`, `3m`, `5m`, `15m`, `30m`, `1h`, hoặc `1d`. Nếu không cung cấp thì hệ thống sẽ sử dụng giá trị mặc định là `1d`.

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
curl -X GET "https://api.ssi.com.vn/api/v3/data/ohlc?symbol=string&from=string&to=string" \
  -H "Content-Type: application/json"
```

200400

Success
```json
{
  "pageSize": 0,
  "pageIndex": 0,
  "data": [
    {
      "symbol": "string",
      "tradingDate": "string",
      "open": "string",
      "high": "string",
      "low": "string",
      "close": "string",
      "volume": "string",
      "value": "string"
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
