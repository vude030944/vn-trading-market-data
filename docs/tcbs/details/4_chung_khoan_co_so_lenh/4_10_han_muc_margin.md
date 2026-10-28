<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/margin-limit
Tieu de goc: 4.10. Hạn mức margin
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/margin-limit>

# 4.10. Hạn mức margin

GET`/aion/v1/customers/{custodyId}/accounts`

Lấy thông tin hạn mức margin của khách hàng theo số tài khoản lưu ký.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Path variable

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `custodyId` | string |  | Số tài khoản lưu ký. |

cURLNode.jsPythonJava

Sao chép

GET /aion/v1/customers/105C738764/accounts
```bash
curl "https://openapi.tcbs.com.vn/aion/v1/customers/105C738764/accounts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `[].custodyID` | string |  | Số tài khoản lưu ký. |
| `[].accountNo` | string |  | Số tiểu khoản. |
| `[].aftype` | string |  | Loại hình hợp đồng. |
| `[].vsdStatus` | string |  | Trạng thái VSD. |
| `[].accountStatus` | enum |  | Trạng thái: A = Được phép đặt lệnh, P = Không được phép, C = Đã đóng, B = Phong tỏa, N = Chờ đóng, R = Từ chối, T = Chờ cập nhật. |
| `[].marginLimit` | number |  | Hạn mức margin của tiểu khoản. |
| `[].accountType` | enum |  | Loại tiểu khoản: normal, margin, copier, trader, CHILD, CW, SPW, SPT. |
| `[].isIA` | enum |  | Có kết nối IA: Y = Có, N = Không. |
| `[].bankName` | string |  | Tên ngân hàng kết nối IA. |
| `[].bankAccount` | string |  | Số tài khoản kết nối IA. |

200 OK

Sao chép
```json
[
  {
    "custodyID": "105C738764",
    "accountNo": "0001000075",
    "aftype": "0075",
    "vsdStatus": "Y",
    "accountStatus": "A",
    "marginLimit": 0,
    "isIA": "Y",
    "bankName": "TCB",
    "bankAccount": "11520154590019",
    "accountType": "normal"
  }
]
```
