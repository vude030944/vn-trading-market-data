<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/purchasing-power
Tieu de goc: 4.7. Lấy sức mua
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/purchasing-power>

# 4.7. Lấy sức mua

GET`/aion/v1/accounts/{accountNo}/ppse`

Lấy sức mua của một tiểu khoản. Có biến thể theo mã (/ppse/{symbol}) và theo mã + giá (/ppse/{symbol}/{price}).

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Path variable

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `accountNo` | string |  | Số tiểu khoản. |
| `symbol` | string |  | Mã chứng khoán (biến thể theo mã). |
| `price` | string |  | Giá tính sức mua (biến thể theo giá). |

cURLNode.jsPythonJava

Sao chép

GET /aion/v1/accounts/0001170730/ppse/FPT/52000
```bash
curl "https://openapi.tcbs.com.vn/aion/v1/accounts/0001170730/ppse/FPT/52000" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `purchasingPower` | number |  | Sức mua khả dụng. |
| `maxQuantity` | int64 |  | Số lượng tối đa có thể mua. |

200 OK

Sao chép
```json
{
  "purchasingPower": 150000000,
  "maxQuantity": 2884
}
```
