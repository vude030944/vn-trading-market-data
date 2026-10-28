# TCBS iFlash Open API — tài liệu chi tiết (bản sao nguyên văn)

Toàn bộ tài liệu chính thống tại <https://developers.tcbs.com.vn/docs/v1.0.0>
được tải về ngày **19/08/2026** (phiên bản tài liệu `v1.0.0`, phát hành 31/07/2026).

Cấu trúc thư mục bám đúng **8 nhóm trên sidebar** của trang gốc; tên file giữ
nguyên số thứ tự của tài liệu (`5.2.` → `5_2_...`) để tra cứu chéo cho nhanh.

**Tổng cộng: 53 trang.** Mỗi file có link nguồn ở đầu trang.

> Site là Next.js SSR nên nội dung được lấy từ HTML render sẵn rồi chuyển sang
> markdown. Riêng phần *Demo tương tác* của các trang WebSocket là widget mô phỏng
> — tài liệu gốc đã tự ghi rõ *"chỉ mang tính minh họa, protocol thực tế là TEXT
> frame phân tách bằng pipe"*; phần này được giữ nguyên để không làm sai lệch bản sao.

> **Lưu ý về dấu `|`:** protocol TCBS dùng ký tự `|` làm dấu phân tách. Trong các
> bảng markdown, ký tự này được escape thành `\|` để bảng không bị vỡ cột — khi đọc
> giá trị thật, bỏ dấu `\` đi (ví dụ `s\|1` là `s|1`).

## Trang gốc

| File | Tiêu đề gốc | URL gốc |
|---|---|---|
| [`00_trang_chu.md`](00_trang_chu.md) | API giao dịch chứng khoán realtime cho developer | <https://developers.tcbs.com.vn/> |

## 0_bat_dau/ — Bắt đầu

| File | Tiêu đề gốc | URL gốc |
|---|---|---|
| [`0_bat_dau/iflash_open_api.md`](0_bat_dau/iflash_open_api.md) | iFlash Open API | <https://developers.tcbs.com.vn/docs/v1.0.0/introduction> |
| [`0_bat_dau/kieu_du_lieu.md`](0_bat_dau/kieu_du_lieu.md) | Kiểu dữ liệu | <https://developers.tcbs.com.vn/docs/v1.0.0/data-types> |
| [`0_bat_dau/so_do_hoat_dong.md`](0_bat_dau/so_do_hoat_dong.md) | Sơ đồ hoạt động | <https://developers.tcbs.com.vn/docs/v1.0.0/workflow> |

## 1_xac_thuc/ — 1. Xác thực

| File | Tiêu đề gốc | URL gốc |
|---|---|---|
| [`1_xac_thuc/1_1_trao_doi_api_key_de_lay_jwt_token.md`](1_xac_thuc/1_1_trao_doi_api_key_de_lay_jwt_token.md) | 1.1. Trao đổi API Key để lấy JWT Token | <https://developers.tcbs.com.vn/docs/v1.0.0/auth/token> |

## 2_tai_khoan/ — 2. Tài khoản

| File | Tiêu đề gốc | URL gốc |
|---|---|---|
| [`2_tai_khoan/2_1_lay_thong_tin_tieu_khoan.md`](2_tai_khoan/2_1_lay_thong_tin_tieu_khoan.md) | 2.1. Lấy thông tin tiểu khoản | <https://developers.tcbs.com.vn/docs/v1.0.0/account/sub-account> |

## 3_tien/ — 3. Tiền

| File | Tiêu đề gốc | URL gốc |
|---|---|---|
| [`3_tien/3_1_chuyen_tien_noi_bo.md`](3_tien/3_1_chuyen_tien_noi_bo.md) | 3.1. Chuyển tiền nội bộ | <https://developers.tcbs.com.vn/docs/v1.0.0/money/transfer> |
| [`3_tien/3_2_rut_ky_quy.md`](3_tien/3_2_rut_ky_quy.md) | 3.2. Rút ký quỹ | <https://developers.tcbs.com.vn/docs/v1.0.0/money/withdraw> |
| [`3_tien/3_3_nop_ky_quy.md`](3_tien/3_3_nop_ky_quy.md) | 3.3. Nộp ký quỹ | <https://developers.tcbs.com.vn/docs/v1.0.0/money/deposit> |

## 4_chung_khoan_co_so_lenh/ — 4. Chứng khoán cơ sở — Lệnh

| File | Tiêu đề gốc | URL gốc |
|---|---|---|
| [`4_chung_khoan_co_so_lenh/4_10_han_muc_margin.md`](4_chung_khoan_co_so_lenh/4_10_han_muc_margin.md) | 4.10. Hạn mức margin | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/margin-limit> |
| [`4_chung_khoan_co_so_lenh/4_11_ty_le_margin_rui_ro.md`](4_chung_khoan_co_so_lenh/4_11_ty_le_margin_rui_ro.md) | 4.11. Tỷ lệ margin & rủi ro | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/risk-ratios> |
| [`4_chung_khoan_co_so_lenh/4_12_goi_vay_bo_tro.md`](4_chung_khoan_co_so_lenh/4_12_goi_vay_bo_tro.md) | 4.12. Gói vay bổ trợ | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/addon-loan> |
| [`4_chung_khoan_co_so_lenh/4_13_danh_sach_khoan_vay.md`](4_chung_khoan_co_so_lenh/4_13_danh_sach_khoan_vay.md) | 4.13. Danh sách khoản vay | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/loan-list> |
| [`4_chung_khoan_co_so_lenh/4_14_tra_cuu_tai_san_co_phieu.md`](4_chung_khoan_co_so_lenh/4_14_tra_cuu_tai_san_co_phieu.md) | 4.14. Tra cứu tài sản cổ phiếu | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/asset> |
| [`4_chung_khoan_co_so_lenh/4_15_lay_thong_tin_so_du_tien.md`](4_chung_khoan_co_so_lenh/4_15_lay_thong_tin_so_du_tien.md) | 4.15. Lấy thông tin số dư tiền | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/cash-balance> |
| [`4_chung_khoan_co_so_lenh/4_16_thong_tin_sao_ke_tien.md`](4_chung_khoan_co_so_lenh/4_16_thong_tin_sao_ke_tien.md) | 4.16. Thông tin sao kê tiền | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/cash-statement> |
| [`4_chung_khoan_co_so_lenh/4_17_tra_cuu_no.md`](4_chung_khoan_co_so_lenh/4_17_tra_cuu_no.md) | 4.17. Tra cứu nợ | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/debt-lookup> |
| [`4_chung_khoan_co_so_lenh/4_18_tra_cuu_goi_lai_suat_margin.md`](4_chung_khoan_co_so_lenh/4_18_tra_cuu_goi_lai_suat_margin.md) | 4.18. Tra cứu gói lãi suất margin | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/pricing-policy> |
| [`4_chung_khoan_co_so_lenh/4_1_dat_lenh_thuong.md`](4_chung_khoan_co_so_lenh/4_1_dat_lenh_thuong.md) | 4.1. Đặt lệnh thường | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/place-order> |
| [`4_chung_khoan_co_so_lenh/4_2_sua_lenh_thuong.md`](4_chung_khoan_co_so_lenh/4_2_sua_lenh_thuong.md) | 4.2. Sửa lệnh thường | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/update-order> |
| [`4_chung_khoan_co_so_lenh/4_3_huy_lenh_thuong.md`](4_chung_khoan_co_so_lenh/4_3_huy_lenh_thuong.md) | 4.3. Huỷ lệnh thường | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/cancel-order> |
| [`4_chung_khoan_co_so_lenh/4_4_lay_so_lenh.md`](4_chung_khoan_co_so_lenh/4_4_lay_so_lenh.md) | 4.4. Lấy sổ lệnh | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/get-orders> |
| [`4_chung_khoan_co_so_lenh/4_5_lay_so_lenh_theo_order_id.md`](4_chung_khoan_co_so_lenh/4_5_lay_so_lenh_theo_order_id.md) | 4.5. Lấy sổ lệnh theo Order ID | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/get-order-by-id> |
| [`4_chung_khoan_co_so_lenh/4_6_lay_thong_tin_khop_lenh.md`](4_chung_khoan_co_so_lenh/4_6_lay_thong_tin_khop_lenh.md) | 4.6. Lấy thông tin khớp lệnh | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/matching-details> |
| [`4_chung_khoan_co_so_lenh/4_7_lay_suc_mua.md`](4_chung_khoan_co_so_lenh/4_7_lay_suc_mua.md) | 4.7. Lấy sức mua | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/purchasing-power> |
| [`4_chung_khoan_co_so_lenh/4_8_lay_suc_mua_theo_ma.md`](4_chung_khoan_co_so_lenh/4_8_lay_suc_mua_theo_ma.md) | 4.8. Lấy sức mua theo mã | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/purchasing-power-symbol> |
| [`4_chung_khoan_co_so_lenh/4_9_lay_suc_mua_theo_ma_gia.md`](4_chung_khoan_co_so_lenh/4_9_lay_suc_mua_theo_ma_gia.md) | 4.9. Lấy sức mua theo mã, giá | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/purchasing-power-symbol-price> |

## 5_chung_khoan_co_so_thi_truong/ — 5. Chứng khoán cơ sở — Thị trường

| File | Tiêu đề gốc | URL gốc |
|---|---|---|
| [`5_chung_khoan_co_so_thi_truong/5_10_lich_su_gia_khop_cung_cau_websocket.md`](5_chung_khoan_co_so_thi_truong/5_10_lich_su_gia_khop_cung_cau_websocket.md) | 5.10. Lịch sử giá khớp, cung cầu (WebSocket) | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/ws-history> |
| [`5_chung_khoan_co_so_thi_truong/5_11_tra_cuu_thong_tin_chung_khoan.md`](5_chung_khoan_co_so_thi_truong/5_11_tra_cuu_thong_tin_chung_khoan.md) | 5.11. Tra cứu thông tin chứng khoán | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/securities-info> |
| [`5_chung_khoan_co_so_thi_truong/5_1_thong_tin_ma_gia.md`](5_chung_khoan_co_so_thi_truong/5_1_thong_tin_ma_gia.md) | 5.1. Thông tin mã, giá | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/market-symbol> |
| [`5_chung_khoan_co_so_thi_truong/5_2_bang_gia_co_so_websocket.md`](5_chung_khoan_co_so_thi_truong/5_2_bang_gia_co_so_websocket.md) | 5.2. Bảng giá cơ sở (WebSocket) | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/ws-price-board> |
| [`5_chung_khoan_co_so_thi_truong/5_3_thong_tin_room_nuoc_ngoai.md`](5_chung_khoan_co_so_thi_truong/5_3_thong_tin_room_nuoc_ngoai.md) | 5.3. Thông tin room nước ngoài | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/foreign-room> |
| [`5_chung_khoan_co_so_thi_truong/5_4_thong_tin_thoa_thuan.md`](5_chung_khoan_co_so_thi_truong/5_4_thong_tin_thoa_thuan.md) | 5.4. Thông tin thỏa thuận | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/put-through> |
| [`5_chung_khoan_co_so_thi_truong/5_5_lich_su_gia_khop.md`](5_chung_khoan_co_so_thi_truong/5_5_lich_su_gia_khop.md) | 5.5. Lịch sử giá khớp | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/price-history> |
| [`5_chung_khoan_co_so_thi_truong/5_6_cung_cau_trong_phien_15m.md`](5_chung_khoan_co_so_thi_truong/5_6_cung_cau_trong_phien_15m.md) | 5.6. Cung cầu trong phiên (15m) | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/supply-demand-intraday> |
| [`5_chung_khoan_co_so_thi_truong/5_7_cung_cau_theo_ngay.md`](5_chung_khoan_co_so_thi_truong/5_7_cung_cau_theo_ngay.md) | 5.7. Cung cầu theo ngày | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/supply-demand-daily> |
| [`5_chung_khoan_co_so_thi_truong/5_8_cung_cau_theo_thang.md`](5_chung_khoan_co_so_thi_truong/5_8_cung_cau_theo_thang.md) | 5.8. Cung cầu theo tháng | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/supply-demand-monthly> |
| [`5_chung_khoan_co_so_thi_truong/5_9_thay_doi_thong_tin_lenh_co_so_websocket.md`](5_chung_khoan_co_so_thi_truong/5_9_thay_doi_thong_tin_lenh_co_so_websocket.md) | 5.9. Thay đổi thông tin lệnh cơ sở (WebSocket) | <https://developers.tcbs.com.vn/docs/v1.0.0/stock/ws-order-matching> |

## 6_chung_khoan_phai_sinh_lenh/ — 6. Chứng khoán phái sinh — Lệnh

| File | Tiêu đề gốc | URL gốc |
|---|---|---|
| [`6_chung_khoan_phai_sinh_lenh/6_10_huy_lenh_thuong.md`](6_chung_khoan_phai_sinh_lenh/6_10_huy_lenh_thuong.md) | 6.10. Huỷ lệnh thường | <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/cancel-order> |
| [`6_chung_khoan_phai_sinh_lenh/6_11_huy_lenh_dieu_kien.md`](6_chung_khoan_phai_sinh_lenh/6_11_huy_lenh_dieu_kien.md) | 6.11. Huỷ lệnh điều kiện | <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/cancel-condition-order> |
| [`6_chung_khoan_phai_sinh_lenh/6_1_tong_quan_tien_ky_quy.md`](6_chung_khoan_phai_sinh_lenh/6_1_tong_quan_tien_ky_quy.md) | 6.1. Tổng quan tiền, ký quỹ | <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/account-status> |
| [`6_chung_khoan_phai_sinh_lenh/6_2_tai_san_vi_the_dong.md`](6_chung_khoan_phai_sinh_lenh/6_2_tai_san_vi_the_dong.md) | 6.2. Tài sản, vị thế đóng | <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/position-closed> |
| [`6_chung_khoan_phai_sinh_lenh/6_3_tai_san_vi_the_mo.md`](6_chung_khoan_phai_sinh_lenh/6_3_tai_san_vi_the_mo.md) | 6.3. Tài sản, vị thế mở | <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/position-open> |
| [`6_chung_khoan_phai_sinh_lenh/6_4_dat_lenh_thuong.md`](6_chung_khoan_phai_sinh_lenh/6_4_dat_lenh_thuong.md) | 6.4. Đặt lệnh thường | <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/place-order> |
| [`6_chung_khoan_phai_sinh_lenh/6_5_dat_lenh_dieu_kien.md`](6_chung_khoan_phai_sinh_lenh/6_5_dat_lenh_dieu_kien.md) | 6.5. Đặt lệnh điều kiện | <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/place-condition-order> |
| [`6_chung_khoan_phai_sinh_lenh/6_6_tra_cuu_so_lenh_thuong.md`](6_chung_khoan_phai_sinh_lenh/6_6_tra_cuu_so_lenh_thuong.md) | 6.6. Tra cứu sổ lệnh thường | <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/get-normal-orders> |
| [`6_chung_khoan_phai_sinh_lenh/6_7_tra_cuu_so_lenh_dieu_kien.md`](6_chung_khoan_phai_sinh_lenh/6_7_tra_cuu_so_lenh_dieu_kien.md) | 6.7. Tra cứu sổ lệnh điều kiện | <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/get-condition-orders> |
| [`6_chung_khoan_phai_sinh_lenh/6_8_sua_lenh_thuong.md`](6_chung_khoan_phai_sinh_lenh/6_8_sua_lenh_thuong.md) | 6.8. Sửa lệnh thường | <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/update-order> |
| [`6_chung_khoan_phai_sinh_lenh/6_9_sua_lenh_dieu_kien.md`](6_chung_khoan_phai_sinh_lenh/6_9_sua_lenh_dieu_kien.md) | 6.9. Sửa lệnh điều kiện | <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/update-condition-order> |

## 7_chung_khoan_phai_sinh_thi_truong/ — 7. Chứng khoán phái sinh — Thị trường

| File | Tiêu đề gốc | URL gốc |
|---|---|---|
| [`7_chung_khoan_phai_sinh_thi_truong/7_1_thong_tin_ma_gia.md`](7_chung_khoan_phai_sinh_thi_truong/7_1_thong_tin_ma_gia.md) | 7.1. Thông tin mã, giá | <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/market-symbol> |
| [`7_chung_khoan_phai_sinh_thi_truong/7_2_bang_gia_phai_sinh_websocket.md`](7_chung_khoan_phai_sinh_thi_truong/7_2_bang_gia_phai_sinh_websocket.md) | 7.2. Bảng giá phái sinh (WebSocket) | <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/ws-price-board> |
| [`7_chung_khoan_phai_sinh_thi_truong/7_3_thay_doi_thong_tin_lenh_phai_sinh_websocket.md`](7_chung_khoan_phai_sinh_thi_truong/7_3_thay_doi_thong_tin_lenh_phai_sinh_websocket.md) | 7.3. Thay đổi thông tin lệnh phái sinh (WebSocket) | <https://developers.tcbs.com.vn/docs/v1.0.0/derivative/ws-order-matching> |

## changelog/

| File | Tiêu đề gốc | URL gốc |
|---|---|---|
| [`changelog/changelog.md`](changelog/changelog.md) | Changelog | <https://developers.tcbs.com.vn/changelog> |

## Trang quan trọng nhất cho bài toán WebSocket

| File | Nội dung |
|---|---|
| [`5_chung_khoan_co_so_thi_truong/5_2_bang_gia_co_so_websocket.md`](5_chung_khoan_co_so_thi_truong/5_2_bang_gia_co_so_websocket.md) | Bảng giá cơ sở — protocol đầy đủ nhất: auth, subscribe/unsubscribe/request, heartbeat, 9 channel ID + schema, reconnect, code mẫu |
| [`7_chung_khoan_phai_sinh_thi_truong/7_2_bang_gia_phai_sinh_websocket.md`](7_chung_khoan_phai_sinh_thi_truong/7_2_bang_gia_phai_sinh_websocket.md) | Bảng giá phái sinh — channel 21/23/24/27, kiểu dữ liệu number |
| [`5_chung_khoan_co_so_thi_truong/5_10_lich_su_gia_khop_cung_cau_websocket.md`](5_chung_khoan_co_so_thi_truong/5_10_lich_su_gia_khop_cung_cau_websocket.md) | Endpoint `ouranos` — C001/C002S60/C002S900, có `timeSec` epoch và `action` BU/SD |
| [`5_chung_khoan_co_so_thi_truong/5_9_thay_doi_thong_tin_lenh_co_so_websocket.md`](5_chung_khoan_co_so_thi_truong/5_9_thay_doi_thong_tin_lenh_co_so_websocket.md) | Endpoint `aither` — sự kiện lệnh cơ sở (timeout 7s) |
| [`7_chung_khoan_phai_sinh_thi_truong/7_3_thay_doi_thong_tin_lenh_phai_sinh_websocket.md`](7_chung_khoan_phai_sinh_thi_truong/7_3_thay_doi_thong_tin_lenh_phai_sinh_websocket.md) | Endpoint `nesoi` — sự kiện lệnh phái sinh (timeout 45s) |
| [`1_xac_thuc/1_1_trao_doi_api_key_de_lay_jwt_token.md`](1_xac_thuc/1_1_trao_doi_api_key_de_lay_jwt_token.md) | Đổi API Key + OTP lấy JWT |
| [`0_bat_dau/so_do_hoat_dong.md`](0_bat_dau/so_do_hoat_dong.md) | Quy trình đăng ký, vòng đời token 8 giờ |
