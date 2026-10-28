<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/derivative/position-open
Tieu de goc: 6.3. Tài sản, vị thế mở
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/position-open>

# 6.3. Tài sản, vị thế mở

GET`/khronos/v1/account/portfolio/status`

Tra cứu danh sách vị thế mở của tài khoản phái sinh.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Request parameter

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `accountId` | string |  | Số tài khoản lưu ký. |
| `subAccountId` | string |  | Tiểu khoản phái sinh. |

cURLNode.jsPythonJava

Sao chép

GET /khronos/v1/account/portfolio/status
```bash
curl "https://openapi.tcbs.com.vn/khronos/v1/account/portfolio/status?accountId=105C031402&subAccountId=105C031402A" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `cmd` | string |  | Tên lệnh phản hồi. |
| `rc` | string |  | Mã kết quả, 1 = thành công. |
| `data` | array |  | Danh sách vị thế mở. |
| `data[].symbol` | string |  | Mã hợp đồng. |
| `data[].im` | string |  | Tỷ lệ ký quỹ. |
| `data[].deliver` | int64 |  | Số đã SHORT. |
| `data[].receive` | int64 |  | Số đã LONG. |
| `data[].net` | int64 |  | Vị thế mở (>0 = LONG, <0 = SHORT). |
| `data[].side` | string |  | L = Long, S = Short. |
| `data[].lastPrice` | number |  | Giá thị trường. |
| `data[].imValue` | number |  | Giá trị ký quỹ ban đầu. |
| `data[].vmValue` | number |  | Lãi/lỗ. |
| `data[].mrValue` | number |  | Ký quỹ yêu cầu. |
| `data[].duedate` | string |  | Ngày đáo hạn. |
| `data[].pc_remain` | string |  | % lãi/lỗ vị thế mở. |

200 OK

Sao chép
```json
{
  "cmd": "Web.Portfolio.PortfolioStatus2",
  "rc": "1",
  "data": [
    {
      "symbol": "VN30F2303",
      "im": "13%",
      "deliver": "4",
      "receive": "11",
      "net": 7,
      "side": "L",
      "account": "000111A",
      "wasp": 1120,
      "wapb": 1159.2,
      "lastPrice": 1198.4,
      "imValue": 109054400,
      "vmValue": 70560000,
      "mrValue": 109054400,
      "duedate": "29/06/2021",
      "netoffvol": 7,
      "avg_remain": 1120,
      "vm_remain": 54880000,
      "pc_remain": "53.85",
      "stoploss": "",
      "takeprofit": ""
    }
  ]
}
```
