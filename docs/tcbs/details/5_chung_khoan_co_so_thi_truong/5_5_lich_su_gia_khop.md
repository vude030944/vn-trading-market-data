<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/stock/price-history
Tieu de goc: 5.5. Lịch sử giá khớp
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/stock/price-history>

# 5.5. Lịch sử giá khớp

GET`/nyx/v1/intraday/{ticker}/his/paging`

Lấy lịch sử giá khớp trong ngày của một mã chứng khoán (có phân trang).

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
| `page` | number |  | Số trang (bắt đầu từ 0). |
| `size` | number |  | Số dòng mỗi trang (tối đa 100). |
| `headIndex` | number |  | Chỉ số đầu để phân trang ngược (mặc định -1). |

cURLNode.jsPythonJava

Sao chép

GET /nyx/v1/intraday/TCB/his/paging?page=0&size=20
```bash
curl "https://openapi.tcbs.com.vn/nyx/v1/intraday/TCB/his/paging?page=0&size=20" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## Response

| Tên | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `page` | number |  | Trang hiện tại. |
| `size` | number |  | Kích thước trang. |
| `headIndex` | number |  | Chỉ số đầu. |
| `numberOfItems` | number |  | Số bản ghi trả về. |
| `total` | number |  | Tổng số lệnh khớp. |
| `ticker` | string |  | Mã cổ phiếu. |
| `data[].p` | number |  | Giá khớp lệnh. |
| `data[].v` | number |  | Khối lượng. |
| `data[].cp` | number |  | Thay đổi giá (giá - giá tham chiếu). |
| `data[].a` | string |  | Hành động (Buy up/Sell down). |
| `data[].ba` | number |  | Tích lũy KL mua lên. |
| `data[].sa` | number |  | Tích lũy KL bán xuống. |
| `data[].hl` | boolean |  | Highlight nếu giá trị > 200M. |
| `data[].t` | string |  | Thời gian nhận lệnh từ sở. |

200 OK

Sao chép
```json
{
  "page": 0,
  "size": 20,
  "headIndex": 3974,
  "numberOfItems": 10,
  "total": 3975,
  "ticker": "TCB",
  "d": "05/08",
  "data": [
    {
      "p": 33850.0,
      "v": 100,
      "cp": -650.0,
      "rcp": 0.0,
      "a": "",
      "ba": 6034800.0,
      "sa": 10320100.0,
      "hl": false,
      "pcp": 0.0,
      "t": "14:45:00"
    }
  ]
}
```
