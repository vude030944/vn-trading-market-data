<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/nodejs/installation-requirements
Tieu de goc: Cài đặt & Thiết lập
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/nodejs/installation-requirements>

# Cài đặt & Thiết lập

Hướng dẫn cài đặt và thiết lập Node.js SDK

## Yêu cầu môi trường

  * Node.js `>=18`
  * Truy cập mạng tới REST API và WebSocket endpoints
  * `clientId`, `apiKey`, `apiSecret` từ SSI
  * `privateKey` để ký lệnh giao dịch
  * OTP cho luồng xác thực Trading/Stream

## Cài đặt
```bash
npm install @ssi.developer/ssi-sdk
```

SDK hỗ trợ cả CommonJS và ES Module (dual CJS/ESM).

## Cấu hình

Tạo đối tượng `Config` với thông tin xác thực:
```python
import { Config } from '@ssi.developer/ssi-sdk';

const config = new Config({
  clientId: 'YOUR_CLIENT_ID',
  apiKey: 'YOUR_API_KEY',
  apiSecret: 'YOUR_API_SECRET',
  privateKey: 'YOUR_PRIVATE_KEY',
});
```

## Luồng khởi tạo
```text
Config → Auth → authenticate(otp) → Data / Trading / Stream
```

  1. Tạo `Config` với thông tin xác thực.
  2. Khởi tạo `Auth` với `new Auth(config)`.
  3. Gọi `await auth.authenticate(otp)` — bỏ trống `otp` nếu chỉ dùng dữ liệu thị trường.
  4. Khởi tạo client cần dùng (`Data`, `Trading`, `Stream`) với `auth`.
  5. Với `Stream`, gọi `await stream.streaming.connect()` trước khi subscribe.
  6. Gọi `stream.disconnect()` để dọn dẹp tài nguyên.

## Ví dụ theo trường hợp sử dụng

### Chỉ lấy dữ liệu thị trường (không cần OTP)
```python
import { Auth, Data, Config } from '@ssi.developer/ssi-sdk';

const config = new Config({
  clientId: 'YOUR_CLIENT_ID',
  apiKey: 'YOUR_API_KEY',
  apiSecret: 'YOUR_API_SECRET',
});

const auth = new Auth(config);
await auth.authenticate();

const data = new Data(auth);
const ohlc = await data.marketData.getOhlc1Minute('SSI');
```

### Giao dịch (cần OTP)
```python
import { Auth, Trading, Config, OrderSide } from '@ssi.developer/ssi-sdk';

const config = new Config({
  clientId: 'YOUR_CLIENT_ID',
  apiKey: 'YOUR_API_KEY',
  apiSecret: 'YOUR_API_SECRET',
  privateKey: 'YOUR_PRIVATE_KEY',
});

const auth = new Auth(config);
await auth.authenticate('222222');

const trading = new Trading(auth);
const accounts = await trading.account.getAccountInfo();
```

### Streaming realtime (cần OTP)
```python
import { Auth, Stream, Config } from '@ssi.developer/ssi-sdk';

const config = new Config({
  clientId: 'YOUR_CLIENT_ID',
  apiKey: 'YOUR_API_KEY',
  apiSecret: 'YOUR_API_SECRET',
  privateKey: 'YOUR_PRIVATE_KEY',
});

const auth = new Auth(config);
await auth.authenticate('222222');

const stream = new Stream(auth);

stream.streaming.onData = (msg) => {
  console.log(msg);
};

await stream.streaming.connect();
stream.streaming.subscribeSymbolTrade(['SSI']);
await stream.streaming.wait();
```

## Mẹo

  * Xác thực trước khi gọi API có bảo vệ bằng token.
  * Với streaming, gọi `connect()` sau khi xác thực thành công.
  * Dùng `logLevel: 'DEBUG'` trong `Config` để gỡ lỗi.
  * Lưu credentials (`apiKey`, `apiSecret`, `privateKey`) trong biến môi trường hoặc secret manager.
  * Gọi `stream.disconnect()` để dọn dẹp đúng cách.
