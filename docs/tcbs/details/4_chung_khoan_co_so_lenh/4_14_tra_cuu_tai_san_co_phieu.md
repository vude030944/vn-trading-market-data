<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/asset
Tieu de goc: 4.14. Tra cứu tài sản cổ phiếu
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/asset>

# 4.14. Tra cứu tài sản cổ phiếu

GET`/aion/v1/accounts/{accountNo}/se`

Tra cứu tài sản cổ phiếu theo tiểu khoản. Số dư tiền dùng /cashInvestments; sao kê tiền dùng /erebos/v2/digital/trans-hist-cashStatements.

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

GET /aion/v1/accounts/0001170730/se
```bash
curl "https://openapi.tcbs.com.vn/aion/v1/accounts/0001170730/se" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `assets` | array |  | Danh sách tài sản cổ phiếu. |
| `assets[].symbol` | string |  | Mã chứng khoán. |
| `assets[].quantity` | int64 |  | Số lượng nắm giữ. |
| `assets[].avgPrice` | number |  | Giá trung bình. |
| `assets[].marketValue` | number |  | Giá trị thị trường. |

200 OK

Sao chép
```json
{
  "assets": [
    {
      "symbol": "VNM",
      "quantity": 500,
      "avgPrice": 78500,
      "marketValue": 40250000
    }
  ]
}
```
