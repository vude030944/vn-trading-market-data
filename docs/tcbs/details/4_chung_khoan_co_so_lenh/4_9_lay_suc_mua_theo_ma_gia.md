<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/purchasing-power-symbol-price
Tieu de goc: 4.9. Lấy sức mua theo mã, giá
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/purchasing-power-symbol-price>

# 4.9. Lấy sức mua theo mã, giá

GET`/aion/v1/accounts/{accountNo}/ppse/{symbol}/{price}`

Lấy sức mua của tiểu khoản theo mã chứng khoán và giá cụ thể.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Path variable

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `accountNo` | string |  | Số tiểu khoản. |
| `symbol` | string |  | Mã chứng khoán, ví dụ FPT. |
| `price` | string |  | Giá tính sức mua. |

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
| `pp0` | number |  | Sức mua cơ bản. |
| `maxQtty` | number |  | Số lượng tối đa có thể mua tại mức giá này. |

200 OK

Sao chép
```json
{
  "pp0": 2057323960,
  "maxQtty": 39564
}
```
