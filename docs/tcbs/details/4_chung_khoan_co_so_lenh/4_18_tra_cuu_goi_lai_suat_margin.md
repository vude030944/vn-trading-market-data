<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/pricing-policy
Tieu de goc: 4.18. Tra cứu gói lãi suất margin
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/pricing-policy>

# 4.18. Tra cứu gói lãi suất margin

GET`/hydros/v1/account/{accountNo}/pricing-policy`

Lấy danh sách pricing policy khả dụng cho tài khoản margin. Bao gồm policy đang active, policy pending (chờ apply), và các policy mà group của account có quyền đăng ký.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Path variable

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `accountNo` | string |  | Số tài khoản margin. |

## Query parameters

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `productId` | int64 |  | ID sản phẩm. Nếu không truyền, hệ thống tự resolve từ account. |

cURLNode.jsPythonJava

Sao chép

GET /hydros/v1/account/0001170730/pricing-policy
```bash
curl -X GET "https://openapi.tcbs.com.vn/hydros/v1/account/0001170730/pricing-policy" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

Trả về danh sách pricing policy. Mỗi policy có thể chứa danh sách `states` là các thay đổi đang chờ apply.

### PricingPolicy

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | int64 |  | ID pricing policy. |
| `name` | string |  | Tên policy. |
| `status` | enum |  | Trạng thái: ACTIVE (đang dùng), INACTIVE (chưa đăng ký), PENDING (chờ apply). |
| `pricingPolicyType` | enum |  | Loại: DEFAULT, T_PLUS, DYNAMIC_MARGIN, TRIFORCE, G1, G2, G3. |
| `undueInterestType` | enum |  | Loại lãi suất trong hạn: FIXED hoặc LADDER. |
| `undueFixedValue` | number |  | Lãi suất cố định trong hạn (% năm), khi type = FIXED. |
| `undueLadderValue` | array |  | Bậc thang lãi suất (khi type = LADDER). Xem bảng LadderInterest. |
| `leastMassRate` | number |  | Lãi suất mass thấp nhất. |
| `greatestMassRate` | number |  | Lãi suất mass cao nhất. |
| `overdueInterest` | number |  | Lãi suất quá hạn (% năm). |
| `extensionInterest` | number |  | Lãi suất gia hạn. |
| `interestCalculationBasis` | int64 |  | Cơ sở tính lãi: 365 hoặc 360. |
| `validFrom` | date |  | Ngày bắt đầu hiệu lực (yyyy-MM-dd). |
| `validTo` | date |  | Ngày kết thúc hiệu lực. |
| `description` | string |  | Mô tả policy. |
| `labels` | array |  | Nhãn phân loại. |
| `discountable` | boolean |  | Có thể chiết khấu lãi suất. |
| `states` | array |  | Danh sách state thay đổi đang chờ apply. |

### LadderInterest

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `id` | int64 |  | ID bậc lãi suất. |
| `rate` | number |  | Lãi suất (% năm). |
| `startDate` | int64 |  | Ngày bắt đầu (ngày thứ n kể từ ngày vay). |
| `dueDate` | int64 |  | Ngày đáo hạn (ngày thứ n). |

Lưu ý: Response chỉ chứa các field có giá trị (null fields bị loại bỏ). Timezone mặc định: Asia/Ho_Chi_Minh (+07:00).

200 OK

Sao chép
```json
{
"data": [
  {
    "id": 1,
    "name": "Standard Policy",
    "status": "ACTIVE",
    "pricingPolicyType": "DEFAULT",
    "undueInterestType": "FIXED",
    "undueFixedValue": 12.5,
    "leastMassRate": 10.0,
    "greatestMassRate": 15.0,
    "overdueInterest": 18.0,
    "extensionInterest": 14.0,
    "interestCalculationBasis": 365,
    "description": "Gói lãi suất tiêu chuẩn",
    "labels": ["standard", "default"],
    "validFrom": "2024-01-01",
    "validTo": "2025-12-31",
    "discountable": true,
    "states": [
      {
        "stateId": 10,
        "name": "State Jan 2025",
        "status": "WAIT_FOR_APPLY",
        "isAppliedForExisting": true,
        "undueInterestType": "LADDER",
        "undueLadderValue": [
          { "id": 5, "rate": 11.0, "startDate": 1, "dueDate": 15 }
        ],
        "overdueInterest": 17.0,
        "extensionInterest": 13.5,
        "validFrom": "2025-02-01",
        "validTo": "2025-12-31"
      }
    ]
  }
]
}
```

## Mã lỗi

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `200` | string |  | Không tìm thấy sản phẩm cho account. |
| `202` | string |  | Không tìm thấy pricing policy hiện tại. |
| `203` | string |  | Account chưa đăng ký sản phẩm với productId chỉ định. |
