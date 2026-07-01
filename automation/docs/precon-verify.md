# TEST-PRECON — mechanical verifier

Playbook: [`.cursor/pipelines/test-precon.md`](../../.cursor/pipelines/test-precon.md). Depth ladder: [`docs/exploration-depth-ladder.json`](../../docs/exploration-depth-ladder.json). Topology: [`docs/precon-topology-contract.json`](../../docs/precon-topology-contract.json). Principal: [`docs/precon-principal-contract.json`](../../docs/precon-principal-contract.json).

## CLI

**Phase 4V loop** (ledger or durable JSON):

```powershell
python automation/tools/precon_verify.py `
  --coverage epics/CRT-639/CRT-639-coverage.json `
  --precon epics/CRT-639/temp/precon-ledger.json `
  --discover epics/CRT-639/CRT-639-discover.json `
  --ref epics/CRT-639/CRT-639-ref.json
```

**Before emit (topology-aware epics):**

```powershell
python automation/tools/precon_verify.py `
  --coverage epics/CRT-639/CRT-639-coverage.json `
  --precon epics/CRT-639/CRT-639-precon.json `
  --discover epics/CRT-639/CRT-639-discover.json `
  --ref epics/CRT-639/CRT-639-ref.json `
  --strict-topology `
  --strict-principal `
  --md epics/CRT-639/CRT-639-precon.md
```

Legacy precon without **`sources.topology_loaded`** may omit **`--strict-topology`**; without **`sources.principal_loaded`** omit **`--strict-principal`**. Archetype **`command_patterns`** rules still apply from coverage **`archetype`** / **`emit_layout`**.

**Principal-only lint:**

```powershell
python automation/tools/precon_verify.py --mode principal `
  --coverage epics/CRT-594/CRT-594-coverage.json `
  --precon epics/CRT-594/CRT-594-precon.json `
  --discover epics/CRT-594/CRT-594-discover.json `
  --ref epics/CRT-594/CRT-594-ref.json
```

Exit **0** = pass. Non-zero = re-run Phase **4R/4D/4C** subprocesses (max **3** cluster iterations).

## Fixture regression

```powershell
python automation/tools/precon_verify.py `
  --coverage automation/tools/fixtures/coverage/coverage-639-formula-reinforce-minimal.json `
  --precon automation/tools/fixtures/precon/precon-639-formula-minimal.json `
  --discover automation/tools/fixtures/discover/discover-639-formula-minimal.json `
  --ref epics/CRT-639/CRT-639-ref.json `
  --strict-topology `
  --md automation/tools/fixtures/precon/precon-639-formula-minimal.md

python automation/tools/precon_verify.py `
  --coverage automation/tools/fixtures/coverage/coverage-594-shell-reinforce-minimal.json `
  --precon automation/tools/fixtures/precon/precon-594-shell-minimal.json `
  --discover automation/tools/fixtures/discover/discover-594-shell-minimal.json `
  --ref epics/CRT-594/CRT-594-ref.json `
  --strict-topology `
  --md automation/tools/fixtures/precon/precon-594-shell-minimal.md
```

**Round 2 principal fixtures:**

```powershell
python automation/tools/precon_verify.py `
  --coverage automation/tools/fixtures/coverage/coverage-594-shell-reinforce-principal-minimal.json `
  --precon automation/tools/fixtures/precon/precon-594-shell-principal-minimal.json `
  --discover automation/tools/fixtures/discover/discover-594-shell-principal-minimal.json `
  --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json `
  --strict-topology `
  --strict-principal `
  --md automation/tools/fixtures/precon/precon-594-shell-principal-minimal.md

python automation/tools/precon_verify.py `
  --coverage automation/tools/fixtures/coverage/coverage-639-formula-reinforce-principal-minimal.json `
  --precon automation/tools/fixtures/precon/precon-639-formula-principal-minimal.json `
  --discover automation/tools/fixtures/discover/discover-639-formula-principal-minimal.json `
  --ref automation/tools/fixtures/epic-prep/ref-639-topology-minimal.json `
  --strict-principal `
  --md automation/tools/fixtures/precon/precon-639-formula-principal-minimal.md

python automation/tools/precon_verify.py --mode principal `
  --coverage automation/tools/fixtures/coverage/coverage-594-shell-reinforce-principal-minimal.json `
  --precon automation/tools/fixtures/precon/precon-principal-bad-missing-provision.json `
  --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json `
  --discover automation/tools/fixtures/discover/discover-594-shell-principal-minimal.json
# expect exit 1
```

## Exploration depth checks (v4)

| Check | Failure when |
|-------|----------------|
| FE `outcome: pass` | `depth_level` below `precon_drill` or missing `view_id` (unless gap documented) |
| Post-login smoke | `outcome: pass` without `depth_level: smoke` |
| Discover `probe_executed` | No matching `precon_drill` row per `satisfies_fixture_ids` |
| Required views | Missing `view_id` from ladder per fixture kind |
| Anti-batch | All `exploration_log[].at` identical in cluster |
| Shallow widgets | `widgets_seen` ⊆ nav denylist only |
| Console extended | Discover notes have instrument/account ids but no `show` in console logs |

## Topology checks (`--strict-topology`)

| Check | Failure when |
|-------|----------------|
| **`metrics_calculation`** / **`formula_first`** | Missing **`command_patterns.ladder_step`** when complete |
| **`widget_ui`** / **`shell_first`** | No widget/console observation pattern keys; **`ladder_step`** sole pattern |
| Oracle binding | Discover **`oracle_binding`** + coverage **`oracle_rule_id`** without matching **`case_outline.pattern_ref`** |
| Delivery blocked | **`tooling_blocked`** / **`delivery_status: failed`** check still in skeleton without **`excluded_checks_with_reason`** |

## Principal checks (`--strict-principal` / `--mode principal`)

| Check | Failure when |
|-------|----------------|
| **`sources.principal_loaded`** | False when ref provision or discover **`principal_loaded`** |
| **`validation_log`** | Missing **`phase1-principal`** when principal handoff active |
| **`pc-setup`** | Missing when ref provision + discover **`ref_principal_provision`** fixture |
| Fixture linkage | **`pc-setup`** **`satisfies_fixture_ids`** / **`satisfies_check_ids`** mismatch |
| Dual-account placeholders | Missing **`group_key_enrg`** / **`group_key_oppt`** when ref **`needs_dual_account_contrast`** |
| Deferral keyed | **`out_of_epic`** deferral checks in skeleton without exclusion; missing **`phase4_skipped_deferral_keyed`** |

Document waivers in **`exploration_gaps[]`** with `reason: tooling_blocked` (or `chrome_unavailable`, `waived`).
