<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/getting-started/api-keys
Tieu de goc: Cách lấy API Key / Access Token
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/getting-started/api-keys>

# Cách lấy API Key / Access Token

Tạo, quản lý, và bảo mật API credentials

## Tạo API Key

### Bước 1: Đăng nhập Developer Portal

Truy cập <https://developers.ssi.com.vn> và đăng nhập bằng tài khoản SSI.

### Bước 2: Tạo API Key mới

Vào **Bảng điều khiển** -> **Quản lý API Key** -> **Tạo Key mới**

Đặt tên cho API Key (ví dụ: "Trading Bot Production")

Click **Tạo** -> **Lưu ngay** API Key và API Secret

**Quan trọng:** API Secret chỉ hiển thị **MỘT LẦN**. Nếu mất, cần vào chi tiết API Key để xem lại.

* * *

## Xác thực với API Key

FastConnect sử dụng cơ chế Bearer token. Flow xác thực:

### 1\. Lấy Access Token

Gọi `/api/v3/auth/token` với API Key và API Secret:
```bash
curl -X POST "https://api.ssi.com.vn/api/v3/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "apiKey": "your_api_key",
    "apiSecret": "your_api_secret"
  }'
```

Response:
```json
{
  "tokenType": "Bearer",
  "accessToken": "eyJhbGciOiJIUzI1NiIs...",
  "refreshToken": "dGhpcyBpcyBhIHJlZnJl...",
  "expiresAt": 1779806203,
  "refreshExpiresAt": 1779892603
}
```

### 2\. Sử dụng Access Token

Truyền token trong header `Authorization` cho tất cả API calls:
```bash
curl -X GET "https://api.ssi.com.vn/api/v3/data/securitiesByBoard?board=HOSE" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

### 3\. Làm mới Token

Khi access token hết hạn, dùng refresh token:
```bash
curl -X POST "https://api.ssi.com.vn/api/v3/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refreshToken": "dGhpcyBpcyBhIHJlZnJl..."
  }'
```

### 4\. Token có quyền giao dịch

Để đặt/sửa/hủy lệnh, access token cần được cấp kèm `otp` hoặc `transactionId` khi gọi `/api/v3/auth/token`. Cách lấy giá trị này phụ thuộc vào loại 2FA của tài khoản, gồm 3 tình huống:

#### Tình huống 1: OTP qua SMS/Email

Áp dụng cho tài khoản dùng 2FA loại SMS hoặc Email. OTP được gửi về số điện thoại/email đã đăng ký sau khi gọi `requestOtp`.
```bash
# Bước 1: Yêu cầu gửi OTP qua SMS/Email
curl -X POST "https://api.ssi.com.vn/api/v3/auth/requestOtp" \
  -H "Content-Type: application/json" \
  -d '{
    "apiKey": "your_api_key",
    "apiSecret": "your_api_secret"
  }'
# Response: { "message": "Thành công" }

# Bước 2: Nhập OTP nhận được qua SMS/Email vào tham số otp
curl -X POST "https://api.ssi.com.vn/api/v3/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "apiKey": "your_api_key",
    "apiSecret": "your_api_secret",
    "otp": "123456"
  }'
```

#### Tình huống 2: Lấy OTP trực tiếp từ app iBoard (SmartOTP)

Áp dụng cho tài khoản dùng 2FA loại SmartOTP. Không cần gọi `requestOtp` — mở app iBoard, vào mục SmartOTP để lấy mã đang hiển thị rồi truyền trực tiếp vào tham số `otp`.
```bash
curl -X POST "https://api.ssi.com.vn/api/v3/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "apiKey": "your_api_key",
    "apiSecret": "your_api_secret",
    "otp": "482913"
  }'
```

#### Tình huống 3: Lấy OTP theo luồng Mobile Approval

Cũng áp dụng cho tài khoản dùng 2FA loại SmartOTP, nhưng khách hàng phê duyệt trực tiếp trên app thay vì nhập mã.

**Lưu ý 1:** `transactionId` có thời gian hiệu lực 30 giây. Khách hàng bắt buộc phải phê duyệt trên app iBoard trong vòng 30 giây để hoàn thành quá trình 2FA này.

**Lưu ý 2:** Để tự động hóa ứng dụng mà không phải nhập thủ công OTP mỗi ngày, bạn nên triển khai theo luồng Mobile Approval này.
```bash
# Bước 1: Gửi yêu cầu phê duyệt tới app iBoard
curl -X POST "https://api.ssi.com.vn/api/v3/auth/requestOtp" \
  -H "Content-Type: application/json" \
  -d '{
    "apiKey": "your_api_key",
    "apiSecret": "your_api_secret"
  }'
# Response:
# {
#   "message": "Please approve the login request via the iBoard mobile app.",
#   "transactionId": "f306c510-0647-417b-9210-bb5b7e155e77"
# }

# Bước 2: Khách hàng mở app iBoard và bấm Phê duyệt yêu cầu

# Bước 3: Gọi token kèm transactionId đã lấy được ở Bước 1 (không cần truyền otp)
curl -X POST "https://api.ssi.com.vn/api/v3/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "apiKey": "your_api_key",
    "apiSecret": "your_api_secret",
    "transactionId": "f306c510-0647-417b-9210-bb5b7e155e77"
  }'
```

Bạn có thể tham khảo ví dụ mẫu về việc triển khai ứng dụng theo hướng SmartOTP với luồng Mobile Approval tại mục [Thực hành](/docs/tutorials).

* * *

## Quản lý API Key

### Xem chi tiết Key

Đăng nhập Developer Portal -> **Bảng điều khiển** -> **Quản lý API Key** -> chọn key cần xem -> **Chi tiết**.

### Rotate (xoay vòng) Key

Tạo API Key mới trên Developer Portal

Cập nhật key mới vào ứng dụng

Test kỹ với key mới

Xóa key cũ

### Xóa Key

Xóa ngay nếu:

  * Key bị lộ ra ngoài
  * Không còn sử dụng
  * Cần thay thế bằng key mới

* * *

## Best Practices bảo mật

### NÊN

  * Lưu key trong **environment variables** hoặc **secret manager**
  * Sử dụng HTTPS cho mọi request
  * Rotate key định kỳ
  * Tạo key riêng cho từng ứng dụng
  * Monitor API usage để phát hiện bất thường

### KHÔNG NÊN

  * Commit key vào Git/GitHub
  * Hardcode key trong source code
  * Share key qua email/chat
  * Dùng key Production cho testing
  * Dùng chung key giữa nhiều ứng dụng

* * *

## Bước tiếp theo

Đã có API Key? Tiếp tục với [API Call đầu tiên](/docs/getting-started/first-api-call)!
