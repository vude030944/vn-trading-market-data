<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/tutorials/cancel-order
Tieu de goc: 9. Hủy lệnh
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/tutorials/cancel-order>

# 9\. Hủy lệnh

Hủy lệnh đang mở chưa khớp hoặc khớp một phần

## Mục tiêu

Hủy phần khối lượng chưa khớp của lệnh đang mở (PENDING, PARTIALLY_FILLED).

## Luồng xử lý
```text
Open Orders → Trading API (Cancel Order) → Order Book State
```

  1. Lấy sổ lệnh, lọc lệnh có trạng thái có thể hủy
  2. Gọi `cancel_order_by_order_id(account_no, order_id)`
  3. API xác thực quyền và trạng thái lệnh
  4. Nếu hợp lệ, hệ thống cập nhật `CANCELLED` cho phần chưa khớp
  5. Xác nhận trạng thái và cập nhật số dư

## Trạng thái có thể hủy
```python
from ssi_sdk.enums import OrderStatus

CANCELLABLE_STATUSES = {
    OrderStatus.PENDING_APPROVAL,
    OrderStatus.READY,
    OrderStatus.SENT,
    OrderStatus.QUEUED,
    OrderStatus.PARTIAL_FILLED,
}
```

## Sample Code — Sync

python/sample_09_cancel_order.py
```python
from ssi_sdk import Auth, Trading, Config
from ssi_sdk.enums import OrderStatus
from auth_helper import ensure_auth

config = Config(
    client_id="<your_client_id>",
    api_key="<your_api_key>",
    api_secret="<your_api_secret>",
    private_key="<your_private_key>",
)
ACCOUNT_NO = "<your_account_no>"
CANCELLABLE_STATUSES = {
    OrderStatus.PENDING_APPROVAL, OrderStatus.READY,
    OrderStatus.SENT, OrderStatus.QUEUED, OrderStatus.PARTIAL_FILLED,
}

with Auth(config) as auth:
    ensure_auth(auth, otp="<your_otp>")

    with Trading(auth) as trading:
        # Bước 1: Tìm lệnh đang mở
        orders = trading.portfolio.get_today_orders(ACCOUNT_NO)
        open_orders = [o for o in orders if o.status in CANCELLABLE_STATUSES]
        print(f"Tổng lệnh: {len(orders)} | Đang mở: {len(open_orders)}")

        if open_orders:
            # Bước 2: Hủy lệnh đầu tiên
            target = open_orders[0]
            print(f"  Hủy lệnh: {target.order_id}")
            result = trading.trading.cancel_order_by_order_id(
                account_no=ACCOUNT_NO,
                order_id=target.order_id,
            )
            print(f"  Kết quả: {result}")

            # Bước 3: Xác nhận trạng thái
            orders_after = trading.portfolio.get_today_orders(ACCOUNT_NO)
            for order in orders_after:
                if order.order_id == target.order_id:
                    print(f"  Status: {order.status.value} | Đã hủy: {order.cancel_quantity}")

        # Bước 4: Cập nhật số dư
        balance = trading.portfolio.get_equity_balance(ACCOUNT_NO)
        print(f"  Tiền mặt khả dụng: {balance.account_balance:,.0f}")
```

## Sample Code — Async

python/sample_09_cancel_order_async.py
```python
import asyncio
from ssi_sdk import AsyncAuth, AsyncTrading, Config
from ssi_sdk.enums import OrderStatus
from auth_helper import ensure_auth_async

config = Config(...)
ACCOUNT_NO = "<your_account_no>"
CANCELLABLE_STATUSES = {
    OrderStatus.PENDING_APPROVAL, OrderStatus.READY,
    OrderStatus.SENT, OrderStatus.QUEUED, OrderStatus.PARTIAL_FILLED,
}

async def main():
    async with AsyncAuth(config) as auth:
        await ensure_auth_async(auth, otp="<your_otp>")
        async with AsyncTrading(auth) as trading:
            orders = await trading.portfolio.get_today_orders(ACCOUNT_NO)
            open_orders = [o for o in orders if o.status in CANCELLABLE_STATUSES]

            if open_orders:
                # Hủy tất cả lệnh đang mở (song song)
                cancel_tasks = [
                    trading.trading.cancel_order_by_order_id(
                        account_no=ACCOUNT_NO, order_id=o.order_id,
                    )
                    for o in open_orders
                ]
                results = await asyncio.gather(*cancel_tasks, return_exceptions=True)
                for order, result in zip(open_orders, results):
                    status = "LỖI" if isinstance(result, Exception) else "OK"
                    print(f"  {order.order_id}: {status}")

asyncio.run(main())
```

## Lưu ý

  * Chỉ có thể hủy lệnh ở trạng thái `PENDING_APPROVAL`, `READY`, `SENT`, `QUEUED`, `PARTIAL_FILLED`.
  * Phiên bản async có thể hủy **nhiều lệnh song song** bằng `asyncio.gather`.
  * Sau khi hủy, số dư tiền mặt sẽ được giải phóng lại.
