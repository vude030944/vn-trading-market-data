<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/tutorials/limit-order
Tieu de goc: 6. Đặt lệnh Limit
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/tutorials/limit-order>

# 6\. Đặt lệnh Limit

Đặt lệnh mua/bán tại mức giá chỉ định (LO)

## Mục tiêu

Đặt lệnh mua/bán cổ phiếu tại mức giá chỉ định. SDK tự gắn Idempotency-Key để chống submit trùng và ký RSA cho request.

## Luồng xử lý
```text
Order → Trading API (Create Order) → Order Tracking
```

  1. Kiểm tra sức mua trước khi đặt lệnh
  2. Gọi `place_limit_order(account_no, symbol, side, quantity, price)`
  3. SDK tự gắn `clientRequestId` (Idempotency-Key) và ký RSA
  4. API trả về kết quả và trạng thái ban đầu
  5. Kiểm tra sổ lệnh bằng `get_today_orders`

## Sample Code — Sync

python/sample_06_limit_order.py
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
        # Bước 1: Kiểm tra sức mua
        max_bs = trading.trading.get_max_buy_sell(ACCOUNT_NO, "SSI", 26000)
        print(f"Sức mua tối đa SSI @ 26,000: {max_bs.max_buy_quantity} CP")

        if max_bs.max_buy_quantity < 100:
            print("Không đủ sức mua, dừng lại.")
        else:
            # Bước 2: Đặt lệnh Limit mua
            result = trading.trading.place_limit_order(
                account_no=ACCOUNT_NO,
                symbol="SSI",
                side=OrderSide.BUY,
                quantity=100,
                price=26000,
            )
            print(f"  Kết quả mua: {result}")

            # Bước 3: Đặt lệnh Limit bán
            result = trading.trading.place_limit_order(
                account_no=ACCOUNT_NO,
                symbol="SSI",
                side=OrderSide.SELL,
                quantity=100,
                price=27000,
            )
            print(f"  Kết quả bán: {result}")

            # Bước 4: Kiểm tra sổ lệnh
            orders = trading.portfolio.get_today_orders(ACCOUNT_NO)
            for order in orders[-5:]:
                print(
                    f"  {order.order_id} | {order.symbol} {order.side.value} "
                    f"{order.order_type.value} | SL: {order.quantity} @ {order.price} "
                    f"| Status: {order.status.value}"
                )
```

## Sample Code — Async

python/sample_06_limit_order_async.py
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
            max_bs = await trading.trading.get_max_buy_sell(ACCOUNT_NO, "SSI", 26000)

            if max_bs.max_buy_quantity >= 100:
                # Đặt song song lệnh mua + bán
                buy_task = trading.trading.place_limit_order(
                    account_no=ACCOUNT_NO, symbol="SSI",
                    side=OrderSide.BUY, quantity=100, price=26000,
                )
                sell_task = trading.trading.place_limit_order(
                    account_no=ACCOUNT_NO, symbol="SSI",
                    side=OrderSide.SELL, quantity=100, price=27000,
                )
                buy_result, sell_result = await asyncio.gather(buy_task, sell_task)
                print(f"  Mua: {buy_result} | Bán: {sell_result}")

asyncio.run(main())
```

## Lưu ý

  * SDK tự động tạo **Idempotency-Key** (`clientRequestId`) để chống gửi trùng lệnh.
  * Request được **ký RSA** bằng private key trong config.
  * Luôn kiểm tra sức mua trước khi đặt lệnh.
