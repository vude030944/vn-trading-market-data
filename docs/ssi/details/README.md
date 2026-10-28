# SSI FastConnect — tài liệu chi tiết (bản sao nguyên văn)

Toàn bộ tài liệu chính thống tại <https://developers.ssi.com.vn/docs> được tải về
ngày **17/08/2026** và giữ nguyên nội dung gốc. Cấu trúc thư mục bám đúng phân cấp
của trang gốc: 4 mục cấp 1 trên thanh điều hướng (Hướng dẫn / Đặc tả API / Tài liệu
SDK / Thực hành), cộng thêm trang giới thiệu và changelog.

**Tổng cộng: 88 trang.** Mỗi file đều có link nguồn ở đầu trang.

> Ghi chú: các route `/docs/api-reference/events/*`, `/docs/api-reference/tickets/*`,
> `/docs/api-reference/operations/getMuseumHours` tồn tại trên site nhưng là trang mẫu
> còn sót của template (Museum API demo), **không thuộc tài liệu SSI** nên không lưu.
> `/docs/getting-started/overview` là bản trùng của `/docs/getting-started`.

## Gốc

| File | Tiêu đề gốc | URL gốc |
|---|---|---|
| [`00_gioi_thieu.md`](00_gioi_thieu.md) | Giới thiệu | <https://developers.ssi.com.vn/docs> |

## 1. guide/ — Hướng dẫn (`/docs/getting-started`)

| File | Tiêu đề gốc | URL gốc |
|---|---|---|
| [`guide/buoc_tiep_theo.md`](guide/buoc_tiep_theo.md) | Bước tiếp theo | <https://developers.ssi.com.vn/docs/getting-started/next-steps> |
| [`guide/cach_lay_api_key_access_token.md`](guide/cach_lay_api_key_access_token.md) | Cách lấy API Key / Access Token | <https://developers.ssi.com.vn/docs/getting-started/api-keys> |
| [`guide/cau_hoi_thuong_gap_faq.md`](guide/cau_hoi_thuong_gap_faq.md) | Câu hỏi thường gặp (FAQ) | <https://developers.ssi.com.vn/docs/getting-started/faq> |
| [`guide/dieu_kien_su_dung_moi_truong.md`](guide/dieu_kien_su_dung_moi_truong.md) | Điều kiện sử dụng & Môi trường | <https://developers.ssi.com.vn/docs/getting-started/terms-and-environments> |
| [`guide/quy_trinh_dang_ky_va_kich_hoat.md`](guide/quy_trinh_dang_ky_va_kich_hoat.md) | Quy trình đăng ký và kích hoạt | <https://developers.ssi.com.vn/docs/getting-started/registration> |
| [`guide/tong_quan_he_thong.md`](guide/tong_quan_he_thong.md) | Tổng quan hệ thống | <https://developers.ssi.com.vn/docs/getting-started> |
| [`guide/trai_nghiem_nhanh.md`](guide/trai_nghiem_nhanh.md) | Trải nghiệm nhanh | <https://developers.ssi.com.vn/docs/getting-started/first-api-call> |

## 2. api_specifications/ — Đặc tả API (`/docs/api-reference`)

| File | Tiêu đề gốc | URL gốc |
|---|---|---|
| [`api_specifications/00_tong_quan_api.md`](api_specifications/00_tong_quan_api.md) | SSI API Overview | <https://developers.ssi.com.vn/docs/api-reference> |
| [`api_specifications/appendix/luong_trang_thai_cua_lenh.md`](api_specifications/appendix/luong_trang_thai_cua_lenh.md) | Luồng trạng thái của lệnh | <https://developers.ssi.com.vn/docs/api-reference/appendix/order-status-flow> |
| [`api_specifications/appendix/tham_khao_dat_lenh_dieu_kien.md`](api_specifications/appendix/tham_khao_dat_lenh_dieu_kien.md) | Tham khảo đặt lệnh điều kiện | <https://developers.ssi.com.vn/docs/api-reference/appendix/fco-reference> |
| [`api_specifications/appendix/tra_cuu_ma_loi_errcode.md`](api_specifications/appendix/tra_cuu_ma_loi_errcode.md) | Tra cứu mã lỗi (ErrCode) | <https://developers.ssi.com.vn/docs/api-reference/appendix/error-codes> |
| [`api_specifications/authentication/auth-refresh.md`](api_specifications/authentication/auth-refresh.md) | auth-refresh | <https://developers.ssi.com.vn/docs/api-reference/auth-refresh> |
| [`api_specifications/authentication/auth-requestOtp.md`](api_specifications/authentication/auth-requestOtp.md) | auth-requestOtp | <https://developers.ssi.com.vn/docs/api-reference/auth-requestOtp> |
| [`api_specifications/authentication/auth-token.md`](api_specifications/authentication/auth-token.md) | auth-token | <https://developers.ssi.com.vn/docs/api-reference/auth-token> |
| [`api_specifications/conditional_order_fco/fco-list.md`](api_specifications/conditional_order_fco/fco-list.md) | fco-list | <https://developers.ssi.com.vn/docs/api-reference/fco-list> |
| [`api_specifications/conditional_order_fco/fco-order-cancel.md`](api_specifications/conditional_order_fco/fco-order-cancel.md) | fco-order-cancel | <https://developers.ssi.com.vn/docs/api-reference/fco-order-cancel> |
| [`api_specifications/conditional_order_fco/fco-order-place.md`](api_specifications/conditional_order_fco/fco-order-place.md) | fco-order-place | <https://developers.ssi.com.vn/docs/api-reference/fco-order-place> |
| [`api_specifications/conditional_order_fco/fco-orderbook.md`](api_specifications/conditional_order_fco/fco-orderbook.md) | fco-orderbook | <https://developers.ssi.com.vn/docs/api-reference/fco-orderbook> |
| [`api_specifications/conditional_order_fco/fco-statusHistory.md`](api_specifications/conditional_order_fco/fco-statusHistory.md) | fco-statusHistory | <https://developers.ssi.com.vn/docs/api-reference/fco-statusHistory> |
| [`api_specifications/market_data/data-indexList.md`](api_specifications/market_data/data-indexList.md) | data-indexList | <https://developers.ssi.com.vn/docs/api-reference/data-indexList> |
| [`api_specifications/market_data/data-indexSummary.md`](api_specifications/market_data/data-indexSummary.md) | data-indexSummary | <https://developers.ssi.com.vn/docs/api-reference/data-indexSummary> |
| [`api_specifications/market_data/data-masterData.md`](api_specifications/market_data/data-masterData.md) | data-masterData | <https://developers.ssi.com.vn/docs/api-reference/data-masterData> |
| [`api_specifications/market_data/data-ohlc.md`](api_specifications/market_data/data-ohlc.md) | data-ohlc | <https://developers.ssi.com.vn/docs/api-reference/data-ohlc> |
| [`api_specifications/market_data/data-securitiesByBoard.md`](api_specifications/market_data/data-securitiesByBoard.md) | data-securitiesByBoard | <https://developers.ssi.com.vn/docs/api-reference/data-securitiesByBoard> |
| [`api_specifications/market_data/data-securitiesSummary.md`](api_specifications/market_data/data-securitiesSummary.md) | data-securitiesSummary | <https://developers.ssi.com.vn/docs/api-reference/data-securitiesSummary> |
| [`api_specifications/trading/account-info.md`](api_specifications/trading/account-info.md) | account-info | <https://developers.ssi.com.vn/docs/api-reference/account-info> |
| [`api_specifications/trading/trade-accountBalance.md`](api_specifications/trading/trade-accountBalance.md) | trade-accountBalance | <https://developers.ssi.com.vn/docs/api-reference/trade-accountBalance> |
| [`api_specifications/trading/trade-maxbuysell.md`](api_specifications/trading/trade-maxbuysell.md) | trade-maxbuysell | <https://developers.ssi.com.vn/docs/api-reference/trade-maxbuysell> |
| [`api_specifications/trading/trade-order-cancel.md`](api_specifications/trading/trade-order-cancel.md) | trade-order-cancel | <https://developers.ssi.com.vn/docs/api-reference/trade-order-cancel> |
| [`api_specifications/trading/trade-order-modify.md`](api_specifications/trading/trade-order-modify.md) | trade-order-modify | <https://developers.ssi.com.vn/docs/api-reference/trade-order-modify> |
| [`api_specifications/trading/trade-order-place.md`](api_specifications/trading/trade-order-place.md) | trade-order-place | <https://developers.ssi.com.vn/docs/api-reference/trade-order-place> |
| [`api_specifications/trading/trade-orderBook.md`](api_specifications/trading/trade-orderBook.md) | trade-orderBook | <https://developers.ssi.com.vn/docs/api-reference/trade-orderBook> |
| [`api_specifications/trading/trade-position.md`](api_specifications/trading/trade-position.md) | trade-position | <https://developers.ssi.com.vn/docs/api-reference/trade-position> |
| [`api_specifications/trading/trade-ppmmrAccount.md`](api_specifications/trading/trade-ppmmrAccount.md) | trade-ppmmrAccount | <https://developers.ssi.com.vn/docs/api-reference/trade-ppmmrAccount> |
| [`api_specifications/websocket/connectWebSocket.md`](api_specifications/websocket/connectWebSocket.md) | Kết nối WebSocket | <https://developers.ssi.com.vn/docs/api-reference/connectWebSocket> |
| [`api_specifications/websocket/getHeartbeatStructure.md`](api_specifications/websocket/getHeartbeatStructure.md) | Heartbeat và Subscription | <https://developers.ssi.com.vn/docs/api-reference/getHeartbeatStructure> |
| [`api_specifications/websocket/subscribeUnsubscribeMarketData.md`](api_specifications/websocket/subscribeUnsubscribeMarketData.md) | Sub/Unsub Market Data | <https://developers.ssi.com.vn/docs/api-reference/subscribeUnsubscribeMarketData> |
| [`api_specifications/websocket/subscribeUnsubscribeTradingData.md`](api_specifications/websocket/subscribeUnsubscribeTradingData.md) | Sub/Unsub Trading Data | <https://developers.ssi.com.vn/docs/api-reference/subscribeUnsubscribeTradingData> |

## 3. sdk_document/ — Tài liệu SDK (`/docs/sdk`)

| File | Tiêu đề gốc | URL gốc |
|---|---|---|
| [`sdk_document/00_gioi_thieu_sdk.md`](sdk_document/00_gioi_thieu_sdk.md) | Giới thiệu SSI SDK | <https://developers.ssi.com.vn/docs/sdk/overview> |
| [`sdk_document/csharp/00_overview.md`](sdk_document/csharp/00_overview.md) | Tổng quan | <https://developers.ssi.com.vn/docs/sdk/csharp/overview> |
| [`sdk_document/csharp/01_installation_requirements.md`](sdk_document/csharp/01_installation_requirements.md) | Cài đặt và cấu hình | <https://developers.ssi.com.vn/docs/sdk/csharp/installation-requirements> |
| [`sdk_document/csharp/02_configuration.md`](sdk_document/csharp/02_configuration.md) | Cấu hình | <https://developers.ssi.com.vn/docs/sdk/csharp/configuration> |
| [`sdk_document/csharp/03_client_classes.md`](sdk_document/csharp/03_client_classes.md) | Client Classes | <https://developers.ssi.com.vn/docs/sdk/csharp/client-classes> |
| [`sdk_document/csharp/04_service_classes.md`](sdk_document/csharp/04_service_classes.md) | API Services | <https://developers.ssi.com.vn/docs/sdk/csharp/service-classes> |
| [`sdk_document/csharp/05_transport_classes.md`](sdk_document/csharp/05_transport_classes.md) | Enums & Hằng số | <https://developers.ssi.com.vn/docs/sdk/csharp/transport-classes> |
| [`sdk_document/csharp/06_utilities.md`](sdk_document/csharp/06_utilities.md) | Models | <https://developers.ssi.com.vn/docs/sdk/csharp/utilities> |
| [`sdk_document/csharp/07_exceptions.md`](sdk_document/csharp/07_exceptions.md) | Xử lý lỗi | <https://developers.ssi.com.vn/docs/sdk/csharp/exceptions> |
| [`sdk_document/go/00_overview.md`](sdk_document/go/00_overview.md) | Tổng quan | <https://developers.ssi.com.vn/docs/sdk/go/overview> |
| [`sdk_document/go/01_installation_requirements.md`](sdk_document/go/01_installation_requirements.md) | Cài đặt & Thiết lập | <https://developers.ssi.com.vn/docs/sdk/go/installation-requirements> |
| [`sdk_document/go/02_configuration.md`](sdk_document/go/02_configuration.md) | Cấu hình | <https://developers.ssi.com.vn/docs/sdk/go/configuration> |
| [`sdk_document/go/03_client_classes.md`](sdk_document/go/03_client_classes.md) | Client Classes | <https://developers.ssi.com.vn/docs/sdk/go/client-classes> |
| [`sdk_document/go/04_service_classes.md`](sdk_document/go/04_service_classes.md) | API Services | <https://developers.ssi.com.vn/docs/sdk/go/service-classes> |
| [`sdk_document/go/05_transport_classes.md`](sdk_document/go/05_transport_classes.md) | Enums & Hằng số | <https://developers.ssi.com.vn/docs/sdk/go/transport-classes> |
| [`sdk_document/go/06_utilities.md`](sdk_document/go/06_utilities.md) | Models | <https://developers.ssi.com.vn/docs/sdk/go/utilities> |
| [`sdk_document/go/07_exceptions.md`](sdk_document/go/07_exceptions.md) | Xử lý lỗi | <https://developers.ssi.com.vn/docs/sdk/go/exceptions> |
| [`sdk_document/java/00_overview.md`](sdk_document/java/00_overview.md) | Tổng quát Java SDK | <https://developers.ssi.com.vn/docs/sdk/java/overview> |
| [`sdk_document/nodejs/00_overview.md`](sdk_document/nodejs/00_overview.md) | Tổng quan | <https://developers.ssi.com.vn/docs/sdk/nodejs/overview> |
| [`sdk_document/nodejs/01_installation_requirements.md`](sdk_document/nodejs/01_installation_requirements.md) | Cài đặt & Thiết lập | <https://developers.ssi.com.vn/docs/sdk/nodejs/installation-requirements> |
| [`sdk_document/nodejs/02_configuration.md`](sdk_document/nodejs/02_configuration.md) | Cấu hình | <https://developers.ssi.com.vn/docs/sdk/nodejs/configuration> |
| [`sdk_document/nodejs/03_client_classes.md`](sdk_document/nodejs/03_client_classes.md) | Client Classes | <https://developers.ssi.com.vn/docs/sdk/nodejs/client-classes> |
| [`sdk_document/nodejs/04_service_classes.md`](sdk_document/nodejs/04_service_classes.md) | API Services | <https://developers.ssi.com.vn/docs/sdk/nodejs/service-classes> |
| [`sdk_document/nodejs/05_transport_classes.md`](sdk_document/nodejs/05_transport_classes.md) | Enums & Hằng số | <https://developers.ssi.com.vn/docs/sdk/nodejs/transport-classes> |
| [`sdk_document/nodejs/06_utilities.md`](sdk_document/nodejs/06_utilities.md) | Models | <https://developers.ssi.com.vn/docs/sdk/nodejs/utilities> |
| [`sdk_document/nodejs/07_exceptions.md`](sdk_document/nodejs/07_exceptions.md) | Xử lý lỗi | <https://developers.ssi.com.vn/docs/sdk/nodejs/exceptions> |
| [`sdk_document/python/00_overview.md`](sdk_document/python/00_overview.md) | Tổng quan | <https://developers.ssi.com.vn/docs/sdk/python/overview> |
| [`sdk_document/python/01_installation_requirements.md`](sdk_document/python/01_installation_requirements.md) | Cài đặt và cấu hình | <https://developers.ssi.com.vn/docs/sdk/python/installation-requirements> |
| [`sdk_document/python/02_configuration.md`](sdk_document/python/02_configuration.md) | Cấu hình | <https://developers.ssi.com.vn/docs/sdk/python/configuration> |
| [`sdk_document/python/03_client_classes.md`](sdk_document/python/03_client_classes.md) | Client classes | <https://developers.ssi.com.vn/docs/sdk/python/client-classes> |
| [`sdk_document/python/04_service_classes.md`](sdk_document/python/04_service_classes.md) | API Services | <https://developers.ssi.com.vn/docs/sdk/python/service-classes> |
| [`sdk_document/python/05_transport_classes.md`](sdk_document/python/05_transport_classes.md) | Enums & Hằng số | <https://developers.ssi.com.vn/docs/sdk/python/transport-classes> |
| [`sdk_document/python/06_utilities.md`](sdk_document/python/06_utilities.md) | Models | <https://developers.ssi.com.vn/docs/sdk/python/utilities> |
| [`sdk_document/python/07_exceptions.md`](sdk_document/python/07_exceptions.md) | Xử lý lỗi | <https://developers.ssi.com.vn/docs/sdk/python/exceptions> |

## 4. practice/ — Thực hành (`/docs/tutorials`)

| File | Tiêu đề gốc | URL gốc |
|---|---|---|
| [`practice/00_tong_quan_thuc_hanh.md`](practice/00_tong_quan_thuc_hanh.md) | Thực hành | <https://developers.ssi.com.vn/docs/tutorials> |
| [`practice/01_xac_thuc_token_cache.md`](practice/01_xac_thuc_token_cache.md) | 1. Xác thực & Token Cache | <https://developers.ssi.com.vn/docs/tutorials/auth> |
| [`practice/02_chi_so_thi_truong.md`](practice/02_chi_so_thi_truong.md) | 2. Chỉ số thị trường | <https://developers.ssi.com.vn/docs/tutorials/index-list> |
| [`practice/03_du_lieu_k_line_ohlc.md`](practice/03_du_lieu_k_line_ohlc.md) | 3. Dữ liệu K-line (OHLC) | <https://developers.ssi.com.vn/docs/tutorials/ohlc> |
| [`practice/04_danh_sach_co_phieu.md`](practice/04_danh_sach_co_phieu.md) | 4. Danh sách cổ phiếu | <https://developers.ssi.com.vn/docs/tutorials/securities> |
| [`practice/05_so_du_tai_khoan.md`](practice/05_so_du_tai_khoan.md) | 5. Số dư tài khoản | <https://developers.ssi.com.vn/docs/tutorials/balance> |
| [`practice/06_dat_lenh_limit.md`](practice/06_dat_lenh_limit.md) | 6. Đặt lệnh Limit | <https://developers.ssi.com.vn/docs/tutorials/limit-order> |
| [`practice/07_dat_lenh_market.md`](practice/07_dat_lenh_market.md) | 7. Đặt lệnh Market | <https://developers.ssi.com.vn/docs/tutorials/market-order> |
| [`practice/08_trang_thai_lenh.md`](practice/08_trang_thai_lenh.md) | 8. Trạng thái lệnh | <https://developers.ssi.com.vn/docs/tutorials/order-status> |
| [`practice/09_huy_lenh.md`](practice/09_huy_lenh.md) | 9. Hủy lệnh | <https://developers.ssi.com.vn/docs/tutorials/cancel-order> |
| [`practice/10_websocket_market_data.md`](practice/10_websocket_market_data.md) | 10. WebSocket Market Data | <https://developers.ssi.com.vn/docs/tutorials/websocket-data> |
| [`practice/11_websocket_trading.md`](practice/11_websocket_trading.md) | 11. WebSocket Trading | <https://developers.ssi.com.vn/docs/tutorials/websocket-trading> |
| [`practice/12_ma_cross_auto_trade.md`](practice/12_ma_cross_auto_trade.md) | 12. MA Cross Auto Trade | <https://developers.ssi.com.vn/docs/tutorials/ma-cross-auto-trade> |
| [`practice/13_lenh_dieu_kien_fco.md`](practice/13_lenh_dieu_kien_fco.md) | 13. Lệnh điều kiện (FCO) | <https://developers.ssi.com.vn/docs/tutorials/fco-order> |

## 5. changelog/ — Changelog (`/docs/changelog`)

| File | Tiêu đề gốc | URL gốc |
|---|---|---|
| [`changelog/changelog.md`](changelog/changelog.md) | Changelog | <https://developers.ssi.com.vn/docs/changelog/overview> |
