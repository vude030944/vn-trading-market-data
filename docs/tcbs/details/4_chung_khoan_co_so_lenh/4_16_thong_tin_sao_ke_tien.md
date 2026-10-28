<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/cash-statement
Tieu de goc: 4.16. Thông tin sao kê tiền
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/cash-statement>

# 4.16. Thông tin sao kê tiền

GET`/erebos/v2/digital/trans-hist-cashStatements`

Lấy thông tin sao kê tiền (lịch sử giao dịch tiền) của một tiểu khoản.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Request parameter

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `accountNo` | string |  | Số tiểu khoản. |
| `fromDate` | string |  | Từ ngày giao dịch (YYYY-MM-DD). |
| `toDate` | string |  | Đến ngày giao dịch (YYYY-MM-DD). |
| `pageSize` | string |  | Số bản ghi mỗi trang. |
| `pageIndex` | string |  | Số trang. |
| `transactionCode` | string |  | Loại giao dịch. |

cURLNode.jsPythonJava

Sao chép

GET /erebos/v2/digital/trans-hist-cashStatements?accountNo=0001170730&fromDate=2025-01-01&toDate=2025-01-15&pageSize=25&pageIndex=1&transactionCode=1153
```bash
curl "https://openapi.tcbs.com.vn/erebos/v2/digital/trans-hist-cashStatements?accountNo=0001170730&fromDate=2025-01-01&toDate=2025-01-15&pageSize=25&pageIndex=1&transactionCode=1153" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `response.pageIndex` | int64 |  | Page index. |
| `response.pageSize` | int64 |  | Page size. |
| `response.totalCreditAmount` | int64 |  | Tổng phát sinh giảm. |
| `response.totalDebitAmount` | int64 |  | Tổng phát sinh tăng. |
| `response.totalCount` | int64 |  | Tổng số bản ghi. |
| `response.data[].custodyID` | string |  | Số tài khoản. |
| `response.data[].transactionCode` | string |  | Loại giao dịch. |
| `response.data[].transactionName` | string |  | Tên loại giao dịch. |
| `response.data[].debitAmount` | number |  | Số tiền phát sinh tăng. |
| `response.data[].creditAmount` | number |  | Số tiền phát sinh giảm. |
| `response.data[].businessDate` | string |  | Ngày làm việc. |
| `response.data[].transactionDate` | string |  | Ngày giao dịch. |
| `response.data[].descriptions` | string |  | Mô tả. |

200 OK

Sao chép
```json
{
  "response": {
    "pageIndex": 1,
    "pageSize": 25,
    "totalCreditAmount": 9545594,
    "totalDebitAmount": 10715,
    "totalCount": 8,
    "data": [
      {
        "custodyID": "105C209414",
        "transactionCode": "1153",
        "transactionName": "Ứng trước tiền bán",
        "debitAmount": 0,
        "creditAmount": 2814359,
        "businessDate": "2022-12-16",
        "transactionDate": "2022-12-16",
        "transactionNum": "6800124310",
        "accountNo": "0001490922",
        "descriptions": "UTTB ngày GD 16-DEC-22, ngày TT 20/12/2022"
      }
    ]
  }
}
```
