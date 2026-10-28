# DNSE LightSpeed API — tài liệu chi tiết (bản sao nguyên văn)

Toàn bộ tài liệu chính thống tại <https://developers.dnse.com.vn/docs> được tải về
ngày **18/08/2026**. Cấu trúc thư mục bám đúng phân cấp URL của trang gốc, tương ứng
4 mục cấp 1 trên thanh điều hướng: **Hướng dẫn** (`guide/`), **SDKs**
(`sdk_document/`), **Đặc tả API** (`api_specifications/`), **Lịch sử cập nhật**
(`changelog/`).

**Tổng cộng: 54 trang.** Mỗi file có link nguồn ở đầu trang.

> **Cách lấy nội dung:** site dùng Docusaurus và có endpoint markdown thô
> (`<đường-dẫn>.md`, phía sau nút *Copy page*). Nội dung trong `details/` lấy từ
> endpoint đó nên **là markdown gốc của tài liệu** (giữ nguyên cả frontmatter,
> khối `<details>`, và các code sample đa ngôn ngữ). HTML render sẵn của các trang
> `Đặc tả API` **thiếu** phần request/response schema vì chúng được vẽ bằng
> JavaScript — nên nếu cần đối chiếu, luôn dùng bản `.md` này.

> Ba trang mục lục nhóm (`/docs/dnse/account`, `/docs/dnse/trading`,
> `/docs/dnse/market-data`) là *generated index* của Docusaurus, không có endpoint
> `.md`; chúng được dựng lại thành các file `00_*.md` từ chính danh sách trên trang gốc.

## 1. guide/ — Hướng dẫn (`/docs/guide`)

| File | Tiêu đề gốc | URL gốc |
|---|---|---|
| [`guide/broker.md`](guide/broker.md) | Dành cho Brokers DNSE | <https://developers.dnse.com.vn/docs/guide/broker> |
| [`guide/enum/market_data.md`](guide/enum/market_data.md) | Enums Dữ liệu thị trường | <https://developers.dnse.com.vn/docs/guide/enum/market_data> |
| [`guide/error_codes.md`](guide/error_codes.md) | Error Codes | <https://developers.dnse.com.vn/docs/guide/error_codes> |
| [`guide/faq.md`](guide/faq.md) | Câu hỏi thường gặp (FAQ) | <https://developers.dnse.com.vn/docs/guide/faq> |
| [`guide/intro/api_platform.md`](guide/intro/api_platform.md) | DNSE API Platform | <https://developers.dnse.com.vn/docs/guide/intro/api_platform> |
| [`guide/intro/authentication.md`](guide/intro/authentication.md) | Xác thực | <https://developers.dnse.com.vn/docs/guide/intro/authentication> |
| [`guide/intro/register_guide.md`](guide/intro/register_guide.md) | Đăng ký & Quản lý dịch vụ | <https://developers.dnse.com.vn/docs/guide/intro/register_guide> |
| [`guide/market-data/broker_connect.md`](guide/market-data/broker_connect.md) | Broker WebSocket | <https://developers.dnse.com.vn/docs/guide/market-data/broker_connect> |
| [`guide/market-data/connect.md`](guide/market-data/connect.md) | Market Data WebSocket | <https://developers.dnse.com.vn/docs/guide/market-data/connect> |
| [`guide/market-data/trading_connect.md`](guide/market-data/trading_connect.md) | Trading Data WebSocket | <https://developers.dnse.com.vn/docs/guide/market-data/trading_connect> |
| [`guide/ratelimits.md`](guide/ratelimits.md) | Rate Limits | <https://developers.dnse.com.vn/docs/guide/ratelimits> |
| [`guide/trading-api/dnse_margin.md`](guide/trading-api/dnse_margin.md) | Margin tại DNSE | <https://developers.dnse.com.vn/docs/guide/trading-api/dnse_margin> |
| [`guide/trading-api/trading_account.md`](guide/trading-api/trading_account.md) | Tài khoản giao dịch | <https://developers.dnse.com.vn/docs/guide/trading-api/trading_account> |
| [`guide/trading-api/trading_order.md`](guide/trading-api/trading_order.md) | Lệnh giao dịch | <https://developers.dnse.com.vn/docs/guide/trading-api/trading_order> |
| [`guide/versioning/api.md`](guide/versioning/api.md) | API Versioning | <https://developers.dnse.com.vn/docs/guide/versioning/api> |
| [`guide/versioning/sdk.md`](guide/versioning/sdk.md) | SDK Versioning | <https://developers.dnse.com.vn/docs/guide/versioning/sdk> |

## 2. sdk_document/ — SDKs (`/docs/sdk`)

| File | Tiêu đề gốc | URL gốc |
|---|---|---|
| [`sdk_document/build_websocket.md`](sdk_document/build_websocket.md) | Tự xây dựng WebSocket Client | <https://developers.dnse.com.vn/docs/sdk/build_websocket> |
| [`sdk_document/market_data.md`](sdk_document/market_data.md) | Market Data SDKs | <https://developers.dnse.com.vn/docs/sdk/market_data> |
| [`sdk_document/trading.md`](sdk_document/trading.md) | Trading SDKs | <https://developers.dnse.com.vn/docs/sdk/trading> |

## 3. api_specifications/ — Đặc tả API (`/docs/dnse`)

| File | Tiêu đề gốc | URL gốc |
|---|---|---|
| [`api_specifications/account/00_account.md`](api_specifications/account/00_account.md) | Thông tin tài khoản | <https://developers.dnse.com.vn/docs/dnse/account> |
| [`api_specifications/account/get-account-balances.md`](api_specifications/account/get-account-balances.md) | Thông tin tiền | <https://developers.dnse.com.vn/docs/dnse/get-account-balances> |
| [`api_specifications/account/get-accounts.md`](api_specifications/account/get-accounts.md) | Tài khoản giao dịch | <https://developers.dnse.com.vn/docs/dnse/get-accounts> |
| [`api_specifications/account/get-corporate-action-history.md`](api_specifications/account/get-corporate-action-history.md) | Lịch sử sự kiện quyền | <https://developers.dnse.com.vn/docs/dnse/get-corporate-action-history> |
| [`api_specifications/account/get-executions.md`](api_specifications/account/get-executions.md) | Chi tiết trạng thái lệnh | <https://developers.dnse.com.vn/docs/dnse/get-executions> |
| [`api_specifications/account/get-loan-packages.md`](api_specifications/account/get-loan-packages.md) | Danh sách gói vay | <https://developers.dnse.com.vn/docs/dnse/get-loan-packages> |
| [`api_specifications/account/get-orders-history.md`](api_specifications/account/get-orders-history.md) | Lịch sử lệnh | <https://developers.dnse.com.vn/docs/dnse/get-orders-history> |
| [`api_specifications/account/get-orders.md`](api_specifications/account/get-orders.md) | Sổ lệnh | <https://developers.dnse.com.vn/docs/dnse/get-orders> |
| [`api_specifications/account/get-pnl-configs-position.md`](api_specifications/account/get-pnl-configs-position.md) | Cấu hình chốt lời, cắt lỗ của vị thế | <https://developers.dnse.com.vn/docs/dnse/get-pnl-configs-position> |
| [`api_specifications/account/get-position-by-id.md`](api_specifications/account/get-position-by-id.md) | Chi tiết vị thế theo ID | <https://developers.dnse.com.vn/docs/dnse/get-position-by-id> |
| [`api_specifications/account/get-positions.md`](api_specifications/account/get-positions.md) | Vị thế nắm giữ | <https://developers.dnse.com.vn/docs/dnse/get-positions> |
| [`api_specifications/account/get-ppse.md`](api_specifications/account/get-ppse.md) | Sức mua, sức bán | <https://developers.dnse.com.vn/docs/dnse/get-ppse> |
| [`api_specifications/market_data/00_market_data.md`](api_specifications/market_data/00_market_data.md) | Dữ liệu thị trường | <https://developers.dnse.com.vn/docs/dnse/market-data> |
| [`api_specifications/market_data/get-expected-price.md`](api_specifications/market_data/get-expected-price.md) | Giá dự khớp | <https://developers.dnse.com.vn/docs/dnse/get-expected-price> |
| [`api_specifications/market_data/get-foreign-trading.md`](api_specifications/market_data/get-foreign-trading.md) | Dữ liệu NĐT nước ngoài | <https://developers.dnse.com.vn/docs/dnse/get-foreign-trading> |
| [`api_specifications/market_data/get-history-trades.md`](api_specifications/market_data/get-history-trades.md) | Lịch sử khớp lệnh | <https://developers.dnse.com.vn/docs/dnse/get-history-trades> |
| [`api_specifications/market_data/get-instruments.md`](api_specifications/market_data/get-instruments.md) | Chi tiết mã chứng khoán | <https://developers.dnse.com.vn/docs/dnse/get-instruments> |
| [`api_specifications/market_data/get-latest-quotes.md`](api_specifications/market_data/get-latest-quotes.md) | Dữ liệu bid/ask gần nhất | <https://developers.dnse.com.vn/docs/dnse/get-latest-quotes> |
| [`api_specifications/market_data/get-latest-trades.md`](api_specifications/market_data/get-latest-trades.md) | Dữ liệu khớp gần nhất | <https://developers.dnse.com.vn/docs/dnse/get-latest-trades> |
| [`api_specifications/market_data/get-market-working-dates.md`](api_specifications/market_data/get-market-working-dates.md) | Ngày làm việc | <https://developers.dnse.com.vn/docs/dnse/get-market-working-dates> |
| [`api_specifications/market_data/get-ohlc-history.md`](api_specifications/market_data/get-ohlc-history.md) | Lịch sử OHLC | <https://developers.dnse.com.vn/docs/dnse/get-ohlc-history> |
| [`api_specifications/market_data/get-price-symbol-close.md`](api_specifications/market_data/get-price-symbol-close.md) | Giá đóng cửa | <https://developers.dnse.com.vn/docs/dnse/get-price-symbol-close> |
| [`api_specifications/market_data/get-quotes.md`](api_specifications/market_data/get-quotes.md) | Lịch sử bid/ask | <https://developers.dnse.com.vn/docs/dnse/get-quotes> |
| [`api_specifications/market_data/get-session.md`](api_specifications/market_data/get-session.md) | Phiên giao dịch | <https://developers.dnse.com.vn/docs/dnse/get-session> |
| [`api_specifications/market_data/get-symbol-secdef.md`](api_specifications/market_data/get-symbol-secdef.md) | Thông tin giao dịch chứng khoán | <https://developers.dnse.com.vn/docs/dnse/get-symbol-secdef> |
| [`api_specifications/trading/00_trading.md`](api_specifications/trading/00_trading.md) | Giao dịch | <https://developers.dnse.com.vn/docs/dnse/trading> |
| [`api_specifications/trading/2-fa-verification.md`](api_specifications/trading/2-fa-verification.md) | Xác thực OTP | <https://developers.dnse.com.vn/docs/dnse/2-fa-verification> |
| [`api_specifications/trading/cancel-order.md`](api_specifications/trading/cancel-order.md) | Hủy lệnh | <https://developers.dnse.com.vn/docs/dnse/cancel-order> |
| [`api_specifications/trading/close-position.md`](api_specifications/trading/close-position.md) | Đóng vị thế | <https://developers.dnse.com.vn/docs/dnse/close-position> |
| [`api_specifications/trading/get-order-detail.md`](api_specifications/trading/get-order-detail.md) | Chi tiết lệnh theo ID | <https://developers.dnse.com.vn/docs/dnse/get-order-detail> |
| [`api_specifications/trading/place-order.md`](api_specifications/trading/place-order.md) | Đặt lệnh | <https://developers.dnse.com.vn/docs/dnse/place-order> |
| [`api_specifications/trading/post-pnl-configs-position.md`](api_specifications/trading/post-pnl-configs-position.md) | Cài đặt chốt lời, cắt lỗ cho vị thế | <https://developers.dnse.com.vn/docs/dnse/post-pnl-configs-position> |
| [`api_specifications/trading/replace-order.md`](api_specifications/trading/replace-order.md) | Sửa lệnh | <https://developers.dnse.com.vn/docs/dnse/replace-order> |
| [`api_specifications/trading/send-email-otp.md`](api_specifications/trading/send-email-otp.md) | Gửi Email OTP | <https://developers.dnse.com.vn/docs/dnse/send-email-otp> |

## 4. changelog/ — Lịch sử cập nhật (`/docs/changelog`)

| File | Tiêu đề gốc | URL gốc |
|---|---|---|
| [`changelog/changelog.md`](changelog/changelog.md) | Changelog | <https://developers.dnse.com.vn/docs/changelog> |

## Trang quan trọng nhất cho bài toán WebSocket

| File | Vì sao |
|---|---|
| [`sdk_document/build_websocket.md`](sdk_document/build_websocket.md) | Đặc tả **toàn bộ protocol** WebSocket: welcome → auth (HMAC) → subscribe → data → ping/pong → reconnect, kèm close code |
| [`guide/market-data/connect.md`](guide/market-data/connect.md) | **Tất cả channel market data** và payload mẫu từng loại |
| [`guide/intro/authentication.md`](guide/intro/authentication.md) | Chữ ký REST, Trading Token (2FA), phương thức OTP |
| [`guide/enum/market_data.md`](guide/enum/market_data.md) | Toàn bộ enum: boardId, resolution, marketIndex, tradingSessionId, eventId... |
| [`guide/market-data/trading_connect.md`](guide/market-data/trading_connect.md) | Channel `order.*` / `position.*` cho tài khoản của mình |
| [`guide/market-data/broker_connect.md`](guide/market-data/broker_connect.md) | Channel broker + giới hạn 1 `investor_id`/kết nối |
| [`guide/faq.md`](guide/faq.md) | 51 câu hỏi, mục WebSocket (#38–45) làm rõ nhiều chi tiết |
