<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/tutorials/index-list
Tieu de goc: 2. Chỉ số thị trường
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/tutorials/index-list>

# 2\. Chỉ số thị trường

Hiển thị VN-Index, HNX-Index và lấy summary chi tiết cho từng chỉ số

## Mục tiêu

Hiển thị danh sách chỉ số thị trường (VN-Index, HNX-Index...) trên dashboard, lọc theo sàn và lấy summary chi tiết.

## Luồng xử lý
```text
UI Dashboard → Market Data API (Index) → Cache State
```

  1. Client gọi endpoint `get_indexes()` để lấy toàn bộ chỉ số
  2. API trả về danh sách chỉ số và dữ liệu giá hiện tại
  3. Lọc chỉ số theo sàn bằng `get_indexes_by_board(Board.HOSE)`
  4. Lấy summary chi tiết cho một chỉ số cụ thể bằng `get_index_summary("VNINDEX")`

## Sample Code — Sync

python/sample_02_index_list.py
```python
from ssi_sdk import Auth, Data, Config
from ssi_sdk.enums import Board
from auth_helper import ensure_auth

config = Config(
    client_id="<your_client_id>",
    api_key="<your_api_key>",
    api_secret="<your_api_secret>",
    private_key="<your_private_key>",
)

with Auth(config) as auth:
    ensure_auth(auth)

    with Data(auth) as data:
        # Bước 1: Lấy toàn bộ chỉ số
        all_indexes = data.market_data.get_indexes()
        print(f"Tổng số chỉ số: {len(all_indexes)}\n")
        for idx in all_indexes:
            print(f"  {idx.index:<15} | {idx.index_name:<30} | Sàn: {idx.board}")

        # Bước 2: Lọc chỉ số theo sàn HOSE
        print("\n--- Chỉ số sàn HOSE ---")
        hose_indexes = data.market_data.get_indexes_by_board(Board.HOSE)
        for idx in hose_indexes:
            print(f"  {idx.index:<15} | {idx.index_name}")

        # Bước 3: Lấy chi tiết summary cho VN-Index
        print("\n--- VN-Index Summary ---")
        summary = data.market_data.get_index_summary("VNINDEX")
        if summary:
            print(f"  Giá trị Index    : {summary.index_value}")
            print(f"  Thay đổi         : {summary.index_change} ({summary.index_change_percent}%)")
            print(f"  Tổng KL khớp     : {summary.total_match}")
            print(f"  Tổng GT khớp     : {summary.total_match_value}")
            print(f"  Tăng / Giảm / Đứng: {summary.total_advance_stock} / {summary.total_decline_stock} / {summary.total_steady_stock}")
            print(f"  Trần / Sàn       : {summary.total_ceiling_stock} / {summary.total_floor_stock}")
```

## Sample Code — Async

python/sample_02_index_list_async.py
```python
import asyncio
from ssi_sdk import AsyncAuth, AsyncData, Config
from ssi_sdk.enums import Board
from auth_helper import ensure_auth_async

config = Config(...)  # Tương tự config ở trên

async def main():
    async with AsyncAuth(config) as auth:
        await ensure_auth_async(auth)

        async with AsyncData(auth) as data:
            all_indexes = await data.market_data.get_indexes()
            print(f"Tổng số chỉ số: {len(all_indexes)}")

            hose_indexes = await data.market_data.get_indexes_by_board(Board.HOSE)
            for idx in hose_indexes:
                print(f"  {idx.index:<15} | {idx.index_name}")

            summary = await data.market_data.get_index_summary("VNINDEX")
            if summary:
                print(f"  Giá trị: {summary.index_value}")
                print(f"  Thay đổi: {summary.index_change} ({summary.index_change_percent}%)")

asyncio.run(main())
```

## API Methods

| Method | Mô tả |
|---|---|
| `get_indexes()` | Lấy toàn bộ chỉ số thị trường |
| `get_indexes_by_board(board)` | Lọc chỉ số theo sàn (HOSE, HNX, UPCOM) |
| `get_index_summary(index_code)` | Lấy summary chi tiết cho một chỉ số |
