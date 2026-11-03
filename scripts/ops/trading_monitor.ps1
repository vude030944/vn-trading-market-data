# Trading-hours monitor (08:00-16:00, Asia/Ho_Chi_Minh).
# Brings up the local observability stack (OTel collector + Prometheus + Grafana)
# and tails the prod-VM ingestion health into a dated log file.
# Idempotent — safe to run twice. Registered in Task Scheduler as "VNMD Monitor Start".
$ErrorActionPreference = "Stop"
$Repo = "D:\self-learning\vn-trading-market-data"
$LogDir = "$Repo\logs\monitor"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Log = "$LogDir\monitor-$(Get-Date -Format 'yyyyMMdd').log"

function Log-Line($msg) {
  $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $msg"
  $line | Tee-Object -FilePath $Log -Append
}

Log-Line "=== VNMD trading-hours monitor start ==="

# Observability network (external network expected by the compose file)
$net = docker network ls --format "{{.Name}}" | Select-String -Pattern "^vnmd-dev$"
if (-not $net) {
  Log-Line "creating docker network vnmd-dev"
  docker network create vnmd-dev | Out-Null
}

Push-Location "$Repo\environment\dev\observability"
try {
  docker compose up -d 2>&1 | ForEach-Object { Log-Line "observability: $_" }
} finally { Pop-Location }

# Snapshot of prod-VM health (one SSH call, no secrets printed)
$sshKey = "$env:USERPROFILE\.ssh\cursor_vm"
$health = ssh -i $sshKey -o StrictHostKeyChecking=no -o ConnectTimeout=15 vuloc@34.87.180.247 "docker ps --format '{{.Names}} {{.Status}}' | sort; echo ---; docker exec ch-prod clickhouse-client --user vnmd --password vnmd_prod_2026_Uk9x7v2m --query 'SELECT source, count() FROM vnmd.raw GROUP BY source' 2>&1" 2>&1
$health | ForEach-Object { Log-Line "prod: $_" }

Log-Line "monitor running — Grafana http://localhost:3000, Prometheus http://localhost:9090"
Log-Line "=== done ==="
