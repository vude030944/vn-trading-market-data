<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/tutorials/fco-order
Tieu de goc: 13. Lệnh điều kiện (FCO)
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/tutorials/fco-order>

# 13\. Lệnh điều kiện (FCO)

Đặt và quản lý các loại lệnh điều kiện linh hoạt (Flexible Conditional Order)

## Mục tiêu

Đặt và quản lý toàn bộ các loại lệnh điều kiện FCO (Flexible Conditional Order): GTD, Stop, Stop Limit, Trailing Stop, Trailing Stop Limit, OCO, Bull Bear — cùng với truy vấn danh sách và hủy lệnh FCO.

## Luồng xử lý
```text
Xác thực (OTP) → Trading API (Place FCO) → Chờ kích hoạt (WAIT) → Đẩy lệnh gốc khi đủ điều kiện
```

  1. Xác thực với OTP qua `Auth` / `Trading`.
  2. Gọi method `place_fco_*` tương ứng với loại lệnh điều kiện cần đặt.
  3. Lệnh được lưu ở trạng thái chờ (`FCOStatus.WAIT`) cho đến khi điều kiện kích hoạt được thoả.
  4. Khi giá thị trường chạm ngưỡng kích hoạt, hệ thống tự động đẩy lệnh gốc (LO/MTL/MP...) vào sổ lệnh.
  5. Truy vấn danh sách/chi tiết bằng `get_fco_by_*`, hoặc hủy bằng `cancel_fco` khi lệnh chưa kích hoạt.

## Các loại lệnh điều kiện

| Loại | Method | Mô tả |
|---|---|---|
| GTD | `place_fco_gtd` | Lệnh có hiệu lực đến ngày (Good-Till-Date) |
| Stop | `place_fco_stop` | Kích hoạt lệnh thị trường khi giá chạm ngưỡng (Stop Market) |
| Stop Limit | `place_fco_stop_limit` | Kích hoạt lệnh giới hạn khi giá chạm ngưỡng (Stop Limit) |
| Trailing Stop | `place_fco_trailing_stop` | Bám sát xu hướng giá theo khoảng cách cố định (Trailing Amount) |
| Trailing Stop Limit | `place_fco_trailing_stop_limit` | Trailing Stop nhưng đẩy lệnh giới hạn khi kích hoạt |
| OCO | `place_fco_oco` | Đặt đồng thời chốt lời (TP) và cắt lỗ (SL) — khớp 1 lệnh sẽ hủy lệnh còn lại |
| Bull Bear | `place_fco_bull_bear` | Kết hợp lệnh vào lệnh với TP/SL đi kèm |

> Xem đầy đủ enum `FCOType`, `FCOOperator`, `FCOStatus` và tham số chi tiết tại trang [Enums SDK Python](/docs/sdk/python/transport-classes).

## Sample Code — Sync

python/sample_13_fco_order.py
```python
from ssi_sdk import Auth, Trading, Config
from ssi_sdk.enums import FCOOperator, OrderSide
from auth_helper import ensure_auth

config = Config(
    client_id="<your_client_id>",
    api_key="<your_api_key>",
    api_secret="<your_api_secret>",
    private_key="<your_private_key>",
)
ACCOUNT_NO = "<your_account_no>"
symbol = "SSI"
from_date = "2026/08/01 00:00:00"
to_date = "2026/08/30 23:59:59"

with Auth(config) as auth:
    ensure_auth(auth, otp="<your_otp>")

    with Trading(auth) as trading:
        # 1. Lệnh GTD (Good-Till-Date)
        gtd_res = trading.trading.place_fco_gtd(
            account_no=ACCOUNT_NO, symbol=symbol, side=OrderSide.BUY,
            quantity=100, price=26000, price_slip=0,
            from_date=from_date, to_date=to_date,
        )
        print(f"  GTD: {gtd_res}")

        # 2. Lệnh Stop (dừng thị trường)
        stop_res = trading.trading.place_fco_stop(
            account_no=ACCOUNT_NO, symbol=symbol, side=OrderSide.BUY,
            quantity=100, stop_price=27000,
            operator=FCOOperator.GREATER_OR_EQUAL,
            from_date=from_date, to_date=to_date,
        )
        print(f"  Stop: {stop_res}")

        # 3. Lệnh Stop Limit
        stop_limit_res = trading.trading.place_fco_stop_limit(
            account_no=ACCOUNT_NO, symbol=symbol, side=OrderSide.BUY,
            quantity=100, price=27500, price_slip=0, stop_price=27000,
            operator=FCOOperator.GREATER_OR_EQUAL,
            from_date=from_date, to_date=to_date,
        )
        print(f"  Stop Limit: {stop_limit_res}")

        # 4. Lệnh Trailing Stop
        trailing_res = trading.trading.place_fco_trailing_stop(
            account_no=ACCOUNT_NO, symbol=symbol, side=OrderSide.SELL,
            quantity=100, active_price=28000, trailing_amount=1000,
            from_date=from_date, to_date=to_date,
        )
        print(f"  Trailing Stop: {trailing_res}")

        # 5. Lệnh Trailing Stop Limit
        trailing_limit_res = trading.trading.place_fco_trailing_stop_limit(
            account_no=ACCOUNT_NO, symbol=symbol, side=OrderSide.SELL,
            quantity=100, active_price=28000, trailing_amount=1000,
            price_slip=500, from_date=from_date, to_date=to_date,
        )
        print(f"  Trailing Stop Limit: {trailing_limit_res}")

        # 6. Lệnh OCO (One-Cancels-the-Other)
        oco_res = trading.trading.place_fco_oco(
            account_no=ACCOUNT_NO, symbol=symbol, side=OrderSide.SELL,
            quantity=100, tp_active_price=30000, sl_active_price=24000,
            tp_price=30000, sl_price=24000, tp_slip=0, sl_slip=0,
            from_date=from_date, to_date=to_date,
        )
        print(f"  OCO: {oco_res}")

        # 7. Lệnh Bull Bear
        bb_res = trading.trading.place_fco_bull_bear(
            account_no=ACCOUNT_NO, symbol=symbol, side=OrderSide.BUY,
            quantity=100, price=26000, price_slip=0,
            tp_active_price=30000, sl_active_price=24000,
            tp_price=30000, sl_price=24000, tp_slip=0, sl_slip=0,
            from_date=from_date, to_date=to_date,
        )
        print(f"  Bull Bear: {bb_res}")

        # 8. Truy vấn danh sách lệnh FCO
        fco_list = trading.trading.get_fco_by_account_no(ACCOUNT_NO, page_index=1, page_size=10)
        print(f"  Tổng số lệnh FCO: {fco_list.items_count}")
        for item in fco_list.fco_list[:5]:
            print(f"  {item.fco_id} | {item.symbol} | {item.type} | {item.status}")

        # 9. Hủy lệnh FCO vừa tạo (nếu còn ở trạng thái WAIT)
        if getattr(gtd_res, "fco_id", None):
            cancel_res = trading.trading.cancel_fco(gtd_res.fco_id)
            print(f"  Hủy FCO: {cancel_res}")
```

## Sample Code — Async

python/sample_13_fco_order_async.py
```python
import asyncio
from ssi_sdk import AsyncAuth, AsyncTrading, Config
from ssi_sdk.enums import FCOOperator, OrderSide
from auth_helper import ensure_auth_async

config = Config(...)
ACCOUNT_NO = "<your_account_no>"
symbol = "SSI"
from_date = "2026/08/01 00:00:00"
to_date = "2026/08/30 23:59:59"

async def main():
    async with AsyncAuth(config) as auth:
        await ensure_auth_async(auth, otp="<your_otp>")

        async with AsyncTrading(auth) as trading:
            gtd_res = await trading.trading.place_fco_gtd(
                account_no=ACCOUNT_NO, symbol=symbol, side=OrderSide.BUY,
                quantity=100, price=26000, price_slip=0,
                from_date=from_date, to_date=to_date,
            )
            print(f"  GTD: {gtd_res}")

            stop_res = await trading.trading.place_fco_stop(
                account_no=ACCOUNT_NO, symbol=symbol, side=OrderSide.BUY,
                quantity=100, stop_price=27000,
                operator=FCOOperator.GREATER_OR_EQUAL,
                from_date=from_date, to_date=to_date,
            )
            print(f"  Stop: {stop_res}")

            oco_res = await trading.trading.place_fco_oco(
                account_no=ACCOUNT_NO, symbol=symbol, side=OrderSide.SELL,
                quantity=100, tp_active_price=30000, sl_active_price=24000,
                tp_price=30000, sl_price=24000, tp_slip=0, sl_slip=0,
                from_date=from_date, to_date=to_date,
            )
            print(f"  OCO: {oco_res}")

            fco_list = await trading.trading.get_fco_by_account_no(ACCOUNT_NO, page_index=1, page_size=10)
            print(f"  Tổng số lệnh FCO: {fco_list.items_count}")

            if getattr(gtd_res, "fco_id", None):
                cancel_res = await trading.trading.cancel_fco(gtd_res.fco_id)
                print(f"  Hủy FCO: {cancel_res}")

asyncio.run(main())
```

## Lưu ý

  * Lệnh FCO không đẩy vào sổ lệnh ngay — chỉ khi điều kiện kích hoạt được thoả, hệ thống mới tạo lệnh gốc thật sự (kiểm tra sức mua/bán tại thời điểm đó).
  * Chỉ có thể hủy (`cancel_fco`) khi lệnh còn ở trạng thái chờ (`INIT`/`WAIT`), chưa kích hoạt (`TRI`/`TRIT`).
  * Tham số `price` của GTD/Bull Bear có thể truyền `OrderType.MTL`/`OrderType.MP` để khớp theo giá thị trường ngay khi kích hoạt, thay vì một mức giá cố định.
  * `operator` (`FCOOperator`) xác định điều kiện so sánh để kích hoạt Stop/Stop Limit — ví dụ `GREATER_OR_EQUAL` khi đặt lệnh mua chờ giá tăng lên ngưỡng.
  * Với OCO/Bull Bear, khi một nhánh (TP hoặc SL) khớp thì nhánh còn lại tự động bị hủy.
  * Theo dõi cập nhật trạng thái FCO theo thời gian thực qua `FCOOrderUpdateMessage` trong [WebSocket Trading](/docs/tutorials/websocket-trading).
