<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/money/deposit
Tieu de goc: 3.3. Nộp ký quỹ
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/money/deposit>

# 3.3. Nộp ký quỹ

POST`/khronos/v1/cash/deposit/update`

Nộp tiền ký quỹ từ tài khoản lưu ký vào tài khoản phái sinh.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Request Body

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `accountId` | string |  | Số tài khoản lưu ký. |
| `subAccountId` | string |  | Số tài khoản phái sinh. |
| `amount` | number |  | Số tiền nộp ký quỹ. |
| `paymentContent` | string |  | Nội dung nộp tiền. |

cURLNode.jsPythonJava

Sao chép

POST /khronos/v1/cash/deposit/update
```bash
curl -X POST https://openapi.tcbs.com.vn/khronos/v1/cash/deposit/update \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"accountId":"105C000113","subAccountId":"105C000113A","amount":1500000,"paymentContent":"NAP TIEN KY QUY"}'
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `cmd` | string |  | Loại bút toán. |
| `rc` | string |  | Mã kết quả. 1: thành công, < 0: lỗi. |
| `rs` | string |  | Chi tiết lỗi. |
| `oID` | string |  | ID giao dịch. |
| `data` | array |  | Dữ liệu trả về (chứa transactionId). |

200 OK

Sao chép
```json
{
  "cmd": "",
  "rc": "1",
  "rs": "",
  "oID": "",
  "data": [{
    "transactionId": "CA330E033D3BD113E053EE02070AED89"
  }]
}
```
