param([string]$TargetDir = (Split-Path -Parent $PSScriptRoot))
$ErrorActionPreference = 'Stop'
$workspace = Split-Path -Parent $PSScriptRoot
$yaml = Join-Path $workspace '.fr.yaml'
if (-not (Test-Path -LiteralPath $yaml)) { throw ".fr.yaml not found: $yaml" }
$text = Get-Content -Raw -LiteralPath $yaml
function Read-Value([string]$section, [string]$key, [string]$fallback) {
  $pattern = '(?ms)^{0}:\s*.*?^\s+{1}:\s*[''\"]?([^''\"\s#]+)' -f [regex]::Escape($section), [regex]::Escape($key)
  $m = [regex]::Match($text, $pattern)
  if ($m.Success) { return $m.Groups[1].Value }
  return $fallback
}
$envData = [ordered]@{
  FR_WORKSPACE=$workspace
  FR_PROJECTS_DIR=(Read-Value 'paths' 'projects_dir' $workspace)
  FR_REPORTLETS=(Read-Value 'paths' 'finereport_reportlets' $workspace)
  FR_SERVER_URL=(Read-Value 'finereport' 'server_url' 'http://localhost:8075')
  FR_PREVIEW_PATH=(Read-Value 'finereport' 'preview_path' '/webroot/decision/view/report?op=write&reportlet=')
  FR_ADMIN_USER=(Read-Value 'finereport' 'admin_user' 'admin')
  FR_MYSQL_HOST=(Read-Value 'mysql' 'host' 'localhost')
  FR_MYSQL_PORT=(Read-Value 'mysql' 'port' '3306')
  FR_MYSQL_DATABASE=(Read-Value 'mysql' 'database' 'common_db')
  FR_MYSQL_USER=(Read-Value 'mysql' 'user' 'root')
}
New-Item -ItemType Directory -Force -Path (Join-Path $TargetDir '.codex') | Out-Null
$envData | ConvertTo-Json | Set-Content -Encoding UTF8 (Join-Path $TargetDir '.codex\env.json')
Write-Output ("Codex environment written to " + (Join-Path $TargetDir '.codex\env.json'))
