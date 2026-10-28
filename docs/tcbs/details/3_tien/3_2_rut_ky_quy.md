<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/money/withdraw
Tieu de goc: 3.2. Rút ký quỹ
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/money/withdraw>

# 3.2. Rút ký quỹ

POST`/khronos/v1/cash/withdraw/update`

Rút tiền ký quỹ từ tài khoản phái sinh về tài khoản lưu ký.

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
| `amount` | number |  | Số tiền rút ký quỹ. |
| `paymentContent` | string |  | Nội dung rút tiền. |

cURLNode.jsPythonJava

Sao chép

POST /khronos/v1/cash/withdraw/update
```bash
curl -X POST https://openapi.tcbs.com.vn/khronos/v1/cash/withdraw/update \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"accountId":"105C000113","subAccountId":"105C000113A","amount":1500000,"paymentContent":"RUT TIEN KY QUY"}'
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `cmd` | string |  | Loại bút toán. |
| `rc` | string |  | Mã kết quả. 1: thành công, < 0: lỗi. |
| `rs` | string |  | Chi tiết lỗi. |
| `oID` | string |  | ID giao dịch. |
| `data` | array |  | Dữ liệu trả về. |

200 OK

Sao chép
```json
{
  "cmd": "",
  "rc": "1",
  "rs": "",
  "oID": "",
  "data": null
}
```
