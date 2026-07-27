# COVERAGE — mechanical verifier

Gate **`-coverage.json`** schema v2 **`obligations_coverage`**. Contracts: [`docs/coverage-obligation-contract.json`](../../docs/coverage-obligation-contract.json), [`docs/coverage-topology-contract.json`](../../docs/coverage-topology-contract.json), [`docs/coverage-principal-contract.json`](../../docs/coverage-principal-contract.json). Playbook: [`.cursor/pipelines/coverage.md`](../../.cursor/pipelines/coverage.md).

## CLI

**After section merge (phase 13b):**

```powershell
python automation/tools/coverage_verify.py --mode obligations `
  --coverage epics/dependencies/CRT-639/CRT-639-coverage.json `
  --ref epics/dependencies/CRT-639/CRT-639-ref.json `
  --md epics/CRT-639/CRT-639-coverage.md
```

**Before emit (phase 14):**

```powershell
python automation/tools/coverage_verify.py --mode emit `
  --coverage epics/dependencies/CRT-639/CRT-639-coverage.json `
  --md epics/CRT-639/CRT-639-coverage.md
```

**Topology lint (phase 14 when ref has `epic_archetype` + `verification_topology`):**

```powershell
python automation/tools/coverage_verify.py --mode emit --strict-topology `
  --coverage epics/dependencies/CRT-594/CRT-594-coverage.json `
  --ref epics/dependencies/CRT-594/CRT-594-ref.json `
  --md epics/CRT-594/CRT-594-coverage.md
```

**Principal lint (opt-in `strict_principal=yes` or ref has principal fields):**

```powershell
python automation/tools/coverage_verify.py --mode emit --strict-topology --strict-principal `
  --coverage automation/tools/fixtures/coverage/coverage-594-shell-principal-minimal.json `
  --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json `
  --md automation/tools/fixtures/coverage/coverage-594-shell-principal-minimal.md
```

**Principal-only:**

```powershell
python automation/tools/coverage_verify.py --mode principal `
  --coverage automation/tools/fixtures/coverage/coverage-594-shell-principal-minimal.json `
  --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json `
  --md automation/tools/fixtures/coverage/coverage-594-shell-principal-minimal.md
```

**Fixture smoke (639 formula_first + 594 shell_first):**

```powershell
python automation/tools/coverage_verify.py --mode obligations `
  --coverage automation/tools/fixtures/coverage/coverage-639-formula-minimal.json `
  --ref epics/dependencies/CRT-639/CRT-639-ref.json `
  --md automation/tools/fixtures/coverage/coverage-639-formula-minimal.md

python automation/tools/coverage_verify.py --mode emit --strict-topology `
  --coverage automation/tools/fixtures/coverage/coverage-594-shell-minimal.json `
  --ref epics/dependencies/CRT-594/CRT-594-ref.json `
  --md automation/tools/fixtures/coverage/coverage-594-shell-minimal.md
```

Exit **0** = pass.

**Rebuild markdown from checks:** [`coverage_md_sync.py`](../tools/coverage_md_sync.py) (`--write` / `--check`). Operator hint catalog: [`docs/coverage-operator-hints.json`](../../docs/coverage-operator-hints.json).

## Modes

| Mode | Checks |
|------|--------|
| **matrix** | `schema_version` ≥ 2; matrix ids; roles vs focus |
| **obligations** | matrix + **`obligations_coverage`** row-complete vs ref primaries; invariant/rounding sections; **semantic gates** (stub wording, single-stub subsection, machine deferral enums, availability placement, `observable_yield` shortfall, redundant context tokens) |
| **checks** | obligations + basic check shape |
| **emit** | matrix + markdown focus verbatim + no temp/CRTQA + **operator md hygiene** (no platform reuse heading; no `> Discover:`/`> Discovery:`; no machine lines in `detail_lines`) |
| **principal** | Principal contract only (focus copy, threads, keyed deferrals) |
| **reinforce** | pass-2 coverage + discover oracle merge; with **`--strict-principal`**: provision fixture merge + deferral skip-deepen |

## `--strict-principal` on reinforce (opt-in)

When **`--mode reinforce`** also sets **`--strict-principal`** (or trigger **`strict_principal=yes`**):

- Runs pass-1 **`verify_strict_principal`** on pass-2 coverage (focus, threads, keyed deferrals)
- When discover **`sources.principal_loaded`**: **`sources.reinforce_principal_loaded`** must be true
- Provision **`fixture_needs`** with **`ref_principal_provision`**: linked setup checks **`linker_trace_lines`** cite fixture **`kind`/`id`/`linked_obligation_ids`**; **`detail_lines`** have operator-allowed prefixes
- Discover **`phaseE_skipped_deferral_keyed`**: deferral checks stay **`out_of_epic`** with **`!`** markers; **`validation_log`** step **`reinforce-2-skipped-deferral-keyed`**

Contract: [`docs/coverage-reinforce-principal-contract.json`](../../docs/coverage-reinforce-principal-contract.json).

```powershell
python automation/tools/coverage_verify.py --mode reinforce --strict-topology --strict-principal `
  --coverage automation/tools/fixtures/coverage/coverage-594-shell-reinforce-principal-minimal.json `
  --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json `
  --discover automation/tools/fixtures/discover/discover-594-shell-principal-minimal.json `
  --md automation/tools/fixtures/coverage/coverage-594-shell-reinforce-principal-minimal.md

python automation/tools/coverage_verify.py --mode reinforce --strict-principal `
  --coverage automation/tools/fixtures/coverage/coverage-reinforce-principal-bad-missing-fixture-merge.json `
  --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json `
  --discover automation/tools/fixtures/discover/discover-594-shell-principal-minimal.json
# expect exit 1
```

## `--strict-principal` (pass-1 / emit)

When set (or **`--mode principal`**):

- If ref has **`verification_focus_proposed.statement`** → **`epic_verification_focus.statement`** must match exactly (unless **`user_trigger_focus`** logged)
- If ref has **`environment_setup`** thread → setup H2 before first surface H2 (`shell_first`)
- Each **`principal_coverage_threads[]`** obligation has a check in the matching section or **`coverage_thread`**
- Each deferral obligation → **`deferred_in_check`** + keyed check with **`obligation_ids`**, or documented exclusion
- Forbidden blanket deferral patterns without **`obligation_ids`** when ref has deferrals

## Backward compatibility

Legacy coverage **without** principal fields passes **`emit`** without **`--strict-principal`**. Round 1 **`--strict-topology`** unchanged.
