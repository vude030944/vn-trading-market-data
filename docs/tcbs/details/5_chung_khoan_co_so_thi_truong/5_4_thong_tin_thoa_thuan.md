<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/put-through
Tieu de goc: 5.4. Thông tin thỏa thuận
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/put-through>

# 5.4. Thông tin thỏa thuận

GET`/tartarus/v1/putThroughSnaps`

Lấy thông tin giao dịch thỏa thuận (quảng cáo mua/bán và khớp thỏa thuận).

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Request parameter

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `floor` | enum |  | Rổ chứng khoán: 1 = HOSE, 2 = HNX, 3 = Upcom. |

cURLNode.jsPythonJava

Sao chép

GET /tartarus/v1/putThroughSnaps?floor=1
```bash
curl "https://openapi.tcbs.com.vn/tartarus/v1/putThroughSnaps?floor=1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `buyAdv[].symbol` | string |  | Mã cổ phiếu. |
| `buyAdv[].price` | number |  | Giá. |
| `buyAdv[].vol` | number |  | Khối lượng. |
| `buyAdv[].time` | string |  | Thời gian. |
| `buyAdv[].side` | string |  | Chiều (B = Mua). |
| `sellAdv[].symbol` | string |  | Mã cổ phiếu. |
| `sellAdv[].price` | number |  | Giá. |
| `sellAdv[].vol` | number |  | Khối lượng. |
| `sellAdv[].side` | string |  | Chiều (S = Bán). |
| `match[].symbol` | string |  | Mã cổ phiếu. |
| `match[].price` | number |  | Giá khớp. |
| `match[].vol` | number |  | Khối lượng khớp. |
| `match[].val` | number |  | Giá trị. |
| `match[].time` | string |  | Thời gian khớp. |
| `match[].accumulatedValue` | number |  | Giá trị tích lũy. |

200 OK

Sao chép
```json
{
  "buyAdv": [
    {
      "symbol": "DHT",
      "price": 24300.0,
      "vol": 50.0,
      "time": "20231220-02:16:13.588",
      "status": 1,
      "color": 3,
      "orderId": "DHT00000000000036",
      "side": "B"
    }
  ],
  "sellAdv": [
    {
      "symbol": "TCB",
      "price": 24300.0,
      "vol": 50.0,
      "time": "20231220-02:16:13.588",
      "status": 1,
      "color": 3,
      "orderId": "TCB00000000000036",
      "side": "S"
    }
  ],
  "match": [
    {
      "symbol": "TCB",
      "price": 23455.5,
      "vol": 5000.0,
      "val": 117275000,
      "time": "20:00:03",
      "accumulatedValue": 254440000
    }
  ]
}
```
