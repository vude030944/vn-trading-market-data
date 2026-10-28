<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/risk-ratios
Tieu de goc: 4.11. Tỷ lệ margin & rủi ro
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/risk-ratios>

# 4.11. Tỷ lệ margin & rủi ro

GET`/hydros/v1/account/{accountNo}/risk`

Lấy tổng nợ gốc, tổng nợ lãi, Rtt thực tế, tỷ lệ ký quỹ ban đầu, tỷ lệ duy trì, tỷ lệ cảnh báo cho tài khoản margin.

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

GET /hydros/v1/account/0001G75216/risk
```bash
curl "https://openapi.tcbs.com.vn/hydros/v1/account/0001G75216/risk" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `[].accountNo` | string |  | Số tiểu khoản. |
| `[].rtt` | number |  | Rtt thực tế. |
| `[].outstanding` | number |  | Tổng nợ gốc. |
| `[].accruedInterest` | number |  | Tổng nợ lãi. |
| `[].dueAmount` | number |  | Nợ đến hạn. |
| `[].overdueAmount` | number |  | Nợ quá hạn. |
| `[].totalFeeDebt` | number |  | Tổng nợ phí (Phí marginsure). |
| `[].riskPolicy.initialMargin` | number |  | Tỷ lệ ký quỹ ban đầu. |
| `[].riskPolicy.maintenanceMargin` | number |  | Tỷ lệ duy trì. |
| `[].riskPolicy.liquidationMargin` | number |  | Tỷ lệ cảnh báo. |
| `[].riskStatus.code` | string |  | Trạng thái RTT. |
| `[].riskStatus.description` | string |  | Mô tả trạng thái RTT. |

200 OK

Sao chép
```json
[
  {
    "accountNo": "0001I97267",
    "rtt": 99.95,
    "outstanding": 8858766677,
    "accruedInterest": 18638724,
    "dueAmount": 34621881,
    "overdueAmount": 34621881,
    "totalFeeDebt": 8885876,
    "riskPolicy": {
      "initialMargin": 100,
      "maintenanceMargin": 80,
      "liquidationMargin": 30
    },
    "riskStatus": {
      "code": "SAFE",
      "description": "An toàn"
    }
  }
]
```
