<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/getting-started/terms-and-environments
Tieu de goc: Điều kiện sử dụng & Môi trường
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/getting-started/terms-and-environments>

# Điều kiện sử dụng & Môi trường

Điều kiện sử dụng, môi trường triển khai, giờ giao dịch và giới hạn

## Điều kiện sử dụng

### Yêu cầu

  * Có tài khoản giao dịch tại SSI
  * Đăng ký FastConnect qua Developer Portal và được phê duyệt
  * Đồng ý điều khoản sử dụng dịch vụ

### Trách nhiệm của người dùng

  * Bảo mật API Key, API Secret và access token. Không chia sẻ, commit vào source code, hoặc để lộ credentials
  * Tuân thủ rate limits của hệ thống
  * Tuân thủ quy định pháp luật về chứng khoán Việt Nam
  * Không lạm dụng API (spam, tấn công, khai thác lỗ hổng)

### Tài khoản bị khóa khi nào?

Tài khoản API có thể bị tạm khóa trong các trường hợp:

  1. Vi phạm điều khoản sử dụng
  2. Phát hiện hoạt động bất thường (security alert)
  3. Yêu cầu từ cơ quan quản lý (UBCKNN)
  4. Khách hàng yêu cầu khóa

Liên hệ bộ phận hỗ trợ để khôi phục tài khoản.

Lệnh giao dịch qua API là lệnh thật, ảnh hưởng trực tiếp đến tài khoản chứng khoán. Kiểm tra kỹ logic trước khi triển khai lên production.

* * *

## Môi trường

### Production

Môi trường chính cho dữ liệu thực và giao dịch thật.

| Thành phần | URL |
|---|---|
| REST API | `https://api.ssi.com.vn` |
| WebSocket | `wss://stream.ssi.com.vn` |
| Developer Portal | `https://developers.ssi.com.vn` |

### UAT (User Acceptance Testing)

Môi trường kiểm thử dành cho việc phát triển và tích hợp. Dữ liệu giả lập, giao dịch không ảnh hưởng tài khoản thật.

Thông tin môi trường UAT sẽ được thông báo khi sẵn sàng cho quý khách hàng trải nghiệm.

* * *

## Giờ giao dịch

### Cổ phiếu (HOSE/HNX)

| Phiên | Giờ | Loại lệnh |
|---|---|---|
| **ATO** | 09:00 - 09:15 | ATO, LO |
| **Liên tục sáng** | 09:15 - 11:30 | LO, MP |
| **Nghỉ trưa** | 11:30 - 13:00 | Không giao dịch |
| **Liên tục chiều** | 13:00 - 14:30 | LO, MP |
| **ATC** | 14:30 - 14:45 | ATC, LO |

### Phái sinh

| Phiên | Giờ |
|---|---|
| **ATO** | 08:45 - 09:00 |
| **Liên tục sáng** | 09:00 - 11:30 |
| **Nghỉ trưa** | 11:30 - 13:00 |
| **Liên tục chiều** | 13:00 - 14:30 |
| **ATC** | 14:30 - 14:45 |

API Market Data và WebSocket hoạt động 24/7. Ngoài giờ giao dịch, dữ liệu giá không cập nhật nhưng vẫn có thể truy vấn dữ liệu lịch sử.

* * *

## Rate Limits

Hệ thống áp dụng rate limit cho từng API Key. Thông tin rate limit được trả về trong response headers:

| Header | Mô tả |
|---|---|
| `X-RATELIMIT-LIMIT` | Số request tối đa trong chu kỳ |
| `X-RATELIMIT-REMAINING` | Số request còn lại trong chu kỳ hiện tại |
| `X-RATELIMIT-RESET` | Thời điểm reset giới hạn |

Khi vượt rate limit, API trả về HTTP `429 Too Many Requests`. Đợi đến thời điểm `X-RATELIMIT-RESET` trước khi gọi tiếp.

* * *

## Giới hạn dữ liệu

| Loại dữ liệu | Phạm vi |
|---|---|
| **OHLCV daily** | Từ ngày mã chứng khoán bắt đầu giao dịch |
| **OHLCV intraday** (1m, 5m, 15m, 30m, 1h) | 1 năm gần nhất |
| **Tải file CSV** | Đường dẫn có hiệu lực trong 30 phút |

* * *

## Bước tiếp theo

Tiếp tục với [Cách lấy API Key](/docs/getting-started/api-keys) để tạo credentials đầu tiên.
