# Luu tru raw + logs va phuong an roi GCP (07/11/2026)

## 1. Vi sao 1 file/source/ngay ma khong tach moi wire 1 file?

- Da LUU HET, khong mat gi: moi file `vnmd_<source>_YYYY-MM-DD.parquet` chua
  FULL 12 cot `vnmd.raw` (source, feed, wire_code, kafka_key, payload verbatim,
  recv_ts_ns, recv_ts, kafka_topic/partition/offset, error, dw_ts).
  Phan biet format nam o cot `wire_code`, khong nam o ten file.
- Ly do khong tach per-wire: hom 06/11 SSI co 6 wire, DNSE 4 wire, TCBS 19 wire.
  Tach ra se co ~30 file/ngay, trong do nhieu file ti hon (DNSE `s` = 9 rows,
  SSI `put_tick` = 179 rows, TCBS `s|38` = 2 rows) -> roi vao "small files
  problem" cua Parquet (mo file ton kem hon doc), list/tra cứu cuc.
  Gi lai: query engine (pandas/pyarrow/DuckDB) loc `WHERE wire_code='s|42'`
  bang predicate pushdown + dictionary encoding, doc dung row-group can thiet,
  khong cham hon tach file ma de quan ly hon nhieu.
- Layout HIVE `data/raw/<source>/YYYY/MM/DD/` cho phep doc ca nam chi bang
  1 glob `data/raw/ssi/2026/**/*.parquet`, partition pruning theo ngay.
- Neu sau nay can toi uu train (chi doc trade_tick): lam them 1 job dao
  `raw -> curated` (tinh, chuan hoa don vi DNSE x1000, map side) chu khong
  dap di cau truc archive.

## 2. Luu moi thu (raw quy nhat)

Trang thai hien tai (da lam sang 07/11):
- `data/raw/ssi/2026/11/06/vnmd_ssi_2026-11-06.parquet` — 171 MB, 5,164,749 rows
- `data/raw/tcbs/2026/11/06/vnmd_tcbs_2026-11-06.parquet` — 112 MB, 4,331,829 rows
- `data/raw/dnse/2026/11/06/vnmd_dnse_2026-11-06.parquet` — 15 MB, 326,607 rows
- `data/logs/2026-11-06/ingest-24h.log` — 5.4 MB (logs 3 container ingestion 48h)
- Tong ~303 MB/ngay. 1 nam (~250 phien) ~75 GB. Dia C (250 GB free) + D (106 GB
  free) chua duoc ~4-5 nam raw thoai mai.
- Script dinh ky: `scripts/ops/export_daily_raw.ps1 [-Day '2026-11-07']`
  (export 3 source tu ClickHouse VM -> scp ve + gom `docker compose logs`).
  Dat Task Scheduler chay 16:05 hang ngay sau phien.
- `data/` da gitignore nen khong day len git.

MinIO local: CHUA CAN. Quy tac: khi nao can doc S3 API / lifecycle
(versioning, expire) hoac share data cho nhieu may train thi moi dung.
Hien tai file system + DuckDB/pandas doc truc tiep la nhanh nhat, it ton RAM
nhat. Neu o cung day >80% thi nang TTL ClickHouse `vnmd.raw` tu 7 ngay len
30-90 ngay truoc khi nghi toi MinIO (xem `src/transform/sql/10_landing.sql`).

## 3. GCP het han: don ve laptop hay tach may 12c/16GB?

So lieu do that 07/11:
- VM GCP: 12 vCPU / 31 GB RAM, dang dung ~13 GB (RP 3x2.2 GB, CH 1.8/8 GB,
  Flink-TM 3.2/8 GB, JM 0.7/2 GB, ingestion 3x~30 MB). CPU idle <5%.
- Laptop: i7-10750H (6 nhan / 12 luong) / 32 GB RAM, C free 250 GB + D free
  106 GB. Airflow local dang chay ~1.9 GB.

Ket luan: DON HET VE LAPTOP VAN CHAY DUOC NHUNG KHONG NEN lam kieu all-in-one
lau dai. Ly do khong phai thieu RAM tren giay (28.5 GB limit vs 32 GB vat ly
la vua du) ma la:
1. Docker Desktop + WSL2 an them 2-4 GB, Windows + IDE + Chrome an 6-8 GB nua
   -> gio cao diem (9:00-9:30, vua thu vua Flink vua Airflow) se swap, de
   rot frame dung luc can nhat.
2. Laptop sleep / Windows Update / cup dien = mat data phien do. VM/server
   moi co uptime 44h+ lien tuc nhu tuan nay.
3. Disk C/D la SSD laptop, ghi lien tuc 285 MB/ngay + WAL Redpanda/CH se mon
   nhanh hon SSD server.

Phuong an chot (da chon): TACH.
- May 12c/16GB (dat co dinh, cam dien + mang day, uu tien Linux): chay NGUYEN
  stack `environment/prod-vm/docker-compose.yml` (RP x3 + CH + Flink + 3
  ingestion). 16 GB RAM du vi muc dung that ~13 GB; neu chat thi ha
  `mem_limit` CH 8g->6g, Flink-TM 8g->6g trong compose override.
  Thay IP `34.87.180.247` trong compose + `.env` thanh IP LAN cua may do,
  mo port 19092-19094/8123/8081 trong LAN la xong. Khong doi code.
- Laptop nay: giu Airflow batch (chay sau 16:05), Grafana/Prometheus xem,
  kho `data/raw` + `data/logs` (archive nam), train AI.
- Thu tu di doi khi GCP het: (1) export CuOI 1 lan full `vnmd.raw` 7 ngay tu
  VM cu, (2) dung stack tren may moi, (3) doi watchdog/monitor sang IP moi,
  (4) chay thu 1 phien, (5) moi huy VM.

Du phong neu bat buoc all-in-one tren laptop: giam RP 3->1 broker, CH
`mem_limit: 8g->4g`, Flink-TM `8g->4g`, Airflow chi `up` sau 16:05 roi `down`
truoc 8:00. De san override khi can.
