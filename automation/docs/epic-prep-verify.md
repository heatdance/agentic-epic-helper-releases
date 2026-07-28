# EPIC-PREP — mechanical verifier

Gate **`-ref.json`** schema v4 **`obligations_proposed[]`**, optional **`verification_topology`**, and optional **principal hints**. Playbook: [`.cursor/pipelines/epic-prep.md`](../../.cursor/pipelines/epic-prep.md). Kinds: [`docs/epic-obligation-kinds.json`](../../docs/epic-obligation-kinds.json). Topology: [`docs/epic-prep-topology-contract.json`](../../docs/epic-prep-topology-contract.json). Principal: [`docs/epic-prep-principal-contract.json`](../../docs/epic-prep-principal-contract.json). Variations: [`docs/variation-catalogue.json`](../../docs/variation-catalogue.json) (D18 — prints `mandated_variations` / `emitted` / `unmatched_patterns`; `--ci-strict` / `page_id_unresolved` non-deferrable).

## CLI

**Before finalize (step 8):**

```powershell
python automation/tools/epic_prep_verify.py --mode ref `
  --ref epics/dependencies/CRT-639/CRT-639-ref.json
```

**New emits (topology required):**

```powershell
python automation/tools/epic_prep_verify.py --mode ref --strict-topology `
  --ref epics/dependencies/CRT-594/CRT-594-ref.json
```

**Principal handoff (opt-in trigger `strict_principal=yes`):**

```powershell
python automation/tools/epic_prep_verify.py --mode ref --strict-topology --strict-principal `
  --ref epics/dependencies/CRT-594/CRT-594-ref.json
```

**Topology-only:**

```powershell
python automation/tools/epic_prep_verify.py --mode topology `
  --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json
```

**Principal-only:**

```powershell
python automation/tools/epic_prep_verify.py --mode principal `
  --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json
```

**After reconcile subprocess (step 6b):**

```powershell
python automation/tools/epic_prep_verify.py --mode reconcile `
  --ref epics/dependencies/CRT-639/CRT-639-ref.json
```

**Fixtures (regression):**

```powershell
python automation/tools/epic_prep_verify.py --mode ref --strict-topology `
  --ref automation/tools/fixtures/epic-prep/ref-639-topology-minimal.json
python automation/tools/epic_prep_verify.py --mode ref --strict-topology --strict-principal `
  --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json
python automation/tools/epic_prep_verify.py --mode principal `
  --ref automation/tools/fixtures/epic-prep/ref-principal-bad-missing-setup.json
```

Exit **0** = pass. Max **2** reconcile iterations on failure per playbook.

## Modes

| Mode | Checks |
|------|--------|
| **ref** | `schema_version` ≥ 4; obligations shape; snippet finalize gate; variation and requirement-pass gates (below); no `/temp/`; no CRTQA keys; topology when `--strict-topology`; principal when `--strict-principal` |
| **topology** | `epic_archetype` + `verification_topology` contract only |
| **principal** | Principal contract only (`verification_focus_proposed`, `downstream_hints`, threads, delivery links, archetype rules) |
| **reconcile** | **ref** checks + `obligations_reconcile.epic_summary_aligned`; primary obligations reviewed |

## Variation and requirement-pass gates (`widget_ui` / `mixed`)

Thresholds come from the snippet, not from declared fields ([decisions.md](../CI/decisions.md) D18–D19):

| Error | Meaning |
|-------|---------|
| `parameter_inventory_undercut` | Declared `parameter_inventory[]` omits rows that the verifier derives from `snippet_text`. A declared inventory may add rows, never drop them. |
| `snippet_truncated` | `snippet_text` is under 60% of the attested `requirement_passes[].source_chars` — transcribe the whole parameter table. |
| `requirement_passes missing` / `requirement_pass_missing` | No per-requirement pass recorded for a requirement with `snippet_status: ok`; step **3c** must fan out one subprocess per requirement. |
| `requirement_pass_stale` | Recorded `snippet_chars` or `inventory_rows` disagrees with what the verifier recomputes from the ref. |
| `observable_yield_undercut` | Declared `observable_yield` is below the catalogue-mandated variation count. |
| `variation_shortfall` | Fewer variation obligations than mandated, or mandated variations left uncovered. |
| `parity_on_availability` | Availability wording emitted as `kind: parity`; use `kind: invariant` under `## Prerequisites`. |

`WARN unmatched_spec_patterns` is advisory: inventory cells with no catalogue rule, which COVERAGE surfaces under `## Not attempted`.

## `--strict-principal` (opt-in)

When set (or **`--mode principal`**):

- Every **`primary_candidate`** obligation has non-empty **`downstream_hints.coverage_thread`** (except **`metrics_calculation`** short-circuit)
- Every deferral has **`deferral_reason`** and **`coverage_thread: deferral_only`**
- **`verification_focus_proposed.statement`** non-empty
- **`widget_ui`** archetype rules: setup thread when setup keywords; invariants thread when invariant primaries; backup thread when backup/EOD keywords
- **`delivery_notes`** with **`known_fail`** / **`excluded`** / **`pending_verification`** have **`linked_obligation_ids`** or **`linked_surface_ids`**
- **`needs_dual_account_contrast: true`** only when **`config_vs_position`** is **`account_group_assignment`**

## Backward compatibility

Legacy refs **without** `epic_archetype` / `verification_topology` pass **`ref`** without **`--strict-topology`**. Legacy refs **without** principal fields pass **`ref`** without **`--strict-principal`**. Re-prep or add fields before using strict flags.
