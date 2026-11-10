# Local session watch - Monday 2026-11-09 (no VM dependency).
# Logs to logs/monitor/monitor-20261109.log, guards 09:01 open explicitly.
$ErrorActionPreference = 'Continue'
$Repo = 'D:\self-learning\vn-trading-market-data'
$Log = Join-Path $Repo 'logs/monitor/monitor-20261109.log'
function MLog($msg) {
  $line = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + ' ' + $msg
  $line | Tee-Object -FilePath $Log -Append | Out-Null
}
MLog '=== local session watch started (SSI+DNSE, Flink, CH) ==='
$warned0901 = $false
while ($true) {
  try {
    $ts = Get-Date -Format 'HH:mm:ss'
    $ssi = docker exec ingest-ssi cat /tmp/health/ingestion.json 2>&1 | Out-String
    $dnse = docker exec ingest-dnse cat /tmp/health/ingestion.json 2>&1 | Out-String
    $ssiOk = ($ssi -match '"connected": true')
    $dnseOk = ($dnse -match '"connected": true')
    if (-not $ssiOk) { MLog ("ALERT ssi down: " + $ssi.Substring(0,[Math]::Min(300,$ssi.Length))) }
    if (-not $dnseOk) {
      if ((Get-Date).Minute % 10 -eq 0) { MLog ("NOTE dnse auth-fail (key rejected from home IP?): " + $dnse.Substring(0,[Math]::Min(200,$dnse.Length))) }
    }
    $jobs = curl.exe -s http://localhost:8081/jobs/overview 2>$null
    if ($jobs -notmatch '"state":"RUNNING"') { MLog 'ALERT flink not RUNNING' }
    # 09:01 open guard: sample frames around the cash-open burst
    $now = Get-Date
    if ($now.Hour -eq 9 -and $now.Minute -eq 1 -and -not $warned0901) {
      $warned0901 = $true
      MLog '=== 09:01 OPEN CHECK ==='
      MLog ("ssi: " + $ssi.Trim())
      MLog ("dnse: " + $dnse.Trim())
      $cnt = docker exec clickhouse clickhouse-client --user vnmd --password vnmd_dev_password --query "SELECT source, count() FROM vnmd.raw GROUP BY source" 2>&1 | Out-String
      MLog ("ch counts @09:01: " + $cnt.Trim())
    }
    # hourly counts
    if ((Get-Date).Minute -lt 2) {
      $cnt = docker exec clickhouse clickhouse-client --user vnmd --password vnmd_dev_password --query "SELECT source, count() FROM vnmd.raw GROUP BY source" 2>&1 | Out-String
      foreach ($c in ($cnt -split "`n")) { MLog ('rows: ' + $c.Trim()) }
    }
    MLog ("tick ok @ " + $ts + " ssiOk=" + $ssiOk + " dnseOk=" + $dnseOk)
  } catch { MLog ('watch error: ' + $_.Exception.Message) }
  Start-Sleep -Seconds 60
}
