<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/tutorials/market-order
Tieu de goc: 7. Đặt lệnh Market
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/tutorials/market-order>

# 7\. Đặt lệnh Market

Khớp lệnh nhanh theo giá thị trường hiện tại (MP)

## Mục tiêu

Đặt lệnh market để khớp nhanh theo giá thị trường hiện tại, không cần chỉ định giá.

## Luồng xử lý
```text
Quick Trade → Trading Matching Engine (qua API) → Portfolio
```

  1. Kiểm tra sức mua/bán ở giá thị trường bằng `get_max_buy_sell_at_market_price`
  2. Gọi `place_market_order(account_no, symbol, side, quantity)` — không truyền price
  3. Hệ thống match theo thanh khoản thị trường tại thời điểm gửi
  4. Kiểm tra trạng thái lệnh và cập nhật số dư

## Sample Code — Sync

python/sample_07_market_order.py
```python
from ssi_sdk import Auth, Trading, Config
from ssi_sdk.enums import OrderSide
from auth_helper import ensure_auth

config = Config(
    client_id="<your_client_id>",
    api_key="<your_api_key>",
    api_secret="<your_api_secret>",
    private_key="<your_private_key>",
)
ACCOUNT_NO = "<your_account_no>"

with Auth(config) as auth:
    ensure_auth(auth, otp="<your_otp>")

    with Trading(auth) as trading:
        # Bước 1: Kiểm tra sức mua ở giá thị trường
        max_bs = trading.trading.get_max_buy_sell_at_market_price(ACCOUNT_NO, "SSI")
        print(f"Max mua (market): {max_bs.max_buy_quantity} CP")
        print(f"Max bán (market): {max_bs.max_sell_quantity} CP")

        # Bước 2: Đặt lệnh Market mua
        result = trading.trading.place_market_order(
            account_no=ACCOUNT_NO,
            symbol="SSI",
            side=OrderSide.BUY,
            quantity=100,
        )
        print(f"  Kết quả: {result}")

        # Bước 3: Kiểm tra trạng thái lệnh
        orders = trading.portfolio.get_today_orders(ACCOUNT_NO)
        for order in orders[-3:]:
            print(
                f"  {order.order_id} | {order.symbol} {order.side.value} "
                f"| Khớp: {order.filled_quantity} | Status: {order.status.value}"
            )

        # Bước 4: Cập nhật số dư sau giao dịch
        balance = trading.portfolio.get_equity_balance(ACCOUNT_NO)
        print(f"  Tiền mặt khả dụng: {balance.account_balance:,.0f}")
```

## Sample Code — Async

python/sample_07_market_order_async.py
```python
import asyncio
from ssi_sdk import AsyncAuth, AsyncTrading, Config
from ssi_sdk.enums import OrderSide
from auth_helper import ensure_auth_async

config = Config(...)
ACCOUNT_NO = "<your_account_no>"

async def main():
    async with AsyncAuth(config) as auth:
        await ensure_auth_async(auth, otp="<your_otp>")
        async with AsyncTrading(auth) as trading:
            result = await trading.trading.place_market_order(
                account_no=ACCOUNT_NO, symbol="SSI",
                side=OrderSide.BUY, quantity=100,
            )

            # Lấy song song trạng thái + số dư + vị thế
            orders, balance, positions = await asyncio.gather(
                trading.portfolio.get_today_orders(ACCOUNT_NO),
                trading.portfolio.get_equity_balance(ACCOUNT_NO),
                trading.portfolio.get_equity_positions(ACCOUNT_NO),
            )

asyncio.run(main())
```

## So sánh Limit vs Market

|  | Limit Order | Market Order |
|---|---|---|
| Giá | Chỉ định giá cụ thể | Giá thị trường hiện tại |
| Tốc độ khớp | Chờ đến khi có thanh khoản | Khớp ngay nếu có thanh khoản |
| Rủi ro | Có thể không khớp | Có thể khớp ở giá bất lợi |
| Phương thức | `place_limit_order(price=...)` | `place_market_order()` |
