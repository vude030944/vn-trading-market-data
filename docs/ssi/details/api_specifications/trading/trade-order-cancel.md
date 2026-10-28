<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/trade-order-cancel
Tieu de goc: trade-order-cancel
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/trade-order-cancel>

# trade-order-cancel

Hủy lệnh hiện có.

Server URL`loading...`

DELETE

``/`api`/`v3`/`trading`/`order`

Send

Authorization

Body

### Authorization

`Bearer `

AuthorizationBearer <token>

Nhập JWT token theo định dạng `Bearer <token>`.

In: `header`

### Header Parameters

- **`Content-Type`** — `string`, *required*

Định dạng nội dung request body. Chủ yếu là application/json.

- **`User-Agent`** — `string`, *optional*

Thông tin client gửi request.

- **`Accept-Language`** — `string`, *optional*

Ngôn ngữ phản hồi mong muốn. Nếu không có header này, hệ thống sẽ mặc định là en

- **`X-Signature`** — `string`, *required*

Chữ ký RSA + SHA256 để xác thực tính toàn vẹn của request. Input bao gồm SecretKey + JSON body.

### Request Body

`application/json`

TypeScript Definitions

Use the request body type in TypeScript.

Copy

- **`body`** — `object`, *required*

- **`clientCancelId`** — `string | null`, *optional*

Định danh hủy lệnh do client tạo ra, dùng để đối chiếu trong các phản hồi sau này. Trường này không bắt buộc nhưng nếu có thì nên đảm bảo tính duy nhất để tránh nhầm lẫn khi xử lý phản hồi. Khi để trống thì hệ thống sẽ tự sinh định danh hủy lệnh cho khách hàng và trả về response & streaming.

- **`clientRequestId`** — `string | null`, *optional*

Định danh lệnh gốc do client tạo ra khi đặt lệnh. Khi để trống thì hệ thống sẽ không đối chiếu dựa trên định danh lệnh gốc mà sẽ dựa vào `orderId` để xác định lệnh cần hủy.

- **`orderId`** — `string | null`, *optional*

Định danh lệnh gốc sinh ra bởi hệ thống SSI. Đây là một trong hai trường (cùng với `clientRequestId`) được sử dụng để xác định lệnh cần hủy. Nếu cả hai trường đều có giá trị, hệ thống sẽ ưu tiên đối chiếu dựa trên `clientRequestId`. Nếu chỉ có `orderId` có giá trị thì hệ thống sẽ đối chiếu dựa trên `orderId`. Nếu cả hai trường đều không có giá trị thì yêu cầu hủy lệnh sẽ bị từ chối do thiếu thông tin xác định lệnh cần hủy.

- **`accountNo`** — `string`, *required*

Số tài khoản giao dịch.

- **`deviceId`** — `string`, *required*

Định danh thiết bị thực hiện gửi yêu cầu hủy lệnh. Thông thường dùng MAC address hoặc IMEI của thiết bị.

- **`userAgent`** — `string | null`, *optional*

Thông tin về trình duyệt hoặc ứng dụng gửi yêu cầu hủy lệnh.

- **`ipAddress`** — `string | null`, *optional*

Địa chỉ IP của thiết bị gửi yêu cầu hủy lệnh.

### Response Headers

- **`X-RATELIMIT-LIMIT`** — `string`, *optional*

Giới hạn số request trong chu kỳ.

- **`X-RATELIMIT-REMAINING`** — `string`, *optional*

Số request còn lại trong chu kỳ hiện tại.

- **`X-RATELIMIT-RESET`** — `string`, *optional*

Thời điểm reset giới hạn request.

### Response Body

### 200

`application/json`

### 400

`application/json`

cURL

JavaScript

Go

Python

Java

C#
```bash
curl -X DELETE "https://api.ssi.com.vn/api/v3/trading/order" \
  -H "Content-Type: application/json" \
  -H "X-Signature: sha256=abc123..." \
  -H "Content-Type: application/json" \
  -d '{    "accountNo": "string",    "deviceId": "string"  }'
```

200400

Success
```json
{
  "clientRequestId": "string",
  "orderId": "string",
  "orderStatus": "string",
  "clientModifyId": "string",
  "clientCancelId": "string"
}
```

Yêu cầu không hợp lệ.
```json
{
  "code": "400",
  "msg": "Invalid request"
}
```
