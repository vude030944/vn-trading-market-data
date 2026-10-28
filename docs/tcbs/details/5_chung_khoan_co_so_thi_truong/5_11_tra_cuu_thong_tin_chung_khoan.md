<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/securities-info
Tieu de goc: 5.11. Tra cứu thông tin chứng khoán
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/securities-info>

# 5.11. Tra cứu thông tin chứng khoán

GET`/ananke/v1/securities`

Tra cứu thông tin chi tiết của mã chứng khoán: thông tin niêm yết, giá trần/sàn, sàn giao dịch, loại chứng khoán, hạn mức giao dịch, v.v.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Query parameters

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `fields` | string |  | Danh sách field cần trả về. Mặc định: all. |
| `filter` | string |  | Bộ lọc theo cú pháp field=value, ví dụ: symbol=TCB. |

cURLNode.jsPythonJava

Sao chép

GET /ananke/v1/securities?fields=all&filter=symbol=TCB
```bash
curl -X GET "https://openapi.tcbs.com.vn/ananke/v1/securities?fields=all&filter=symbol=TCB" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

Trả về danh sách chứng khoán có phân trang. Mỗi item chứa thông tin cơ bản và object `securitiesInfo` chứa chi tiết niêm yết.

### Level 1 — Thông tin cơ bản

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `codeId` | string |  | Mã số qui ước của chứng khoán. |
| `issuerId` | string |  | Mã tổ chức phát hành. |
| `issuerName` | string |  | Tên tổ chức phát hành. |
| `symbol` | string |  | Mã niêm yết giao dịch. |
| `secType` | enum |  | Phân loại CK: 001=Cổ phiếu phổ thông, 002=CP ưu đãi, 003=TP chuyển đổi, 006=Trái phiếu, ... |
| `investmentType` | enum |  | Hình thức đầu tư: 001=Ngắn hạn, 002=Dài hạn. |
| `issueDate` | datetime |  | Ngày phát hành. |
| `expDate` | datetime |  | Ngày hết hạn. |
| `underlyingSymbol` | string |  | Mã gốc (VD: mã chứng quyền). |
| `coveredWarrantType` | string |  | Loại chứng quyền. |
| `exercisePrice` | number |  | Giá quyền. |
| `parValue` | number |  | Mệnh giá chứng khoán. |
| `tradePlace` | enum |  | Nơi giao dịch: 001=HOSE, 002=HNX, 005=UPCOM. |
| `status` | string |  | Có sử dụng hay không (Y/N). |
| `halt` | string |  | Tạm ngừng giao dịch (Y/N). |

### Level 2 — securitiesInfo

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `symbol` | string |  | Mã niêm yết. |
| `status` | enum |  | Trạng thái GD: 001=Bình thường, 002=Tạm ngừng, 003=Dừng, 004=Giám sát, 005=Cảnh báo. |
| `listingQtty` | int64 |  | Tổng khối lượng niêm yết. |
| `txDate` | date |  | Ngày giao dịch. |
| `listingStatus` | enum |  | Trạng thái niêm yết: N=Bình thường, L=Niêm yết mới, U=Hủy, I=Tăng vốn, D=Giảm vốn. |
| `tradeUnit` | int64 |  | Đơn vị giá giao dịch. |
| `ceilingPrice` | int64 |  | Giá trần. |
| `floorPrice` | int64 |  | Giá sàn. |
| `basicPrice` | int64 |  | Giá tham chiếu. |
| `tradeLot` | int64 |  | Đơn vị khối lượng giao dịch. |
| `tradeBuySell` | string |  | Cho phép mua bán cùng ngày (Y/N). |
| `marginLimitMax` | int64 |  | Hạn mức giao dịch margin tối đa. |
| `currentRoom` | int64 |  | Room còn lại của NĐTNN. |
| `securedRatioMax` | number |  | Tỷ lệ ký quỹ tối đa. |
| `mortageRatioMax` | number |  | Tỷ lệ cầm cố tối đa. |

### Phân trang

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `totalElements` | int64 |  | Tổng số bản ghi. |
| `totalPages` | int64 |  | Tổng số trang. |
| `size` | int64 |  | Số bản ghi mỗi trang (mặc định 1000). |
| `number` | int64 |  | Trang hiện tại (0-indexed). |
| `first` | boolean |  | Có phải trang đầu. |
| `last` | boolean |  | Có phải trang cuối. |

200 OK

Sao chép
```json
{
"content": [
  {
    "codeId": "003415",
    "issuerId": "0000001736",
    "issuerName": "Công ty cổ phần Kỹ thương",
    "symbol": "TCB",
    "secType": "001",
    "investmentType": "002",
    "issueDate": "2016-12-14T00:00:00.000+07:00",
    "expDate": "2016-12-14T00:00:00.000+07:00",
    "parValue": 10000,
    "tradePlace": "001",
    "status": "Y",
    "securitiesInfo": {
      "symbol": "TCB",
      "status": "001",
      "listingQtty": 3517238514,
      "txDate": "2016-12-13",
      "listingStatus": "N",
      "tradeUnit": 1000,
      "ceilingPrice": 56700,
      "floorPrice": 49300,
      "tradeLot": 100,
      "tradeBuySell": "Y",
      "securedRatioMax": 102
    }
  }
],
"totalElements": 1,
"totalPages": 1,
"size": 1000,
"number": 0,
"first": true,
"last": true
}
```
