# TEST-PREP — mechanical verifier

Gate **verification plan** (temp), **verification exploration** (8a¾), **8c merge**, and **`-tests.json`** drafts. Playbook: [`.cursor/pipelines/test-prep.md`](../../.cursor/pipelines/test-prep.md) (v3). Registry: [`docs/test-verification-classes.json`](../../docs/test-verification-classes.json). Profiles: [`docs/test-prep-draft-profiles.json`](../../docs/test-prep-draft-profiles.json). TBD: [`docs/test-prep-tbd-contract.json`](../../docs/test-prep-tbd-contract.json). Depth: [`docs/exploration-depth-ladder.json`](../../docs/exploration-depth-ladder.json).

## CLI

**Plan loop** (after phase 8a½, max 3 epic iterations):

```powershell
python automation/tools/test_prep_verify.py --mode plan `
  --coverage epics/CRT-639/CRT-639-coverage.json `
  --plan epics/CRT-639/temp/test-prep-plan.json
```

**Verification exploration** (after phase 8a¾, max 2 per bundle):

```powershell
python automation/tools/test_prep_verify.py --mode explore `
  --coverage epics/CRT-639/CRT-639-coverage.json `
  --plan epics/CRT-639/temp/test-prep-plan.json `
  --precon epics/CRT-639/CRT-639-precon.json `
  --bundle-id tb-003
```

**Per-bundle draft** (after phase 8b / 8c merge, max 2 retries):

```powershell
python automation/tools/test_prep_verify.py --mode draft `
  --coverage epics/CRT-639/CRT-639-coverage.json `
  --tests epics/CRT-639/CRT-639-tests.json `
  --bundle-id tb-002 `
  --plan epics/CRT-639/temp/test-prep-plan.json
```

**Post-8c merge** (crtqa_outline):

```powershell
python automation/tools/test_prep_verify.py --mode merge `
  --tests epics/CRT-639/CRT-639-tests.json `
  --plan epics/CRT-639/temp/test-prep-plan.json
```

**Emit gate** (before writing durable `-tests.json`):

```powershell
python automation/tools/test_prep_verify.py --mode tests `
  --coverage epics/CRT-639/CRT-639-coverage.json `
  --tests epics/CRT-639/CRT-639-tests.json `
  --plan epics/CRT-639/temp/test-prep-plan.json
```

Exit code **0** = pass. Non-zero = fix and re-run the matching loop.

## Modes

| Mode | Checks |
|------|--------|
| **plan** | Primary checks in plan; registry classes; **crtqa_outline**: `case_outline[]` length ≥ `min_case_count`; required `case_id`, `title`, `intent` |
| **explore** | `verification_exploration[]` at `prep_verify_view`; surfaces; prep labels ⊇ precon drill |
| **draft** | Precon cite; action/result parity; Yogi only in results; **crtqa_outline**: forbidden TBD patterns; ladder templates; **teaching**: legacy ladder `[TBD]` rule |
| **merge** | Merged bundle action count ≥ plan `min_case_count` sum |
| **tests** | Traceability; greenfield; **crtqa_outline**: no forbidden TBD / CRTQA keys in drafts |

## Profiles

- **`crtqa_outline`** (default): full case matrix; see TBD contract.
- **`teaching`** (`draft_profile=teaching`): legacy v2 illustration budget.

## Generation (greenfield)

No live CRTQA Jira fetch — [docs/harness-principles.md](../../docs/harness-principles.md) §3. Optional **`shape_ref=benchmark`** is shape-only (playbook); verifier still forbids CRTQA keys in durable output.
