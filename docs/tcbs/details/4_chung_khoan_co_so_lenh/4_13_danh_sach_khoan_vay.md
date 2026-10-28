<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/loan-list
Tieu de goc: 4.13. Danh sách khoản vay
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/loan-list>

# 4.13. Danh sách khoản vay

GET`/khaos/v1/loan/{accountNo}`

Lấy danh sách khoản vay của tài khoản margin.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Path variable

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `accountNo` | string |  | Số tài khoản margin. |

cURLNode.jsPythonJava

Sao chép

GET /khaos/v1/loan/0001G75216
```bash
curl "https://openapi.tcbs.com.vn/khaos/v1/loan/0001G75216" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `size` | number |  | Số bản ghi. |
| `content[].openingDate` | string |  | Ngày mở khoản vay. |
| `content[].dueDate` | string |  | Ngày đáo hạn. |
| `content[].renewTime` | number |  | Số lần đã gia hạn nợ. |
| `content[].maxRenewTime` | number |  | Giới hạn số lần gia hạn. |
| `content[].isRenewable` | boolean |  | Có được gia hạn: true/false. |
| `content[].reasonList` | array |  | Lý do không được gia hạn. |
| `content[].insurance.insuranceName` | string |  | Tên gói marginsure. |
| `content[].insurance.insuranceCode` | string |  | Mã gói marginsure. |
| `content[].insurance.insuranceFee` | number |  | Phí marginsure. |

200 OK

Sao chép
```json
{
  "size": 10,
  "content": [
    {
      "openingDate": "2024-09-06",
      "dueDate": "2024-12-04",
      "renewTime": 0,
      "maxRenewTime": 1,
      "isRenewable": false,
      "reasonList": ["Chưa đến ngày xin gia hạn"],
      "insurance": {
        "insuranceName": "Phòng ngự",
        "insuranceCode": "MRX_INSURANCE_PREMIUM_1",
        "insuranceFee": 0.15
      }
    }
  ]
}
```
