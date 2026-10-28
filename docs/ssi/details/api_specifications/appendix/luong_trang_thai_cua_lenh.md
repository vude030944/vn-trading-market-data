<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/appendix/order-status-flow
Tieu de goc: Luồng trạng thái của lệnh
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/appendix/order-status-flow>

# Luồng trạng thái của lệnh

Mô tả chi tiết các trạng thái của lệnh trong hệ thống FastConnect và luồng chuyển đổi giữa các trạng thái.

# Luồng trạng thái của lệnh

## Tổng quan

Mỗi lệnh giao dịch qua FastConnect API sẽ trải qua các trạng thái khác nhau trong vòng đời của nó. Tài liệu này mô tả ý nghĩa từng trạng thái và luồng chuyển đổi giữa chúng.

## Sơ đồ trạng thái

## Bảng trạng thái

| # | FC Status | Tên đầy đủ | Mô tả |
|---|---|---|---|
| 1 | `PD` | Pending | Trạng thái ghi nhận — lệnh cơ sở đã được tiếp nhận vào hệ thống. |
| 2 | `RS` | Ready to Send | Lệnh sẵn sàng gửi lên sở giao dịch. |
| 3 | `SD` | Sent to Exchange | Lệnh đã được gửi lên sở giao dịch (áp dụng cho lệnh phiên). |
| 4 | `QU` | Queue in Exchange | Lệnh đang chờ khớp tại sở giao dịch. |
| 5 | `WA` | Waiting Approval | Lệnh đang chờ phê duyệt. |
| 6 | `FF` | Fully Filled | Lệnh đã khớp toàn bộ khối lượng. Trạng thái kết thúc. |
| 7 | `PF` | Partially Filled | Lệnh đã khớp một phần khối lượng, phần còn lại tiếp tục chờ khớp. |
| 8 | `FFPC` | Fully Filled Partially Cancelled | Lệnh đã khớp một phần, phần còn lại bị hủy. Trạng thái kết thúc. |
| 9 | `WM` | Waiting Modify | Lệnh đang chờ sửa đổi (giá hoặc khối lượng). |
| 10 | `WC` | Waiting Cancel | Lệnh đang chờ hủy. |
| 11 | `CL` | Cancelled | Lệnh đã hủy thành công. Trạng thái kết thúc. |
| 12 | `RJ` | Rejected | Lệnh bị từ chối (không đủ điều kiện, sai tham số...). Trạng thái kết thúc. |
| 13 | `EX` | Expired | Lệnh hết hiệu lực hoặc bị sở từ chối. Trạng thái kết thúc. |
| 14 | `IAV` | PreSessionOrder | Lệnh trước phiên (lệnh PS) — đặt trước giờ giao dịch, chờ gửi khi phiên mở. |
| 15 | `SOI` | PreSessionStopOrder | Lệnh dừng trước phiên — lệnh stop đặt trước giờ giao dịch. |
| 16 | `PAS` | WaitingApprovalStopOrder | Lệnh dừng đang chờ phê duyệt. |

## Luồng chuyển đổi chi tiết

### Đặt lệnh mới

  1. Khi consumer gửi request đặt lệnh, hệ thống ghi nhận lệnh với trạng thái:
     * **PD** (Pending) cho lệnh cơ sở
     * **IAV** (PreSessionOrder) cho lệnh trước phiên
  2. Lệnh chuyển sang **RS** (Ready to Send) khi sẵn sàng gửi lên sở.
  3. Nếu không đủ điều kiện (thiếu ký quỹ, sai tham số, vi phạm room...) → **RJ** (Rejected).
  4. Lệnh được gửi lên sở → **SD** (Sent to Exchange), sau đó xếp hàng chờ khớp → **QU** (Queue in Exchange).

### Khớp lệnh

  * Khớp toàn bộ khối lượng → **FF** (Fully Filled). Kết thúc.
  * Khớp một phần → **PF** (Partially Filled). Phần còn lại tiếp tục chờ khớp.

### Sửa lệnh

  * Từ trạng thái **QU** hoặc **PF** , consumer có thể gửi yêu cầu sửa lệnh.
  * Lệnh chuyển sang **WM** (Waiting Modify).
  * Khi sửa thành công, lệnh quay về trạng thái trước đó (**QU** hoặc **PF**) với thông tin đã cập nhật.

### Hủy lệnh

  * Từ trạng thái **QU** : hủy lệnh → **WC** (Waiting Cancel) → **CL** (Cancelled). Kết thúc.
  * Từ trạng thái **PF** : hủy phần còn lại → **WC** → **FFPC** (Fully Filled Partially Cancelled). Kết thúc.

### Hết hiệu lực

  * Lệnh tại sở bị reject → **EX** (Expired). Kết thúc.
  * Lệnh khớp một phần (**PF**) hết thời gian hiệu lực → **FFPC**. Kết thúc.

### Các trạng thái kết thúc (End State)

| Trạng thái | Ý nghĩa |
|---|---|
| `FF` | Lệnh khớp hết — giao dịch hoàn tất. |
| `FFPC` | Lệnh khớp một phần, phần còn lại bị hủy hoặc hết hiệu lực. |
| `CL` | Lệnh đã hủy toàn bộ. |
| `RJ` | Lệnh bị từ chối ngay từ đầu. |
| `EX` | Lệnh hết hiệu lực hoặc bị sở từ chối. |
