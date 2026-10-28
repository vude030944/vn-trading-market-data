<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/derivative/position-closed
Tieu de goc: 6.2. Tài sản, vị thế đóng
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/position-closed>

# 6.2. Tài sản, vị thế đóng

GET`/khronos/v1/account/portfolio/position/close`

Tra cứu danh sách vị thế đã đóng của tài khoản phái sinh.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Request parameter

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `accountId` | string |  | Số tài khoản lưu ký. |
| `subAccountId` | string |  | Tiểu khoản phái sinh. |
| `symbol` | string |  | Mã chứng khoán (để trống = tất cả). |
| `pageNo` | number |  | Số trang. |
| `pageSize` | number |  | Số dòng mỗi trang. |

cURLNode.jsPythonJava

Sao chép

GET /khronos/v1/account/portfolio/position/close
```bash
curl "https://openapi.tcbs.com.vn/khronos/v1/account/portfolio/position/close?accountId=105C031402&subAccountId=105C031402A&symbol=&pageNo=1&pageSize=20" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `cmd` | string |  | Tên lệnh phản hồi. |
| `rc` | string |  | Mã kết quả, 1 = thành công. |
| `data` | array |  | Danh sách vị thế đóng. |
| `data[].symbol` | string |  | Mã hợp đồng. |
| `data[].side` | string |  | Loại giao dịch (B/S). |
| `data[].openPrice` | number |  | Giá mở TB. |
| `data[].closePrice` | number |  | Giá đóng TB. |
| `data[].closePosition` | string |  | Số vị thế đóng / tổng. |
| `data[].fee` | number |  | Phí giao dịch. |
| `data[].tax` | number |  | Thuế. |
| `data[].closeVM` | number |  | Lãi lỗ đã đóng. |
| `data[].unrealize` | number |  | Lãi lỗ chưa đóng. |
| `data[].closePC` | number |  | % lãi/lỗ đã đóng. |
| `data[].time` | string |  | Thời gian đóng cuối. |

200 OK

Sao chép
```json
{
  "cmd": "Web.Portfolio.PositionClose",
  "rc": "1",
  "data": [
    {
      "symbol": "TOTAL",
      "side": "",
      "openPrice": 0,
      "closePrice": 0,
      "closePosition": 0,
      "fee": 11400,
      "tax": 15275,
      "closeVM": 500000,
      "unrealize": 500000,
      "closePC": 0,
      "time": ""
    },
    {
      "symbol": "VN30F2103",
      "side": "S",
      "openPrice": 1180,
      "closePrice": 1175,
      "closePosition": "1/1",
      "fee": 5700,
      "tax": 7637.5,
      "closeVM": 500000,
      "unrealize": 0,
      "closePC": 3.26,
      "time": "11:56:24"
    }
  ]
}
```
