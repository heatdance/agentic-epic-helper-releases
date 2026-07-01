# TEST-PREP — mechanical verifier (scenario_intent v3 + legacy crtqa_outline)

**Production default (draft_truth_v3):** **`--mode scenario_intent`**. Contract: [`docs/test-prep-scenario-intent-contract.json`](../../docs/test-prep-scenario-intent-contract.json). Playbook: [`.cursor/pipelines/test-prep.md`](../../.cursor/pipelines/test-prep.md). Fixtures: [`tests-594-scenario-intent-pass.json`](../tools/fixtures/test_prep/tests-594-scenario-intent-pass.json), [`tests-scenario-intent-bad-ui-hallucination.json`](../tools/fixtures/test_prep/tests-scenario-intent-bad-ui-hallucination.json).

```powershell
python automation/tools/test_prep_verify.py --mode scenario_intent `
  --coverage epics/CRT-594/CRT-594-coverage.json `
  --tests epics/CRT-594/CRT-594-tests.json
```

**Legacy** modes (`plan`, `explore`, `draft`, `merge`, `tests`, `crtqa_outline`) below.

---

# TEST-PREP — mechanical verifier (v3.1 + topology + principal) — LEGACY

Gate **verification plan** (temp), **verification exploration** (8a¾), **8c merge**, and **`-tests.json`** drafts. Playbook: [`.cursor/pipelines/test-prep.md`](../../.cursor/pipelines/test-prep.md). Topology: [`docs/test-prep-topology-contract.json`](../../docs/test-prep-topology-contract.json). Principal: [`docs/test-prep-principal-contract.json`](../../docs/test-prep-principal-contract.json). Registry: [`docs/test-verification-classes.json`](../../docs/test-verification-classes.json) (`selection_rules_machine`). Profiles: [`docs/test-prep-draft-profiles.json`](../../docs/test-prep-draft-profiles.json). TBD + expansion: [`docs/test-prep-tbd-contract.json`](../../docs/test-prep-tbd-contract.json). Fixtures: [`automation/tools/fixtures/test_prep/`](../tools/fixtures/test_prep/).

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
  --plan epics/CRT-639/temp/test-prep-plan.json `
  --precon epics/CRT-639/CRT-639-precon.json `
  --ref epics/CRT-639/CRT-639-ref.json `
  --strict-topology `
  --strict-principal
```

**Post-8c merge** (`crtqa_outline`) — **`--tests` and `--plan` required**:

```powershell
python automation/tools/test_prep_verify.py --mode merge `
  --coverage epics/CRT-639/CRT-639-coverage.json `
  --tests epics/CRT-639/CRT-639-tests.json `
  --plan epics/CRT-639/temp/test-prep-plan.json `
  --precon epics/CRT-639/CRT-639-precon.json `
  --ref epics/CRT-639/CRT-639-ref.json `
  --strict-topology `
  --strict-principal
```

**Emit gate** (before writing durable `-tests.json`) — **`--plan` required** for `crtqa_outline`:

```powershell
python automation/tools/test_prep_verify.py --mode tests `
  --coverage epics/CRT-639/CRT-639-coverage.json `
  --tests epics/CRT-639/CRT-639-tests.json `
  --plan epics/CRT-639/temp/test-prep-plan.json `
  --precon epics/CRT-639/CRT-639-precon.json `
  --ref epics/CRT-639/CRT-639-ref.json `
  --strict-topology `
  --strict-principal
```

**Principal-only lint** (Round 2 step 7):

```powershell
python automation/tools/test_prep_verify.py --mode principal `
  --coverage epics/CRT-594/CRT-594-coverage.json `
  --precon epics/CRT-594/CRT-594-precon.json `
  --tests epics/CRT-594/CRT-594-tests.json `
  --ref epics/CRT-594/CRT-594-ref.json
```

Legacy tests without **`sources.topology_loaded`** may omit **`--strict-topology`**. Legacy without **`sources.principal_loaded`** may omit **`--strict-principal`**.

Exit code **0** = pass. Non-zero = fix and re-run the matching loop.

## Fixture regression (topology)

```powershell
$fix = "automation/tools/fixtures"

python automation/tools/test_prep_verify.py --mode tests `
  --coverage "$fix/coverage/coverage-639-formula-reinforce-minimal.json" `
  --tests "$fix/test_prep/tests-639-formula-minimal.json" `
  --plan "$fix/test_prep/plan-639-formula-minimal.json" `
  --precon "$fix/precon/precon-639-formula-minimal.json" `
  --ref epics/CRT-639/CRT-639-ref.json `
  --strict-topology

python automation/tools/test_prep_verify.py --mode tests `
  --coverage "$fix/coverage/coverage-594-shell-reinforce-minimal.json" `
  --tests "$fix/test_prep/tests-594-shell-minimal.json" `
  --plan "$fix/test_prep/plan-594-shell-minimal.json" `
  --precon "$fix/precon/precon-594-shell-minimal.json" `
  --ref epics/CRT-594/CRT-594-ref.json `
  --strict-topology
```

## Fixture regression (principal)

```powershell
$fix = "automation/tools/fixtures"

python automation/tools/test_prep_verify.py --mode tests `
  --coverage "$fix/coverage/coverage-594-shell-reinforce-principal-minimal.json" `
  --tests "$fix/test_prep/tests-594-shell-principal-minimal.json" `
  --plan "$fix/test_prep/plan-594-shell-principal-minimal.json" `
  --precon "$fix/precon/precon-594-shell-principal-minimal.json" `
  --ref "$fix/epic-prep/ref-594-topology-full.json" `
  --strict-topology `
  --strict-principal

python automation/tools/test_prep_verify.py --mode tests `
  --coverage "$fix/coverage/coverage-639-formula-reinforce-principal-minimal.json" `
  --tests "$fix/test_prep/tests-639-formula-principal-minimal.json" `
  --plan "$fix/test_prep/plan-639-formula-principal-minimal.json" `
  --precon "$fix/precon/precon-639-formula-principal-minimal.json" `
  --ref "$fix/epic-prep/ref-639-topology-minimal.json" `
  --strict-principal

python automation/tools/test_prep_verify.py --mode principal `
  --coverage "$fix/coverage/coverage-594-shell-reinforce-principal-minimal.json" `
  --precon "$fix/precon/precon-594-shell-principal-minimal.json" `
  --tests "$fix/test_prep/tests-principal-bad-missing-setup.json" `
  --ref "$fix/epic-prep/ref-594-topology-full.json"
# expect exit 1
```

## Modes

| Mode | Checks |
|------|--------|
| **plan** | Primary checks in plan; registry classes; `case_outline[]` length ≥ `min_case_count`; required `case_id`, `title`, `intent`; **`selection_rules_machine`** class/priority lint unless `selection_override_reason` |
| **explore** | `verification_exploration[]` at `prep_verify_view`; surfaces; prep labels ⊇ precon drill |
| **draft** | Precon cite; action/result parity; Yogi only in results; forbidden TBD; ladder templates; **v3.1:** outline cardinality + duplicate actions when bundle uses `stateful_ladder` / `rounding_matrix` / topology **`pattern_ref`** keys (**requires `--plan`**) |
| **merge** | Post-8c merged drafts match plan case counts; same cardinality gates as draft |
| **tests** | Emit: primary traceability; `coverage_gaps[]` ↔ excluded; greenfield CRTQA skip; **v3.1** outline cardinality when `--plan` present |
| **principal** | Principal-only lint per [`test-prep-principal-contract.json`](../../docs/test-prep-principal-contract.json) |

## Topology checks (`--strict-topology`)

Requires **`--precon`** and **`--ref`**. Active when **`sources.topology_loaded`** on tests or precon.

| Check | Failure when |
|-------|----------------|
| **`pattern_ref` expansion** | Plan row with `pattern_ref` but action missing sub-bullets from precon `command_patterns` key |
| **Delivery excluded** | Blocked primary still in `covers_check_ids` or missing from `coverage_gaps[]` |
| **`platform_reuse_annex`** | Missing when ref has `platform_reuse_candidates`; CRTQA keys in annex |
| **Legacy** | No topology_loaded → strict oracle/reuse rules no-op |

## Principal checks (`--strict-principal`)

Requires **`--precon`** and **`--ref`**. Skips when no principal handoff on precon/ref. Active when **`sources.principal_loaded`** or precon has **`pc-setup`**.

| Check | Failure when |
|-------|----------------|
| **`sources.principal_loaded`** | Missing on tests when principal handoff active |
| **`validation_log`** | Missing `phase1-principal`, `phase8b_principal_paste`; `phase8a_persona_split` when `pc-setup` present |
| **`tb-setup` / `pc-setup`** | No setup bundle covering `chk-s1`/`chk-s2` when precon has `pc-setup` |
| **Dual-account paste** | Missing `<group_key_enrg>` / `<group_key_oppt>` in draft when ref `needs_dual_account_contrast` |
| **Persona split** | Retail-primary and dealer-primary checks share a bundle |
| **Deferral skip** | Deferral-keyed check in `covers_check_ids` without exclusion + `coverage_gaps[]` |
| **Observation order** | Non-setup bundle first precondition missing `pc-setup` cite |

## v3.1 expansion (reminder)

One numbered Action/Result pair per **`case_outline[]`** row. **`command_patterns[pattern_ref]`** lines are sub-bullets inside that Action — not separate numbered pairs. See [`docs/test-prep-tbd-contract.json`](../../docs/test-prep-tbd-contract.json) **`expansion_policy`**.
