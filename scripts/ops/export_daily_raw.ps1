# Daily raw export: ClickHouse vnmd.raw (VM) -> data/raw/<source>/YYYY/MM/DD/*.parquet + logs.
# Usage: powershell -File scripts/ops/export_daily_raw.ps1 [-Day '2026-11-06']
param([string]$Day = '')
$ErrorActionPreference = 'Continue'
$Repo = 'D:\self-learning\vn-trading-market-data'
if (-not $Day) { $Day = (Get-Date).AddDays(-1).ToString('yyyy-MM-dd') }
$dt = [datetime]::ParseExact($Day, 'yyyy-MM-dd', $null)
$ymd = $dt.ToString('yyyy/MM/dd'); $dash = $dt.ToString('yyyy-MM-dd')
$next = $dt.AddDays(1).ToString('yyyy-MM-dd')
$sshKey = Join-Path $env:USERPROFILE '.ssh\cursor_vm'
$sshBase = @('-i', $sshKey, '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=15', 'vuloc@34.87.180.247')

foreach ($s in @('ssi','tcbs','dnse')) {
  $dir = Join-Path $Repo "data/raw/$s/$ymd"
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  $sql = "SELECT source, feed, wire_code, kafka_key, payload, recv_ts_ns, recv_ts, kafka_topic, kafka_partition, kafka_offset, error, dw_ts FROM vnmd.raw WHERE source = '$s' AND recv_ts BETWEEN toDateTime64('$Day 00:00:00', 9, 'Asia/Ho_Chi_Minh') AND toDateTime64('$next 00:00:00', 9, 'Asia/Ho_Chi_Minh') INTO OUTFILE '/tmp/vnmd_${s}_${dash}.parquet' FORMAT Parquet"
  $sql | ssh @sshBase "docker exec -i ch-prod clickhouse-client --multiquery" 2>&1 | ForEach-Object { Write-Output "export $s ${Day}: $_" }
  ssh @sshBase "mkdir -p ~/vnmd_export/${dash}; docker cp ch-prod:/tmp/vnmd_${s}_${dash}.parquet ~/vnmd_export/${dash}/; rm -f /tmp/vnmd_${s}_${dash}.parquet" 2>&1 | ForEach-Object { Write-Output "stage $s ${Day}: $_" }
  scp -i $sshKey -o StrictHostKeyChecking=no "vuloc@34.87.180.247:vnmd_export/${dash}/vnmd_${s}_${dash}.parquet" "$dir/" 2>&1 | ForEach-Object { Write-Output "scp $s ${Day}: $_" }
}
# Gom logs container ngay hom do (json-file, max 100m x5) ve data/logs/YYYY-MM-DD/
$logDir = Join-Path $Repo "data/logs/$dash"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
ssh @sshBase 'cd ~/vnmd/environment/prod-vm && docker compose logs --since 24h --no-color ingest-ssi ingest-dnse ingest-tcbs > ~/vnmd_export/daily-ingest.log 2>&1; echo done' 2>&1 | Out-Null
scp -i $sshKey -o StrictHostKeyChecking=no "vuloc@34.87.180.247:vnmd_export/daily-ingest.log" "$logDir/ingest-24h.log" 2>&1 | ForEach-Object { Write-Output "scp logs: $_" }
Get-ChildItem "data/raw/*/2026/*/*/*.parquet" | ForEach-Object { Write-Output "$($_.FullName) $([math]::Round($_.Length/1MB,1)) MB" }
