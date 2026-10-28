<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference
Tieu de goc: SSI API Overview
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference>

# SSI API Overview

Tổng quan hệ sinh thái API FastConnect gồm Authentication, Trading, Market Data và WebSocket.

## Giới thiệu

FastConnect API được thiết kế để hỗ trợ đầy đủ vòng đời tích hợp giao dịch điện tử, từ xác thực truy cập, xử lý nghiệp vụ giao dịch, truy vấn dữ liệu thị trường đến nhận dữ liệu thời gian thực.

Bộ tài liệu trong mục **API Reference** được tổ chức theo 6 nhóm chức năng chính:

  1. **Authentication** — Xác thực và quản lý phiên truy cập.
  2. **Trading** — Đặt/sửa/hủy lệnh, truy vấn tài khoản.
  3. **Market Data** — Dữ liệu thị trường qua REST API.
  4. **WebSocket** — Dữ liệu realtime qua WebSocket.
  5. **Lệnh điều kiện (FCO)** — Đặt/hủy lệnh điều kiện, truy vấn sổ lệnh FCO.
  6. **Phụ lục tham khảo** — Luồng trạng thái lệnh, tham khảo FCO, tra cứu mã lỗi.

## Mục tiêu tích hợp

Nền tảng API hướng đến các mục tiêu sau:

  * Xác thực và quản lý phiên truy cập an toàn.
  * Đặt/sửa/hủy lệnh và truy vấn trạng thái giao dịch.
  * Đặt lệnh điều kiện (FCO) với nhiều chiến lược khác nhau.
  * Truy vấn dữ liệu thị trường theo REST API.
  * Nhận dữ liệu realtime qua WebSocket.

Trang này cung cấp góc nhìn tổng thể trước khi đi vào tài liệu endpoint chi tiết.

## Luồng tích hợp đề xuất

Luồng triển khai phổ biến:

  1. Gọi nhóm **Authentication** để lấy token truy cập.
  2. Dùng token để gọi các API **Trading** , **Lệnh điều kiện (FCO)** và **Market Data** qua REST.
  3. Dùng token để kết nối **WebSocket** và subscribe các topic realtime.
  4. Tham khảo **Phụ lục** để tra cứu mã lỗi, luồng trạng thái lệnh và tham số FCO.

## 1) Authentication

Nhóm API này phụ trách cấp mới và làm mới token, là tiền đề cho mọi phiên làm việc với hệ thống.

  * `auth-token`: cấp `accessToken` và `refreshToken`.
  * `auth-refresh`: làm mới cặp token trước khi hết hạn.
  * `auth-requestOtp`: yêu cầu OTP phục vụ các nghiệp vụ cần xác minh.

Xem chi tiết tại:

  * [auth-token](./api-reference/auth-token)
  * [auth-refresh](./api-reference/auth-refresh)
  * [auth-requestOtp](./api-reference/auth-requestOtp)

## 2) Trading

Nhóm Trading phục vụ các nghiệp vụ giao dịch cốt lõi và truy vấn dữ liệu tài khoản:

  * Đặt/sửa/hủy lệnh.
  * Truy vấn thông tin tài khoản, vị thế, số dư, sức mua.
  * Truy vấn sổ lệnh và dữ liệu liên quan tới quản trị rủi ro.

Một số API quan trọng:

  * [trade-order-place](./api-reference/trade-order-place)
  * [trade-order-modify](./api-reference/trade-order-modify)
  * [trade-order-cancel](./api-reference/trade-order-cancel)
  * [trade-orderBook](./api-reference/trade-orderBook)
  * [trade-position](./api-reference/trade-position)
  * [trade-accountBalance](./api-reference/trade-accountBalance)
  * [trade-maxbuysell](./api-reference/trade-maxbuysell)
  * [trade-ppmmrAccount](./api-reference/trade-ppmmrAccount)
  * [account-info](./api-reference/account-info)

Mỗi lệnh trải qua nhiều trạng thái trong vòng đời đặt/sửa/hủy/khớp lệnh (PD → RS → SD → QU → PF/FF, hoặc WC → CL, RJ, EX...). Khi tích hợp, consumer cần hiểu ý nghĩa từng trạng thái và luồng chuyển đổi giữa chúng để xử lý đúng phản hồi của các API trên cũng như các sự kiện streaming (`orderEvent`, `orderMatchEvent`).

> 📄 **Đọc thêm:** [Luồng trạng thái của lệnh](./api-reference/appendix/order-status-flow) — sơ đồ và mô tả chi tiết 16 trạng thái lệnh cùng các luồng đặt/sửa/hủy/khớp.

## 3) Market Data

Nhóm Market Data cung cấp dữ liệu thị trường qua REST API để phục vụ phân tích, hiển thị và xử lý nghiệp vụ:

  * Danh sách và tổng hợp chỉ số.
  * Danh sách và tổng hợp chứng khoán.
  * Dữ liệu OHLC và tệp dữ liệu thị trường.
  * Tải file dữ liệu thị trường.

Một số API quan trọng:

  * [data-securitiesByBoard](./api-reference/data-securitiesByBoard)
  * [data-securitiesSummary](./api-reference/data-securitiesSummary)
  * [data-indexList](./api-reference/data-indexList)
  * [data-indexSummary](./api-reference/data-indexSummary)
  * [data-ohlc](./api-reference/data-ohlc)

## 4) WebSocket

Nhóm WebSocket cung cấp luồng dữ liệu realtime với 2 kênh chính:

  * **Trading stream** : sự kiện liên quan lệnh, khớp lệnh, biến động tài khoản.
  * **Market stream** : sự kiện trade/quote/room/market theo topic.

Tài liệu WebSocket bao gồm:

  * [Kết nối WebSocket](./api-reference/connectWebSocket)
  * [Heartbeat và Subscription](./api-reference/getHeartbeatStructure)
  * [Sub/Unsub Trading Data](./api-reference/subscribeUnsubscribeTradingData)
  * [Sub/Unsub Market Data](./api-reference/subscribeUnsubscribeMarketData)

## 5) Lệnh điều kiện (FCO)

Nhóm API Lệnh điều kiện (FastConnect Conditional Order) cho phép đặt các lệnh tự động kích hoạt khi thỏa điều kiện thị trường. Hệ thống hỗ trợ 7 loại lệnh điều kiện:

  * **Trailing Stop (TS)** — lệnh dừng trượt theo giá thị trường.
  * **Take Profit (PRO)** — chốt lời khi đạt mức giá mục tiêu.
  * **Stop Loss (ST)** — cắt lỗ khi giá chạm ngưỡng.
  * **Trailing Take Profit (TPRO)** — chốt lời với mức trượt.
  * **Bull/Bear (BB)** — kết hợp chốt lời và cắt lỗ.
  * **One Cancels Other (OCO)** — hai lệnh loại trừ nhau.
  * **Market Alert (MA)** — cảnh báo khi điều kiện thị trường thỏa.

Các API chính:

  * [fco-order-place](./api-reference/fco-order-place) — Đặt lệnh điều kiện mới.
  * [fco-order-cancel](./api-reference/fco-order-cancel) — Hủy lệnh điều kiện.
  * [fco-list](./api-reference/fco-list) — Danh sách lệnh điều kiện.
  * [fco-orderbook](./api-reference/fco-orderbook) — Sổ lệnh điều kiện.
  * [fco-statusHistory](./api-reference/fco-statusHistory) — Lịch sử trạng thái lệnh.

## 6) Phụ lục tham khảo

Các tài liệu bổ sung giúp hiểu rõ hơn về quy trình nghiệp vụ và xử lý lỗi:

  * [Luồng trạng thái lệnh](./api-reference/appendix/order-status-flow) — Sơ đồ và mô tả chi tiết 16 trạng thái lệnh trong vòng đời đặt/sửa/hủy/khớp lệnh.
  * [Tham khảo đặt lệnh điều kiện](./api-reference/appendix/fco-reference) — Tham số chi tiết và ví dụ JSON cho từng loại lệnh FCO.
  * [Tra cứu mã lỗi (ErrCode)](./api-reference/appendix/error-codes) — Bảng mã lỗi đầy đủ phân theo HTTP status code (400, 401, 403, 404, 405, 408, 409, 429, 500, 502, 503, 504).

## Khuyến nghị triển khai

  * Quản lý chặt vòng đời token (cấp mới, refresh, hết hạn).
  * Chuẩn hóa xử lý lỗi dựa trên `ErrCode` — xem [Tra cứu mã lỗi](./api-reference/error-codes) để map code sang hành động cụ thể.
  * Tách biệt luồng REST và luồng realtime trong kiến trúc tích hợp.
  * Với WebSocket, luôn triển khai cơ chế reconnect và subscribe lại topic.
  * Với lệnh điều kiện (FCO), tham khảo [bảng tham số chi tiết](./api-reference/fco-reference) để đảm bảo đúng tham số cho từng loại lệnh.

## Phạm vi trang này

Đây là trang **tổng quan nghiệp vụ và kiến trúc**. Thông số field-level, schema chi tiết, sample request/response và ràng buộc được mô tả tại từng trang API tương ứng ở sidebar.
