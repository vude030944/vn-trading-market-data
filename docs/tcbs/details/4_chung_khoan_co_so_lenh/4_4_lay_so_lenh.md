<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/get-orders
Tieu de goc: 4.4. Lấy sổ lệnh
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/get-orders>

# 4.4. Lấy sổ lệnh

GET`/aion/v1/accounts/{accountNo}/orders`

Lấy toàn bộ sổ lệnh của một tiểu khoản. Có thể lấy theo Order ID qua /orders/{orderID}.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Path variable

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `accountNo` | string |  | Số tiểu khoản, ví dụ: 0001170730. |

cURLNode.jsPythonJava

Sao chép

GET /aion/v1/accounts/0001170730/orders
```bash
curl "https://openapi.tcbs.com.vn/aion/v1/accounts/0001170730/orders" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

Xem realtime khớp lệnh tại mục 5.9 (WebSocket).

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `orders` | array |  | Danh sách lệnh trong sổ lệnh. |
| `orders[].orderId` | string |  | Mã lệnh. |
| `orders[].symbol` | string |  | Mã chứng khoán. |
| `orders[].execType` | string |  | Chiều giao dịch (NB/NS). |
| `orders[].price` | int64 |  | Giá đặt. |
| `orders[].quantity` | int64 |  | Khối lượng đặt. |
| `orders[].status` | string |  | Trạng thái lệnh. |

200 OK

Sao chép
```json
{
  "orders": [
    {
      "orderId": "9202205230000324355",
      "symbol": "VNM",
      "execType": "NB",
      "price": 10000,
      "quantity": 100,
      "status": "FILLED"
    }
  ]
}
```
