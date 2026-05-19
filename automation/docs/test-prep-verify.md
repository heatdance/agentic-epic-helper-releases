# TEST-PREP — mechanical verifier (v3.1)

Gate **verification plan** (temp), **verification exploration** (8a¾), **8c merge**, and **`-tests.json`** drafts. Playbook: [`.cursor/pipelines/test-prep.md`](../../.cursor/pipelines/test-prep.md) (v3.1). Registry: [`docs/test-verification-classes.json`](../../docs/test-verification-classes.json) (`selection_rules_machine`). Profiles: [`docs/test-prep-draft-profiles.json`](../../docs/test-prep-draft-profiles.json). TBD + expansion: [`docs/test-prep-tbd-contract.json`](../../docs/test-prep-tbd-contract.json). Fixtures: [`automation/tools/fixtures/test_prep/`](../tools/fixtures/test_prep/).

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

**Per-bundle draft** (after phase 8b / 8c merge, max 2 retries) — **`--plan` required** for `crtqa_outline`:

```powershell
python automation/tools/test_prep_verify.py --mode draft `
  --coverage epics/CRT-639/CRT-639-coverage.json `
  --tests epics/CRT-639/CRT-639-tests.json `
  --bundle-id tb-002 `
  --plan epics/CRT-639/temp/test-prep-plan.json
```

**Post-8c merge** (`crtqa_outline`) — **`--tests` and `--plan` required**:

```powershell
python automation/tools/test_prep_verify.py --mode merge `
  --tests epics/CRT-639/CRT-639-tests.json `
  --plan epics/CRT-639/temp/test-prep-plan.json
```

**Emit gate** (before writing durable `-tests.json`) — **`--plan` required** for `crtqa_outline`:

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
| **plan** | Primary checks in plan; registry classes; `case_outline[]` length ≥ `min_case_count`; required `case_id`, `title`, `intent`; **`selection_rules_machine`** class/priority lint unless `selection_override_reason` |
| **explore** | `verification_exploration[]` at `prep_verify_view`; surfaces; prep labels ⊇ precon drill |
| **draft** | Precon cite; action/result parity; Yogi only in results; forbidden TBD; ladder templates; **v3.1:** outline cardinality + duplicate actions when bundle uses `stateful_ladder` / `rounding_matrix` / `pattern_ref: ladder_step` (**requires `--plan`**) |
| **merge** | **v3.1:** for single-pair bundles, `len(actions)==len(case_outline)` and no duplicate full action lines; else legacy `actions >= min_case_count` sum (**requires `--plan`**) |
| **tests** | Traceability; greenfield; forbidden TBD / CRTQA keys; **v3.1:** excluded primary ↔ `coverage_gaps[]`; outline cardinality when `--plan` present (**required** for `crtqa_outline`) |

## v3.1 expansion gates (single-pair bundles)

Applies when any plan row has `verification_class` in `stateful_ladder`, `rounding_matrix`, or any `case_outline[].pattern_ref` is `ladder_step`.

| Failure | Meaning |
|---------|---------|
| `actions count N != case_outline rows M` | Template lines were expanded as separate numbered pairs |
| `duplicate action lines detected` | Same action text repeated (padding) |
| `excluded primary chk-XXX must have coverage_gaps[] row` | Emit integrity: deferrals must mirror in `reverse_validation` |
| `verification_class X != expected Y` | Plan class disagrees with `selection_rules_machine` |

**Not gated globally:** `config_posture`, `journey_smoke`, etc. may have more than one command per row without `ladder_step` pattern.

## Fixture proof

See [automation/tools/fixtures/test_prep/README.md](../tools/fixtures/test_prep/README.md).

## Profiles

- **`crtqa_outline`** (default): full case matrix; see TBD contract + expansion_policy.
- **`teaching`** (`draft_profile=teaching`): legacy v2 illustration budget.

## Generation (greenfield)

No live CRTQA Jira fetch — [docs/harness-principles.md](../../docs/harness-principles.md) §3. Optional **`shape_ref=benchmark`** is shape-only (playbook); verifier still forbids CRTQA keys in durable output.
