<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/nodejs/client-classes
Tieu de goc: Client Classes
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/nodejs/client-classes>

# Client Classes

Auth, Data, Trading, Stream — khởi tạo và sử dụng

SDK cung cấp 4 client chuyên biệt. Tất cả method API đều là `async` và trả về `Promise`.

## Auth

Client gốc — quản lý REST client, xác thực, và token. Tất cả client khác nhận `Auth` làm tham số.
```python
import { Auth, Config } from '@ssi.developer/ssi-sdk';

const config = new Config({
  clientId: 'YOUR_CLIENT_ID',
  apiKey: 'YOUR_API_KEY',
  apiSecret: 'YOUR_API_SECRET',
  privateKey: 'YOUR_PRIVATE_KEY',
});

const auth = new Auth(config);

const token = await auth.authenticate('222222');
console.log(`Access token: ${token.accessToken}`);
```

### Các method xác thực
```javascript
// Yêu cầu gửi OTP
await auth.requestOtp();

// Xác thực với OTP
const token = await auth.authenticate('222222');

// Xác thực không cần OTP (chỉ dữ liệu thị trường)
const token = await auth.authenticate();

// Làm mới token
const token = await auth.refresh();

// Đảm bảo xác thực (tự refresh nếu hết hạn)
await auth.ensureAuthenticated('222222');
```

### Approve OTP (Smart OTP push-approval)

Tài khoản đã kích hoạt Smart OTP có thể duyệt trực tiếp trên app thay vì nhập mã. Gọi `requestOtp()` để gửi yêu cầu, lấy `transactionId`, rồi truyền vào `ensureAuthenticated()` — SDK tự poll cho đến khi user bấm duyệt.
```javascript
// Bước 1: gửi yêu cầu duyệt, nhận transactionId
const otpResult = await auth.requestOtp();
const transactionId = otpResult.transactionId as string;

// Bước 2: SDK tự poll cho đến khi user bấm duyệt trên app Smart OTP
// (otp truyền undefined vì đang dùng transactionId)
const accessToken = await auth.ensureAuthenticated(undefined, transactionId);
```

Trong lúc chờ, server trả HTTP 202 + code `401114` ("Push-approval is pending") — SDK tự xử lý. Nếu hết số lần poll mà vẫn chưa duyệt, `ensureAuthenticated` reject với lỗi xác thực.

### Trạng thái token
```text
auth.getToken();   // lấy token hiện tại
auth.setToken(t);  // thiết lập token (cache)
```

## Data

Client dữ liệu thị trường. **Không cần OTP** — chỉ cần `auth.authenticate()`.
```python
import { Auth, Data, Config } from '@ssi.developer/ssi-sdk';

const auth = new Auth(config);
await auth.authenticate();

const data = new Data(auth);

const ohlc = await data.marketData.getOhlc1Minute('SSI');
const indexes = await data.marketData.getIndexes();
const info = await data.marketData.getSecuritiesInfo('SSI');
```

**Service:** `data.marketData` (`MarketDataService`) — OHLC, chỉ số, chứng khoán.

## Trading

Client giao dịch, tài khoản, và danh mục. **Cần OTP**.
```python
import { Auth, Trading, Config, OrderSide } from '@ssi.developer/ssi-sdk';

const auth = new Auth(config);
await auth.authenticate('222222');

const trading = new Trading(auth);

// Tài khoản
const accounts = await trading.account.getAccountInfo();

// Danh mục
const balance = await trading.portfolio.getEquityBalance('1234561');
const positions = await trading.portfolio.getEquityPositions('1234561');
const orders = await trading.portfolio.getTodayOrders('1234561');

// Giao dịch
const result = await trading.trading.placeLimitOrder(
  '1234561', 'SSI', OrderSide.BUY, 100, 66000,
);
```

**Services:**

  * `trading.account` (`AccountService`) — thông tin tài khoản.
  * `trading.portfolio` (`PortfolioService`) — số dư, vị thế, sổ lệnh, PPMMR.
  * `trading.trading` (`TradingService`) — đặt/sửa/huỷ lệnh, sức mua/bán, lệnh điều kiện (FCO).

## Stream

Client streaming realtime qua WebSocket. **Cần OTP**.
```python
import { Auth, Stream, Config } from '@ssi.developer/ssi-sdk';

const auth = new Auth(config);
await auth.authenticate('222222');

const stream = new Stream(auth);

// Đăng ký callback
stream.streaming.onData = (msg) => {
  console.log('[DATA]', msg);
};

stream.streaming.onTrading = (msg) => {
  console.log('[TRADING]', msg);
};

stream.streaming.onHeartbeat = (msg) => {
  console.log('[HEARTBEAT]', msg);
};

// Kết nối và subscribe
await stream.streaming.connect();

stream.streaming.subscribeSymbol(['SSI', 'HPG']);
stream.streaming.subscribeOrderStatus();

await stream.streaming.wait();
```

**Service:** `stream.streaming` (`StreamingService`) — subscribe/unsubscribe dữ liệu realtime.

**Callbacks:**

| Property | Kiểu | Mô tả |
|---|---|---|
| `onData` | `(msg: DataMessage) => void` | Nhận dữ liệu thị trường |
| `onTrading` | `(msg: TradingMessage) => void` | Nhận sự kiện giao dịch (trạng thái lệnh thường, lệnh điều kiện FCO, danh mục) |
| `onHeartbeat` | `(msg: HeartbeatMessage) => void` | Nhận heartbeat |

**Cập nhật token:**
```text
// Cập nhật token cho stream sau khi refresh
stream.updateToken();
```

## Ví dụ đầy đủ
```python
import { Auth, Data, Trading, Stream, Config, OrderSide } from '@ssi.developer/ssi-sdk';

const config = new Config({
  clientId: 'YOUR_CLIENT_ID',
  apiKey: 'YOUR_API_KEY',
  apiSecret: 'YOUR_API_SECRET',
  privateKey: 'YOUR_PRIVATE_KEY',
});

const auth = new Auth(config);
await auth.authenticate('222222');

// Dữ liệu thị trường
const data = new Data(auth);
const ohlc = await data.marketData.getOhlc1Minute('SSI');
console.log(ohlc);

// Giao dịch
const trading = new Trading(auth);
const accounts = await trading.account.getAccountInfo();
console.log(accounts);

// Streaming
const stream = new Stream(auth);

stream.streaming.onData = (msg) => {
  console.log('[DATA]', msg);
};

stream.streaming.onTrading = (msg) => {
  console.log('[TRADING]', msg);
};

await stream.streaming.connect();

stream.streaming.subscribeSymbol(['SSI', 'HPG']);
stream.streaming.subscribeOrderStatus();

await stream.streaming.wait();

stream.disconnect();
```

## Ghi chú

  * Tất cả method API đều là `async` — dùng `await` hoặc `.then()`.
  * Tất cả client dùng chung HTTP connection qua `Auth`.
  * Gọi `stream.disconnect()` để dọn dẹp tài nguyên WebSocket.
  * Lỗi thường gặp: `AuthenticationError` (xác thực), `WebSocketError` (stream), `APIError` (lỗi HTTP).
