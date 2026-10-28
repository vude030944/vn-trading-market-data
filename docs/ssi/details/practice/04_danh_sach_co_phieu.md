<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/tutorials/securities
Tieu de goc: 4. Danh sách cổ phiếu
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/tutorials/securities>

# 4\. Danh sách cổ phiếu

Lấy danh sách cổ phiếu theo sàn, chỉ số và xem thông tin chi tiết

## Mục tiêu

Tạo watchlist/screener theo tiêu chí thị trường — lấy danh sách mã cổ phiếu theo sàn (HOSE, HNX), theo chỉ số (VN30), và xem chi tiết từng mã.

## Luồng xử lý
```text
Screener → Market Data API (Securities) → Watchlist State
```

  1. Gọi `get_securities_info_by_board(Board.HOSE)` để lấy danh sách theo sàn
  2. Gọi `get_securities_info_by_index("VN30")` để lấy theo chỉ số
  3. Gọi `get_securities_info("SSI")` để xem chi tiết một mã
  4. Khi user chọn mã, chuyển sang luồng xem chi tiết/đặt lệnh

## Sample Code — Sync

python/sample_04_securities.py
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
        # Bước 1: Cổ phiếu sàn HOSE
        hose = data.market_data.get_securities_info_by_board(Board.HOSE)
        print(f"HOSE: {len(hose)} mã")
        for sec in hose[:10]:
            print(f"  {sec.symbol:<10} | {sec.symbol_name_vi or '':<30} | Lot: {sec.lot_size}")

        # Bước 2: Cổ phiếu sàn HNX
        hnx = data.market_data.get_securities_info_by_board(Board.HNX)
        print(f"HNX: {len(hnx)} mã")

        # Bước 3: Cổ phiếu thuộc VN30
        vn30 = data.market_data.get_securities_info_by_index("VN30")
        print(f"VN30: {len(vn30)} mã")
        for sec in vn30:
            print(f"  {sec.symbol:<10} | {sec.symbol_name_vi or ''}")

        # Bước 4: Chi tiết một mã
        info = data.market_data.get_securities_info("SSI")
        print(f"  Mã: {info.symbol} | Tên: {info.symbol_name_vi}")
        print(f"  Sàn: {info.board} | Lot: {info.lot_size}")
        print(f"  ICB: {info.icb_code} - {info.icb_name}")
        print(f"  Listed Shares: {info.listed_shares}")
```

## Sample Code — Async

python/sample_04_securities_async.py
```python
import asyncio
from ssi_sdk import AsyncAuth, AsyncData, Config
from ssi_sdk.enums import Board
from auth_helper import ensure_auth_async

config = Config(...)

async def main():
    async with AsyncAuth(config) as auth:
        await ensure_auth_async(auth)
        async with AsyncData(auth) as data:
            # Lấy song song HOSE + HNX
            hose_task = data.market_data.get_securities_info_by_board(Board.HOSE)
            hnx_task = data.market_data.get_securities_info_by_board(Board.HNX)
            hose, hnx = await asyncio.gather(hose_task, hnx_task)
            print(f"HOSE: {len(hose)} mã | HNX: {len(hnx)} mã")

            vn30 = await data.market_data.get_securities_info_by_index("VN30")
            info = await data.market_data.get_securities_info("SSI")

asyncio.run(main())
```

## API Methods

| Method | Mô tả |
|---|---|
| `get_securities_info_by_board(board)` | Lấy danh sách mã theo sàn |
| `get_securities_info_by_index(index)` | Lấy danh sách mã theo chỉ số |
| `get_securities_info(symbol)` | Lấy chi tiết một mã |
