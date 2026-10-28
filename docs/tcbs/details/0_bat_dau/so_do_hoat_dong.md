<!--
Nguon goc (source): https://developers.tcbs.com.vn/docs/v1.0.0/workflow
Tieu de goc: Sơ đồ hoạt động
Cap nhat (fetched): 2026-08-19
-->

> **Nguồn:** <https://developers.tcbs.com.vn/docs/v1.0.0/workflow>

# Sơ đồ hoạt động

## Sequence Diagram

Quy trình tích hợp iFlash Open API

## Đăng ký lấy API Key

Khách hàng có thể tự đăng ký iFlash Open API miễn phí tại:

URL: <https://tcinvest.tcbs.com.vn/iflash-open-api>

Truy cập TCInvest: Menu trái → Tiện ích → iFlash Open API

## Lấy Token

Khách hàng sử dụng API Key đã đăng ký + iOTP để lấy Token sử dụng khi gọi các API nghiệp vụ. Xem chi tiết tại endpoint Xác thực (auth/token).

## Thời gian hiệu lực của Access Token

Mã truy cập (Access Token) có hiệu lực tối đa 8 giờ kể từ khi nhận được xác thực iOTP từ ứng dụng TCInvest. Khi Access Token hết hạn, Quý khách cần lấy mã mới để đảm bảo việc sử dụng không bị gián đoạn.

## Huỷ API Key

Quý khách có thể huỷ API Key đã đăng ký tại cùng trang quản lý iFlash Open API.
