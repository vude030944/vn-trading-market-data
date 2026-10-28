<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/cash-balance
Tieu de goc: 4.15. Lấy thông tin số dư tiền
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/cash-balance>

# 4.15. Lấy thông tin số dư tiền

GET`/aion/v1/accounts/{accountNo}/cashInvestments`

Lấy thông tin số dư tiền của một tiểu khoản.

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

GET /aion/v1/accounts/0001170730/cashInvestments
```bash
curl "https://openapi.tcbs.com.vn/aion/v1/accounts/0001170730/cashInvestments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `totalCount` | int64 |  | Tổng số bản ghi trả ra. |
| `pageSize` | int64 |  | Kích thước trang (mặc định = 20). |
| `pageIndex` | int64 |  | Index trang (mặc định = 1). |
| `data[].bodBalance` | number |  | Tiền mặt tại TCBS. |
| `data[].cashBalance` | number |  | Tiền mặt. |
| `data[].pp0forBF` | number |  | Sức mua cơ bản cho sản phẩm BOND/FUND. |
| `data[].bankAvlBalanceBF` | number |  | Tổng số dư khả dụng IA cho BOND/FUND. |
| `data[].accountNo` | string |  | Số tiểu khoản. |

200 OK

Sao chép
```json
{
  "totalCount": 20,
  "pageSize": 20,
  "pageIndex": 1,
  "data": [
    {
      "bodBalance": 918000000,
      "cashBalance": 918000000,
      "pp0forBF": 2057323960,
      "bankAvlBalanceBF": 6500000,
      "accountNo": "0001170730"
    }
  ]
}
```
