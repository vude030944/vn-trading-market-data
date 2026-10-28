<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/addon-loan
Tieu de goc: 4.12. Gói vay bổ trợ
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/addon-loan>

# 4.12. Gói vay bổ trợ

GET`/campaign-management/v1/margin/subscription/{accountNo}/addons/detail`

Lấy thông tin chi tiết gói vay bổ trợ (Marginsure, T+) của tài khoản margin.

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

GET /campaign-management/v1/margin/subscription/0001G75216/addons/detail
```bash
curl "https://openapi.tcbs.com.vn/campaign-management/v1/margin/subscription/0001G75216/addons/detail" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `marginSureViews[].id` | number |  | Id gói marginsure. |
| `marginSureViews[].name` | string |  | Tên gói marginsure. |
| `marginSureViews[].code` | string |  | Mã gói marginsure. |
| `marginSureViews[].subscriptionFee` | number |  | Phí tham gia. |
| `marginSureViews[].status` | string |  | Trạng thái đăng ký gói. |
| `tplus.data[].id` | number |  | ID gói T+. |
| `tplus.data[].name` | string |  | Tên gói T+. |
| `tplus.data[].firstRate` | number |  | Lãi suất bậc 1 của gói T+. |
| `tplus.data[].status` | string |  | Trạng thái gói T+. |

200 OK

Sao chép
```json
{
  "marginSureViews": [
    {
      "id": 37,
      "name": "Phòng ngự_E2E",
      "code": "MRX_INSURANCE_PREMIUM",
      "subscriptionFee": 0.12,
      "status": "INACTIVE",
      "proposals": [
        {
          "id": 82,
          "marginInsuranceId": 37,
          "interestAdjustmentValue": -2.5,
          "interestPercentThreshold": -3.0,
          "thresholdType": "LOWER"
        }
      ],
      "default": true
    }
  ],
  "tplus": {
    "data": [
      {
        "id": 153,
        "name": "E2E MARGIN T5",
        "firstRate": 5,
        "status": "ACTIVE",
        "undueInterestType": "LADDER",
        "overdueInterest": 150
      }
    ]
  }
}
```
