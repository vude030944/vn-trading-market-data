<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/derivative/account-status
Tieu de goc: 6.1. Tổng quan tiền, ký quỹ
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/account-status>

# 6.1. Tổng quan tiền, ký quỹ

GET`/khronos/v1/account/status`

Lấy tổng quan tiền và ký quỹ của tài khoản phái sinh.

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
| `getType` | enum |  | 0 = lấy toàn bộ, 1 = chỉ lấy tiền. |

cURLNode.jsPythonJava

Sao chép

GET /khronos/v1/account/status
```bash
curl "https://openapi.tcbs.com.vn/khronos/v1/account/status?accountId=105C031402&subAccountId=105C031402A&getType=1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `cmd` | string |  | Tên lệnh phản hồi. |
| `rc` | string |  | Mã kết quả, 1 = thành công. |
| `data` | object |  | Dữ liệu tổng quan tiền và ký quỹ. |

200 OK

Sao chép
```json
{
  "cmd": "Web.Portfolio.AccountStatus",
  "rc": "1",
  "data": { }
}
```
