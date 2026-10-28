<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/tutorials/ohlc
Tieu de goc: 3. Dữ liệu K-line (OHLC)
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/tutorials/ohlc>

# 3\. Dữ liệu K-line (OHLC)

Lấy dữ liệu nến cho biểu đồ và phân tích kỹ thuật

## Mục tiêu

Cung cấp dữ liệu OHLCV (Open/High/Low/Close/Volume) cho biểu đồ nến và phân tích kỹ thuật. Hỗ trợ nhiều timeframe: 1m, 5m, 15m, 1h, 1d.

## Luồng xử lý
```text
Chart/Strategy Module → Market Data API (OHLC) → Chart Engine
```

  1. Client gửi `symbol`, `interval`, `from_date`, `to_date`
  2. API trả về mảng OHLCV theo mốc thời gian
  3. Chuẩn hóa dữ liệu (time/open/high/low/close/volume)
  4. Nếu lịch sử dài thì lặp theo paging

## Sample Code — Sync

python/sample_03_ohlc.py
```python
from ssi_sdk import Auth, Data, Config
from auth_helper import ensure_auth

config = Config(
    client_id="<your_client_id>",
    api_key="<your_api_key>",
    api_secret="<your_api_secret>",
    private_key="<your_private_key>",
)

SYMBOL = "SSI"

with Auth(config) as auth:
    ensure_auth(auth)

    with Data(auth) as data:
        # Bước 1: OHLC ngày gần nhất
        print(f"--- OHLC 1 ngày ({SYMBOL}) ---")
        daily = data.market_data.get_ohlc_1day_historical(
            SYMBOL, from_date="2026/03/01 00:00:00", to_date="2026/03/27 23:59:59"
        )
        for bar in daily[:5]:
            print(
                f"  {bar.trading_date} | "
                f"O:{bar.open_price:>10} H:{bar.high_price:>10} "
                f"L:{bar.low_price:>10} C:{bar.close_price:>10} "
                f"V:{bar.volume:>12}"
            )

        # Bước 2: OHLC lịch sử với paging
        hist = data.market_data.get_ohlc_1day_historical(
            symbol=SYMBOL,
            from_date="2026/01/01 00:00:00",
            to_date="2026/03/27 23:59:59",
            page=1,
            size=20,
        )

        # Bước 3: OHLC theo timeframe khác (1h)
        hourly = data.market_data.get_ohlc_1hour(SYMBOL)
        for bar in hourly[:5]:
            print(
                f"  {bar.trading_date} | O:{bar.open_price} H:{bar.high_price} "
                f"L:{bar.low_price} C:{bar.close_price} V:{bar.volume}"
            )

        # Bước 4: Phân trang cho dữ liệu lớn (1 phút)
        page = 1
        total_bars = 0
        while True:
            bars = data.market_data.get_ohlc_1minute_historical(
                symbol=SYMBOL,
                from_date="2026/03/25 09:00:00",
                to_date="2026/03/25 15:00:00",
                page=page,
                size=100,
            )
            if not bars:
                break
            total_bars += len(bars)
            page += 1
        print(f"Tổng cộng {total_bars} nến 1 phút.")
```

## Sample Code — Async

python/sample_03_ohlc_async.py
```python
import asyncio
from ssi_sdk import AsyncAuth, AsyncData, Config
from auth_helper import ensure_auth_async

config = Config(...)  # Tương tự config ở trên

SYMBOL = "SSI"

async def main():
    async with AsyncAuth(config) as auth:
        await ensure_auth_async(auth)
        async with AsyncData(auth) as data:
            daily = await data.market_data.get_ohlc_1day_historical(
                SYMBOL, from_date="2026/03/01 00:00:00", to_date="2026/03/27 23:59:59"
            )
            for bar in daily[:5]:
                print(f"  {bar.trading_date} | C:{bar.close_price} V:{bar.volume}")

            hourly = await data.market_data.get_ohlc_1hour(SYMBOL)

asyncio.run(main())
```

## API Methods

| Method | Timeframe | Mô tả |
|---|---|---|
| `get_ohlc_1day_historical(symbol, from_date, to_date)` | 1 ngày | Nến ngày lịch sử |
| `get_ohlc_1hour(symbol)` | 1 giờ | Nến 1 giờ gần nhất |
| `get_ohlc_1minute_historical(symbol, from_date, to_date, page, size)` | 1 phút | Nến phút lịch sử (có paging) |
| `get_ohlc_5minute_historical(...)` | 5 phút | Nến 5 phút lịch sử |
| `get_ohlc_15minute_historical(...)` | 15 phút | Nến 15 phút lịch sử |
