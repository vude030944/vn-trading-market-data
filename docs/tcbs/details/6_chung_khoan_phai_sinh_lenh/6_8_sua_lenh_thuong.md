<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/derivative/update-order
Tieu de goc: 6.8. Sửa lệnh thường
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/update-order>

# 6.8. Sửa lệnh thường

POST`/khronos/v1/order/change`

Sửa lệnh thường đang chờ khớp trên thị trường phái sinh.

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
| `orderNo` | string |  | orderNo từ API đặt lệnh. |
| `refId` | string |  | Số tham chiếu duy nhất. |
| `nvol` | number |  | Khối lượng mới (> 0). |
| `nprice` | number |  | Giá mới. |

cURLNode.jsPythonJava

Sao chép

POST /khronos/v1/order/change
```bash
curl -X POST https://openapi.tcbs.com.vn/khronos/v1/order/change \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"accountId":"105C031402","subAccountId":"105C031402A","orderNo":"17","refId":"000123.H.HH2104062","nvol":300,"nprice":56000.5}'
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `rc` | string |  | Mã kết quả, 1 = thành công. |
| `data[].orderNo` | string |  | Số hiệu lệnh. |
| `data[].status` | string |  | Trạng thái (PC = pending change). |
| `data[].showPrice` | string |  | Giá mới. |
| `data[].volume` | string |  | Khối lượng mới. |
| `data[].pk_orderNo` | string |  | Key lệnh. |

200 OK

Sao chép
```json
{
  "cmd": "Web.changeOrder",
  "rc": "1",
  "data": [
    {
      "orderNo": 9,
      "msg_type": "1P",
      "status": "PC",
      "showPrice": "1290.0",
      "volume": "4",
      "pk_orderNo": 20029858
    }
  ]
}
```
