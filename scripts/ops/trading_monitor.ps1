# Trading-hours monitor (08:00-16:00, Asia/Ho_Chi_Minh).
# Brings up the local observability stack (OTel collector + Prometheus + Grafana)
# and snapshots the prod-VM ingestion health into a dated log file.
# Idempotent - safe to run twice. Registered in Task Scheduler as "VNMD Monitor Start".
# NOTE: native docker output goes to stderr - keep preference Continue so log
# lines from docker do not abort the script. Critical failures checked via $LASTEXITCODE.
$ErrorActionPreference = 'Continue'
$Repo = 'D:\self-learning\vn-trading-market-data'
$LogDir = Join-Path $Repo 'logs\monitor'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Log = Join-Path $LogDir ('monitor-' + (Get-Date -Format 'yyyyMMdd') + '.log')

function Log-Line($msg) {
  $line = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + ' ' + $msg
  $line | Tee-Object -FilePath $Log -Append
}

Log-Line '=== VNMD trading-hours monitor start ==='

$net = docker network ls --format '{{.Name}}' | Select-String -Pattern '^vnmd-dev$'
if (-not $net) {
  Log-Line 'creating docker network vnmd-dev'
  docker network create vnmd-dev | Out-Null
}

Push-Location (Join-Path $Repo 'environment\dev\observability')
try {
  # Observability persists locally under data/observability (gitignored).
  $env:DATA_ROOT = Join-Path $Repo 'data\observability'
  New-Item -ItemType Directory -Force -Path (Join-Path $env:DATA_ROOT 'prometheus') | Out-Null
  New-Item -ItemType Directory -Force -Path (Join-Path $env:DATA_ROOT 'grafana') | Out-Null
  docker compose up -d 2>&1 | ForEach-Object { Log-Line ('observability: ' + $_) }
} finally { Pop-Location }

$sshKey = Join-Path $env:USERPROFILE '.ssh\cursor_vm'
$sshBase = @('-i', $sshKey, '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=15', 'vuloc@34.87.180.247')
# NOTE: remote quoting uses single quotes only - PowerShell strips inner double
# quotes when passing a spaced string to native ssh, which broke docker --format.
$remotePs = 'docker ps --format ''{{.Names}} {{.Status}}'' | sort'
$health = & ssh @sshBase $remotePs 2>&1
foreach ($h in $health) { Log-Line ('prod: ' + $h) }

$remoteCounts = 'set -a; . ~/vnmd/environment/prod-vm/.env >/dev/null 2>&1; set +a; docker exec ch-prod clickhouse-client --user $CH_USER --password $CH_PASSWORD --query ''SELECT source, count() FROM vnmd.raw GROUP BY source'''
$counts = & ssh @sshBase $remoteCounts 2>&1
foreach ($c in $counts) { Log-Line ('clickhouse: ' + $c) }

Log-Line 'monitor running - Grafana http://localhost:3000, Prometheus http://localhost:9090'
Log-Line '=== done ==='
