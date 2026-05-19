# ANALYSE — mechanical verifier

Gate **`-analysis.json`** schema v2. Contract: [`docs/analysis-gap-contract.json`](../../docs/analysis-gap-contract.json). Playbook: [`.cursor/pipelines/analysis.md`](../../.cursor/pipelines/analysis.md).

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

Exit **0** = pass.

## Modes

| Mode | Checks |
|------|--------|
| **gaps** | `schema_version` ≥ 2; gap shape; no `confidence: low`; cap open gaps; no hypothesis `questions[]` |
| **downstream** | `exploration_suppressed[]` shape; no `/temp/`; no CRTQA keys |
| **emit** | gaps + downstream + md has `## Gaps` only (no Summary/Questions); Known issues section only when `sources.known_issues_enabled` |
