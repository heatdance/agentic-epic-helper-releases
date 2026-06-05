# afterFileEdit — advisory only: returns agent_message when path is outside Corner allowlist.
# Does NOT block the IDE from saving files. See HOW-TO.md (Path guard).
$ErrorActionPreference = "Continue"
$inputJson = [Console]::In.ReadToEnd()
$path = ""
try {
  $o = $inputJson | ConvertFrom-Json
  if ($o.file_path) { $path = $o.file_path }
  elseif ($o.path) { $path = $o.path }
} catch {}

if (-not $path) { "{}"; exit 0 }

$norm = $path -replace '\\', '/'
$leaf = Split-Path -Leaf $norm

$allowPatterns = @(
  '^\.cursor/',
  '^epics/',
  '^docs/',
  '^automation/',
  '^auto-tests/',
  '^releases/',
  '^stats/',
  '^\.agents/',
  '^qa-handoff\.md$',
  '^README\.md$',
  '^AGENTS\.md$',
  '^HOW-TO\.md$'
)

$allowed = $false
foreach ($p in $allowPatterns) {
  if ($norm -match $p) { $allowed = $true; break }
}

if ($allowed) {
  "{}"
  exit 0
}

$msg = "Corner structure: unexpected write outside allowlist (epics/, docs/, automation/, auto-tests/, .cursor/, releases/, stats/, qa-handoff.md, root README|AGENTS|HOW-TO). Path: $path"
@{ agent_message = $msg } | ConvertTo-Json -Compress
