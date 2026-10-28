<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/matching-details
Tieu de goc: 4.6. Lấy thông tin khớp lệnh
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/matching-details>

# 4.6. Lấy thông tin khớp lệnh

GET`/aion/v1/accounts/{accountNo}/matching-details`

Lấy thông tin chi tiết khớp lệnh của một tiểu khoản.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Path variable

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `accountNo` | string |  | Số tiểu khoản. |

cURLNode.jsPythonJava

Sao chép

GET /aion/v1/accounts/0001170730/matching-details
```bash
curl "https://openapi.tcbs.com.vn/aion/v1/accounts/0001170730/matching-details" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `totalCount` | int64 |  | Tổng số bản ghi trả ra. |
| `pageSize` | int64 |  | Số lượng phần tử 1 trang. |
| `pageIndex` | int64 |  | Mục lục trang. |
| `data[].orderId` | string |  | Số hiệu lệnh. |
| `data[].side` | enum |  | Chiều lệnh: S = Bán, B = Mua. |
| `data[].symbol` | string |  | Mã chứng khoán. |
| `data[].quoteQtty` | number |  | Khối lượng đặt. |
| `data[].quotePrice` | number |  | Giá đặt. |
| `data[].tradeId` | string |  | Id lệnh khớp. |
| `data[].qtty` | number |  | Khối lượng khớp. |
| `data[].price` | number |  | Giá khớp. |
| `data[].timeExec` | string |  | Thời điểm khớp. |

200 OK

Sao chép
```json
{
  "totalCount": 25,
  "pageSize": 25,
  "pageIndex": 0,
  "data": [
    {
      "orderId": "9202407170000280679",
      "side": "B",
      "symbol": "FPT",
      "quoteQtty": 800,
      "quotePrice": 54000,
      "tradeId": "202409160000220391",
      "qtty": 200,
      "price": 53000,
      "timeExec": "2024-09-16T17:05:20"
    }
  ]
}
```
