<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/derivative/market-symbol
Tieu de goc: 7.1. Thông tin mã, giá
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/market-symbol>

# 7.1. Thông tin mã, giá

GET`/tartarus/v1/derivatives`

Lấy thông tin bảng giá tất cả hợp đồng phái sinh (giá trần, sàn, tham chiếu, 3 bước giá mua/bán, khớp lệnh, khối lượng).

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

cURLNode.jsPythonJava

Sao chép

GET /tartarus/v1/derivatives
```bash
curl "https://openapi.tcbs.com.vn/tartarus/v1/derivatives" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `data` | array |  | Danh sách hợp đồng phái sinh. |
| `data[].symbol` | string |  | Mã hợp đồng. |
| `data[].ceilPrice` | number |  | Giá trần. |
| `data[].floorPrice` | number |  | Giá sàn. |
| `data[].refPrice` | number |  | Giá tham chiếu. |
| `data[].bidPrice01` | number |  | Giá mua 1. |
| `data[].bidQtty01` | number |  | Khối lượng mua 1. |
| `data[].offerPrice01` | number |  | Giá bán 1. |
| `data[].offerQtty01` | number |  | Khối lượng bán 1. |
| `data[].matchPrice` | number |  | Giá khớp. |
| `data[].matchQtty` | number |  | Khối lượng khớp. |
| `data[].change` | number |  | Thay đổi giá. |
| `data[].changePercent` | number |  | % thay đổi. |
| `data[].totalVol` | number |  | Tổng khối lượng. |
| `data[].openVol` | number |  | Khối lượng mở. |
| `data[].expiryDate` | string |  | Ngày đáo hạn. |

200 OK

Sao chép
```json
{
  "data": [
    {
      "symbol": "VN30F2412",
      "ceilPrice": 1614.6,
      "floorPrice": 1403.4,
      "refPrice": 1509.0,
      "bidPrice01": 1499.5,
      "bidPrice02": 1499.3,
      "bidPrice03": 1499.2,
      "bidQtty01": 1.0,
      "bidQtty02": 3.0,
      "bidQtty03": 1.0,
      "offerPrice01": 1500.5,
      "offerPrice02": 1500.7,
      "offerPrice03": 1500.8,
      "offerQtty01": 1.0,
      "offerQtty02": 1.0,
      "offerQtty03": 1.0,
      "matchPrice": 1500.6,
      "matchQtty": 1.0,
      "change": -8.4,
      "changePercent": -0.56,
      "open": 1508.0,
      "high": 1509.4,
      "low": 1497.0,
      "totalVol": 370.0,
      "openVol": 897.0,
      "buyForeignQtty": 30.0,
      "sellForeignQtty": 58.0,
      "expiryDate": "18/11/2021",
      "avg": 150417189.19
    }
  ]
}
```
