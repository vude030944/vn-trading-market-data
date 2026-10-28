<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/tutorials/balance
Tieu de goc: 5. Số dư tài khoản
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/tutorials/balance>

# 5\. Số dư tài khoản

Kiểm tra khả năng giao dịch, sức mua và vị thế trước khi đặt lệnh

## Mục tiêu

Kiểm tra số dư, sức mua tối đa, vị thế cổ phiếu trước khi đặt lệnh. Chặn đặt lệnh nếu không đủ điều kiện.

## Luồng xử lý
```text
Trading Service → Account API → Validation Rule Engine
```

  1. Gọi `get_account_info()` lấy danh sách tài khoản
  2. Gọi `get_equity_balance(account_no)` lấy số dư
  3. Gọi `get_max_buy_sell(account_no, symbol, price)` kiểm tra sức mua
  4. Nếu không đủ điều kiện → chặn, đủ → cho phép đặt lệnh
  5. Gọi `get_equity_positions(account_no)` xem vị thế hiện có

## Sample Code — Sync

python/sample_05_balance.py
```python
from ssi_sdk import Auth, Trading, Config
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
        # Bước 1: Danh sách tài khoản
        accounts = trading.account.get_account_info()
        for acc in accounts:
            print(f"  - {acc.account_no} ({acc.account_type.value})")

        # Bước 2: Số dư Equity
        balance = trading.portfolio.get_equity_balance(ACCOUNT_NO)
        print(f"  Tiền mặt khả dụng: {balance.account_balance:>15,.0f}")
        print(f"  Tổng nợ          : {balance.total_debt:>15,.0f}")
        print(f"  Mua T0/T1/T2     : {balance.buy_t0:,.0f} / {balance.buy_t1:,.0f} / {balance.buy_t2:,.0f}")

        # Bước 3: Sức mua tối đa
        max_bs = trading.trading.get_max_buy_sell(ACCOUNT_NO, "SSI", 26000)
        print(f"  Max mua : {max_bs.max_buy_quantity} cổ phiếu")
        print(f"  Max bán : {max_bs.max_sell_quantity} cổ phiếu")
        print(f"  Sức mua : {max_bs.purchase_power:,.0f}")

        # Bước 4: Kiểm tra trước khi đặt lệnh
        desired_quantity = 100
        desired_price = 26000
        required = desired_quantity * desired_price
        if balance.account_balance >= required:
            print(f"  ✓ Đủ điều kiện: cần {required:,.0f}, có {balance.account_balance:,.0f}")
        else:
            print(f"  ✗ Không đủ: cần {required:,.0f}, chỉ có {balance.account_balance:,.0f}")

        # Bước 5: Vị thế hiện có
        positions = trading.portfolio.get_equity_positions(ACCOUNT_NO)
        for pos in positions:
            print(f"  {pos.symbol:<10} | SL: {pos.quantity} | Bán được: {pos.sellable_quantity}")
```

## Sample Code — Async

python/sample_05_balance_async.py
```python
import asyncio
from ssi_sdk import AsyncAuth, AsyncTrading, Config
from auth_helper import ensure_auth_async

config = Config(...)
ACCOUNT_NO = "<your_account_no>"

async def main():
    async with AsyncAuth(config) as auth:
        await ensure_auth_async(auth, otp="<your_otp>")
        async with AsyncTrading(auth) as trading:
            # Lấy song song số dư + sức mua + vị thế
            balance, max_bs, positions = await asyncio.gather(
                trading.portfolio.get_equity_balance(ACCOUNT_NO),
                trading.trading.get_max_buy_sell(ACCOUNT_NO, "SSI", 26000),
                trading.portfolio.get_equity_positions(ACCOUNT_NO),
            )
            print(f"  Tiền mặt: {balance.account_balance:,.0f}")
            print(f"  Max mua: {max_bs.max_buy_quantity} CP")

asyncio.run(main())
```

## Lưu ý

  * Endpoint Trading API **cần OTP** khi authenticate.
  * Luôn kiểm tra `account_balance` hoặc `max_buy_quantity` trước khi đặt lệnh.
  * Phiên bản async có thể lấy song song nhiều thông tin bằng `asyncio.gather`.
