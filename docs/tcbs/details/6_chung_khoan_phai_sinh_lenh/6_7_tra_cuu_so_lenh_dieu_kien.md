<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/derivative/get-condition-orders
Tieu de goc: 6.7. Tra cứu sổ lệnh điều kiện
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/get-condition-orders>

# 6.7. Tra cứu sổ lệnh điều kiện

GET`/khronos/v1/order/condition/detail`

Tra cứu sổ lệnh điều kiện của tài khoản phái sinh.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Request parameter

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `accountId` | string |  | Số tài khoản lưu ký. |
| `subAccountID` | string |  | Số tài khoản phái sinh. |
| `pageNo` | string |  | Số trang. |
| `PageSize` | string |  | Số phần tử trong trang. |
| `orderStatus` | enum |  | 0 = tất cả, 1 = chờ kích hoạt, 2 = đã kích hoạt, 3 = từ chối. |
| `orderType` | enum |  | '' = tất cả, 3 = Arbitrage, 4 = SL/TP, 5 = Stop order. |
| `Symbol` | string |  | Lọc: ALL,ALL = tất cả; VN30F2303,B = theo mã. |

cURLNode.jsPythonJava

Sao chép

GET /khronos/v1/order/condition/detail
```bash
curl "https://openapi.tcbs.com.vn/khronos/v1/order/condition/detail?accountId=105C031402&subAccountID=105C031402A&pageNo=1&PageSize=25&orderStatus=0&orderType=&Symbol=ALL,ALL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `rc` | string |  | Mã kết quả, 1 = thành công. |
| `data` | array |  | Danh sách lệnh điều kiện. |
| `data[].orderNo` | string |  | Số hiệu lệnh. |
| `data[].pk_orderNo` | string |  | Key lệnh. |
| `data[].side` | string |  | B = Long, S = Short. |
| `data[].symbol` | string |  | Mã hợp đồng. |
| `data[].showPrice` | number |  | Giá đặt. |
| `data[].volume` | number |  | Khối lượng đặt. |
| `data[].soPrice` | number |  | Giá stop. |
| `data[].orderType` | string |  | SL = giá >=, SU = giá <=. |
| `data[].status` | enum |  | 0 = chờ kích hoạt, 1 = đã kích hoạt, 2 = đã hủy, 3 = từ chối. |
| `data[].notes` | string |  | Loại lệnh: SL/TP, Stop order, Arbitrage. |

200 OK

Sao chép
```json
{
  "cmd": "Web.Order.ConditionOrder",
  "rc": "1",
  "data": [
    {
      "orderNo": "1",
      "groupOrder": "463502",
      "pk_orderNo": "463504",
      "accountCode": "000112A",
      "side": "B",
      "symbol": "VN30F2303",
      "showPrice": "1190.5",
      "volume": "2",
      "soPrice": "1190.5",
      "orderType": "SL",
      "from_time": "29/04/2021",
      "exp_time": "29/04/2021",
      "status": "0",
      "send_time": "14:01:01",
      "notes": "SL/TP"
    }
  ]
}
```
