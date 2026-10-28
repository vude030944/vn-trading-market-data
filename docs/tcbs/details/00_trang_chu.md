<!--
Nguon goc (source): https://developers.tcbs.com.vn/
Tieu de goc: API giao dịch chứng khoán realtime cho developer
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/>

# API giao dịch chứng khoán realtime cho developer

[/ OpenAPI](/)

[Tài liệu](/docs/v1.0.0/introduction/)

vien

# API giao dịch chứng khoán realtime cho developer

Đặt lệnh, nhận giá realtime và quản lý danh mục qua REST API và WebSocket — tích hợp vào ứng dụng của bạn trong vài giờ.

[Xem tài liệu](/docs/v1.0.0/introduction/)[Đăng ký iFlash OpenAPI](https://tcinvest.tcbs.com.vn/iflash-open-api)

99.9999%

Cam kết uptime

<50ms

Độ trễ trung bình

REST + WSS

Giao thức hỗ trợ

## Đặt lệnh, nhận giá, quản lý danh mục — tất cả qua API

Các building block cốt lõi để xây dựng ứng dụng giao dịch tự động.

### Giao dịch

Đặt/sửa/huỷ lệnh cổ phiếu & phái sinh qua REST API.

### Dữ liệu thị trường

Giá realtime, thông tin mã CK, bảng giá qua WebSocket.

### Quản lý tiền

Chuyển tiền, nộp/rút ký quỹ, kiểm tra số dư tài khoản.

### WebSocket Streaming

Nhận dữ liệu realtime: bảng giá, khớp lệnh, lịch sử.

## Bắt đầu trong 3 bước

1

### Lấy API Key

Đăng ký và nhận API Key từ TCBS.

2

### Xác thực

Trao đổi API Key lấy JWT token.

3

### Gọi API

Đặt lệnh, tra cứu danh mục, nhận giá realtime.

[Đọc tài liệu đầy đủ](/docs/v1.0.0/introduction/)

## Khách hàng nói gì về iFlash Open API

“

WebSocket streaming của iFlash cực kỳ ổn định — chúng tôi chạy bot giao dịch 24/5 mà chưa bao giờ bị mất kết nối ngoài giờ bảo trì.

CL

Khuynh Thành Chi Luyến

Lead Engineer, FinTech Startup

“

Độ trễ dưới 50ms cho dữ liệu thị trường realtime — đủ nhanh cho chiến lược giao dịch thuật toán của tôi. API docs rất rõ ràng.

VL

Lê Văn Lưu

Quant Developer

“

Với sự hỗ trợ của AI, tích hợp REST API chỉ mất 2 giờ. Xác thực JWT đơn giản, response chuẩn — team dev của tôi rất hài lòng.

TT

Trịnh Thế Thành

CTO, Trading Company

## Câu hỏi thường gặp

Làm thế nào để lấy API Key?

API Key được tạo trên nền tảng TCInvest. Sau đó bạn trao đổi API Key lấy JWT token qua endpoint /gaia/v1/oauth2/openapi/token kèm OTP xác thực.

Xác thực hoạt động như thế nào?

Sử dụng API Key + OTP để nhận JWT Bearer token. Token có hiệu lực tối đa 8 giờ. Đính kèm token này vào header Authorization cho mọi request.

Hỗ trợ thị trường nào?

Hỗ trợ cổ phiếu cơ sở (HOSE, HNX, UPCOM) và phái sinh thị trường Việt Nam, qua cả REST API và WebSocket streaming.

Có giới hạn tốc độ (rate limit) không?

Khuyến nghị 1 kết nối WebSocket trên mỗi token. Với REST API, không có rate limit cứng nhưng nên giữ dưới 10 request/giây. Liên hệ hỗ trợ nếu cần throughput cao hơn.

Làm thế nào để được hỗ trợ?

Email cskh@tcbs.com.vn, Zalo hoặc Messenger. Đội ngũ hỗ trợ phản hồi trong giờ làm việc.

/ OpenAPI

Nền tảng API kết nối giao dịch chứng khoán, dữ liệu thị trường thời gian thực và quản lý danh mục của TCBS.

### Sản phẩm

  * [Tài liệu](/docs/v1.0.0/introduction/)
  * [Bắt đầu](/docs/v1.0.0/workflow/)
  * [Xác thực](/docs/v1.0.0/auth/token/)
  * [WebSocket API](/docs/v1.0.0/derivative/ws-price-board/)

### Tài nguyên

  * [Câu hỏi thường gặp](/#faq)
  * [Hướng dẫn WebSocket](/docs/v1.0.0/stock/ws-price-board/)
  * [Giới thiệu](/docs/v1.0.0/introduction/)
  * [Đăng ký iFlash OpenAPI](https://tcinvest.tcbs.com.vn/iflash-open-api)
  * [Changelog](/changelog)

### Liên hệ

  * [cskh@tcbs.com.vn](mailto:cskh@tcbs.com.vn)
  * [Zalo](https://zalo.me/4237937732491753255)
  * [Messenger](https://m.me/TechcomSecurities)
  * [tcbs.com.vn](https://www.tcbs.com.vn)

© 2026 TCBS — Công ty Cổ phần Chứng khoán Kỹ Thương (Techcom Securities)
