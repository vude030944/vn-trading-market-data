<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/sdk/nodejs/overview
Tieu de goc: Tổng quan
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/sdk/nodejs/overview>

# Tổng quan

Tổng quan về SSI FastConnect Node.js SDK — REST API và WebSocket streaming

Node.js SDK cho nền tảng giao dịch chứng khoán SSI. Hỗ trợ REST API và WebSocket streaming.

**Yêu cầu:** Node.js 18+

**Mã nguồn:** [github.com/SSI-Securities-Inc/ssi-sdk-node](https://github.com/SSI-Securities-Inc/ssi-sdk-node)

## Cài đặt
```bash
npm install @ssi.developer/ssi-sdk
```

## Kiến trúc Client

SDK sử dụng kiến trúc **modular** với 4 client chuyên biệt:

| Client | Mô tả | Yêu cầu |
|---|---|---|
| `Auth` | Xác thực & quản lý token | `Config` |
| `Data` | Dữ liệu thị trường (OHLC, chỉ số, chứng khoán) | `Auth` (không cần OTP) |
| `Trading` | Giao dịch + danh mục + tài khoản | `Auth` (cần OTP) |
| `Stream` | Streaming realtime qua WebSocket | `Auth` (cần OTP) |

**Luồng khởi tạo:**
```text
Config → Auth → authenticate(otp) → Data / Trading / Stream
```

`Auth` là client gốc — quản lý REST client và token. `Data`, `Trading`, và `Stream` đều nhận `Auth` làm tham số và dùng chung HTTP connection. Tất cả method API đều là `async` và trả về `Promise`.

**Service của mỗi client:**

| Client | Service | Truy cập | Mô tả |
|---|---|---|---|
| `Auth` | `TokenManager` | `auth` (trực tiếp) | Xác thực, OTP, làm mới token |
| `Data` | `MarketDataService` | `data.marketData` | OHLC, chỉ số, chứng khoán |
| `Trading` | `TradingService` | `trading.trading` | Đặt/sửa/huỷ lệnh, sức mua/bán, lệnh điều kiện (FCO) |
| `Trading` | `AccountService` | `trading.account` | Thông tin tài khoản |
| `Trading` | `PortfolioService` | `trading.portfolio` | Số dư, vị thế, sổ lệnh, PPMMR |
| `Stream` | `StreamingService` | `stream.streaming` | Subscribe/unsubscribe dữ liệu realtime |

## Bắt đầu nhanh

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
console.log(ohlc);
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
console.log(accounts);

const result = await trading.trading.placeLimitOrder(
  '1234561', 'SSI', OrderSide.BUY, 100, 66000,
);
console.log(result);
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
  console.log('[DATA]', msg);
};

await stream.streaming.connect();
stream.streaming.subscribeSymbolTrade(['SSI']);
await stream.streaming.wait();
```

## Trường hợp sử dụng

| Trường hợp | Client | Xác thực |
|---|---|---|
| Dữ liệu thị trường (OHLC, chỉ số, chứng khoán) | `Data` | Không cần OTP |
| Đặt/sửa/huỷ lệnh, tài khoản, danh mục | `Trading` | Cần OTP |
| Streaming WebSocket realtime | `Stream` | Cần OTP |

## Điều hướng tài liệu

  * **Cài đặt & Cấu hình**: môi trường, packages, `Config`.
  * **Client Classes** : `Auth`, `Data`, `Trading`, `Stream` — khởi tạo và sử dụng.
  * **API Services** : chi tiết các method API.
  * **Cấu hình** : tham chiếu đầy đủ `Config`.
  * **Xử lý lỗi** : các loại error và cách xử lý.
  * **Enums** : hằng số như `OrderSide`, `OrderType`, `Board`, ...
  * **Models** : các interface TypeScript và message streaming.
