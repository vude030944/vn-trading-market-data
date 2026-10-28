<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/market-symbol
Tieu de goc: 5.1. Thông tin mã, giá
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/market-symbol>

# 5.1. Thông tin mã, giá

GET`/tartarus/v1/tickerCommons`

Lấy thông tin mã và giá của thị trường cơ sở. Bảng giá realtime dùng WebSocket ở mục 5.2.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Request parameter

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `tickers` | string |  | Danh sách mã cổ phiếu, phân tách bằng dấu phẩy. Không dùng kết hợp với param index. |
| `index` | number |  | Rổ chứng khoán: 1 = HOSE, 2 = VN30, 3 = HNX, 4 = HNX30, 5 = UPCOM, 10 = Midcap, 11 = VN100, 12 = VNAllShare, 13 = VNSmallCap, 14 = VNXAllShare, 15 = VN50, 16 = VNSI. Không dùng kết hợp với param tickers. |

cURLJavaGoPythonTypeScript

Sao chép

GET /tartarus/v1/tickerCommons?tickers=FPT,VNM
```bash
curl "https://openapi.tcbs.com.vn/tartarus/v1/tickerCommons?tickers=FPT,VNM" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `data` | array |  | Danh sách thông tin mã. |
| `data[].symbol` | string |  | Mã cổ phiếu. |
| `data[].ceilPrice` | number |  | Giá trần. |
| `data[].floorPrice` | number |  | Giá sàn. |
| `data[].refPrice` | number |  | Giá tham chiếu. |
| `data[].bidPrice01` | number |  | Dư mua giá 1. |
| `data[].bidPrice02` | number |  | Dư mua giá 2. |
| `data[].bidPrice03` | number |  | Dư mua giá 3. |
| `data[].bidQtty01` | number |  | Dư mua KL 1. |
| `data[].bidQtty02` | number |  | Dư mua KL 2. |
| `data[].bidQtty03` | number |  | Dư mua KL 3. |
| `data[].offerPrice01` | number |  | Dư bán giá 1. |
| `data[].offerPrice02` | number |  | Dư bán giá 2. |
| `data[].offerPrice03` | number |  | Dư bán giá 3. |
| `data[].offerQtty01` | number |  | Dư bán KL 1. |
| `data[].offerQtty02` | number |  | Dư bán KL 2. |
| `data[].offerQtty03` | number |  | Dư bán KL 3. |
| `data[].matchPrice` | number |  | Giá khớp. |
| `data[].matchQtty` | number |  | Khối lượng khớp. |
| `data[].change` | number |  | Thay đổi giá. |
| `data[].changePercent` | number |  | Phần trăm thay đổi. |
| `data[].open` | number |  | Giá mở cửa. |
| `data[].high` | number |  | Giá cao nhất. |
| `data[].low` | number |  | Giá thấp nhất. |
| `data[].avg` | number |  | Giá trung bình. |
| `data[].totalVol` | number |  | Tổng khối lượng giao dịch. |
| `data[].totalVal` | number |  | Tổng giá trị giao dịch. |
| `data[].buyForeignQtty` | number |  | KL mua nước ngoài. |
| `data[].sellForeignQtty` | number |  | KL bán nước ngoài. |
| `data[].room` | string |  | Room nước ngoài. |
| `data[].indexNumber` | number |  | Mã rổ chứng khoán. |
| `tradingDate` | string |  | Ngày giao dịch (dd/MM/yyyy). |

200 OK

Sao chép
```json
{
  "data": [
    {
      "symbol": "FPT",
      "ceilPrice": 106100.0,
      "floorPrice": 92300.0,
      "refPrice": 99200.0,
      "bidPrice01": 98700.0,
      "bidPrice02": 98600.0,
      "bidPrice03": 98500.0,
      "bidQtty01": 11300.0,
      "bidQtty02": 56800.0,
      "bidQtty03": 45600.0,
      "offerPrice01": 98800.0,
      "offerPrice02": 98900.0,
      "offerPrice03": 99000.0,
      "offerQtty01": 100.0,
      "offerQtty02": 23200.0,
      "offerQtty03": 56100.0,
      "matchPrice": 98800.0,
      "matchQtty": 100.0,
      "change": -400.0,
      "changePercent": -0.4032,
      "open": 99200.0,
      "avg": 98800.0,
      "high": 99200.0,
      "low": 98500.0,
      "totalVol": 833900.0,
      "totalVal": 82409370000.0,
      "buyForeignQtty": 647300.0,
      "sellForeignQtty": 648500.0,
      "room": "84",
      "indexNumber": 1
    }
  ],
  "tradingDate": "29/10/2024"
}
```
