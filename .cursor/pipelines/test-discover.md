# Pipeline: test-discover (linker only)

**Trigger**: user message starts with **`TEST-DISCOVER:`** and includes a Jira **Epic key** (e.g. `TEST-DISCOVER: CRT-594`).

Optional tokens on the **same line**:

- **`crtqa_index=yes`** — enable CRTQA Jira index (Step **C-index** only); default **off**.
- **`strict_topology=yes`** — opt-in; Step **G** runs **`discover_verify.py --strict-topology`** (requires **`--ref`**, **`--analysis`** when delivery topology loaded).
- **`strict_principal=yes`** — opt-in principal fixture lint (requires **`--ref`**, **`--discover`** at verify).

**Scope**: **one Epic** per run. **Router**: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc).

**Doctrine**: [docs/harness-principles.md](../../docs/harness-principles.md) §8 — **linker only** after human coverage freeze. Contract: [docs/discover-linker-contract.json](../../docs/discover-linker-contract.json). Master chain: [docs/draft-truth-contract.json](../../docs/draft-truth-contract.json).

**Forbidden:** Phase 0 env gates, Chrome MCP, browser login, **`dxtrade5_creds`**, **`webbroker_creds`**, **`proceed`**, **`skip_cold_gate`**, **`fe_exploration_waived`**, live probes, **`-coverage.json`** writes.

---

## Epic workspace (`{EpicDir}`)

Resolve **`{EpicDir}`** = `epics/<KEY>/`.

**Prerequisites (hard stop):**

- `{EpicDir}dependencies/<KEY>-ref.json` (schema v4)
- `{EpicDir}dependencies/<KEY>-coverage.json` with **`sources.coverage_frozen_at`** set (human gate / helper path)

If **`coverage_frozen_at`** missing: **STOP** — complete human coverage review first.

**Ephemeral**: `{EpicDir}temp/` — ledger scratch only. **Delete** before finish.

---

## Normative rules

- **MUST NOT** open browser, run **`crtqa_console_probe.py`** as a discover step, or invoke console from this pipeline.
- **MUST NOT** set **`setup_depth`** above **`classified_only`** on **`fixture_needs[]`** or affordances.
- **MUST NOT** populate **`fe_credentials`**, **`fe_ui_sessions`**, **`session_gates`**, or **`operator_recovery`** on emit.
- **MUST** set **`sources.discovery_mode: linker_only`** on **`-discover.json`**.
- **MUST** use **`jq`** per [automation/docs/jq.md](../../automation/docs/jq.md) before loading full JSON for inspection.

---

## Step A — Materialize obligation ledger (deterministic)

1. Load primary **`checks[]`** from frozen **`-coverage.json`** (`verification_role: primary` or unset).
2. For each primary check, emit **`obligation_ledger[]`** row: **`check_id`**, **`matrix_ids`**, **`surfaces`** (from check **`shell`**), **`requirement_keys`**, **`evidence_need`**, initial **`disposition: pending`**.
3. Apply delivery suppressions from **`-analysis.json`** **`exploration_suppressed`** and coverage **`delivery_status`** **`failed`** / **`excluded`** → set **`disposition: tooling_blocked`** with **`disposition_note`** (not **`scope_gap`**).
4. Set **`sources.discover_run_started_at`** (ISO-8601 UTC) once at Step A start.
5. Set **`sources.topology_loaded`** / **`ref_topology_fields[]`** when ref/coverage oracle topology consumed.

**Subprocess:** one batch per competency or matrix section when **>5** primary rows; merge into single ledger.

---

## Step B — Affordance mapping (no live execution)

For each ledger row not **`tooling_blocked`**:

1. Emit **`verification_affordances[]`**: **`id`**, **`linked_check_ids`**, **`competency`**, **`summary`**, **`setup_depth: classified_only`**, **`evidence_grade: doc_only`** or **`classified`**.
2. **Console checks:** cite coverage **`runtime_probes[].verified_syntax`** when present; else **`pattern_ref`** / **`oracle_binding`** from coverage **`oracle_rule_id`** + ref **`pricing_oracle_rules`**.
3. **UI checks (dxtrade5/webbroker):** set **`harness_location_ref`** when a matching entry exists in [docs/dxtrade5-harness/locations/](../../docs/dxtrade5-harness/locations/) or webbroker harness; else **`topology_surface_id`** + **`oracle_binding`** from ref/coverage.
4. Set ledger **`disposition: affordance_mapped`** and **`affordance_ids[]`**.

**MUST NOT** claim **`observed_runtime`** or **`probe_executed`**.

Optional: read harness location slices ( **`jq`** ) — do not crawl entire **`locations/ctqa.json`**.

---

## Step C-fixture — Classify fixture needs

1. From primary checks + ref **`client_shell_impact`**, derive **`fixture_needs[]`**: **`id`**, **`kind`**, **`surfaces`**, **`linked_check_ids`**, **`derivation`**, **`setup_depth: classified_only`** only.
2. Link **`topology_surface_id`** when ref surfaces exist.
3. Set ledger **`fixture_need_ids`** and **`disposition: fixture_need_mapped`** where applicable.

Kinds: see [`docs/discover-fixture-probes.json`](../../docs/discover-fixture-probes.json) for **classification labels only** — **do not** execute probe recipes.

---

## Step C-index — CRTQA reference index (conditional)

Run **only** when **`crtqa_index=yes`** on trigger. Otherwise **`reference_index[]`**, **`precondition_signals[]`**, **`prerequisite_edges[]`** **MUST** be **`[]`**.

---

## Step G — Final emit

1. Set **`obligation_closure`**: **`primary_count`**, **`dispositioned_count`**, **`verifier_passed`** (after verify).
2. **`discovery_status`**: **`complete`** when all primaries dispositioned and verifier passes; else **`incomplete`** with honest **`closure_gaps`**.
3. **`test_prep_gates`**: **`blocked: false`** (linker does not block PREP).
4. Run verifier:

```powershell
python automation/tools/discover_verify.py `
  --mode linker `
  --coverage {EpicDir}dependencies/<KEY>-coverage.json `
  --discover {EpicDir}dependencies/<KEY>-discover.json `
  [--ref {EpicDir}dependencies/<KEY>-ref.json] `
  [--analysis {EpicDir}dependencies/<KEY>-analysis.json] `
  [--strict-topology] `
  [--strict-principal]
```

5. **Delete** `{EpicDir}temp/` before finish.

---

## Downstream

- **TEST-PRECON** — optional read of linker **`-discover.json`**; live exploration in PRECON Phase 0/4 only.
- **TEST-PREP** — optional discover slices; not required for bundle planning.
- **CLOSE** — **`-discover.json`** still required at preflight.

---

## Related

| Doc | Role |
|-----|------|
| [epics/templates/discover-ref.json](../../epics/templates/discover-ref.json) | Schema v3 template |
| [automation/docs/discover-verify.md](../../automation/docs/discover-verify.md) | Verifier modes |
| [docs/discover-topology-contract.json](../../docs/discover-topology-contract.json) | Opt-in **`--strict-topology`** |
| [docs/discover-principal-contract.json](../../docs/discover-principal-contract.json) | Opt-in **`--strict-principal`** |
