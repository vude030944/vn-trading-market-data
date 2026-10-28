<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/debt-lookup
Tieu de goc: 4.17. Tra cứu nợ
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/debt-lookup>

# 4.17. Tra cứu nợ

GET`/erebos/v2/digital/margin-info`

Tra cứu thông tin nợ margin của một tiểu khoản.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Request parameter

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `acctno` | string |  | Số tiểu khoản. |
| `fromdate` | string |  | Từ ngày (YYYY-MM-DD). |
| `toDate` | string |  | Đến ngày (YYYY-MM-DD). |
| `page` | string |  | Số trang. |
| `size` | string |  | Số bản ghi mỗi trang. |
| `custodycd` | string |  | Số tài khoản lưu ký. |

cURLNode.jsPythonJava

Sao chép

GET /erebos/v2/digital/margin-info?acctno=0001170730&fromdate=2025-01-01&toDate=2025-01-15&page=1&size=25&custodycd=105C209414
```bash
curl "https://openapi.tcbs.com.vn/erebos/v2/digital/margin-info?acctno=0001170730&fromdate=2025-01-01&toDate=2025-01-15&page=1&size=25&custodycd=105C209414" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `response.totalRow` | int64 |  | Số bản ghi. |
| `response.totalPage` | int64 |  | Số trang. |
| `response.data[].releaseDate` | string |  | Ngày giải ngân. |
| `response.data[].overDueDate` | string |  | Ngày đáo hạn. |
| `response.data[].releasedAmount` | number |  | Gốc giải ngân. |
| `response.data[].printAmount` | number |  | Nợ gốc hiện tại. |
| `response.data[].intAmount` | number |  | Nợ lãi và phí hiện tại. |
| `response.data[].remainingInterestFee` | number |  | Tổng nợ lãi và phí hiện tại. |
| `response.data[].paidInterestFee` | number |  | Tổng lãi và phí đã trả. |
| `response.data[].rate2` | number |  | Lãi suất. |
| `response.data[].releasedDay` | number |  | Số ngày vay. |
| `response.data[].paidFee` | number |  | Phí đã trả. |
| `response.data[].remainingFee` | number |  | Phí còn lại. |

200 OK

Sao chép
```json
{
  "response": {
    "totalRow": 1,
    "totalPage": 6,
    "data": [
      {
        "releaseDate": "2022-07-11",
        "overDueDate": "2022-10-10",
        "releasedAmount": 14444940,
        "printAmount": 0,
        "intAmount": 0,
        "remainingInterestFee": 0,
        "paidInterestFee": 18205,
        "rate2": 11.5,
        "releasedDay": 4,
        "paidFee": 0,
        "remainingFee": 0
      }
    ]
  }
}
```
