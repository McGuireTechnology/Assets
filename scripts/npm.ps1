param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]] $Arguments
)

$root = Split-Path -Parent $PSScriptRoot
$nodePath = Join-Path $root ".tools\node"
$env:PATH = "$nodePath;$env:PATH"
$env:npm_config_cache = Join-Path $root ".tools\npm-cache"

& (Join-Path $nodePath "npm.cmd") @Arguments
exit $LASTEXITCODE
