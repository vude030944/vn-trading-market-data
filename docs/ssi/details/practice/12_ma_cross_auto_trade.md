<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/tutorials/ma-cross-auto-trade
Tieu de goc: 12. MA Cross Auto Trade
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/tutorials/ma-cross-auto-trade>

# 12\. MA Cross Auto Trade

Bot tự động giao dịch theo tín hiệu MA5 cắt MA10 qua WebSocket real-time

## Mục tiêu

Tự động giao dịch khi MA5 cắt MA10: kết hợp WebSocket để nhận tick real-time, tự aggregate thành nến, tính MA, đặt lệnh khi có tín hiệu và theo dõi lệnh qua stream.

## Luồng xử lý
```text
Strategy → Market Data API → Account API → Trading API → Monitor/Logger
```

  1. Seed dữ liệu lịch sử 5m để khởi tạo MA
  2. Mở WebSocket, subscribe trade stream (market data) và order stream (trading)
  3. Mỗi `TradeMessage` → cập nhật nến hiện tại (OHLCV)
  4. Khi nến đóng → tính MA5/MA10 → kiểm tra giao cắt
  5. Có tín hiệu + không có lệnh đang chờ → kiểm tra risk → đặt lệnh MARKET
  6. `OrderStatusMessage` phản hồi trạng thái lệnh real-time, không polling
  7. SDK ping keepalive định kỳ để giữ kết nối

## Kiến trúc
```text
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│ WebSocket    │────→│ BarBuilder   │────→│ MA Signal    │
│ Trade Tick   │     │ (OHLCV 5m)  │     │ Detector     │
└─────────────┘     └──────────────┘     └──────┬───────┘
                                                 │ BUY/SELL
                                                 ▼
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│ WebSocket    │←────│ Order State  │←────│ Risk Check   │
│ Order Status │     │ Manager      │     │ + Place Order│
└─────────────┘     └──────────────┘     └──────────────┘
```

## Core Components

### BarBuilder — Aggregate tick thành nến
```python
from dataclasses import dataclass
from collections import deque

@dataclass
class Bar:
    ts: int
    open: float
    high: float
    low: float
    close: float
    volume: int

class BarBuilder:
    def __init__(self, interval_seconds: int):
        self.interval = interval_seconds
        self._current: Bar | None = None
        self.closed: deque[Bar] = deque(maxlen=200)

    def seed(self, historical_bars) -> None:
        """Nạp dữ liệu lịch sử để khởi tạo MA."""
        for b in historical_bars:
            self.closed.append(
                Bar(0, b.open_price, b.high_price, b.low_price, b.close_price, b.volume)
            )

    def on_trade(self, price: float, quantity: int) -> Bar | None:
        """Trả về Bar vừa đóng nếu chuyển bucket, None nếu chưa đóng."""
        bucket = (int(time.time()) // self.interval) * self.interval
        if self._current is None or self._current.ts != bucket:
            closed = self._current
            self._current = Bar(bucket, price, price, price, price, quantity)
            if closed is not None:
                self.closed.append(closed)
                return closed
            return None
        self._current.high = max(self._current.high, price)
        self._current.low = min(self._current.low, price)
        self._current.close = price
        self._current.volume += quantity
        return None
```

### MA Signal Detector
```python
def calculate_ma(bars: list[Bar], period: int) -> float | None:
    if len(bars) < period:
        return None
    return sum(b.close for b in bars[-period:]) / period

def detect_cross(bars: list[Bar], fast: int, slow: int) -> str | None:
    if len(bars) < slow + 1:
        return None
    mf_now = calculate_ma(bars, fast)
    ms_now = calculate_ma(bars, slow)
    mf_prev = calculate_ma(bars[:-1], fast)
    ms_prev = calculate_ma(bars[:-1], slow)
    if mf_prev <= ms_prev and mf_now > ms_now:
        return "BUY"
    if mf_prev >= ms_prev and mf_now < ms_now:
        return "SELL"
    return None
```

## Sample Code — Sync

python/sample_12_ma_cross_auto_trade.py
```python
from ssi_sdk import Auth, Data, Stream, Trading, Config
from ssi_sdk.enums import OrderSide, OrderStatus
from ssi_sdk.models.streaming import TradeMessage, OrderStatusMessage
from auth_helper import ensure_auth

config = Config(
    client_id="<your_client_id>",
    api_key="<your_api_key>",
    api_secret="<your_api_secret>",
    private_key="<your_private_key>",
)

ACCOUNT_NO = "<your_account_no>"
SYMBOL = "SSI"
MA_FAST, MA_SLOW = 5, 10
QUANTITY = 100
BAR_SECONDS = 300  # Nến 5 phút

with Auth(config) as auth:
    ensure_auth(auth, otp="<your_otp>")

    # Bước 1: Seed lịch sử
    builder = BarBuilder(BAR_SECONDS)
    with Data(auth) as data:
        hist = data.market_data.get_ohlc_5minute_historical(
            symbol=SYMBOL, from_date="2026/01/01 00:00:00",
            to_date="2026/05/12 23:59:59", page=1, size=MA_SLOW + 5,
        )
        builder.seed(hist)

    state = {"active_order_id": None, "last_signal": None}

    with Trading(auth) as trading:
        # Bước 2: Callbacks
        def on_market_data(msg):
            if not isinstance(msg, TradeMessage):
                return
            closed_bar = builder.on_trade(msg.price, msg.quantity)
            if closed_bar is None:
                return
            bars = builder.snapshot()
            signal = detect_cross(bars, MA_FAST, MA_SLOW)
            if signal and state["active_order_id"] is None and state["last_signal"] != signal:
                state["last_signal"] = signal
                side = OrderSide.BUY if signal == "BUY" else OrderSide.SELL
                # Risk check + đặt lệnh
                max_bs = trading.trading.get_max_buy_sell_at_market_price(ACCOUNT_NO, SYMBOL)
                max_qty = max_bs.max_buy_quantity if signal == "BUY" else max_bs.max_sell_quantity
                if max_qty >= QUANTITY:
                    result = trading.trading.place_market_order(
                        account_no=ACCOUNT_NO, symbol=SYMBOL, side=side, quantity=QUANTITY,
                    )
                    state["active_order_id"] = getattr(result, "order_id", "pending")

        def on_trading_event(msg):
            if isinstance(msg, OrderStatusMessage) and msg.status in TERMINAL_STATUSES:
                state["active_order_id"] = None

        # Bước 3: Kết nối WebSocket
        with Stream(auth) as stream:
            stream.streaming.on_data = on_market_data
            stream.streaming.on_trading = on_trading_event
            stream.streaming.connect()
            stream.streaming.subscribe_symbol([SYMBOL])
            stream.streaming.subscribe_order_status(ACCOUNT_NO)
            stream.streaming.ping(interval=30)

            try:
                stream.streaming.wait(timeout=3600)
            except KeyboardInterrupt:
                print("Dừng bot.")
```

## Sample Code — Async

Phiên bản async tương tự nhưng sử dụng `AsyncAuth`, `AsyncData`, `AsyncStream`, `AsyncTrading` và `asyncio.Lock` thay cho `threading.Lock`. Xem file `python/sample_12_ma_cross_auto_trade_async.py` để biết chi tiết.

## Lưu ý quan trọng

  * **Đây là sample code minh họa** , không phải chiến lược giao dịch thực tế.
  * Luôn kiểm tra risk (sức mua/bán) trước khi đặt lệnh.
  * Sử dụng `ping(interval=30)` để giữ kết nối WebSocket.
  * `OrderStatusMessage` giúp theo dõi lệnh real-time mà không cần polling.
  * Tránh đặt lệnh lặp cùng chiều bằng cách lưu `last_signal`.
