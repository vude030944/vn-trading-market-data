<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/getting-started
Tieu de goc: Tổng quan hệ thống
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/getting-started>

# Tổng quan hệ thống

## FastConnect API là gì?

FastConnect API là nền tảng kết nối giao dịch của SSI, cho phép khách hàng và đối tác truy cập trực tiếp vào hệ thống giao dịch thông qua API chuẩn hóa. Giải pháp hỗ trợ xây dựng và vận hành hệ thống đầu tư - giao dịch tự động với độ trễ thấp và mức độ bảo mật cao.

## Các nhóm API

FastConnect API cung cấp **4 nhóm tính năng chính** :

### 1\. Authentication (Xác thực)

Xác thực bằng API Key và API Secret để lấy Bearer token (JWT). Token kiểm soát quyền truy cập:

  * **Token Market Data** : Gọi `/api/v3/auth/token` với `apiKey` \+ `apiSecret`
  * **Token Trading** : Thêm trường `otp` để token có quyền giao dịch
  * **Refresh Token** : Làm mới token qua `/api/v3/auth/refresh`
  * **Request OTP** : Lấy mã OTP qua SMS/Email với `/api/v3/auth/requestOtp`

### 2\. Market Data (Dữ liệu thị trường)

Truy xuất dữ liệu thị trường chứng khoán Việt Nam qua REST API:

  * **Danh sách chứng khoán** : Tra cứu mã chứng khoán theo sàn (HOSE, HNX, UPCOM) hoặc chỉ số
  * **Thông tin giao dịch** : Dữ liệu tổng hợp giao dịch theo ngày (giá, khối lượng, giá trị)
  * **Dữ liệu nến OHLCV** : Dữ liệu nến theo nhiều khung thời gian (1m, 5m, 15m, 30m, 1h, 1d)
  * **Chỉ số thị trường** : Danh sách và thông tin tổng hợp các chỉ số (VNINDEX, VN30, HNXIndex...)
  * **Tải file dữ liệu** : Tải file CSV dữ liệu thị trường theo ngày

### 3\. Trading (Giao dịch)

Đặt lệnh và quản lý tài khoản giao dịch:

  * **Đặt lệnh** : Mua/bán với các loại lệnh LO, MP, ATO, ATC
  * **Sửa/Hủy lệnh** : Thay đổi giá, khối lượng hoặc hủy lệnh đang chờ
  * **Sổ lệnh** : Tra cứu lịch sử lệnh theo tài khoản, trạng thái, thời gian
  * **Vị thế** : Danh mục cổ phiếu và phái sinh đang nắm giữ
  * **Số dư tài khoản** : Tiền mặt, sức mua, dư nợ, tiền chờ thanh toán (T+0/T+1/T+2)
  * **PP/MMR** : Thông tin sức mua và tỷ lệ ký quỹ
  * **KL mua/bán tối đa** : Kiểm tra khối lượng tối đa có thể đặt lệnh

### 4\. WebSocket Streaming (Dữ liệu thời gian thực)

Nhận dữ liệu realtime qua kết nối WebSocket tại `wss://stream.ssi.com.vn`:

  * **Market Data** : Subscribe theo mã chứng khoán (kênh `F:STOCK`, `F:INDEX`, `F:DERIVATIVE`)
  * **Trading Data** : Trạng thái lệnh, khớp lệnh, cập nhật tài khoản (kênh `T:ORDER`, `T:ACCOUNT`, `T:POSITION`)
  * **Heartbeat** : Server gửi ping mỗi 30 giây, client phải trả lời pong để giữ kết nối

* * *

## Ai nên sử dụng FastConnect API?

user

### Trader cá nhân

Nhà đầu tư muốn tự động hóa giao dịch, theo dõi danh mục, hoặc phân tích dữ liệu theo cách riêng

building

### Công ty Fintech

Startup/công ty muốn xây dựng ứng dụng tài chính, robo-advisor, hoặc nền tảng đầu tư số

chart-line

### Quants & Algo Traders

Nhà phân tích định lượng cần dữ liệu để backtest, nghiên cứu, và triển khai chiến lược tự động

code

### Nhà phát triển ứng dụng

Developer muốn tích hợp tính năng chứng khoán vào app/website hiện có

* * *

## Công nghệ hỗ trợ

  * **Protocols** : REST API (JSON), WebSocket
  * **Authentication** : API Key + Secret, Bearer JWT
  * **Data Format** : JSON, CSV (qua endpoint tải file dữ liệu)
  * **SDKs** : [Node.js](/docs/sdk/nodejs/overview), [Python](/docs/sdk/python/overview), [Java](/docs/sdk/java/overview), [C#](/docs/sdk/csharp/overview), [Go](/docs/sdk/go/overview)
  * **Rate Limits** : Kiểm soát qua response headers `X-RATELIMIT-LIMIT`, `X-RATELIMIT-REMAINING`, `X-RATELIMIT-RESET`

* * *

## Bước tiếp theo

Tiếp tục với [Quy trình đăng ký](/docs/getting-started/registration) để tạo tài khoản API.
