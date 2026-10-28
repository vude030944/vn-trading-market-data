<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/purchasing-power-symbol
Tieu de goc: 4.8. Lấy sức mua theo mã
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/purchasing-power-symbol>

# 4.8. Lấy sức mua theo mã

GET`/aion/v1/accounts/{accountNo}/ppse/{symbol}`

Lấy sức mua của tiểu khoản theo mã chứng khoán cụ thể.

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

cURLNode.jsPythonJava

Sao chép

GET /aion/v1/accounts/0001170730/ppse/FPT
```bash
curl "https://openapi.tcbs.com.vn/aion/v1/accounts/0001170730/ppse/FPT" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `pp0` | number |  | Sức mua cơ bản. |
| `maxQtty` | number |  | Số lượng tối đa có thể mua. |

200 OK

Sao chép
```json
{
  "pp0": 2057323960,
  "maxQtty": 15000
}
```
