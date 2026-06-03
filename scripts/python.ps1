param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]] $Arguments
)

$root = Split-Path -Parent $PSScriptRoot
$backendPath = Join-Path $root "backend"

if (Test-Path $backendPath) {
  $env:PYTHONPATH = "$backendPath;$env:PYTHONPATH"
}

& (Join-Path $root ".venv\Scripts\python.exe") @Arguments
exit $LASTEXITCODE
