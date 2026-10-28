<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/money/transfer
Tieu de goc: 3.1. Chuyển tiền nội bộ
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/money/transfer>

# 3.1. Chuyển tiền nội bộ

POST`/physis/v1/stock/transfer`

Chuyển tiền giữa hai tiểu khoản trong cùng tài khoản.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Request Body

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `sourceAccountNumber` | string |  | Tiểu khoản nguồn. |
| `destinationAccountNumber` | string |  | Tiểu khoản đích. |
| `amount` | number |  | Số tiền cần chuyển. |
| `description` | string |  | Nội dung chuyển tiền. |

cURLNode.jsPythonJava

Sao chép

POST /physis/v1/stock/transfer
```bash
curl -X POST https://openapi.tcbs.com.vn/physis/v1/stock/transfer \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sourceAccountNumber":"0001170730","destinationAccountNumber":"105C738764A","amount":90000,"description":"CHUYEN TIEN PHAI SINH"}'
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `code` | string |  | Code trả về, 200 là thành công, khác 200 là lỗi. |
| `message` | string |  | Mô tả mã lỗi nếu có. |

200 OK

Sao chép
```json
{
  "code": "200",
  "message": "OK"
}
```
