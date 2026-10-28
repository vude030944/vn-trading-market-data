<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/tutorials/order-status
Tieu de goc: 8. Trạng thái lệnh
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/tutorials/order-status>

# 8\. Trạng thái lệnh

Theo dõi tiến trình khớp lệnh bằng cơ chế polling

## Mục tiêu

Theo dõi tiến trình khớp của một lệnh cụ thể bằng cách polling sổ lệnh theo chu kỳ.

## Luồng xử lý
```text
Order Monitor Service → Trading API (Order Detail) → Execution
```

  1. Đặt lệnh và lưu `orderId`
  2. Polling `get_today_orders` theo chu kỳ ngắn (3 giây)
  3. Kiểm tra trạng thái: `FILLED`, `CANCELLED`, `REJECTED`, `EXPIRED`
  4. Nếu chưa hoàn tất → tiếp tục polling
  5. Khi đạt trạng thái kết thúc → đóng vòng theo dõi

## Trạng thái lệnh

| Status | Ý nghĩa |
|---|---|
| `PENDING_APPROVAL` | Chờ duyệt |
| `READY` / `SENT` / `QUEUED` | Đang chờ khớp |
| `PARTIAL_FILLED` | Khớp một phần |
| `FILLED` | Khớp toàn bộ |
| `CANCELLED` | Đã hủy |
| `REJECTED` | Bị từ chối |
| `EXPIRED` | Hết hạn |

## Sample Code — Sync

python/sample_08_order_status.py
```python
import time
from ssi_sdk import Auth, Trading, Config
from ssi_sdk.enums import OrderSide, OrderStatus
from auth_helper import ensure_auth

config = Config(
    client_id="<your_client_id>",
    api_key="<your_api_key>",
    api_secret="<your_api_secret>",
    private_key="<your_private_key>",
)
ACCOUNT_NO = "<your_account_no>"

TERMINAL_STATUSES = {
    OrderStatus.FILLED, OrderStatus.CANCELLED,
    OrderStatus.REJECTED, OrderStatus.EXPIRED,
    OrderStatus.PARTIAL_CANCELLED,
}

with Auth(config) as auth:
    ensure_auth(auth, otp="<your_otp>")

    with Trading(auth) as trading:
        # Bước 1: Đặt lệnh
        result = trading.trading.place_limit_order(
            account_no=ACCOUNT_NO, symbol="SSI",
            side=OrderSide.BUY, quantity=100, price=26000,
        )
        print(f"  Kết quả: {result}")

        # Bước 2-5: Polling trạng thái
        max_polls = 10
        poll_interval = 3  # giây

        for i in range(1, max_polls + 1):
            orders = trading.portfolio.get_today_orders(ACCOUNT_NO)
            if not orders:
                time.sleep(poll_interval)
                continue

            latest = orders[-1]
            remaining = latest.quantity - latest.filled_quantity - latest.cancel_quantity
            print(
                f"  Poll {i}: OrderID={latest.order_id} | "
                f"Status={latest.status.value} | "
                f"Khớp={latest.filled_quantity}/{latest.quantity} | Còn={remaining}"
            )

            if latest.status in TERMINAL_STATUSES:
                print(f"  → Lệnh kết thúc: {latest.status.value}")
                if latest.filled_quantity > 0:
                    print(f"  Đã khớp: {latest.filled_quantity} CP @ {latest.avg_price:,.0f}")
                break

            time.sleep(poll_interval)
        else:
            print(f"  Hết {max_polls} lần poll, lệnh vẫn đang mở.")
```

## Sample Code — Async

python/sample_08_order_status_async.py
```python
import asyncio
from ssi_sdk import AsyncAuth, AsyncTrading, Config
from ssi_sdk.enums import OrderSide, OrderStatus
from auth_helper import ensure_auth_async

config = Config(...)
ACCOUNT_NO = "<your_account_no>"
TERMINAL_STATUSES = {
    OrderStatus.FILLED, OrderStatus.CANCELLED,
    OrderStatus.REJECTED, OrderStatus.EXPIRED,
    OrderStatus.PARTIAL_CANCELLED,
}

async def main():
    async with AsyncAuth(config) as auth:
        await ensure_auth_async(auth, otp="<your_otp>")
        async with AsyncTrading(auth) as trading:
            result = await trading.trading.place_limit_order(
                account_no=ACCOUNT_NO, symbol="SSI",
                side=OrderSide.BUY, quantity=100, price=26000,
            )

            for i in range(1, 11):
                orders = await trading.portfolio.get_today_orders(ACCOUNT_NO)
                if orders and orders[-1].status in TERMINAL_STATUSES:
                    print(f"  Lệnh kết thúc: {orders[-1].status.value}")
                    break
                await asyncio.sleep(3)

asyncio.run(main())
```

## Lưu ý

  * Polling phù hợp cho kiểm tra nhanh. Cho real-time, dùng [WebSocket Trading](/docs/tutorials/websocket-trading).
  * Giới hạn số lần poll và thêm timeout để tránh vòng lặp vô hạn.
