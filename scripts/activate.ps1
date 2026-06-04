$root = Split-Path -Parent $PSScriptRoot
$miseDir = Join-Path $root ".cache/mise/bin"
$miseExe = Join-Path $miseDir "mise.exe"
$env:MISE_DATA_DIR = Join-Path $root ".cache/mise/data"
$env:MISE_CACHE_DIR = Join-Path $root ".cache/mise/cache"
$env:MISE_TMP_DIR = Join-Path $root ".cache/mise/tmp"
New-Item -ItemType Directory -Force -Path $env:MISE_DATA_DIR, $env:MISE_CACHE_DIR, $env:MISE_TMP_DIR | Out-Null

if (-not (Test-Path $miseExe) -and -not (Get-Command "mise" -ErrorAction SilentlyContinue)) {
  Write-Error "mise was not found. Run .\scripts\install.ps1 first."
  return
}

if ((Test-Path $miseDir) -and -not ($env:PATH -split [System.IO.Path]::PathSeparator | Where-Object { $_ -eq $miseDir })) {
  $env:PATH = "$miseDir$([System.IO.Path]::PathSeparator)$env:PATH"
}

$mise = Get-Command "mise" -ErrorAction SilentlyContinue
if ($mise) {
  Invoke-Expression (& $mise.Source activate pwsh)
}

if (-not $env:ASSETS_MISE_PROMPT_ACTIVE) {
  $env:ASSETS_MISE_PROMPT_ACTIVE = "1"

  if (Test-Path Function:\prompt) {
    Set-Item -Path Env:ASSETS_MISE_ORIG_PROMPT_DEFINED -Value "1"
    $script:AssetsMiseOriginalPrompt = (Get-Command prompt).ScriptBlock
  }

  function global:prompt {
    Write-Host "(Assets) " -NoNewline -ForegroundColor Cyan

    if ($script:AssetsMiseOriginalPrompt) {
      & $script:AssetsMiseOriginalPrompt
    } else {
      "PS $($executionContext.SessionState.Path.CurrentLocation)$('>' * ($nestedPromptLevel + 1)) "
    }
  }
}
