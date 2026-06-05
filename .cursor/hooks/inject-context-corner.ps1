# sessionStart only — refresh inject-corner.json and inject additional_context once per session.
$ErrorActionPreference = "Continue"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $Root

$inputJson = [Console]::In.ReadToEnd()
$event = "sessionStart"
try {
  $obj = $inputJson | ConvertFrom-Json
  if ($obj.hook_event_name) { $event = $obj.hook_event_name }
} catch {}

if ($event -ne "sessionStart") {
  @{ continue = $true } | ConvertTo-Json -Compress
  exit 0
}

& (Join-Path $Root ".cursor/scripts/refresh-inject-corner.ps1")
if ($LASTEXITCODE -ne 0) {
  @{ additional_context = "Corner harness: refresh-inject-corner.ps1 failed; read qa-handoff.md and docs/grounding-integration.json." } | ConvertTo-Json -Compress
  exit 0
}

$path = Join-Path $Root ".cursor/docs/inject-corner.json"
$ctx = ""
if (Test-Path $path) {
  $bytes = [System.IO.File]::ReadAllBytes($path)
  if ($bytes.Length -gt 5120) {
    $ctx = "Corner harness: read .cursor/docs/inject-corner.json (truncated in hook; open file). T0 anchors inside."
  } else {
    $utf8 = New-Object System.Text.UTF8Encoding $false
    $ctx = "Corner harness snapshot:`n" + $utf8.GetString($bytes)
  }
}

@{ additional_context = $ctx } | ConvertTo-Json -Compress
