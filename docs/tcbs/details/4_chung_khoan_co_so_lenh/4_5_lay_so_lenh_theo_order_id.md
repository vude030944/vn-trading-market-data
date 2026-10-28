<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/get-order-by-id
Tieu de goc: 4.5. Lấy sổ lệnh theo Order ID
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/get-order-by-id>

# 4.5. Lấy sổ lệnh theo Order ID

GET`/aion/v1/accounts/{accountNo}/orders/{orderID}`

Lấy chi tiết một lệnh theo Order ID của một tiểu khoản.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Path variable

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `accountNo` | string |  | Số tiểu khoản. |
| `orderID` | string |  | Số hiệu lệnh. |

cURLNode.jsPythonJava

Sao chép

GET /aion/v1/accounts/0001170730/orders/9202110200000060280
```bash
curl "https://openapi.tcbs.com.vn/aion/v1/accounts/0001170730/orders/9202110200000060280" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `object` | string |  | Mặc định = 'List'. |
| `pageSize` | int64 |  | Kích thước trang. |
| `pageIndex` | int64 |  | Index trang. |
| `totalCount` | int64 |  | Tổng số bản ghi. |
| `data[].orderID` | string |  | Số hiệu lệnh. |
| `data[].accountNo` | string |  | Số tiểu khoản. |
| `data[].symbol` | string |  | Mã chứng khoán. |
| `data[].execType` | string |  | Loại lệnh (NB/NS). |
| `data[].orderQtty` | number |  | Khối lượng đặt. |
| `data[].execQtty` | number |  | Khối lượng khớp. |
| `data[].priceType` | string |  | Loại giá. |
| `data[].limitPrice` | number |  | Giá đặt lệnh. |
| `data[].matchPrice` | number |  | Giá khớp trung bình. |
| `data[].orStatus` | enum |  | Trạng thái lệnh: 0 = Từ chối, 2 = Đã gửi, 3 = Đã hủy, 4 = Đã khớp, 5 = Hết hiệu lực, 8 = Chờ gửi, 10 = Đã sửa, 11 = Đang gửi, 12 = Khớp hết, A = Đang sửa, C = Đang hủy, S = Hoàn tất. |
| `data[].txdate` | string |  | Ngày đặt lệnh (RFC 3339). |
| `data[].txtime` | string |  | Giờ đặt lệnh. |

200 OK

Sao chép
```json
{
  "object": "List",
  "pageSize": 10,
  "pageIndex": 1,
  "totalCount": 1,
  "data": [
    {
      "orderID": "9202110200000060280",
      "accountNo": "0001170730",
      "symbol": "HPG",
      "execType": "NB",
      "orderQtty": 2500,
      "execQtty": 0,
      "priceType": "LO",
      "limitPrice": 25000,
      "matchPrice": 0,
      "orStatus": "11",
      "txdate": "2021-08-19T00:00:00.000+07:00",
      "txtime": "14:15:34"
    }
  ]
}
```
