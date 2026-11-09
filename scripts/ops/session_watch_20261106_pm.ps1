# Afternoon session watch 2026-11-06: 11:31 -> 15:05 (covers lunch + afternoon + ATC).
$ErrorActionPreference = 'Continue'
$sshKey = Join-Path $env:USERPROFILE '.ssh\cursor_vm'
$sshBase = @('-i', $sshKey, '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=15', 'vuloc@34.87.180.247')
$deadline = Get-Date -Date '2026-11-06 15:05:00'
Write-Output "PM-WATCH-START $(Get-Date -Format 'HH:mm:ss') deadline $($deadline.ToString('HH:mm:ss'))"
while ((Get-Date) -lt $deadline) {
  $t = (Get-Date).ToString('HH:mm:ss')
  try {
    $ssi = ssh @sshBase 'docker exec ingest-ssi-prod cat /tmp/health/ingestion.json' 2>&1 | Out-String
    $dnse = ssh @sshBase 'docker exec ingest-dnse-prod cat /tmp/health/ingestion.json' 2>&1 | Out-String
    $tcbs = ssh @sshBase 'docker exec ingest-tcbs-prod cat /tmp/health/ingestion.json' 2>&1 | Out-String
    $ssiOk = ($ssi -match '"connected": true')
    $dnseOk = ($dnse -match '"connected": true')
    $tcbsOk = ($tcbs -match '"connected": true')
    $bad = @()
    if (-not $ssiOk) { $bad += 'SSI-DOWN' }
    if (-not $dnseOk) { $bad += 'DNSE-DOWN' }
    if (-not $tcbsOk) { $bad += 'TCBS-DOWN' }
    if ($bad.Count -gt 0) {
      Write-Output "$t ALERT $($bad -join ',')"
      Write-Output "  ssi: $($ssi.Substring(0, [Math]::Min(200, $ssi.Length)))"
      Write-Output "  dnse: $($dnse.Substring(0, [Math]::Min(200, $dnse.Length)))"
      Write-Output "  tcbs: $($tcbs.Substring(0, [Math]::Min(200, $tcbs.Length)))"
      if (-not $ssiOk) {
        ssh @sshBase 'cd ~/vnmd/environment/prod-vm && docker compose restart ingest-ssi' 2>&1 | ForEach-Object { Write-Output "  heal-ssi: $_" }
      }
      if (-not $dnseOk) {
        ssh @sshBase 'cd ~/vnmd/environment/prod-vm && docker compose restart ingest-dnse' 2>&1 | ForEach-Object { Write-Output "  heal-dnse: $_" }
      }
    } else {
      $ssiF = ([regex]::Match($ssi, '"frames":\s*(\d+)')).Groups[1].Value
      $dnseF = ([regex]::Match($dnse, '"frames":\s*(\d+)')).Groups[1].Value
      $tcbsF = ([regex]::Matches($tcbs, '"frames":\s*(\d+)') | ForEach-Object { [int]$_.Groups[1].Value } | Measure-Object -Sum).Sum
      Write-Output "$t tick ok ssi_frames=$ssiF dnse_frames=$dnseF tcbs_frames=$tcbsF"
    }
  } catch {
    Write-Output "$t WATCH-ERR $($_.Exception.Message)"
  }
  $remain = ($deadline - (Get-Date)).TotalSeconds
  if ($remain -le 0) { break }
  if ($remain -gt 120) { $remain = 120 }
  Start-Sleep -Seconds ([int]$remain)
}
Write-Output "PM-WATCH-DONE $(Get-Date -Format 'HH:mm:ss')"
$counts = ssh @sshBase 'docker exec ch-prod clickhouse-client --query ''SELECT source, count() FROM vnmd.raw GROUP BY source ORDER BY source''' 2>&1
foreach ($c in $counts) { Write-Output "rows: $c" }
