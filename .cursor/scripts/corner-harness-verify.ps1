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

# coach_contract
$contract = "docs/operator-assist-contract.json"
if (Test-Path $contract) {
  if (Get-Command jq -ErrorAction SilentlyContinue) {
    jq empty $contract 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
      $bp = jq -r '.betterPrompt.version // empty' $contract 2>$null
      $bs = jq -r '.betterSkill.version // empty' $contract 2>$null
      if ($bp -eq "1" -and $bs -eq "1") { Pass "coach_contract" } else { Fail "coach_contract" "version mismatch bp=$bp bs=$bs" }
    } else { Fail "coach_contract" "invalid JSON" }
  }
} else { Fail "coach_contract" "missing $contract" }

# coach_commands
@(
  ".cursor/commands/better-prompt.md",
  ".cursor/commands/better-skill.md",
  ".cursor/skills/better-prompt/SKILL.md",
  ".cursor/skills/better-skill/SKILL.md"
) | ForEach-Object {
  if (Test-Path $_) { Pass "exists_$_" } else { Fail "exists_$_" "missing" }
}

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

# skill_patterns
$sp = "docs/skill-authoring-patterns.json"
if ((Test-Path $sp) -and (Get-Command jq -ErrorAction SilentlyContinue)) {
  jq empty $sp 2>$null | Out-Null
  if ($LASTEXITCODE -eq 0) { Pass "skill_patterns" } else { Fail "skill_patterns" "invalid JSON" }
} elseif (-not (Test-Path $sp)) {
  Fail "skill_patterns" "missing $sp"
}

# karpathy (minimal + full)
$kgSkill = ".cursor/skills/karpathy-guidelines/SKILL.md"
$kgContract = "docs/karpathy-guidelines-contract.json"
if (Test-Path $kgSkill) { Pass "exists_$kgSkill" } else { Fail "exists_$kgSkill" "missing" }
if ((Test-Path $kgContract) -and (Get-Command jq -ErrorAction SilentlyContinue)) {
  jq empty $kgContract 2>$null | Out-Null
  if ($LASTEXITCODE -ne 0) { Fail "karpathy_contract_valid" "invalid JSON" }
  else {
    $kv = jq -r '.version // empty' $kgContract 2>$null
    $ks = jq -r '.skill // empty' $kgContract 2>$null
    if ($kv -eq "1" -and $ks -eq $kgSkill -and (Test-Path $ks)) { Pass "karpathy_contract_valid" }
    else { Fail "karpathy_contract_valid" "version=$kv skill=$ks expected v=1 path=$kgSkill" }
  }
} elseif (-not (Test-Path $kgContract)) {
  Fail "karpathy_contract_valid" "missing $kgContract"
}

# crtqa-helper (minimal + full)
$helperContract = "docs/crtqa-helper-contract.json"
$helperCmd = ".cursor/commands/crtqa-helper.md"
$helperSkill = ".cursor/skills/crtqa-helper/SKILL.md"
if ((Test-Path $helperContract) -and (Get-Command jq -ErrorAction SilentlyContinue)) {
  jq empty $helperContract 2>$null | Out-Null
  if ($LASTEXITCODE -ne 0) { Fail "crtqa_helper_contract_valid" "invalid JSON" }
  else {
    $hv = jq -r '.crtqaHelper.version // empty' $helperContract 2>$null
    if ($hv -eq "1") { Pass "crtqa_helper_contract_valid" } else { Fail "crtqa_helper_contract_valid" "crtqaHelper.version=$hv expected 1" }
  }
} elseif (-not (Test-Path $helperContract)) {
  Fail "crtqa_helper_contract_valid" "missing $helperContract"
}
@(
  $helperCmd,
  $helperSkill,
  "epics/templates/helper-session-ref.json",
  "automation/tools/crtqa_helper_affordances.py",
  ".cursor/pipelines/coverage-reinforce.md"
) | ForEach-Object {
  if (Test-Path $_) { Pass "exists_$_" } else { Fail "exists_$_" "missing" }
}

# teach (minimal + full)
$atContract = "docs/auto-tests-contract.json"
$teachCmd = ".cursor/commands/teach.md"
$teachSkill = ".cursor/skills/teach/SKILL.md"
if ((Test-Path $atContract) -and (Get-Command jq -ErrorAction SilentlyContinue)) {
  jq empty $atContract 2>$null | Out-Null
  if ($LASTEXITCODE -ne 0) { Fail "auto_tests_contract_valid" "invalid JSON" }
  else {
    $tv = jq -r '.teach.version // empty' $atContract 2>$null
    if ($tv -eq "2") {
      Pass "auto_tests_contract_valid"
      $opRoot = jq -r '.teach.operator_profile.root // empty' $atContract 2>$null
      if ($opRoot -eq "temp/profile/") { Pass "teach_operator_profile_block" } else { Fail "teach_operator_profile_block" "operator_profile.root=$opRoot" }
    } else { Fail "auto_tests_contract_valid" "teach.version=$tv expected 2" }
  }
} elseif (-not (Test-Path $atContract)) {
  Fail "auto_tests_contract_valid" "missing $atContract"
}
@(
  $teachCmd,
  $teachSkill,
  "auto-tests/README.md",
  "auto-tests/.teacher-session.example.json",
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

$smokeSchema = "auto-tests/specs/schema.json"
if ((Test-Path $smokeSchema) -and (Get-Command jq -ErrorAction SilentlyContinue)) {
  jq empty $smokeSchema 2>$null | Out-Null
  if ($LASTEXITCODE -eq 0) { Pass "smoke_schema_valid" } else { Fail "smoke_schema_valid" "invalid JSON" }
} elseif (-not (Test-Path $smokeSchema)) {
  Fail "smoke_schema_valid" "missing $smokeSchema"
}

# coach_goldens (full profile only; needs jq)
if ($Profile -eq "full" -and (Get-Command jq -ErrorAction SilentlyContinue)) {
  $ev = jq -r '.betterPrompt.version // empty' $contract 2>$null
  $bpGolden = "automation/tools/fixtures/operator-assist/better-prompt-golden.json"
  if (Test-Path $bpGolden) {
    jq empty $bpGolden 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { Fail "better_prompt_golden_valid" "invalid JSON" }
    else {
      $gev = jq -r '.expectCoachVersion // empty' $bpGolden 2>$null
      $cc = jq -r '(.cases | length) // 0' $bpGolden 2>$null
      if ($gev -eq $ev -and [int]$cc -ge 1) { Pass "better_prompt_golden_valid" }
      else { Fail "better_prompt_golden_valid" "expectCoachVersion=$gev cases=$cc expected v=$ev" }
    }
  } else { Fail "better_prompt_golden_valid" "missing $bpGolden" }
  $bsGolden = "automation/tools/fixtures/operator-assist/better-skill-golden.json"
  $esv = jq -r '.betterSkill.version // empty' $contract 2>$null
  if (Test-Path $bsGolden) {
    jq empty $bsGolden 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { Fail "better_skill_golden_valid" "invalid JSON" }
    else {
      $gev = jq -r '.expectCoachVersion // empty' $bsGolden 2>$null
      $cc = jq -r '(.cases | length) // 0' $bsGolden 2>$null
      if ($gev -eq $esv -and [int]$cc -ge 1) { Pass "better_skill_golden_valid" }
      else { Fail "better_skill_golden_valid" "expectCoachVersion=$gev cases=$cc expected v=$esv" }
    }
  } else { Fail "better_skill_golden_valid" "missing $bsGolden" }
  $teachGolden = "automation/tools/fixtures/operator-assist/teach-golden.json"
  $etv = jq -r '.teach.version // empty' $atContract 2>$null
  if (Test-Path $teachGolden) {
    jq empty $teachGolden 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { Fail "teach_golden_valid" "invalid JSON" }
    else {
      $gev = jq -r '.expectTeachVersion // empty' $teachGolden 2>$null
      $cc = jq -r '(.cases | length) // 0' $teachGolden 2>$null
      if ($gev -eq $etv -and [int]$cc -ge 1) { Pass "teach_golden_valid" }
      else { Fail "teach_golden_valid" "expectTeachVersion=$gev cases=$cc expected v=$etv" }
    }
  } else { Fail "teach_golden_valid" "missing $teachGolden" }
  $helperGolden = "automation/tools/fixtures/operator-assist/crtqa-helper-golden.json"
  $ehv = jq -r '.crtqaHelper.version // empty' $helperContract 2>$null
  if (Test-Path $helperGolden) {
    jq empty $helperGolden 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { Fail "crtqa_helper_golden_valid" "invalid JSON" }
    else {
      $gev = jq -r '.expectHelperVersion // empty' $helperGolden 2>$null
      $cc = jq -r '(.cases | length) // 0' $helperGolden 2>$null
      if ($gev -eq $ehv -and [int]$cc -ge 1) { Pass "crtqa_helper_golden_valid" }
      else { Fail "crtqa_helper_golden_valid" "expectHelperVersion=$gev cases=$cc expected v=$ehv" }
    }
  } else { Fail "crtqa_helper_golden_valid" "missing $helperGolden" }
  @(
    ".cursor/skills/better-prompt/examples.md",
    ".cursor/skills/better-skill/examples.md",
    ".cursor/skills/teach/examples.md"
  ) | ForEach-Object {
    if (Test-Path $_) { Pass "exists_$_" } else { Fail "exists_$_" "missing" }
  }
  if (Test-Path ".cursor/scripts/refresh-inject-corner.ps1") { Pass "refresh_inject_script" } else { Fail "refresh_inject_script" "missing" }
}

if ($Profile -eq "full") {
  # hooks_session_start_only
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
