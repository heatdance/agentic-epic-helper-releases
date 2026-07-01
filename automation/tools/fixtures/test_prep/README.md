# TEST-PREP verifier fixtures (v3.1 + topology)

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
| `plan-639-formula-minimal.json` | Plan chained from precon-639-formula-minimal |
| `tests-639-formula-minimal.json` | Ladder + config expansion; chk-003 excluded |
| `plan-594-shell-minimal.json` | Plan chained from precon-594-shell-minimal |
| `tests-594-shell-minimal.json` | Widget observation pattern_ref expansion; chk-004 excluded |
| `plan-594-shell-principal-minimal.json` | Principal plan with tb-setup + persona-split bundles |
| `tests-594-shell-principal-minimal.json` | tb-setup pc-setup; retail/dealer split; `--strict-topology --strict-principal` |
| `plan-639-formula-principal-minimal.json` | Principal 639 ladder plan (chk-001 only) |
| `tests-639-formula-principal-minimal.json` | Deferrals excluded; `--strict-principal` |
| `tests-principal-bad-missing-setup.json` | Negative: missing tb-setup → `--mode principal` exit 1 |

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

# Topology 639 — expect exit 0
python automation/tools/test_prep_verify.py --mode tests `
  --coverage automation/tools/fixtures/coverage/coverage-639-formula-reinforce-minimal.json `
  --tests "$fix/tests-639-formula-minimal.json" `
  --plan "$fix/plan-639-formula-minimal.json" `
  --precon automation/tools/fixtures/precon/precon-639-formula-minimal.json `
  --ref epics/CRT-639/CRT-639-ref.json `
  --strict-topology

# Topology 594 — expect exit 0
python automation/tools/test_prep_verify.py --mode tests `
  --coverage automation/tools/fixtures/coverage/coverage-594-shell-reinforce-minimal.json `
  --tests "$fix/tests-594-shell-minimal.json" `
  --plan "$fix/plan-594-shell-minimal.json" `
  --precon automation/tools/fixtures/precon/precon-594-shell-minimal.json `
  --ref epics/CRT-594/CRT-594-ref.json `
  --strict-topology

# Principal 594 — expect exit 0
python automation/tools/test_prep_verify.py --mode tests `
  --coverage automation/tools/fixtures/coverage/coverage-594-shell-reinforce-principal-minimal.json `
  --tests "$fix/tests-594-shell-principal-minimal.json" `
  --plan "$fix/plan-594-shell-principal-minimal.json" `
  --precon automation/tools/fixtures/precon/precon-594-shell-principal-minimal.json `
  --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json `
  --strict-topology `
  --strict-principal

# Principal bad — expect exit 1
python automation/tools/test_prep_verify.py --mode principal `
  --coverage automation/tools/fixtures/coverage/coverage-594-shell-reinforce-principal-minimal.json `
  --precon automation/tools/fixtures/precon/precon-594-shell-principal-minimal.json `
  --tests "$fix/tests-principal-bad-missing-setup.json" `
  --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json
```

## Archived CRT-639 (optional manual check)

After v3.1, archived `epics/CRT-639/context/CRT-639-tests.json` tb-002 fails `draft`/`merge` when paired with a 5-row plan (no regen in harness PR). Strict-topology requires `--plan`, `--precon`, and `--ref`.
