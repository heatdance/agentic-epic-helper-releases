# COVERAGE — mechanical verifier

Gate **`-coverage.json`** schema v2 **`obligations_coverage`**. Contract: [`docs/coverage-obligation-contract.json`](../../docs/coverage-obligation-contract.json). Playbook: [`.cursor/pipelines/coverage.md`](../../.cursor/pipelines/coverage.md).

## CLI

**After section merge (phase 13b):**

```powershell
python automation/tools/coverage_verify.py --mode obligations `
  --coverage epics/CRT-639/CRT-639-coverage.json `
  --ref epics/CRT-639/CRT-639-ref.json
```

**Before emit (phase 14):**

```powershell
python automation/tools/coverage_verify.py --mode emit `
  --coverage epics/CRT-639/CRT-639-coverage.json `
  --md epics/CRT-639/CRT-639-coverage.md
```

**Matrix-only (optional mid-run):**

```powershell
python automation/tools/coverage_verify.py --mode matrix `
  --coverage epics/CRT-639/CRT-639-coverage.json
```

Exit **0** = pass.

## Modes

| Mode | Checks |
|------|--------|
| **matrix** | `schema_version` ≥ 2; matrix ids; roles vs focus |
| **obligations** | matrix + row-complete `obligations_coverage` vs ref `primary_candidate`; section headings; forbidden deferral patterns; primary check grounding |
| **checks** | obligations + ungrounded pre-emit |
| **emit** | matrix + empty `ungrounded_check_ids`; focus verbatim in `.md`; no `/temp/`; no CRTQA |
