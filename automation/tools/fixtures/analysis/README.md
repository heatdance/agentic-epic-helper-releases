# ANALYSE fixtures

Minimal `-analysis.json` + `.md` pairs for `analysis_verify.py` regression.

## Commands

**Round 1 topology (594 delivery):**

```powershell
python automation/tools/analysis_verify.py --mode emit --strict-topology `
  --analysis automation/tools/fixtures/analysis/analysis-594-shell-minimal.json `
  --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json `
  --coverage automation/tools/fixtures/coverage/coverage-594-shell-minimal.json `
  --md automation/tools/fixtures/analysis/analysis-594-shell-minimal.md
```

**Round 1 formula deferral (639 legacy calculation_contract path):**

```powershell
python automation/tools/analysis_verify.py --mode emit `
  --analysis automation/tools/fixtures/analysis/analysis-639-formula-minimal.json `
  --md automation/tools/fixtures/analysis/analysis-639-formula-minimal.md
```

**Round 2 principal — keyed deferrals (639):**

```powershell
python automation/tools/analysis_verify.py --mode emit --strict-principal `
  --analysis automation/tools/fixtures/analysis/analysis-639-formula-principal-minimal.json `
  --ref automation/tools/fixtures/epic-prep/ref-639-topology-minimal.json `
  --coverage automation/tools/fixtures/coverage/coverage-639-formula-principal-minimal.json `
  --md automation/tools/fixtures/analysis/analysis-639-formula-principal-minimal.md
```

**Round 2 principal — delivery linked obligation_id (594):**

```powershell
python automation/tools/analysis_verify.py --mode emit --strict-topology --strict-principal `
  --analysis automation/tools/fixtures/analysis/analysis-594-shell-principal-minimal.json `
  --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json `
  --coverage automation/tools/fixtures/coverage/coverage-594-shell-principal-minimal.json `
  --md automation/tools/fixtures/analysis/analysis-594-shell-principal-minimal.md
```

**Negative — silent zero gaps with deferrals:**

```powershell
python automation/tools/analysis_verify.py --mode principal `
  --analysis automation/tools/fixtures/analysis/analysis-principal-bad-empty-gaps.json `
  --ref automation/tools/fixtures/epic-prep/ref-639-topology-minimal.json `
  --coverage automation/tools/fixtures/coverage/coverage-639-formula-principal-minimal.json
# expect exit 1
```

## Fixture table

| Fixture | `--strict-topology` | `--strict-principal` | Expected |
|---------|---------------------|----------------------|----------|
| `analysis-594-shell-minimal.*` | pass | n/a (no deferrals) | Round 1 delivery |
| `analysis-639-formula-minimal.*` | n/a | n/a | Round 1 legacy deferral |
| `analysis-639-formula-principal-minimal.*` | n/a | pass | Two keyed deferral gaps |
| `analysis-594-shell-principal-minimal.*` | pass | pass | Delivery + obligation_id |
| `analysis-principal-bad-empty-gaps.json` | n/a | exit **1** | Empty gaps honesty failure |
