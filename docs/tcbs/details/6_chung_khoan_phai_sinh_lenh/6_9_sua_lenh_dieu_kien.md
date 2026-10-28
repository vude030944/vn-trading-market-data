<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/derivative/update-condition-order
Tieu de goc: 6.9. Sửa lệnh điều kiện
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/update-condition-order>

# 6.9. Sửa lệnh điều kiện

POST`/khronos/v2/order/condition/change`

Sửa lệnh điều kiện đang chờ kích hoạt trên thị trường phái sinh.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Request Body

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `accountId` | string |  | Số tài khoản lưu ký. |
| `pkOrderNo` | string |  | pk_orderNo từ API tra cứu sổ lệnh. |
| `refId` | string |  | Số tham chiếu duy nhất. |
| `soPrice` | number |  | Giá kích hoạt mới. |
| `type` | string |  | Loại (để trống). |
| `cmd` | string |  | Web.Order.ChangeCondition. |

cURLNode.jsPythonJava

Sao chép

POST /khronos/v2/order/condition/change
```bash
curl -X POST https://openapi.tcbs.com.vn/khronos/v2/order/condition/change \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"accountId":"105C031402","pkOrderNo":"901938","refId":"000123.H.HH2104062","soPrice":1453.9,"type":"","cmd":"Web.Order.ChangeCondition"}'
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `rc` | string |  | Mã kết quả, 1 = thành công. |
| `data[].showPrice` | string |  | Giá kích hoạt. |
| `data[].price` | string |  | Giá đặt. |
| `data[].volume` | string |  | Khối lượng. |
| `data[].pkOrderNo` | string |  | Số hiệu lệnh. |
| `data[].notes` | string |  | Loại lệnh điều kiện. |

200 OK

Sao chép
```json
{
  "cmd": "Web.Order.ChangeConditionOrder",
  "rc": "1",
  "data": [
    {
      "showPrice": "1453.9",
      "price": "1362.2",
      "volume": "1",
      "pkOrderNo": "901943",
      "notes": "Stop order"
    }
  ]
}
```
