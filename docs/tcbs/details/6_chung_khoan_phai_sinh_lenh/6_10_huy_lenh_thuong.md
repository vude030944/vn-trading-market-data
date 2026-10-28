<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/derivative/cancel-order
Tieu de goc: 6.10. Huỷ lệnh thường
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/cancel-order>

# 6.10. Huỷ lệnh thường

POST`/khronos/v1/order/cancel`

Huỷ lệnh thường đang chờ khớp trên thị trường phái sinh.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Request Body

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `accountId` | string |  | Số tài khoản lưu ký. |
| `orderNo` | string |  | orderNo từ API sổ lệnh thường. |
| `cmd` | string |  | Web.cancelOrder. |
| `pin` | string |  | Kênh đặt lệnh (F). |
| `refId` | string |  | Số tham chiếu. |

cURLNode.jsPythonJava

Sao chép

POST /khronos/v1/order/cancel
```bash
curl -X POST https://openapi.tcbs.com.vn/khronos/v1/order/cancel \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"accountId":"105C031402","orderNo":"1","cmd":"Web.cancelOrder","pin":"F","refId":""}'
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `rc` | string |  | Mã kết quả, 1 = thành công. |
| `data[].orderNo` | string |  | Số hiệu lệnh. |
| `data[].status` | string |  | Trạng thái (PW = pending withdrawal). |
| `data[].pk_orderNo` | string |  | Key lệnh. |
| `data[].cancelTime` | string |  | Thời gian hủy. |

200 OK

Sao chép
```json
{
  "cmd": "Web.changeOrder",
  "rc": "1",
  "data": [
    {
      "orderNo": 1,
      "msg_type": "1C",
      "status": "PW",
      "pk_orderNo": 7625368,
      "cancelTime": "16:20:15"
    }
  ]
}
```
