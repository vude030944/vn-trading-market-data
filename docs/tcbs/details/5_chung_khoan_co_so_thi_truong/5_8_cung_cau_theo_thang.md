<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/supply-demand-monthly
Tieu de goc: 5.8. Cung cầu theo tháng
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/supply-demand-monthly>

# 5.8. Cung cầu theo tháng

GET`/nyx/v1/intraday/{ticker}/bsa-month`

Lấy dữ liệu cung cầu theo tháng của một mã chứng khoán.

## Header

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `Authorization` | string |  | Bearer <access token>. |
| `Content-Type` | string |  | application/json. |

## Path variable

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `ticker` | string |  | Mã cổ phiếu, ví dụ TCB. |

## Request parameter

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `timeWindow` | string |  | Khung thời gian: 1M. |
| `type` | enum |  | Loại NĐT: sheep (cá nhân nhỏ lẻ), wolf (tổ chức vừa), shark (tổ chức lớn), all (tất cả, mặc định). |

cURLNode.jsPythonJava

Sao chép

GET /nyx/v1/intraday/TCB/bsa-month?timeWindow=1M&type=all
```bash
curl "https://openapi.tcbs.com.vn/nyx/v1/intraday/TCB/bsa-month?timeWindow=1M&type=all" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `ticker` | string |  | Mã cổ phiếu. |
| `data[].bup` | number |  | Tỷ lệ % mua tích cực. |
| `data[].sdp` | number |  | Tỷ lệ % bán tiêu cực. |
| `data[].bsr` | number |  | Tỷ lệ mua/bán. |
| `data[].t` | string |  | Thời gian (DD/MM). |

200 OK

Sao chép
```json
{
  "ticker": "TCB",
  "data": [
    {
      "bup": 0.65,
      "sdp": 0.35,
      "bsr": 1.25,
      "t": "07/05"
    }
  ]
}
```
