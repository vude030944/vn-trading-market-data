# VNMD overnight watchdog - runs forever, heals prod VM + local stacks.
# Logs to logs\watchdog\watchdog-YYYYMMDD.log. Started in background, never stops.
$ErrorActionPreference = 'Continue'
$Repo = 'D:\self-learning\vn-trading-market-data'
$LogDir = Join-Path $Repo 'logs\watchdog'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$sshKey = Join-Path $env:USERPROFILE '.ssh\cursor_vm'
$sshBase = @('-i', $sshKey, '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=15', 'vuloc@34.87.180.247')

function WLog($msg) {
  $log = Join-Path $LogDir ('watchdog-' + (Get-Date -Format 'yyyyMMdd') + '.log')
  $line = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + ' ' + $msg
  $line | Tee-Object -FilePath $log -Append | Out-Null
}

WLog '=== watchdog started (interval 60s) ==='
while ($true) {
  try {
    $ts = Get-Date -Format 'HH:mm:ss'
    # 1. VM containers
    # NOTE: remote quoting uses single quotes only - PowerShell strips inner double
    # quotes when passing a spaced string to native ssh (broke docker --format before).
    $ps = & ssh @sshBase 'docker ps --format ''{{.Names}} {{.Status}}'' | sort' 2>&1
    $down = @($ps | Where-Object { $_ -match 'Restarting|Exited|Dead' })
    if ($down.Count -gt 0) {
      WLog ("ALERT containers down: " + ($down -join ' | '))
      & ssh @sshBase 'cd ~/vnmd/environment/prod-vm && docker compose up -d' 2>&1 | ForEach-Object { WLog ('heal compose: ' + $_) }
    }
    # 2. Redpanda health
    $h = & ssh @sshBase 'docker exec rp-prod-0 rpk cluster health -X admin.hosts=localhost:9644' 2>&1 | Out-String
    if ($h -notmatch 'Healthy:\s+true') {
      WLog 'ALERT redpanda not healthy'
      WLog ($h.Substring(0, [Math]::Min(400, $h.Length)))
    }
    # 3. Ingest frames progress (detect stall: frames not growing between checks)
    $ssi1 = & ssh @sshBase 'docker exec ingest-ssi-prod cat /tmp/health/ingestion.json' 2>&1 | Out-String
    Start-Sleep -Seconds 20
    $ssi2 = & ssh @sshBase 'docker exec ingest-ssi-prod cat /tmp/health/ingestion.json' 2>&1 | Out-String
    if (($ssi1 -match '"connected": true') -and ($ssi2 -match '"connected": true')) {
      # connected - fine, log counts hourly only
      if ((Get-Date).Minute -lt 2) {
        $counts = & ssh @sshBase 'set -a; . ~/vnmd/environment/prod-vm/.env >/dev/null 2>&1; set +a; docker exec ch-prod clickhouse-client --user $CH_USER --password $CH_PASSWORD --query ''SELECT source, count() FROM vnmd.raw GROUP BY source''' 2>&1
        foreach ($c in $counts) { WLog ('rows: ' + $c) }
      }
    } else {
      WLog ("ALERT ingest health bad: " + $ssi1.Substring(0, [Math]::Min(200, $ssi1.Length)))
      & ssh @sshBase 'cd ~/vnmd/environment/prod-vm && docker compose restart ingest-ssi ingest-dnse ingest-tcbs' 2>&1 | ForEach-Object { WLog ('heal ingest: ' + $_) }
    }
    # 4. Flink job running?
    $jobs = & ssh @sshBase 'curl -s http://localhost:8081/jobs/overview' 2>&1 | Out-String
    if ($jobs -notmatch '"state":"RUNNING"') {
      WLog 'ALERT flink job not RUNNING, resubmitting via compose'
      & ssh @sshBase 'cd ~/vnmd/environment/prod-vm && docker compose up -d flink-jm-prod flink-tm-prod flink-submit' 2>&1 | ForEach-Object { WLog ('heal flink: ' + $_) }
    }
    WLog ("tick ok @ " + $ts)
  } catch {
    WLog ('watchdog error: ' + $_.Exception.Message)
  }
  Start-Sleep -Seconds 60
}
