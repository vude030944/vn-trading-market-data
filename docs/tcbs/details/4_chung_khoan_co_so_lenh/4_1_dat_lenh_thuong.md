<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/place-order
Tieu de goc: 4.1. Đặt lệnh thường
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/place-order>

# 4.1. Đặt lệnh thường

POST`/akhlys/v1/accounts/{accountNo}/orders`

Đặt lệnh thường trên thị trường cơ sở cho một tiểu khoản.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Path variable

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `accountNo` | string |  | Số tiểu khoản, ví dụ 0001170730. |

## Request Body

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `execType` | enum |  | Chiều giao dịch: NS = bán, NB = mua. |
| `symbol` | string |  | Mã chứng khoán, ví dụ VNM. |
| `priceType` | enum |  | Loại giá: LO, ATO, ATC, PLO, MP, MTL, MOK, MAK. |
| `price` | int64 |  | Giá giao dịch. |
| `quantity` | int64 |  | Khối lượng giao dịch. |

cURLNode.jsPythonJava

Sao chép

POST /akhlys/v1/accounts/0001170730/orders
```bash
curl -X POST https://openapi.tcbs.com.vn/akhlys/v1/accounts/0001170730/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"execType":"NB","symbol":"VNM","priceType":"LO","price":10000,"quantity":100}'
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `error` | string |  | Mã lỗi, 0 = thành công. |
| `message` | string |  | Thông báo kết quả. |
| `orderId` | string |  | Mã lệnh được tạo. |

200 OK

Sao chép
```json
{
  "error": "0",
  "message": "Đặt lệnh thành công!",
  "orderId": "9202205230000324355"
}
```
