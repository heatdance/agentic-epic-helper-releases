# Refresh .cursor/docs/inject-corner.json (ASCII-safe; no secrets or epic JSON bodies).
# Usage: powershell -NoProfile -File .cursor/scripts/refresh-inject-corner.ps1
$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $Root

function Get-AsciiResume {
  param([string]$HandoffPath)
  if (-not (Test-Path $HandoffPath)) { return $null }
  $text = Get-Content $HandoffPath -Raw -Encoding UTF8
  if ($text -notmatch '(?ms)^## Resume\s*\r?\n\s*\r?\n(.+?)\r?\n\r?\n## Next') { return $null }
  $r = ($Matches[1] -replace '\s+', ' ').Trim()
  $r = $r -replace '[^\x09\x0A\x0D\x20-\x7E]', ''
  if ($r.Length -gt 200) { $r = $r.Substring(0, 200) + "..." }
  if ([string]::IsNullOrWhiteSpace($r)) { return $null }
  return $r
}

$resume = Get-AsciiResume (Join-Path $Root "qa-handoff.md")
$generated = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

$out = [ordered]@{
  v = 1
  generated = $generated
  note = "Refreshed by refresh-inject-corner.ps1 on sessionStart. Read qa-handoff.md each substantive turn; inject runs once per Cursor session."
  docClose = @{
    pending = $false
    hint = "Update qa-handoff.md Resume/Next/Anchors + Last updated after substantive Action (harness-principles section 14; not machine-detected)."
    reasons = @()
  }
  t0 = @{
    read = @("qa-handoff.md", "AGENTS.md")
    doctrine = "docs/harness-principles.md"
    routing = "docs/harness-map.json"
  }
  actionOpen = @(
    "Read inject-corner.json once per session; then qa-handoff.md for Resume/Next/Anchors every substantive turn."
    "Classify Conversation vs Action (harness-principles section 14)."
    "Pipeline triggers: high confidence for declared scope (intent-corner.mdc)."
    "Low confidence on non-pipeline Action: Blocking + Questions only; no writes."
    "Inspect large JSON with jq (jq-json.mdc); verifiers authoritative for epics."
  )
}
if ($resume) { $out.currentResume = $resume }

$path = Join-Path $Root ".cursor/docs/inject-corner.json"
$json = $out | ConvertTo-Json -Depth 8 -Compress
if ($json.Length -gt 5120) {
  Write-Warning "inject-corner.json exceeds 5KB; trim before commit."
}
$utf8 = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($path, $json, $utf8)
Write-Host "OK refreshed $path"
