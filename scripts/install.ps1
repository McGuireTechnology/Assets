$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$env:MISE_DATA_DIR = Join-Path $root ".cache/mise/data"
$env:MISE_CACHE_DIR = Join-Path $root ".cache/mise/cache"
$env:MISE_TMP_DIR = Join-Path $root ".cache/mise/tmp"
New-Item -ItemType Directory -Force -Path $env:MISE_DATA_DIR, $env:MISE_CACHE_DIR, $env:MISE_TMP_DIR | Out-Null

$mise = Get-Command "mise" -ErrorAction SilentlyContinue

if (-not $mise) {
  $scoop = Get-Command "scoop" -ErrorAction SilentlyContinue
  $winget = Get-Command "winget" -ErrorAction SilentlyContinue

  if ($scoop) {
    & $scoop.Source install mise
  } elseif ($winget) {
    & $winget.Source install --id jdx.mise --exact --source winget
  } else {
    Write-Error "mise was not found. Install Scoop or Winget, then run this script again."
    exit 1
  }

  $mise = Get-Command "mise" -ErrorAction SilentlyContinue
  if (-not $mise) {
    Write-Error "mise was installed but is not on PATH yet. Restart your shell, then run this script again."
    exit 1
  }
}

Push-Location $root
try {
  & $mise.Source install --locked
  if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
  }

  & $mise.Source run bootstrap
  exit $LASTEXITCODE
} finally {
  Pop-Location
}
