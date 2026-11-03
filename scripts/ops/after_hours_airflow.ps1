# After-hours batch (16:05, Asia/Ho_Chi_Minh).
# Stops the trading-hours monitor stack, then brings up Airflow (+dbt) for the
# cross-source data-quality comparison (tick completeness, latency, spread
# divergence across SSI / DNSE / TCBS).
# Idempotent — safe to run twice. Registered in Task Scheduler as "VNMD AfterHours Airflow".
$ErrorActionPreference = "Stop"
$Repo = "D:\self-learning\vn-trading-market-data"
$LogDir = "$Repo\logs\airflow"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Log = "$LogDir\airflow-$(Get-Date -Format 'yyyyMMdd').log"

function Log-Line($msg) {
  $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $msg"
  $line | Tee-Object -FilePath $Log -Append
}

Log-Line "=== VNMD after-hours batch start ==="

# 1. Stop the trading-hours monitor to free RAM/CPU for Airflow
Push-Location "$Repo\environment\dev\observability"
try {
  Log-Line "stopping observability stack"
  docker compose down 2>&1 | ForEach-Object { Log-Line "observability: $_" }
} finally { Pop-Location }

# 2. Ensure Airflow has its required .env (FERNET_KEY has no compose default)
$AirflowDir = "$Repo\examples\airflow"
$AirflowEnv = "$AirflowDir\.env"
if (-not (Test-Path $AirflowEnv)) {
  Log-Line "generating $AirflowEnv (FERNET_KEY)"
  $fernet = python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 2>$null
  if (-not $fernet) {
    # fallback: 32 random bytes, base64 — valid Fernet key format
    $bytes = New-Object byte[] 32
    (New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes)
    $fernet = [Convert]::ToBase64String($bytes)
  }
  @"
AIRFLOW_IMAGE_NAME=apache/airflow:3.3.2
AIRFLOW_UID=50000
AIRFLOW_PROJ_DIR=.
FERNET_KEY=$fernet
AIRFLOW__API_AUTH__JWT_SECRET=airflow_jwt_secret_change_me
"@ | Out-File -FilePath $AirflowEnv -Encoding utf8
}

# 3. Bring up Airflow
Push-Location $AirflowDir
try {
  Log-Line "starting Airflow (init + up)"
  docker compose up airflow-init 2>&1 | Select-Object -Last 5 | ForEach-Object { Log-Line "airflow-init: $_" }
  docker compose up -d 2>&1 | ForEach-Object { Log-Line "airflow: $_" }
} finally { Pop-Location }

Log-Line "Airflow running — UI http://localhost:8080 (admin/admin default)"
Log-Line "Unpause your data-quality DAG in the UI; results feed the morning report."
Log-Line "=== done ==="
