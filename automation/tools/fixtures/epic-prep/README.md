# EPIC-PREP verifier fixtures

Regression refs for `epic_prep_verify.py` topology and principal modes.

## PowerShell examples

```powershell
# 639 metrics — topology only (legacy-safe without principal)
python automation/tools/epic_prep_verify.py --mode ref --strict-topology `
  --ref automation/tools/fixtures/epic-prep/ref-639-topology-minimal.json

# 639 metrics — principal short-circuit (focus only; no setup thread required)
python automation/tools/epic_prep_verify.py --mode ref --strict-principal `
  --ref automation/tools/fixtures/epic-prep/ref-639-topology-minimal.json

# 594 widget — topology + principal pass
python automation/tools/epic_prep_verify.py --mode ref --strict-topology --strict-principal `
  --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json

# Principal-only mode
python automation/tools/epic_prep_verify.py --mode principal `
  --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json

# Negative — missing environment_setup thread (expect exit 1)
python automation/tools/epic_prep_verify.py --mode principal `
  --ref automation/tools/fixtures/epic-prep/ref-principal-bad-missing-setup.json
```

## Files

| Fixture | Role |
|---------|------|
| `ref-639-topology-minimal.json` | `metrics_calculation`; topology pass; principal optional focus |
| `ref-594-topology-full.json` | `widget_ui`; full topology + principal threads/hints |
| `ref-principal-bad-missing-setup.json` | `--strict-principal` / `--mode principal` exit **1** |

Contract: [docs/epic-prep-principal-contract.json](../../../docs/epic-prep-principal-contract.json).
