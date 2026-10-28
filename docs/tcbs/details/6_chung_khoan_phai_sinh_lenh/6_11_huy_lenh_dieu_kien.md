<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/derivative/cancel-condition-order
Tieu de goc: 6.11. Huỷ lệnh điều kiện
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/cancel-condition-order>

# 6.11. Huỷ lệnh điều kiện

POST`/khronos/v1/order/condition/cancel`

Huỷ lệnh điều kiện đang chờ kích hoạt trên thị trường phái sinh.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Request Body

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `accountId` | string |  | Số tài khoản lưu ký. |
| `subAccountId` | string |  | Số tiểu khoản phái sinh. |
| `orderNo` | string |  | pk_orderNo từ API sổ lệnh điều kiện. |

cURLNode.jsPythonJava

Sao chép

POST /khronos/v1/order/condition/cancel
```bash
curl -X POST https://openapi.tcbs.com.vn/khronos/v1/order/condition/cancel \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"accountId":"105C031402","subAccountId":"105C031402A","orderNo":"1"}'
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `rc` | string |  | Mã kết quả, 1 = thành công. |
| `rs` | string |  | Chi tiết lỗi (nếu có). |
| `data` | array |  | Mảng rỗng nếu thành công. |

200 OK

Sao chép
```json
{
  "cmd": "Web.cancelActivatedOrder",
  "rc": "1",
  "data": []
}
```
