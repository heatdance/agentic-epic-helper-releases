# COVERAGE verifier fixtures

Regression artifacts for `coverage_verify.py` topology and principal modes.

## PowerShell examples

```powershell
# Round 1 topology (legacy-safe)
python automation/tools/coverage_verify.py --mode emit --strict-topology `
  --coverage automation/tools/fixtures/coverage/coverage-594-shell-minimal.json `
  --ref epics/CRT-594/CRT-594-ref.json `
  --md automation/tools/fixtures/coverage/coverage-594-shell-minimal.md

# Round 2 principal — 594 shell + setup thread
python automation/tools/coverage_verify.py --mode emit --strict-topology --strict-principal `
  --coverage automation/tools/fixtures/coverage/coverage-594-shell-principal-minimal.json `
  --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json `
  --md automation/tools/fixtures/coverage/coverage-594-shell-principal-minimal.md

# 639 formula — focus copy only (metrics short-circuit)
python automation/tools/coverage_verify.py --mode emit --strict-principal `
  --coverage automation/tools/fixtures/coverage/coverage-639-formula-principal-minimal.json `
  --ref automation/tools/fixtures/epic-prep/ref-639-topology-minimal.json `
  --md automation/tools/fixtures/coverage/coverage-639-formula-principal-minimal.md

# Principal-only mode
python automation/tools/coverage_verify.py --mode principal `
  --coverage automation/tools/fixtures/coverage/coverage-594-shell-principal-minimal.json `
  --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json `
  --md automation/tools/fixtures/coverage/coverage-594-shell-principal-minimal.md

# Round 2 reinforce principal — 594 shell + setup fixture merge
python automation/tools/coverage_verify.py --mode reinforce --strict-topology --strict-principal `
  --coverage automation/tools/fixtures/coverage/coverage-594-shell-reinforce-principal-minimal.json `
  --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json `
  --discover automation/tools/fixtures/discover/discover-594-shell-principal-minimal.json `
  --md automation/tools/fixtures/coverage/coverage-594-shell-reinforce-principal-minimal.md

# 639 formula — deferral skip-deepen
python automation/tools/coverage_verify.py --mode reinforce --strict-principal `
  --coverage automation/tools/fixtures/coverage/coverage-639-formula-reinforce-principal-minimal.json `
  --ref automation/tools/fixtures/epic-prep/ref-639-topology-minimal.json `
  --discover automation/tools/fixtures/discover/discover-639-formula-principal-minimal.json

# Negative — missing provision merge (expect exit 1)
python automation/tools/coverage_verify.py --mode reinforce --strict-principal `
  --coverage automation/tools/fixtures/coverage/coverage-reinforce-principal-bad-missing-fixture-merge.json `
  --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json `
  --discover automation/tools/fixtures/discover/discover-594-shell-principal-minimal.json
```

## Files

| Fixture | Role |
|---------|------|
| `coverage-594-shell-minimal.*` | Round 1 shell_first; `--strict-topology` without principal |
| `coverage-594-shell-principal-minimal.*` | Setup H2 + focus copy; `--strict-principal` pass |
| `coverage-639-formula-minimal.*` | Round 1 formula_first |
| `coverage-639-formula-principal-minimal.*` | Focus copy + keyed deferrals |
| `coverage-594-shell-reinforce-principal-minimal.*` | Pass-2 principal; setup fixture merge; `--mode reinforce --strict-principal` |
| `coverage-639-formula-reinforce-principal-minimal.*` | Pass-2 principal; deferral skip-deepen |
| `coverage-reinforce-principal-bad-missing-fixture-merge.json` | `--mode reinforce --strict-principal` exit **1** |
| `coverage-principal-bad-blanket-deferral.*` | `--strict-principal` exit **1** |

Contracts: [docs/coverage-principal-contract.json](../../../docs/coverage-principal-contract.json), [docs/coverage-reinforce-principal-contract.json](../../../docs/coverage-reinforce-principal-contract.json).
