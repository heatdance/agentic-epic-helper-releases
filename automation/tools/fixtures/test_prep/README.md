# TEST-PREP verifier fixtures (v3.1)

Minimal artefacts for `test_prep_verify.py` regression checks. Not production epic data.

## Files

| File | Role |
|------|------|
| `coverage_snippet.json` | Minimal coverage checks for plan lint |
| `plan_tb002_minimal.json` | 5-row `stateful_ladder` plan for tb-002 |
| `tests_tb002_bad_expand.json` | 26 actions / 10 unique (bad expansion) |
| `tests_tb002_good_skeleton.json` | 5 actions / 5 results (good) |
| `plan_config_posture.json` | 2-row config bundle (non-ladder) |
| `tests_config_posture_ok.json` | 3 actions for 2 rows (no single-pair gate) |

## Commands (from repo root)

```powershell
$fix = "automation/tools/fixtures/test_prep"
$cov = "$fix/coverage_snippet.json"

# Bad tb-002 — expect exit 1
python automation/tools/test_prep_verify.py --mode draft `
  --coverage $cov --tests "$fix/tests_tb002_bad_expand.json" `
  --bundle-id tb-002 --plan "$fix/plan_tb002_minimal.json"

# Good tb-002 — expect exit 0
python automation/tools/test_prep_verify.py --mode draft `
  --coverage $cov --tests "$fix/tests_tb002_good_skeleton.json" `
  --bundle-id tb-002 --plan "$fix/plan_tb002_minimal.json"

# Config posture — not subject to strict outline equality
python automation/tools/test_prep_verify.py --mode draft `
  --coverage $cov --tests "$fix/tests_config_posture_ok.json" `
  --bundle-id tb-001 --plan "$fix/plan_config_posture.json"

# Merge bad — expect exit 1
python automation/tools/test_prep_verify.py --mode merge `
  --coverage $cov --tests "$fix/tests_tb002_bad_expand.json" `
  --plan "$fix/plan_tb002_minimal.json"
```

## Archived CRT-639 (optional manual check)

After v3.1, archived `epics/CRT-639/context/CRT-639-tests.json` tb-002 should fail `draft`/`merge` when paired with a 5-row plan (no regen in harness PR).
