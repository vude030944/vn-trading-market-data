<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/account/sub-account
Tieu de goc: 2.1. Lấy thông tin tiểu khoản
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/account/sub-account>

# 2.1. Lấy thông tin tiểu khoản

GET`/eros/v2/get-profile/by-username/{custodyCode}`

Lấy thông tin hồ sơ của một tài khoản lưu ký theo danh sách trường yêu cầu.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Path variable

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `custodyCode` | string |  | Số tài khoản lưu ký, ví dụ: 105C334455. |

## Request parameter

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `fields` | string |  | Danh sách thông tin cần lấy, ví dụ: basicInfo,bankSubAccounts. |

cURLNode.jsPythonJava

Sao chép

GET /eros/v2/get-profile/by-username/105C334455
```bash
curl "https://openapi.tcbs.com.vn/eros/v2/get-profile/by-username/105C334455?fields=basicInfo,bankSubAccounts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `basicInfo` | object |  | Thông tin cơ bản tài khoản. |
| `bankSubAccounts` | array |  | Danh sách tiểu khoản. |
| `bankSubAccounts[].accountNo` | string |  | Số tiểu khoản. |
| `bankSubAccounts[].accountName` | string |  | Tên chủ tài khoản. |
| `bankSubAccounts[].bankCode` | string |  | Mã ngân hàng (có thể null). |
| `bankSubAccounts[].accountType` | string |  | Loại tiểu khoản: NORMAL, MARGIN, DERIVATIVE. |
| `bankSubAccounts[].accountTypeName` | string |  | Tên loại tiểu khoản. |
| `bankSubAccounts[].status` | string |  | Trạng thái tiểu khoản. |
| `bankSubAccounts[].isDefault` | string |  | Là tiểu khoản mặc định (Y/N). |

200 OK

Sao chép
```json
{
  "basicInfo": {
    "custodyCode": "105C334455",
    "fullName": "NGUYEN VAN A",
    "status": "ACTIVE"
  },
  "bankSubAccounts": [
    {
      "accountNo": "0001K36265",
      "accountName": "Khuynh Thanh Chi Luyen",
      "bankCode": null,
      "accountType": "NORMAL",
      "accountTypeName": "Thường",
      "status": "1",
      "isDefault": "N"
    },
    {
      "accountNo": "0001G75216",
      "accountName": "Khuynh Thanh Chi Luyen",
      "bankCode": null,
      "accountType": "MARGIN",
      "accountTypeName": "Ký quỹ",
      "status": "1",
      "isDefault": "N"
    },
    {
      "accountNo": "105C738764A",
      "accountName": "Khuynh Thanh Chi Luyen",
      "bankCode": "105C738764A",
      "accountType": "DERIVATIVE",
      "accountTypeName": "Phái sinh",
      "status": "1",
      "isDefault": "N"
    }
  ]
}
```
