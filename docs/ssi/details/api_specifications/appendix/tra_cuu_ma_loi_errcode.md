<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/appendix/error-codes
Tieu de goc: Tra cứu mã lỗi (ErrCode)
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/appendix/error-codes>

# Tra cứu mã lỗi (ErrCode)

Danh sách đầy đủ các mã lỗi (ErrCode) trả về từ FastConnect API, phân nhóm theo HTTP status code.

# Tra cứu mã lỗi (ErrCode)

## Tổng quan

Khi gọi FastConnect API, mỗi response lỗi sẽ chứa trường `status` (HTTP status code) và `ErrCode` (mã lỗi chi tiết) giúp xác định chính xác nguyên nhân lỗi.

## Quy ước đặt mã lỗi

Mã lỗi FastConnect tuân theo quy ước `{HTTP_STATUS}{xxx}` với `xxx` là mã chi tiết:

| Nhóm | Phạm vi | Ý nghĩa |
|---|---|---|
| `4000xx` | 400000 – 400015 | Lỗi chung cho cả Trading và Market Data |
| `4001xx` | 400101 – 400165 | Lỗi riêng cho Trading |
| `4002xx` | 400200+ | Lỗi riêng cho Market Data |

* * *

## HTTP 200 — Success

Request thành công, server trả về dữ liệu như mong đợi.

| Mã lỗi | Tên lỗi | Ý nghĩa |
|---|---|---|
| `200` | Success | Request thành công, server trả về dữ liệu như mong đợi. |

* * *

## HTTP 202 — Accepted

Request đã được nhận và đang xử lý bất đồng bộ — không phải lỗi, client cần chờ hoặc tự thử lại.

| Mã lỗi | Tên lỗi | Ý nghĩa |
|---|---|---|
| `401114` | Push-approval is pending | Yêu cầu Smart OTP push-approval đang chờ người dùng bấm duyệt trên app. SDK (`ensure_authenticated`/`EnsureAuthenticated`/...) tự động poll lại; nếu gọi API trực tiếp, client cần tự retry sau vài giây. |

* * *

## HTTP 400 — Bad Request

Request sai định dạng, thiếu tham số hoặc dữ liệu không hợp lệ.

### Lỗi chung (4000xx)

Áp dụng cho cả Trading API và Market Data API.

| Mã lỗi | Tên lỗi | Ý nghĩa |
|---|---|---|
| `400000` | Invalid Request | Request không hợp lệ. |
| `400001` | Malformed JSON Body | JSON body sai cú pháp. |
| `400002` | Missing Required Field | Thiếu trường bắt buộc. |
| `400003` | Invalid Field Value | Giá trị trường dữ liệu không hợp lệ. |
| `400004` | Invalid Field Format | Sai định dạng dữ liệu (regex/date/id). |
| `400005` | Invalid Field Error | Trường dữ liệu không hợp lệ. |
| `400006` | Missing Request Body | Thiếu body cho API. |
| `400007` | Data is available only for the latest x years | Dữ liệu chỉ hỗ trợ trong x năm gần nhất. |
| `400008` | Query time range cannot exceed y months | Khoảng truy vấn không vượt quá y tháng. |
| `400009` | From Date cannot be greater than To Date | From Date không được lớn hơn To Date. |
| `400010` | Query time range cannot exceed z years | Khoảng truy vấn không vượt quá z năm. |
| `400011` | The lookup time must be earlier than the current date | Thời điểm tra cứu phải nhỏ hơn hiện tại. |
| `400012` | Invalid Date/Timestamp | Định dạng ngày/thời gian không hợp lệ. |
| `400013` | Invalid Timezone | Timezone không hợp lệ. |
| `400014` | Invalid PageNumber | PageNumber không hợp lệ. |
| `400015` | Invalid PageSize | PageSize không hợp lệ. |

### Lỗi Trading — Xác thực và cấu hình (400101 – 400110)

Lỗi liên quan đến credential, 2FA, OTP và cấu hình tài khoản giao dịch.

| Mã lỗi | Tên lỗi | Ý nghĩa |
|---|---|---|
| `400101` | Credential has no associated client | Credential không liên kết với client nào. |
| `400102` | Failed to get 2FA info | Không lấy được thông tin 2FA. |
| `400103` | 2FA info not available for this account | Thông tin 2FA không khả dụng cho tài khoản này. |
| `400104` | Failed to send OTP | Gửi OTP thất bại. |
| `400105` | Unsupported Core_Type for account | Core_Type không được hỗ trợ cho tài khoản. |
| `400106` | Order rejected: stock disclosure policy violation | Lệnh bị từ chối do vi phạm chính sách công bố cổ phiếu. |
| `400107` | Do not edit price and quantity at the same time | Không được sửa giá và khối lượng cùng lúc. |
| `400108` | OrderType is not allowed | Loại lệnh không được phép. |
| `400109` | Modify order rejected: stock disclosure policy violation | Sửa lệnh bị từ chối do vi phạm chính sách công bố cổ phiếu. |
| `400110` | No accounts found for client | Không tìm thấy tài khoản cho client. |

### Lỗi Trading — Nghiệp vụ đặt lệnh (400111 – 400148)

Lỗi validate nghiệp vụ khi đặt/sửa/hủy lệnh: giá, khối lượng, mã chứng khoán, phiên giao dịch.

| Mã lỗi | Tên lỗi | Ý nghĩa |
|---|---|---|
| `400111` | Symbol Not Tradable | Mã chứng khoán không được giao dịch. |
| `400112` | Price Out of Range | Giá đặt phải nằm trong khoảng trần sàn. |
| `400113` | Invalid Lot Size | Khối lượng đặt phải chia hết cho lô giao dịch. |
| `400114` | Price Must Be Positive | Giá phải > 0. |
| `400115` | Price Must Be Zero | Giá phải = 0. |
| `400116` | Price Must Be Zero For Market Orders | Giá đặt phải = 0, với các loại lệnh ATO, ATC, MTL, MAK, MOK, PLO. |
| `400117` | Order Type Not Allowed In Current Session | Không đặt được loại lệnh này trong phiên hiện tại. |
| `400118` | Price Not Divisible By Tick Size | Giá đặt không chia hết cho bước giá. |
| `400119` | Sell Not Allowed In This Session | Không cho phép đặt lệnh bán trong phiên này. |
| `400120` | Quantity Below Minimum | Khối lượng đặt không được nhỏ hơn khối lượng Min. |
| `400121` | Quantity Exceeds Maximum | Khối lượng đặt không được lớn hơn khối lượng Max. |
| `400122` | Duplicate Order In Periodic Session | Lệnh trùng trong phiên định kỳ (có cả mua và bán). |
| `400123` | Symbol Not Registered With Exchange | Mã chứng khoán không được khai báo với sàn giao dịch nào. |
| `400124` | Symbol Rule Not Configured | Mã chứng khoán chưa được cài đặt rule. |
| `400125` | Symbol Even Lot Rule Not Configured | Mã chứng khoán chưa được cài đặt rule lô chẵn. |
| `400126` | Symbol Odd Lot Rule Not Configured | Mã chứng khoán chưa được cài đặt rule lô lẻ. |
| `400127` | Cannot Change From Even To Odd Lot | Không được sửa khối lượng từ lô chẵn sang lô lẻ. |
| `400128` | Cannot Change From Odd To Even Lot | Không được sửa khối lượng từ lô lẻ sang lô chẵn. |
| `400129` | OrderQty Must Match Original | OrderQty phải bằng khối lượng của lệnh cần sửa. |
| `400130` | Invalid Lot Quantity | Khối lượng lớn hơn lô và không chia hết cho lô giao dịch. |
| `400131` | Order Cannot Be Cancelled | Trạng thái của lệnh không thể hủy. |
| `400132` | Order Cannot Be Modified | Trạng thái của lệnh không thể sửa. |
| `400133` | No Changes Detected | Lệnh sửa không có sự thay đổi thông tin. |
| `400134` | Invalid Symbol Format | Mã chứng khoán không chứa khoảng trắng, độ dài ≤ 20 ký tự. |
| `400135` | Pre-session Order Type Not Bound | Loại lệnh nhập trước không được gắn với phiên nào. |
| `400136` | Cannot Modify MP In Continuous Session | Không cho phép sửa loại lệnh MP trong phiên liên tục. |
| `400137` | Cannot Modify MOK In Continuous Session | Không cho phép sửa loại lệnh MOK trong phiên liên tục. |
| `400138` | Cannot Modify MTL In Continuous Session | Không cho phép sửa loại lệnh MTL trong phiên liên tục. |
| `400139` | Cannot Modify MAK In Continuous Session | Không cho phép sửa loại lệnh MAK trong phiên liên tục. |
| `400140` | Derivative Account Required | Tài khoản đặt lệnh phải là tài khoản phái sinh. |
| `400141` | Symbol Buy Restricted | Mã chứng khoán bị hạn chế giao dịch mua. |
| `400142` | Symbol Sell Restricted | Mã chứng khoán bị hạn chế giao dịch bán. |
| `400143` | Symbol Not On Derivative Exchange | Mã chứng khoán không thuộc sàn giao dịch phái sinh. |
| `400144` | Account Cannot Trade Derivative Symbol | Tài khoản không đặt được mã chứng khoán phái sinh. |
| `400145` | Account Suspended | Tài khoản bị tạm ngưng do vượt quá số lượng lệnh cho phép. |
| `400146` | Symbol Required | Mã chứng khoán không được bỏ trống. |
| `400147` | Quantity Must Be Positive | Khối lượng phải lớn hơn 0. |
| `400148` | Quantity Exceeds Limit | Khối lượng quá hạn mức. |

### Lỗi Trading — Phiên giao dịch, tài khoản và FCO (400149 – 400165)

Lỗi liên quan đến giờ giao dịch, tài khoản, tham số lệnh cơ bản và lệnh điều kiện (FCO).

| Mã lỗi | Tên lỗi | Ý nghĩa |
|---|---|---|
| `400149` | Before Trading Hours | Trước giờ giao dịch. |
| `400150` | After Trading Hours / Trading Account Required | Sau giờ giao dịch. Hoặc: thiếu AccountNo/ClientId, tài khoản không tìm thấy. |
| `400151` | Symbol Required | Thiếu mã giao dịch (symbol). |
| `400152` | Invalid Symbol | Symbol không hợp lệ. |
| `400153` | Order Side Required | Thiếu side (BUY/SELL). |
| `400154` | Invalid Order Side | Side đặt không hợp lệ. |
| `400155` | Order Type Required | Thiếu orderType. |
| `400156` | Invalid Order Type | orderType không hợp lệ. |
| `400157` | Quantity Required / Price Required | Thiếu quantity hoặc thiếu giá. |
| `400158` | Invalid Quantity | Khối lượng không hợp lệ. |
| `400159` | Invalid Price | Giá không hợp lệ. |
| `400160` | Operation Not Permitted | Thao tác không được phép. |
| `400161` | FCO Strategy Not Supported | Chiến lược FCO không khớp với các chiến lược được hỗ trợ. |
| `400162` | FCO Cannot Set StopOrder | Loại lệnh FCO không thể thiết lập stopOrder=True. |
| `400163` | FCO Cannot Set Price Main Order | Loại lệnh FCO không thể thiết lập mức giá cho lệnh chính. |
| `400164` | FCO Activation Limit Reached | Số lượng kích hoạt đã đầy. Không thể kích hoạt thêm. |
| `400165` | FCO Indicator Type Mismatch | Giá trị chỉ báo không cùng kiểu dữ liệu. |

* * *

## HTTP 401 — Unauthorized

Thiếu hoặc sai token/credentials, chưa xác thực người dùng.

### Access Token (401000 – 401016)

| Mã lỗi | Tên lỗi | Ý nghĩa |
|---|---|---|
| `401000` | Missing Authorization Header | Thiếu header Authorization. |
| `401001` | Unauthorized | Chưa xác thực. |
| `401002` | Access Token Missing | Thiếu access token. |
| `401003` | Access Token Invalid | Access token không hợp lệ. |
| `401004` | Access Token Expired | Access token đã hết hạn. |
| `401009` | Access Token Not Yet Valid | Access token chưa đến thời điểm hiệu lực (nbf). |
| `401010` | Token Signature Invalid | Chữ ký token không hợp lệ. |
| `401011` | Missing Signature Header | Thiếu header chữ ký (X-Signature). |
| `401012` | Signature Not Recognized | Chữ ký không được nhận diện. |
| `401013` | Signature Not Valid | Chữ ký không hợp lệ. Token value không hợp lệ. |
| `401014` | Signature Not Matched | Chữ ký không khớp. |
| `401015` | Signature Body Empty | Chữ ký không hợp lệ. Body request rỗng. |
| `401016` | Token Not Include OTP | Token không bao gồm OTP. |

### Refresh Token và OTP (401100 – 401108)

| Mã lỗi | Tên lỗi | Ý nghĩa |
|---|---|---|
| `401100` | OTP Verification Failed | Xác thực OTP thất bại. |
| `401101` | Invalid Refresh Token | Refresh token không hợp lệ. |
| `401102` | Refresh Token Missing Client | Refresh token thiếu thông tin client. |
| `401103` | Refresh Token Revoked or Expired | Refresh token đã bị thu hồi hoặc hết hạn. |
| `401104` | Invalid API Key Reference | API key reference từ refresh token không hợp lệ. |
| `401105` | Invalid API Key or Secret | API key hoặc secret không hợp lệ. |
| `401106` | Invalid Token Type | Loại token không đúng, yêu cầu refresh token. |
| `401107` | Refresh Token Missing JTI | Refresh token thiếu claim jti. |
| `401108` | Refresh Token Missing Key ID | Refresh token thiếu claim key_id. |

* * *

## HTTP 403 — Forbidden

Người dùng đã xác thực nhưng không có quyền thực hiện hành động.

| Mã lỗi | Tên lỗi | Ý nghĩa |
|---|---|---|
| `403000` | Forbidden | Không có quyền truy cập tài nguyên/thao tác. |
| `403001` | Insufficient Scope | Token/API key không đủ scope quyền. |
| `403100` | No Scopes Granted | API key không được cấp scope nào. |
| `403102` | Product Not Enabled For Account | Tài khoản chưa mở quyền cho sản phẩm này. |

* * *

## HTTP 404 — Not Found

API endpoint hoặc tài nguyên không tồn tại.

| Mã lỗi | Tên lỗi | Ý nghĩa |
|---|---|---|
| `404000` | Resource Not Found | Không tìm thấy tài nguyên yêu cầu. |
| `404100` | ClientRequestId Not Found | Không tìm thấy ClientRequestId. |
| `404101` | ClientRequestId Has No OrderId | ClientRequestId không có OrderId tương ứng. |
| `404102` | OrderId Not Found | Không tìm thấy OrderId. |
| `404103` | Account Not Found | Không tìm thấy tài khoản. |
| `404204` | Symbol Not Found | Không tìm thấy mã chứng khoán. |

* * *

## HTTP 405 — Method Not Allowed

Sử dụng sai HTTP method (ví dụ: dùng GET thay vì POST).

| Mã lỗi | Tên lỗi | Ý nghĩa |
|---|---|---|
| `405000` | Method Not Allowed | Method không được hỗ trợ cho endpoint. |
| `405001` | GET Not Allowed | Endpoint này không hỗ trợ GET. |
| `405002` | POST Not Allowed | Endpoint này không hỗ trợ POST. |
| `405003` | PUT Not Allowed | Endpoint này không hỗ trợ PUT. |
| `405004` | PATCH Not Allowed | Endpoint này không hỗ trợ PATCH. |
| `405005` | DELETE Not Allowed | Endpoint này không hỗ trợ DELETE. |
| `405006` | OPTIONS Not Allowed | Endpoint này không hỗ trợ OPTIONS. |

* * *

## HTTP 408 — Request Timeout

Server chờ nhận request từ client quá thời gian cho phép.

| Mã lỗi | Tên lỗi | Ý nghĩa |
|---|---|---|
| `408000` | Request Timeout | Request bị timeout. |
| `408200` | Market Data Export Request Timeout | Timeout khi nhận request export dữ liệu thị trường. |

* * *

## HTTP 409 — Conflict

Request hợp lệ nhưng xung đột với trạng thái hiện tại của tài nguyên/nghiệp vụ.

| Mã lỗi | Tên lỗi | Ý nghĩa |
|---|---|---|
| `409000` | Conflict | Xung đột trạng thái tổng quát. |
| `409100` | Duplicate Request | Request trùng lặp — đã submit trước đó với cùng RequestId. |
| `409101` | Resource Already Exists | Tài nguyên đã tồn tại nên không thể tạo mới. |
| `409102` | Insufficient Buying Power | Không đủ sức mua để đặt lệnh. |
| `409103` | Insufficient Account Balance | Số dư tài khoản không đủ. |

* * *

## HTTP 429 — Too Many Requests

Gửi quá nhiều request trong một khoảng thời gian, bị giới hạn (rate limit).

### Rate Limit chung (429000 – 429100)

| Mã lỗi | Tên lỗi | Ý nghĩa |
|---|---|---|
| `429000` | Rate Limit Exceeded | Vượt giới hạn request tổng quát của hệ thống. |
| `429100` | Daily Order Limit Exceeded | Vượt quá hạn mức đặt lệnh trong ngày của tài khoản. |

### Hạn mức giao dịch (429101 – 429126)

| Mã lỗi | Tên lỗi | Ý nghĩa |
|---|---|---|
| `429101` | Volume Exceeds Current Room | Khối lượng vượt quá current room. |
| `429102` | Deposit Exceeds Approval Limit | Số tiền nộp vượt quá hạn mức duyệt. |
| `429103` | Exceeds Allowable Input Limit | Vượt quá hạn mức có thể nhập. |
| `429104` | Exceeds Allowable Approval Limit | Vượt quá hạn mức có thể duyệt. |
| `429105` | Override Exceeds Withdrawable Amount | Số tiền ghi đè vượt quá số tiền có thể rút. |
| `429106` | Exceeds Withdrawable Amount | Vượt quá số tiền có thể rút. |
| `429107` | Exceeds Daily Transaction Limit | Vượt quá hạn mức giao dịch trong ngày. |
| `429108` | Exceeds Maximum Withdrawable Amount | Vượt quá số tiền tối đa có thể rút. |
| `429109` | Exceeds Account Transaction Limit | Vượt quá số tiền giao dịch của tài khoản. |
| `429110` | Exceeds Maximum Withdrawable Balance | Vượt quá số dư tiền tối đa có thể rút. |
| `429111` | Exceeds Allowable Input Limit | Vượt quá hạn mức có thể nhập. |
| `429112` | Exceeds Allowable Input Amount | Vượt quá số tiền có thể nhập. |
| `429113` | Exceeds Daily Transaction Limit | Vượt quá hạn mức giao dịch trong ngày. |
| `429114` | Exceeds Transferable Amount | Vượt quá số tiền có thể chuyển. |
| `429115` | Exceeds Maximum Transferable Amount | Vượt quá số tiền tối đa có thể chuyển khi duyệt. |
| `429116` | Exceeds Daily Transferable Limit | Vượt quá số tiền có thể chuyển trong một ngày. |
| `429117` | Transfer Exceeds Napas Limit | Số tiền chuyển vượt quá hạn mức Napas. |
| `429118` | Exceeds Maximum Withdrawable Balance | Vượt quá số dư tiền tối đa có thể rút. |
| `429119` | Cash Advance Exceeds Maximum Limit | Số tiền ứng trước vượt quá mức tối đa cho phép. |
| `429120` | Received Cash Advance Exceeds Maximum | Số tiền nhận ứng trước vượt quá mức tối đa cho phép. |
| `429121` | Blocked Volume Exceeds Available Balance | Khối lượng phong tỏa vượt quá số dư khả dụng. |
| `429122` | Released Volume Exceeds Blocked Volume | Khối lượng giải tỏa vượt quá khối lượng phong tỏa. |
| `429123` | Exceeds Allowable Input Limit | Vượt quá hạn mức có thể nhập. |
| `429124` | Exceeds Auto-Approval Cash Advance | Vượt quá số tiền tự động duyệt ứng trước tối đa. |
| `429125` | Rejection Reason Length Exceeded | Lý do từ chối vượt quá độ dài cho phép. |
| `429126` | Volume Exceeds Limit | Khối lượng vượt quá hạn mức. |

* * *

## HTTP 500 — Internal Server Error

Lỗi phía server, không xử lý được request.

| Mã lỗi | Tên lỗi | Ý nghĩa |
|---|---|---|
| `500000` | Internal Server Error | Lỗi phía server, không xử lý được request. |
| `500002` | Database Execution Error | Lỗi xử lý nghiệp vụ ở tầng database. |
| `500100` | Token Verification Failed: Client ID Mismatch | Xác minh token thất bại: client_id không khớp. |
| `500101` | Token Verification Failed: Scopes Missing | Xác minh token thất bại: thiếu claim scopes. |
| `500200` | Market Data Persistence Error | Lỗi lưu trữ dữ liệu market data. |

* * *

## HTTP 502 — Bad Gateway

Server trung gian nhận phản hồi không hợp lệ từ upstream server.

| Mã lỗi | Tên lỗi | Ý nghĩa |
|---|---|---|
| `502000` | Bad Gateway | Lỗi gateway tổng quát với hệ thống upstream. |
| `502100` | CashPosition No Data | Upstream CashPosition không trả về dữ liệu cho tài khoản. |
| `502101` | GetCashBalance No Data | Upstream GetCashBalance không trả về dữ liệu cho tài khoản. |
| `502102` | GetAssetsExtends Failed | Upstream GetAssetsExtends thất bại cho tài khoản. |

* * *

## HTTP 503 — Service Unavailable

Dịch vụ tạm thời không khả dụng (quá tải/bảo trì/phụ thuộc lỗi).

| Mã lỗi | Tên lỗi | Ý nghĩa |
|---|---|---|
| `503000` | Service Unavailable | Dịch vụ tạm thời không phục vụ được. |
| `503001` | System Maintenance Window | Hệ thống đang trong thời gian bảo trì. |

* * *

## HTTP 504 — Gateway Timeout

Server trung gian không nhận được phản hồi kịp từ upstream server.

| Mã lỗi | Tên lỗi | Ý nghĩa |
|---|---|---|
| `504000` | Gateway Timeout | Timeout tổng quát khi gọi upstream. |
