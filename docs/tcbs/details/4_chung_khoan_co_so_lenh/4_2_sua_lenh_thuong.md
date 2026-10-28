<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/update-order
Tieu de goc: 4.2. Sửa lệnh thường
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/update-order>

# 4.2. Sửa lệnh thường

PUT`/akhlys/v1/accounts/{accountNo}/orders/{orderId}`

Sửa giá hoặc khối lượng của một lệnh đang chờ khớp.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Path variable

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `accountNo` | string |  | Số tiểu khoản. |
| `orderId` | string |  | Số hiệu lệnh cần sửa. |

## Request Body

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `price` | int64 |  | Giá giao dịch mới. |
| `quantity` | int64 |  | Khối lượng giao dịch mới. |

cURLNode.jsPythonJava

Sao chép

PUT /akhlys/v1/accounts/0001170730/orders/9202205230000324355
```bash
curl -X PUT https://openapi.tcbs.com.vn/akhlys/v1/accounts/0001170730/orders/9202205230000324355 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"price":10500,"quantity":200}'
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `error` | string |  | Mã lỗi, 0 = thành công. |
| `message` | string |  | Mô tả mã lỗi nếu có. |
| `orderId` | string |  | Mã lệnh đã sửa. |

200 OK

Sao chép
```json
{
  "error": "0",
  "message": "Sửa lệnh thành công!",
  "orderId": "9202205230000324355"
}
```
