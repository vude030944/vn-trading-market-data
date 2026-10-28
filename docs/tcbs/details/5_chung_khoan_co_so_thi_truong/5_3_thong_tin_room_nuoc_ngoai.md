<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/foreign-room
Tieu de goc: 5.3. Thông tin room nước ngoài
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/foreign-room>

# 5.3. Thông tin room nước ngoài

GET`/tartarus/v1/tickerSnaps`

Lấy thông tin room nước ngoài và snapshot thị trường theo rổ chứng khoán.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Request parameter

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `index` | enum |  | Rổ chứng khoán: 1 = HOSE, 2 = VN30, 3 = HNX, 4 = HNX30, 5 = Upcom, 10 = Midcap, 11 = VN100, 12 = VNAllshare, 13 = VNSmallcap, 14 = VNXAllshare, 15 = VN50, 16 = VNSI. |

cURLNode.jsPythonJava

Sao chép

GET /tartarus/v1/tickerSnaps?index=1
```bash
curl "https://openapi.tcbs.com.vn/tartarus/v1/tickerSnaps?index=1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `tradingDate` | string |  | Ngày giao dịch. |
| `data[].symbol` | string |  | Mã cổ phiếu. |
| `data[].refPrice` | number |  | Giá tham chiếu. |
| `data[].ceilPrice` | number |  | Giá trần. |
| `data[].floorPrice` | number |  | Giá sàn. |
| `data[].matchPrice` | number |  | Giá khớp. |
| `data[].matchQtty` | number |  | Khối lượng khớp. |
| `data[].change` | number |  | Thay đổi giá. |
| `data[].changePercent` | number |  | % thay đổi. |
| `data[].totalVolume` | number |  | Tổng khối lượng. |
| `data[].totalValue` | number |  | Tổng giá trị. |
| `data[].buyForeignQtty` | number |  | KL nước ngoài mua. |
| `data[].sellForeignQtty` | number |  | KL nước ngoài bán. |
| `data[].room` | string |  | Room nước ngoài. |

200 OK

Sao chép
```json
{
  "tradingDate": "07/08/2025",
  "data": [
    {
      "symbol": "CRE",
      "ceilPrice": 30850,
      "floorPrice": 26850,
      "refPrice": 28850,
      "bidPrice01": 28750,
      "bidPrice02": 28700,
      "bidPrice03": 28650,
      "bidQtty01": 8700,
      "bidQtty02": 16200,
      "bidQtty03": 17500,
      "offerPrice01": 28800,
      "offerPrice02": 28850,
      "offerPrice03": 28900,
      "offerQtty01": 2200,
      "offerQtty02": 8600,
      "offerQtty03": 8900,
      "matchPrice": 28800,
      "matchQtty": 400,
      "change": -50.0,
      "changePercent": -0.17331,
      "totalVolume": 620700,
      "totalValue": 17916500000,
      "buyForeignQtty": 3400,
      "sellForeignQtty": 40500,
      "room": "44386227",
      "open": 28900,
      "high": 29100,
      "low": 28700
    }
  ]
}
```
