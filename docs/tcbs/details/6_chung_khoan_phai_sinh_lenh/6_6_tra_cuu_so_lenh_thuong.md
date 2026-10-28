<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/derivative/get-normal-orders
Tieu de goc: 6.6. Tra cứu sổ lệnh thường
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/get-normal-orders>

# 6.6. Tra cứu sổ lệnh thường

GET`/khronos/v1/order/in-day`

Tra cứu sổ lệnh thường trong ngày của tài khoản phái sinh.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Request parameter

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `accountId` | string |  | Số tài khoản lưu ký. |
| `pageNo` | number |  | Số trang. |
| `pageSize` | number |  | Số phần tử trong trang. |
| `symbol` | string |  | Lọc: ALL,ALL = tất cả; VN30F2303,B = theo mã; ALL,B = theo L/S. |
| `orderType` | enum |  | Lọc loại lệnh: '' = tất cả, 3 = Arbitrage, 4 = SL/TP, 5 = ForceClose, 6 = Thường. |
| `status` | enum |  | 0 = tất cả, 1 = chờ khớp, 2 = đã khớp. |
| `refId` | string |  | Ref ID của lệnh. |

cURLNode.jsPythonJava

Sao chép

GET /khronos/v1/order/in-day
```bash
curl "https://openapi.tcbs.com.vn/khronos/v1/order/in-day?accountId=105C031402&pageNo=1&pageSize=20&symbol=ALL,ALL&orderType=&status=0" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `rc` | string |  | Mã kết quả, 1 = thành công. |
| `data` | array |  | Danh sách lệnh thường. |
| `data[].orderNo` | string |  | Số hiệu lệnh. |
| `data[].pk_orderNo` | string |  | Key lệnh. |
| `data[].side` | string |  | B = Long, S = Short. |
| `data[].symbol` | string |  | Mã hợp đồng. |
| `data[].volume` | number |  | Khối lượng đặt. |
| `data[].showPrice` | string |  | Giá đặt. |
| `data[].matchVolume` | number |  | Khối lượng khớp. |
| `data[].status` | string |  | Trạng thái lệnh. |
| `data[].isCancel` | string |  | 0 = không thể hủy, 1 = có thể hủy. |
| `data[].isAmend` | string |  | 0 = không thể sửa, 1 = có thể sửa. |

200 OK

Sao chép
```json
{
  "cmd": "Web.Order.IndayOrder",
  "rc": "1",
  "data": [
    {
      "orderNo": "37",
      "pk_orderNo": "7625908",
      "refId": "H.7387641765855363489",
      "orderTime": "13:34:47",
      "accountCode": "000112A",
      "side": "S",
      "symbol": "VN30F2303",
      "volume": "1",
      "showPrice": "MTL (1198)",
      "matchVolume": "1",
      "status": "PM",
      "orderStatus": "4",
      "channel": "I",
      "group": "FU",
      "isCancel": "0",
      "isAmend": "0",
      "orderType": "N",
      "source": "SYS"
    }
  ]
}
```
