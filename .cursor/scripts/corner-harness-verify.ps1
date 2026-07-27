# Corner harness hygiene. Run from repo root.
# Usage: powershell -NoProfile -File .cursor/scripts/corner-harness-verify.ps1 [-Profile minimal|full]
param(
  [ValidateSet("minimal", "full")]
  [string]$Profile = "minimal"
)

$ErrorActionPreference = "Continue"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $Root

$passed = [System.Collections.Generic.List[string]]::new()
$failed = [System.Collections.Generic.List[string]]::new()

function Pass([string]$n) { $script:passed.Add($n); Write-Host "OK $n" -ForegroundColor Green }
function Fail([string]$n, [string]$d) {
  $script:failed.Add($n)
  Write-Host "FAIL $n" -ForegroundColor Red
  if ($d) { Write-Host "  $d" -ForegroundColor DarkRed }
}

# jq_present
if (Get-Command jq -ErrorAction SilentlyContinue) { Pass "jq_present" } else { Fail "jq_present" "install jq (see automation/docs/jq.md)" }

# corner_rules
@(
  ".cursor/rules/intent-corner.mdc",
  ".cursor/rules/delegation-corner.mdc",
  ".cursor/rules/preservation-corner.mdc",
  ".cursor/rules/communication-corner.mdc"
) | ForEach-Object {
  if (Test-Path $_) { Pass "exists_$_" } else { Fail "exists_$_" "missing" }
}

# grounding_integration
$gi = "docs/grounding-integration.json"
if (Test-Path $gi) {
  if (Get-Command jq -ErrorAction SilentlyContinue) {
    jq empty $gi 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) { Pass "grounding_integration" } else { Fail "grounding_integration" "invalid JSON" }
  }
} else { Fail "grounding_integration" "missing" }

# slash_commands (6 only)
@(
  ".cursor/commands/epic-helper.md",
  ".cursor/commands/epic-stats.md",
  ".cursor/commands/epic-calibrate.md",
  ".cursor/commands/clean-release.md",
  ".cursor/commands/release-notes.md",
  ".cursor/commands/crtqa-console.md"
) | ForEach-Object {
  if (Test-Path $_) { Pass "exists_$_" } else { Fail "exists_$_" "missing" }
}

$removedCmd = @(
  ".cursor/commands/better-prompt.md",
  ".cursor/commands/better-skill.md",
  ".cursor/commands/teach.md",
  ".cursor/commands/crtqa-helper.md",
  ".cursor/commands/crtqa-stats.md",
  ".cursor/commands/crtqa-calibrate.md",
  ".cursor/commands/clean.md",
  ".cursor/commands/crtqa-env.md"
)
foreach ($rc in $removedCmd) {
  if (-not (Test-Path $rc)) { Pass "removed_$rc" } else { Fail "removed_$rc" "should be deleted" }
}

if (Test-Path ".cursor/skills") { Fail "skills_dir_absent" ".cursor/skills must not exist" } else { Pass "skills_dir_absent" }

# epic-helper (minimal + full)
$helperContract = "docs/epic-helper-contract.json"
$helperCmd = ".cursor/commands/epic-helper.md"
if ((Test-Path $helperContract) -and (Get-Command jq -ErrorAction SilentlyContinue)) {
  jq empty $helperContract 2>$null | Out-Null
  if ($LASTEXITCODE -ne 0) { Fail "epic_helper_contract_valid" "invalid JSON" }
  else {
    $hv = jq -r '.epicHelper.version // empty' $helperContract 2>$null
    if ($hv -eq "7") { Pass "epic_helper_contract_valid" } else { Fail "epic_helper_contract_valid" "epicHelper.version=$hv expected 7" }
  }
} elseif (-not (Test-Path $helperContract)) {
  Fail "epic_helper_contract_valid" "missing $helperContract"
}
@(
  $helperCmd,
  "epics/templates/helper-session-ref.json",
  "automation/tools/crtqa_console_probe.py",
  "automation/tools/crtqa_console_common.py",
  "automation/tools/epic_helper_affordances.py",
  ".cursor/pipelines/ground.md",
  ".cursor/pipelines/coverage-reinforce.md",
  "docs/draft-truth-contract.json",
  "docs/discover-linker-contract.json",
  "docs/scenario-groups-contract.json",
  "docs/test-prep-scenario-intent-contract.json"
) | ForEach-Object {
  if (Test-Path $_) { Pass "exists_$_" } else { Fail "exists_$_" "missing" }
}

# epic-stats contract
$statsContract = "docs/epic-stats-contract.json"
if ((Test-Path $statsContract) -and (Get-Command jq -ErrorAction SilentlyContinue)) {
  jq empty $statsContract 2>$null | Out-Null
  if ($LASTEXITCODE -ne 0) { Fail "epic_stats_contract_valid" "invalid JSON" }
  else {
    $sr = jq -r '.paths.stats_root // empty' $statsContract 2>$null
    if ($sr -eq "stats/epic-stats") { Pass "epic_stats_contract_valid" } else { Fail "epic_stats_contract_valid" "stats_root=$sr" }
  }
} elseif (-not (Test-Path $statsContract)) {
  Fail "epic_stats_contract_valid" "missing $statsContract"
}

# auto-tests (minimal + full; no  command)
$atContract = "docs/auto-tests-contract.json"
if ((Test-Path $atContract) -and (Get-Command jq -ErrorAction SilentlyContinue)) {
  jq empty $atContract 2>$null | Out-Null
  if ($LASTEXITCODE -eq 0) { Pass "auto_tests_contract_valid" } else { Fail "auto_tests_contract_valid" "invalid JSON" }
} elseif (-not (Test-Path $atContract)) {
  Fail "auto_tests_contract_valid" "missing $atContract"
}
@(
  "auto-tests/README.md",
  "auto-tests/specs/schema.json",
  "auto-tests/specs/smoke-manifest.json"
) | ForEach-Object {
  if (Test-Path $_) { Pass "exists_$_" } else { Fail "exists_$_" "missing" }
}

$smokeManifest = "auto-tests/specs/smoke-manifest.json"
if ((Test-Path $smokeManifest) -and (Get-Command jq -ErrorAction SilentlyContinue)) {
  jq empty $smokeManifest 2>$null | Out-Null
  if ($LASTEXITCODE -ne 0) { Fail "smoke_manifest_valid" "invalid JSON" }
  else {
    $rc = jq -r '.row_count // 0' $smokeManifest 2>$null
    $rl = jq -r '.rows | length' $smokeManifest 2>$null
    $bad = jq -r '[.rows[] | select(.id == null or .crtqa_key == null or .status == null)] | length' $smokeManifest 2>$null
    if ($rc -eq "32" -and $rl -eq "32" -and $bad -eq "0") { Pass "smoke_manifest_valid" }
    else { Fail "smoke_manifest_valid" "row_count=$rc rows=$rl bad_rows=$bad" }
  }
} elseif (-not (Test-Path $smokeManifest)) {
  Fail "smoke_manifest_valid" "missing $smokeManifest"
}

# epic-helper golden (full profile only)
if ($Profile -eq "full" -and (Get-Command jq -ErrorAction SilentlyContinue)) {
  $helperGolden = "automation/tools/fixtures/operator-assist/epic-helper-golden.json"
  $ehv = jq -r '.epicHelper.version // empty' $helperContract 2>$null
  if ($ehv -eq "") { $ehv = jq -r '.expectHelperVersion // empty' $helperGolden 2>$null }
  if (Test-Path $helperGolden) {
    jq empty $helperGolden 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { Fail "epic_helper_golden_valid" "invalid JSON" }
    else {
      $gev = jq -r '.expectHelperVersion // empty' $helperGolden 2>$null
      $cc = jq -r '(.cases | length) // 0' $helperGolden 2>$null
      $cv = jq -r '.epicHelper.version // empty' $helperContract 2>$null
      if ($gev -eq $cv -and [int]$cc -ge 1) { Pass "epic_helper_golden_valid" }
      else { Fail "epic_helper_golden_valid" "expectHelperVersion=$gev cases=$cc expected v=$cv" }
    }
  } else { Fail "epic_helper_golden_valid" "missing $helperGolden" }
  if (Test-Path ".cursor/scripts/refresh-inject-corner.ps1") { Pass "refresh_inject_script" } else { Fail "refresh_inject_script" "missing" }
}

if ($Profile -eq "full") {
  if (Test-Path ".cursor/hooks.json") {
    $hooks = Get-Content ".cursor/hooks.json" -Raw | ConvertFrom-Json
    $bsp = $hooks.hooks.beforeSubmitPrompt
    if ($null -ne $bsp -and @($bsp).Count -gt 0) {
      Fail "hooks_session_start_only" "beforeSubmitPrompt must be empty or absent (sessionStart inject only)"
    } else {
      Pass "hooks_session_start_only"
    }
    $ok = $true
    foreach ($prop in $hooks.hooks.PSObject.Properties) {
      foreach ($entry in $hooks.hooks.($prop.Name)) {
        $c = [string]$entry.command
        if ($c -notmatch 'powershell' -or $c -notmatch '\.ps1') { $ok = $false; Fail "hooks_json_ps1" $c }
      }
    }
    if ($ok) { Pass "hooks_json_ps1" }
  } else { Fail "hooks_json_ps1" "missing hooks.json" }

  $hookSh = Get-ChildItem ".cursor/hooks" -Filter "*.sh" -ErrorAction SilentlyContinue
  if ($hookSh -and $hookSh.Count -gt 0) { Fail "no_hook_sh" ($hookSh.Name -join ", ") } else { Pass "no_hook_sh" }

  $snap = ".cursor/docs/inject-corner.json"
  if (Test-Path $snap) {
    $len = (Get-Item $snap).Length
    if ($len -le 5120) { Pass "inject_corner_size" } else { Fail "inject_corner_size" "$len bytes" }
    try {
      $s = Get-Content $snap -Raw | ConvertFrom-Json
      if ($s.docClose.pending -is [bool]) { Pass "inject_corner_doc_close" } else { Fail "inject_corner_doc_close" "missing docClose.pending" }
    } catch { Fail "inject_corner_doc_close" "parse error" }
    $raw = [System.IO.File]::ReadAllText((Join-Path $Root $snap))
    $nonAscii = $false
    foreach ($ch in $raw.ToCharArray()) {
      if ([int][char]$ch -gt 127) { $nonAscii = $true; break }
    }
    if ($nonAscii) { Fail "inject_corner_no_mojibake" "non-ASCII characters in inject-corner.json" }
    else { Pass "inject_corner_no_mojibake" }
  } else { Fail "inject_corner_size" "missing inject-corner.json" }

  foreach ($hook in @("inject-context-corner.ps1", "guard-paths-corner.ps1")) {
    if (Test-Path ".cursor/hooks/$hook") { Pass "hook_$hook" } else { Fail "hook_$hook" "missing" }
  }
}

Write-Host ""
if ($failed.Count -eq 0) {
  Write-Host "OK: corner-harness-verify ($Profile) passed" -ForegroundColor Green
  exit 0
}
Write-Host "VERIFY FAILED ($Profile): $($failed -join ', ')" -ForegroundColor Red
exit 1
