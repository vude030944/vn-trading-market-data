<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/supply-demand-intraday
Tieu de goc: 5.6. Cung cầu trong phiên (15m)
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/supply-demand-intraday>

# 5.6. Cung cầu trong phiên (15m)

GET`/nyx/v1/intraday/{ticker}/bsa-ext`

Lấy dữ liệu cung cầu trong ngày theo khung thời gian 15 phút hoặc 60 phút.

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
| `timeWindow` | enum |  | Khung thời gian (phút): 15 hoặc 60. |
| `tWindow` | enum |  | Khung thời gian (phút): 15. |
| `type` | enum |  | Loại NĐT: sheep (cá nhân nhỏ lẻ), wolf (tổ chức vừa), shark (tổ chức lớn), all (tất cả, mặc định). |

cURLNode.jsPythonJava

Sao chép

GET /nyx/v1/intraday/TCB/bsa-ext?timeWindow=15&tWindow=15&type=all
```bash
curl "https://openapi.tcbs.com.vn/nyx/v1/intraday/TCB/bsa-ext?timeWindow=15&tWindow=15&type=all" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `ticker` | string |  | Mã cổ phiếu. |
| `data[].bu` | number |  | Khối lượng mua tích cực. |
| `data[].bms` | number |  | Tổng tích lũy mua. |
| `data[].bup` | number |  | Tỷ lệ % mua tích cực. |
| `data[].sd` | number |  | Khối lượng bán tiêu cực. |
| `data[].sms` | number |  | Tổng tích lũy bán. |
| `data[].sdp` | number |  | Tỷ lệ % bán tiêu cực. |
| `data[].bsr` | number |  | Tỷ lệ mua/bán. |
| `data[].t` | string |  | Thời gian (HH:mm:ss). |
| `data[].s` | number |  | Thời gian (timestamp). |

200 OK

Sao chép
```json
{
  "ticker": "TCB",
  "data": [
    {
      "bu": 1000000,
      "bms": 5000000,
      "bup": 0.65,
      "sd": 800000,
      "sms": 3000000,
      "sdp": 0.35,
      "bsr": 1.25,
      "t": "09:15:00",
      "s": 1640995200000
    }
  ]
}
```
