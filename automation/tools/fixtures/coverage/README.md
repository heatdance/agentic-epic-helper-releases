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
| `crt635-skeleton-bad-*` | Build-43 stub skeleton — `--mode obligations` exit **1** (`tag_level_stub_check`, `single_stub_subsection`, `machine_deferral_reason`, `availability_misplaced`) |
| `crt635-target-good-*` | Target semantics (Prerequisites availability + field checks, no Rounding H2) — `--mode obligations` / `--mode emit --strict-topology` exit **0** |
| `crt635-*-minimal.*` | Compact CRT-635 smoke for atomic field emit |
| `crt635-undercut-bad-ref.json` | D19 negative — `epic_prep_verify --mode ref` exit **1** (`parameter_inventory_undercut`, `snippet_truncated`, `requirement_pass_missing`, `requirement_pass_stale`) |
| `crt677-watchlist-portability-ref.json` | Non-CRT-635 portability — variation gates on a Watchlist epic; `--mode ref` exit **0** |

```powershell
# Negative — stub skeleton (expect exit 1)
python automation/tools/coverage_verify.py --mode obligations `
  --coverage automation/tools/fixtures/coverage/crt635-skeleton-bad-coverage.json `
  --ref automation/tools/fixtures/coverage/crt635-skeleton-bad-ref.json `
  --md automation/tools/fixtures/coverage/crt635-skeleton-bad.md

# Positive — target form (expect exit 0)
python automation/tools/coverage_verify.py --mode obligations `
  --coverage automation/tools/fixtures/coverage/crt635-target-good-coverage.json `
  --ref automation/tools/fixtures/coverage/crt635-target-good-ref.json `
  --md automation/tools/fixtures/coverage/crt635-target-good.md

# D19 negative — inventory undercut and truncated snippet (expect exit 1)
python automation/tools/epic_prep_verify.py --mode ref `
  --ref automation/tools/fixtures/coverage/crt635-undercut-bad-ref.json

# D19 portability — same gates on a non-CRT-635 epic (expect exit 0)
python automation/tools/epic_prep_verify.py --mode ref `
  --ref automation/tools/fixtures/coverage/crt677-watchlist-portability-ref.json
```

Contracts: [docs/coverage-principal-contract.json](../../../docs/coverage-principal-contract.json), [docs/coverage-reinforce-principal-contract.json](../../../docs/coverage-reinforce-principal-contract.json), [docs/coverage-obligation-contract.json](../../../docs/coverage-obligation-contract.json).
