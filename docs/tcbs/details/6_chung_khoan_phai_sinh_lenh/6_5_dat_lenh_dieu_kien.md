<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/derivative/place-condition-order
Tieu de goc: 6.5. Đặt lệnh điều kiện
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/place-condition-order>

# 6.5. Đặt lệnh điều kiện

POST`/khronos/v1/order/condition/place`

Đặt lệnh điều kiện trên thị trường phái sinh (Stop order, Trailing Stop, SL/TP, Arbitrage).

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
| `symbol` | string |  | Mã phái sinh, ví dụ VN30F2110. |
| `price` | number |  | Giá đặt. |
| `volume` | number |  | Số lượng, lớn hơn 0. |
| `orderType` | enum |  | SOL = giá TT >= soPrice, SOU = giá TT <= soPrice, TSO = Trailing Stop. |
| `soPrice` | number |  | Giá kích hoạt. |
| `callbackPoint` | number |  | Biên trượt (chỉ dùng khi orderType = TSO). |
| `activationPrice` | number |  | Giá kích hoạt (chỉ dùng khi orderType = TSO). |
| `refId` | string |  | Số chống trùng theo từng lệnh. |

cURLNode.jsPythonJava

Sao chép

POST /khronos/v1/order/condition/place
```bash
curl -X POST https://openapi.tcbs.com.vn/khronos/v1/order/condition/place \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"accountId":"105C031402","subAccountId":"105C031402A","side":"B","symbol":"VN30F2110","price":1506.0,"volume":300,"orderType":"SOL","soPrice":1505.7,"callbackPoint":0.1,"activationPrice":1505.7,"refId":""}'
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `rc` | string |  | Mã kết quả, 1 = thành công. |
| `data[].symbol` | string |  | Mã hợp đồng. |
| `data[].status` | string |  | Trạng thái lệnh. |
| `data[].orderNo` | int64 |  | Số hiệu lệnh. |
| `data[].pk_orderNo` | string |  | Key lệnh (để hủy/sửa). |

200 OK

Sao chép
```json
{
  "cmd": "Web.newOrder",
  "rc": "1",
  "data": [
    {
      "symbol": "VN30F2110",
      "status": "P",
      "msg_type": "1I",
      "showPrice": "1504.4",
      "orderTime": "20:16:57",
      "accountCode": "100159A",
      "orderNo": 1,
      "matchVolume": 0,
      "side": "B",
      "volume": "1",
      "pk_orderNo": "7843961",
      "channel": "D",
      "group": "FU",
      "quote": "G"
    }
  ]
}
```
