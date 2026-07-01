# ANALYSE — mechanical verifier

Gate **`-analysis.json`** schema v2. Contracts: [`docs/analysis-gap-contract.json`](../../docs/analysis-gap-contract.json), [`docs/analysis-topology-contract.json`](../../docs/analysis-topology-contract.json), [`docs/analysis-principal-contract.json`](../../docs/analysis-principal-contract.json). Playbook: [`.cursor/pipelines/analysis.md`](../../.cursor/pipelines/analysis.md).

## CLI

**Before finalize (phase 10):**

```powershell
python automation/tools/analysis_verify.py --mode gaps `
  --analysis epics/CRT-642/CRT-642-analysis.json

python automation/tools/analysis_verify.py --mode downstream `
  --analysis epics/CRT-642/CRT-642-analysis.json
```

**After writing `.md` (phase 10 emit):**

```powershell
python automation/tools/analysis_verify.py --mode emit `
  --analysis epics/CRT-642/CRT-642-analysis.json `
  --md epics/CRT-642/CRT-642-analysis.md
```

**Topology lint (phase 10 when ref has `delivery_notes` or unresolved oracle rules):**

```powershell
python automation/tools/analysis_verify.py --mode emit --strict-topology `
  --analysis epics/CRT-594/CRT-594-analysis.json `
  --ref epics/CRT-594/CRT-594-ref.json `
  --coverage epics/CRT-594/CRT-594-coverage.json `
  --md epics/CRT-594/CRT-594-analysis.md
```

**Fixture smoke:**

```powershell
python automation/tools/analysis_verify.py --mode emit --strict-topology `
  --analysis automation/tools/fixtures/analysis/analysis-594-shell-minimal.json `
  --ref epics/CRT-594/CRT-594-ref.json `
  --coverage automation/tools/fixtures/coverage/coverage-594-shell-minimal.json `
  --md automation/tools/fixtures/analysis/analysis-594-shell-minimal.md

python automation/tools/analysis_verify.py --mode emit `
  --analysis automation/tools/fixtures/analysis/analysis-639-formula-minimal.json `
  --md automation/tools/fixtures/analysis/analysis-639-formula-minimal.md

python automation/tools/analysis_verify.py --mode emit --strict-topology `
  --analysis automation/tools/fixtures/analysis/analysis-oracle-unresolved-minimal.json `
  --ref automation/tools/fixtures/analysis/ref-topology-unresolved-oracle.json `
  --coverage automation/tools/fixtures/coverage/coverage-594-shell-minimal.json `
  --md automation/tools/fixtures/analysis/analysis-oracle-unresolved-minimal.md
```

Exit **0** = pass.

## Modes

| Mode | Checks |
|------|--------|
| **gaps** | `schema_version` ≥ 2; gap shape (incl. topology kinds); no `confidence: low`; cap open gaps; no hypothesis `questions[]` |
| **downstream** | `exploration_suppressed[]` shape; no `/temp/`; no CRTQA keys |
| **emit** | gaps + downstream + md has `## Gaps` only (no Summary/Questions); Known issues section only when `sources.known_issues_enabled` |
| **principal** | `--strict-principal` rules only (requires `--ref` + `--coverage`) |

## `--strict-topology` (requires `--ref` + `--coverage`)

When ref `verification_topology` has **`delivery_notes`** and/or **`pricing_oracle_rules`** with `oracle_rule=unresolved`:

| Check | Rule |
|-------|------|
| `known_fail` notes | ≥1 `delivery_known_fail` gap with matching `delivery_note_id` |
| `excluded` notes | ≥1 `delivery_excluded` gap with matching `delivery_note_id` |
| `oracle_rule=unresolved` | ≥1 `surface_oracle_unresolved` gap with matching `oracle_rule_id` |
| Coverage delivery | Each check with `delivery_status` failed/excluded has `exploration_suppressed` row |
| Actions | Gap `recommended_action` matches topology contract map |

Legacy analysis without topology on ref: strict mode no-op when ref lacks delivery notes and unresolved rules.

## `--strict-principal` (opt-in; requires `--ref` + `--coverage`)

When ref has deferral obligations or principal fields (`verification_focus_proposed`, `principal_coverage_threads`):

| Check | Rule |
|-------|------|
| Ref deferral obligations | Each id has `deferred_check` gap with `pointers.obligation_id` |
| Coverage `deferred_in_check` | Each row has matching `deferred_check` gap |
| Forbidden | No `obligation_uncovered` gap for deferral oids marked `deferred_in_check` |
| Delivery links | Delivery gaps for notes with single `linked_obligation_ids` include `obligation_id` |
| Audit | `validation_log` contains step `3-principal` when ref has deferrals |

**Principal lint (opt-in trigger `strict_principal=yes`):**

```powershell
python automation/tools/analysis_verify.py --mode emit --strict-principal `
  --analysis epics/CRT-639/CRT-639-analysis.json `
  --ref epics/CRT-639/CRT-639-ref.json `
  --coverage epics/CRT-639/CRT-639-coverage.json `
  --md epics/CRT-639/CRT-639-analysis.md
```

**Fixture smoke (principal):**

```powershell
python automation/tools/analysis_verify.py --mode emit --strict-principal `
  --analysis automation/tools/fixtures/analysis/analysis-639-formula-principal-minimal.json `
  --ref automation/tools/fixtures/epic-prep/ref-639-topology-minimal.json `
  --coverage automation/tools/fixtures/coverage/coverage-639-formula-principal-minimal.json `
  --md automation/tools/fixtures/analysis/analysis-639-formula-principal-minimal.md

python automation/tools/analysis_verify.py --mode emit --strict-topology --strict-principal `
  --analysis automation/tools/fixtures/analysis/analysis-594-shell-principal-minimal.json `
  --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json `
  --coverage automation/tools/fixtures/coverage/coverage-594-shell-principal-minimal.json `
  --md automation/tools/fixtures/analysis/analysis-594-shell-principal-minimal.md

python automation/tools/analysis_verify.py --mode principal `
  --analysis automation/tools/fixtures/analysis/analysis-principal-bad-empty-gaps.json `
  --ref automation/tools/fixtures/epic-prep/ref-639-topology-minimal.json `
  --coverage automation/tools/fixtures/coverage/coverage-639-formula-principal-minimal.json
# expect exit 1
```

Legacy analysis **without** principal deferrals passes **`emit`** without **`--strict-principal`**. Round 1 **`--strict-topology`** unchanged.
