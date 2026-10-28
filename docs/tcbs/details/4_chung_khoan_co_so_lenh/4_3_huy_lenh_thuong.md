<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/cancel-order
Tieu de goc: 4.3. Huỷ lệnh thường
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/cancel-order>

# 4.3. Huỷ lệnh thường

PUT`/akhlys/v1/accounts/{accountNo}/cancel-orders`

Huỷ một hoặc nhiều lệnh chưa khớp hết bằng danh sách order ID.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Path variable

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `accountNo` | string |  | Số tiểu khoản. |

## Request Body

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `ordersList` | array |  | Danh sách lệnh cần huỷ. |

cURLNode.jsPythonJava

Sao chép

PUT /akhlys/v1/accounts/0001170730/cancel-orders
```bash
curl -X PUT https://openapi.tcbs.com.vn/akhlys/v1/accounts/0001170730/cancel-orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ordersList":[{"orderID":"9202205230000324355"}]}'
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `error` | string |  | Mã lỗi, 0 = thành công. |
| `message` | string |  | Mô tả mã lỗi nếu có. |

200 OK

Sao chép
```json
{
  "error": "0",
  "message": "Huỷ lệnh thành công!"
}
```
