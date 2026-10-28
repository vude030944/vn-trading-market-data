<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/derivative/place-order
Tieu de goc: 6.4. Đặt lệnh thường
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/place-order>

# 6.4. Đặt lệnh thường

POST`/khronos/v1/order/place`

Đặt lệnh thường trên thị trường phái sinh. Lệnh điều kiện dùng 6.5.

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
| `side` | enum |  | B = mua, S = bán. |
| `symbol` | string |  | Mã phái sinh, ví dụ VN30F2103. |
| `price` | number |  | Giá đặt (trong khoảng trần sàn). |
| `volume` | int64 |  | Số lượng. |
| `orderType` | string |  | 0 = lệnh thường; SLP=1.0,0.8 = SL/TP; ABI=mã HĐTL = lệnh đối ứng. |
| `refId` | string |  | Số ngẫu nhiên duy nhất xác định kênh đặt lệnh (H.<số tự sinh>). Có thể dùng UUID cho trường hợp này. |

cURLNode.jsPythonJava

Sao chép

POST /khronos/v1/order/place
```bash
curl -X POST https://openapi.tcbs.com.vn/khronos/v1/order/place \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"accountId":"105C031402","subAccountId":"105C031402A","side":"B","symbol":"VN30F2103","price":1198.7,"volume":10,"orderType":"0","refId":"H.OWsC4418qYN59HXcvGtD3z"}'
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `cmd` | string |  | Lệnh gọi (echo). |
| `rc` | string |  | Mã kết quả, 1 = thành công. |
| `rs` | string |  | Thông báo lỗi (nếu có). |
| `oID` | string |  | ID phiên đặt lệnh. |
| `data[].orderNo` | string |  | Số hiệu lệnh. |
| `data[].pk_orderNo` | string |  | Key lệnh. |
| `data[].showPrice` | string |  | Giá hiển thị. |

200 OK

Sao chép
```json
{
  "cmd": "Web.placeOrder",
  "rc": "1",
  "rs": "",
  "oID": "H.OWsC4418qYN59HXcvGtD3z",
  "data": [
    {
      "orderNo": "1",
      "pk_orderNo": "7625400",
      "showPrice": "1198.7"
    }
  ]
}
```
