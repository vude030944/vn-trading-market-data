<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/tutorials
Tieu de goc: Thực hành
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/tutorials>

# Thực hành

Những gì bạn sẽ học, yêu cầu tiên quyết, và cách điều hướng các tutorial

## Tổng quan

Các tutorial hướng dẫn bạn sử dụng **FastConnect Python SDK** (`ssi_sdk`) để tích hợp với hệ thống giao dịch chứng khoán — từ xác thực, truy vấn dữ liệu thị trường, đặt/hủy lệnh, đến streaming real-time và auto trading.

Mỗi tutorial tương ứng với một sample code Python hoàn chỉnh, có cả phiên bản **sync** và **async**.

> Các tutorial ở đây sử dụng **Python** làm ngôn ngữ minh họa. Repo GitHub bên dưới cũng chứa source code cho các ngôn ngữ khác — tham khảo [SDK](/docs/sdk/overview) để xem danh sách đầy đủ.

## Source code

Toàn bộ source code của các tutorial có sẵn trên GitHub:

[github.com/SSI-Securities-Inc/ssi-fastconnect-v3-tutorials](https://github.com/SSI-Securities-Inc/ssi-fastconnect-v3-tutorials)
```text
git clone https://github.com/SSI-Securities-Inc/ssi-fastconnect-v3-tutorials.git
```

## Yêu cầu

  * Tài khoản FastConnect API (Consumer ID, API Key, API Secret, Private Key)
  * Python 3.10+
  * Cài đặt SDK: `pip install ssi-sdk`

## Lộ trình học

### [1\. Xác thực & TokenĐăng nhập, lấy token, cache token để tái sử dụng](/docs/tutorials/auth)### [2\. Chỉ số thị trườngLấy VN-Index, HNX-Index và summary chi tiết](/docs/tutorials/index-list)### [3\. Dữ liệu K-line (OHLC)Lấy dữ liệu nến cho biểu đồ và phân tích kỹ thuật](/docs/tutorials/ohlc)### [4\. Danh sách cổ phiếuLấy mã cổ phiếu theo sàn, chỉ số, xem chi tiết](/docs/tutorials/securities)### [5\. Số dư tài khoảnKiểm tra sức mua, vị thế trước khi đặt lệnh](/docs/tutorials/balance)### [6\. Đặt lệnh LimitĐặt lệnh mua/bán tại mức giá chỉ định](/docs/tutorials/limit-order)### [7\. Đặt lệnh MarketKhớp lệnh nhanh theo giá thị trường](/docs/tutorials/market-order)### [8\. Trạng thái lệnhTheo dõi tiến trình khớp lệnh bằng polling](/docs/tutorials/order-status)### [9\. Hủy lệnhHủy lệnh đang mở chưa khớp](/docs/tutorials/cancel-order)### [10\. WebSocket Market DataNhận giá khớp, bảng giá, room nước ngoài real-time](/docs/tutorials/websocket-data)### [11\. WebSocket TradingNhận trạng thái lệnh và danh mục real-time](/docs/tutorials/websocket-trading)### [12\. MA Cross Auto TradeBot tự động giao dịch theo tín hiệu MA Cross](/docs/tutorials/ma-cross-auto-trade)### [13\. Lệnh điều kiện (FCO)Đặt và quản lý lệnh GTD, Stop, Trailing Stop, OCO, Bull Bear...](/docs/tutorials/fco-order)

## Luồng tổng thể
```text
Auth (token cache) → Market Data → Account Check → Place Order → Track/Cancel → Realtime Update
```

  * **Manual flow:** Auth → Market Data → Account Check → Place Order → Track/Cancel → Realtime Update
  * **Auto flow:** Auth → OHLC/Indicator → Signal Engine → Risk Check → Auto Order → Monitor → P&L Logging

## Cấu trúc code

Mỗi tutorial cung cấp:

  * **Mục tiêu** — code làm gì và tại sao
  * **Luồng** — sơ đồ từng bước
  * **Sync sample** — code tuần tự đơn giản
  * **Async sample** — code dùng `asyncio` cho workload đồng thời
  * **Ghi chú** — lưu ý quan trọng và best practices

Tất cả sample dùng chung module `auth_helper.py` để cache token (giới thiệu ở [Tutorial 1](/docs/tutorials/auth)).

## Mẹo

  * Bắt đầu với **Tutorial 1 (Xác thực)** — tất cả tutorial khác đều phụ thuộc vào nó.
  * Tutorial 1–4 không cần OTP, nên bạn có thể khám phá dữ liệu thị trường mà không cần trading credentials.
  * Lưu credentials trong biến môi trường hoặc config file, không hard-code.
  * Thêm `token_cache.json` vào `.gitignore`.
