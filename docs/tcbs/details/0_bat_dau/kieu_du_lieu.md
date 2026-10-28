<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/data-types
Tieu de goc: Kiểu dữ liệu
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/data-types>

# Kiểu dữ liệu

Bảng dưới đây mô tả các kiểu dữ liệu được sử dụng xuyên suốt tài liệu API. Tất cả các endpoint đều tuân theo quy ước này.

## Bảng kiểu dữ liệu

| Kiểu | Mô tả | Ví dụ |
|---|---|---|
| `string` | Chuỗi ký tự UTF-8. | "TCB", "Bearer abc..." |
| `int64` | Số nguyên 64-bit. Dùng cho ID, số tiền (VND), giá, khối lượng, số trang, số bản ghi. | 25500, 3517238514 |
| `number` | Số thực dấu phẩy động (IEEE 754). Dùng cho tỷ lệ, phần trăm, lãi suất. | 12.5, 0.82 |
| `boolean` | Giá trị true hoặc false. | true, false |
| `enum` | Tập giá trị cố định (liệt kê trong mô tả). | "NB", "ACTIVE" |
| `date` | Chuỗi ngày theo định dạng yyyy-MM-dd. | "2024-01-15" |
| `datetime` | Chuỗi thời gian ISO 8601 kèm timezone. | "2024-01-15T10:30:00+07:00" |
| `array` | Danh sách (mảng JSON). Kiểu phần tử được mô tả trong cột Description. | [1, 2, 3] |
| `object` | Đối tượng JSON lồng nhau. Các field con được mô tả riêng. | {"key": "value"} |

💡 Tất cả giá tiền (VND) đều là số nguyên (int64), không có phần thập phân. Ví dụ: giá 25,500 VND được biểu diễn là 25500.

## Quy ước đặc biệt

Một số quy ước bổ sung áp dụng cho toàn bộ API:

  * **Null fields** : Response chỉ chứa các field có giá trị. Field null sẽ không xuất hiện trong JSON trả về.
  * **Timezone** : Mặc định Asia/Ho_Chi_Minh (+07:00) cho tất cả datetime.
  * **Pagination** : Các API có phân trang dùng query param `page` (0-indexed) và `size`.
  * **Enum values** : Luôn là string, case-sensitive. Giá trị cụ thể được liệt kê tại mỗi field.
