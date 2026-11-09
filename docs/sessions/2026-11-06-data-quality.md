# Phien 2026-11-06 — Data quality & diem dac biet (SSI / DNSE / TCBS)

Ngay: 2026-11-06 (Thu 6). Gio VN (Asia/Ho_Chi_Minh).
Nguon so lieu: ClickHouse `vnmd.raw` (payload verbatim) + cac bang target
(`trades`, `book`, ...) tren VM prod `34.87.180.247`.

DAG Airflow tuong ung: `examples/airflow/dags/vnmd_cross_source_quality.py`
(9 nhom check: feed_health, wire_inventory, unknown_frames, trades_per_session,
cross_source, latency, book_depth, schema_probe, payload_samples).
Hom nay chay thu cong cac query cua DAG (tuong duong 1:1) vi batch Airflow
chinh thuc chay sau 16:05 theo `scripts/ops/after_hours_airflow.ps1`.

## 1. Tom tat phien — ca 3 feed xanh ca ngay

Watch giu lien tuc 08:28 -> 09:06 (bat loi mo cua 09:01) roi 09:06 -> 11:31
va 11:31 -> 15:05, moi 60-120s kiem tra `/tmp/health/ingestion.json` 1 lan.

- 09:01 mo cua: KHONG loi. Ca 3 `connected=true` suot phien.
- Khong co restart khan cap nao (watchdog chi log `tick ok`).
- Flink `vnmd-transform` RUNNING lien tuc, Redpanda Healthy=true, 0 partition
  under-replicated.

| source | raw cuoi phien (count) | tang trong ngay | ghi chu |
|---|---|---|---|
| ssi | 14,826,364 | ~+5.15M (9,676,574 -> 14,826,364) | manh nhat |
| tcbs | 8,311,197 | ~+4.33M (3,979,915 -> 8,311,197) | hoi phuc hoan toan sau su co token toi 05/11 |
| dnse | 974,399 | ~+323k (650,966 -> 974,399) | it nhat, dung ban chat (1 socket, it ma) |

`v_feed_health` luc 15:05 (gio VN):

| source | feed | msgs_today | wire_codes | kafka_errors | last_recv |
|---|---|---|---|---|---|
| dnse | dnse.market | 323,489 | 4 | 0 | 15:05:21 |
| ssi | ssi.market | 5,150,055 | 6 | 0 | 15:05:22 |
| tcbs | tcbs.derivative | 1,657,555 | 7 | 0 | 14:45:30 (phai sinh nghi som) |
| tcbs | tcbs.ouranos | 162,060 | 3 | 0 | 15:00:03 |
| tcbs | tcbs.stock | 2,512,214 | 19 | 0 | 15:05:10 |

## 2. Su co TCBS toi 05/11 -> tu hoi phuc rang sang 06/11

Timeline (gio UTC tren log container, VN = UTC+7):

- 05/11 toi: update `TCBS_TOKEN` moi (exp tuoi, scope giu nguyen
  `bond,fund,stock,socket:all`). Restart `ingest-tcbs-prod` van
  `Close(1008, 'Invalid policy')` ngay sau `d|33|15`, KHONG co
  `d|0 success`, cung KHONG con `211110 Invalid JWT`.
- Probe co lap 1 ket noi duy nhat tu may local (da stop container de loai
  tru tranh chap token) cho ket qua Y HET -> loai nguyen nhan multi-connection.
- Rang sang 06/11 KHONG doi gi them: `17:00:01Z` (= 00:00 VN) ouranos
  `Handshake OK`, `18:00:02Z` (= 01:00 VN) stock+derivative `Handshake OK`
  + `Subscription sent` day du, frames bat dau chay.
- Ca phien 06/11 TCBS `reconnects=0`, frames stock ~2.5M.

Nhan xet (ghi nhan hien tuong, chua ket luan): token dung scope/role nhung
server tu choi bang `1008 Invalid policy` trong nhieu gio lien tuc roi tu
chap nhan sau 00:00. Co the la policy theo khung gio / kich hoat tai khoan
pilot phia TCBS, khong phai loi code handshake (code giu nguyen, auth frame
`d|a|||<b64>` + cho `d|0` + subscribe moi gui). Tai lieu TCBS (5_2, 7_2,
changelog 31/07/2026) KHONG nhac toi `Invalid policy` cho thesis.

## 3. Don vi gia KHAC NHAU giua cac broker (quan trong nhat hom nay)

`v_last_trade` hom nay cho thay DNSE nho hon SSI/TCBS dung 1000 lan
tren CUNG 1 ma:

| symbol | price_ssi | price_dnse | price_tcbs | spread |
|---|---|---|---|---|
| VIC | 234500 | 234.5 | 234500 | 234265.5 |
| VJC | 134700 | 134.7 | 134700 | 134565.3 |
| VNM | 57800 | 57.8 | 57800 | 57742.2 |
| FPT | 50800 | 50.8 | 51179 | 51128.2 |

-> DNSE tra gia theo don vi NGHIN DONG (12.4 = 12,400 VND), SSI/TCBS tra
theo DONG. Parser/transform hien tai chua chuan hoa don vi nay — ai so sanh
`v_cross_source` phai nhan 1000 cho DNSE truoc. Tai lieu DNSE khong nhan manh
diem nay trong vi du payload.

Mau DNSE `te` (khop lenh):
```json
{"T":"te","avgPrice":12.246,"boardId":"G1","highestPrice":12.7,"lowestPrice":11.8,
 "matchPrice":12.4,"matchQtty":10,"openPrice":12.2,"side":"BUY","symbol":"CEO", ...}
```

Mau SSI `trade_tick` (cung ban chat khop lenh):
```json
{"channel":"DATA","topic":"trade.KOS","data":{"s":"KOS","t":"2026/11/06 13:09:58.043",
 "p":"3790","q":"1000","a":"3838.34","si":"B","o":"3850","h":"3940","l":"3720","v":"4115400"}}
```
Nhan xet: SSI boc trong `data`, gia la STRING (`"p":"3790"`), co san
open/high/low (`o/h/l`) trong moi tick — DNSE de rieng kenh `f`/ohlc.

## 4. Wire inventory thuc te hom nay (so voi docs)

### 4.1 SSI (6 wire)
| wire | n | keys | nhan xet |
|---|---|---|---|
| quote_tick | 4,219,590 | 1771 | so lenh, doc ghi top 10 — dung (xem §6) |
| trade_tick | 717,308 | 1270 | khop lenh |
| room_tick | 154,916 | 419 | room ngoai |
| oddlot_tick | 52,567 | 756 | lo le |
| market | 5,737 | 1906 | trang thai san |
| put_tick | 179 | 67 | thoa thuan, rat it |

### 4.2 DNSE (4 wire)
| wire | n | keys | nhan xet |
|---|---|---|---|
| te | 255,922 | 59 | khop (trade execution) |
| f | 54,433 | 57 | foreign/statistics theo ma |
| mi | 13,167 | 4 | index (VN-INDEX...) |
| s | 9 | 1 | LA: session events (xem §5), khong co trong tai lieu parse hien tai |

### 4.3 TCBS (19 wire — phong phu nhat)
| wire | n | keys | nhan xet |
|---|---|---|---|
| s\|42 | 1,580,690 | 1 | depth 10 muc phai sinh — KHONG co trong tai lieu, chiem ~38% traffic TCBS |
| s\|1 / s\|2 | 521,816 / 421,083 | 1276 / 1314 | bid/offer rieng 2 message (SSI/DNSE gop 1) |
| s\|6 | 430,049 | 947 | ticker match co so |
| s\|24 / s\|23 | 415,155 / 352,614 | 4 / 4 | offer/bid phai sinh (top 3) |
| C001 | 154,987 | 30 | ouranos trade — DUY NHAT co exchange_ts dang hoang (timeSec) |
| s\|29 / s\|28 | 128k / 122k | 340 / 340 | offer/bid CHUNG QUYEN — tai lieu khong he nhac |
| s\|21 | 99,718 | 4 | ticker match phai sinh |
| s\|3 | 63,525 | 1305 | foreign co so (co `room`) |
| s\|8 | 10,521 | 5 | index |
| s\|18 | 10,238 | 302 | ticker match chung quyen — khong co trong tai lieu |
| s\|5 | 7,296 | 947 | day summary co so (kieu du lieu loan — xem §4.4) |
| C002S60 / C002S900 | 6,592 / 481 | 30 / 30 | cung/cau chu dong (aggressor side) — chi ouranos co |
| s\|27 | 2,934 | 4 | day summary phai sinh |
| s\|32 | 1,876 | 302 | matched price chung quyen |
| s\|17 | 769 | 77 | khop thoa thuan |
| s\|25 | 747 | 4 | foreign phai sinh (khong co `room`) |
| s\|30 | 434 | 74 | foreign chung quyen (co `foreignNet`, khong co `room`) |
| s\|4 | 10 | 5 | base price — MAU RONG (xem §4.4) |
| s\|38 | 2 | 2 | snapshot tra ve `tradingDate` (xem §5) |

## 5. Khac biet du lieu thuc te vs docs (evidence verbatim)

### (a) DNSE wire `s` — session events, tai lieu khong mo ta cach route
Ngoai 3 wire quen thuoc (`te/f/mi`), hom nay co 9 frame wire `s` roi vao
`unknown_frames` (parser hien tai route DNSE theo SHAPE payload, khong theo
`T`, nen `T=s` khong khop rule nao):
```json
{"T":"s","boardId":"G1","eventId":"AC2","marketId":"STO","tradingSessionId":"99",...}
{"T":"s","boardId":"G1","eventId":"BC1","marketId":"STO","tradingSessionId":"30",...}
{"T":"s","boardId":"G1","eventId":"AD1","marketId":"STO","tradingSessionId":"60",...}
```
Day la ban tin phien (bat dau/ket thuc phien theo `tradingSessionId`),
khong phai du lieu gia. Quyet dinh hien tai (giua/`unknown_frames`) la DUNG —
khong nen co parse thanh trades.

### (b) TCBS `s|38` (snapshot) chi tra `tradingDate`
Docs (5_2): request `d|r|tk||...` tra snapshot day du cac truong s|4/s|5/s|6.
Thuc te hom nay (2/2 mau):
```json
{"tradingDate": "05/11/2026"}
```
Luu y date la 05/11 trong khi phien dang chay 06/11 — co the server tra
ngay giao dich truoc do (T-1) hoac do reconnect luc nua dem. Parser khong
nen doi hoi snapshot co `symbol`.

### (c) TCBS `s|4` (base price) co mau RONG
Docs: `{"symbol","ceilPrice","floorPrice","refPrice"}` (ghi la number).
Thuc te:
```json
{"symbol": "DNP"}
```
Khong ceil/floor/ref. Day khong phai loi parse — server gui thieu.
Parser phai coi 3 truong la nullable (hien tai da nullable — dung).

### (d) TCBS `s|5` kieu du lieu LAN LON (docs sai 1 nua)
Docs (5_2): `high/low/avg/open` deu number.
Thuc te 06/11:
```json
{"symbol": "MSH", "high": "35350", "low": "34400", "avg": 34750.0, "open": "34400"}
```
`high/low/open` la STRING, chi `avg` la number. Giong het nhan xet trong
`docs/tcbs/brief/DOCUMENT.md` §6 (s|4/s|5 docs ghi number nhung chay that
string) — hom nay xac nhan lai lan nua. Quy tac parse `Json.num()` (chap nhan
ca string lan number) la bat buoc.

### (e) TCBS `s|6` co mau CUC NGAN
```json
{"symbol": "VFS", "totalVolume": "200", "totalValue": "1860000"}
```
Khong co `matchPrice/matchQtty/change` nhu docs. Co the la ban tin tong ket
cuoi phien cho ma kem thanh khoan, hoac frame rut gon. Parser phai chiu
`matchPrice=NULL` (hien tai nullable — dung).

### (f) TCBS `s|42` — kenh nang nhat nhung tai lieu KHONG co
1,580,690 frames (~94% topic future theo audit cu, ~38% TCBS hom nay).
Moi message = 1 muc gia + chi so `top`, khac han SSI/DNSE gui ca mang:
```json
{"symbol": "41I1GC000", "top": 1, "bidPrice": 1807.5, "bidQty": 1.0,
 "bidCumulativeQty": 1.0, "offerPrice": 1888.0, "offerQty": 1.0,
 "offerCumulativeQty": 1.0, "action": "U"}
```
Mo khoa bang cach them code `dtn` vao subscribe (tai lieu khong ghi).
Bang `book` co rieng cot `level/bid_cum_qty/ask_cum_qty` cho kenh nay — dung.

### (g) TCBS ouranos `C001` — nguon exchange_ts tot nhat
```json
{"symbol": "ACB", "closePrice": 20350.0, "closeVol": 100.0, "change": -200.0,
 "reference": 20550.0, "timeSec": "1793931300", "unitTimeFrame": "60",
 "tradingValue": 2035000.0, "totalTradingValue": 1.628E7, ...}
```
`timeSec` la epoch seconds (string). Latency C001 hom nay p50 ~2.1s —
chap nhan duoc cho duong truyen VN -> GCP Singapore.

## 6. Do sau so lenh (book_depth hom nay)

| source | wire | rows | bid_lv | ask_lv | syms | nhan xet |
|---|---|---|---|---|---|---|
| ssi | quote_tick | 4,219,590 | 10 | 10 | 1771 | ca 2 phia trong 1 message |
| ssi | oddlot_tick | 52,567 | 3 | 3 | 756 | lo le 3 muc |
| tcbs | s\|1 | 521,816 | 3 | 0 | 1276 | bid rieng |
| tcbs | s\|2 | 421,083 | 0 | 3 | 1314 | ask rieng — phai ghep lai khi doc (`v_last_book` da lam) |
| tcbs | s\|23 | 326,902 | 3 | 0 | 4 | bid phai sinh |
| tcbs | s\|24 | 365,189 | 0 | 3 | 4 | ask phai sinh |
| tcbs | s\|28/s\|29 | 122k/128k | 3/0 | 0/3 | 340 | chung quyen, tach 2 phia nhu co so |
| tcbs | s\|42 | 1,580,690 | 1 | 1 | 1 | 1 level/message + `top` (futures `41I1G*`) |

## 7. Do tre (latency, exchange_ts -> recv_ts, chi noi co timestamp moi tinh duoc)

| source | wire | n | avg_ms | nhan xet |
|---|---|---|---|---|
| dnse | te | 255,922 | 781.5 | tot nhat (nanoseconds) |
| ssi | trade_tick | 717,308 | 848.7 | timestamp `YYYY/MM/DD HH:mi:ss` (giay) nen do phan giai thap |
| ssi | oddlot_tick | 52,567 | 1,513.2 | lo le cham hon — binh thuong |
| ssi | put_tick | 179 | 598.0 | mau nho |
| tcbs | C001 | 154,987 | 2,068.9 | ouranos seconds — cham nhat nhung van < 3s |
| tcbs | s\|17 | 769 | 581.8 | thoa thuan co time |

TCBS thesis (s|1…s|42): KHONG co exchange_ts -> latency NULL mai mai.
Day la gioi han broker, khong phai bug. Chi `recv_ts` moi so sanh duoc
xuyen 3 nguon.

## 8. Schema thuc te (da verify `system.columns` khop DDL `sql/20_targets.sql`)

- `raw`: source/feed/wire_code/kafka_key/payload + recv_ts_ns + kafka_* — giu
  verbatim, khong transform.
- `trades`: price/qty/avg_price/total_volume/total_value/change/change_percent
  nullable; `side`: B/S (SSI) – BU/SD (ouranos) – BUY/SELL (DNSE) — chua chuan
  hoa, query phai tu map.
- `book`: bid/ask la Array; TCBS 1 phia thi phia kia rong; s|42 them
  level/bid_cum_qty/ask_cum_qty.
- `supply_demand`: chi TCBS ouranos co (C002S60/C002S900). Tai lieu goi
  C002S900 la "foreign" la SAI — schema y het C002S60, chi khac window 900s.
- Tat ca bang target la `ReplacingMergeTree ORDER BY (..., kafka_partition,
  kafka_offset)` + view `*_v` (`FINAL`) de dedup sau replay.

## 9. Viec con lai

- [ ] Chuan hoa don vi gia DNSE (x1000) o tang transform HOAC ghi ro trong
  contract — hien tai de tho se lech 1000x khi so sanh cheo.
- [ ] Chuan hoa `side` 3 broker ve 1 enum (B/S).
- [ ] Cap nhat `docs/tcbs/brief/DOCUMENT.md` §6 bang wire hom nay (them s|42
  dominance, s|38/s|4 rong).
- [ ] Bao dong `v_unknown_summary` khi DNSE `s` tang dot bien (doi protocol).
- [ ] Batch Airflow 16:05 chay DAG `vnmd_cross_source_quality`, report
  `/opt/airflow/reports/vnmd-quality-2026-11-06.md` de doi chieu voi file nay.
