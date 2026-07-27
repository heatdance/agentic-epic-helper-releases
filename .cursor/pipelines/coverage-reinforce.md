> **Legacy opt-in (draft+truth v1):** This pipeline is **not** in the default epic chain. After human **coverage review** (`coverage_frozen_at`), running reinforce **conflicts** with `coverage_immutable` — use only when operator explicitly opts in. See [`docs/draft-truth-contract.json`](../../docs/draft-truth-contract.json).

# Pipeline: coverage-reinforce

**Trigger**: user message starts with `COVERAGE-REINFORCE:` and includes a Jira **Epic key** (e.g. `COVERAGE-REINFORCE: CRT-639`). Optional **`strict_principal=yes`** — opt-in principal fixture merge lint (Phase **4**).

**Scope**: **one Epic** per run. **Router**: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc).

**Purpose:** Second coverage pass after **TEST-DISCOVER** — merge **verification affordances**, **obligation ledger** closure hints, **topology oracle bindings**, **principal fixture provisioning depth**, and **operator feedback** into the existing Smart Checklist without re-running full greenfield COVERAGE from ref-only inputs.

**Schema:** Same as production COVERAGE — **`schema_version: 2`**, **`obligations_coverage`**. Set **`coverage_pass: 2`**, **`reinforced_at`** (ISO-8601 UTC), **`sources.reinforce_topology_loaded`** when discover topology consumed, and **`sources.reinforce_principal_loaded`** when discover principal consumed.

**Topology contract:** [`docs/coverage-reinforce-topology-contract.json`](../../docs/coverage-reinforce-topology-contract.json).

**Principal contract:** [`docs/coverage-reinforce-principal-contract.json`](../../docs/coverage-reinforce-principal-contract.json).
## Epic workspace (`{EpicDir}`)

Resolve **`{EpicDir}`** = `epics/<KEY>/`.

**Prerequisites:**

- `{EpicDir}dependencies/<KEY>-ref.json` (schema v4)
- `{EpicDir}dependencies/<KEY>-coverage.json` + `.md` (pass 1)
- `{EpicDir}dependencies/<KEY>-discover.json` (schema v3, `discover_verify.py` OK)

**`/epic-helper` path (required when helper session active):**

- `{EpicDir}helper/affordances-slice.json` (from `epic_helper_affordances.py` after discover)
- `{EpicDir}helper/operator-feedback.md` (may be empty; ingest from `/epic-helper resume` comments)

**Standalone `COVERAGE-REINFORCE:`** may **`jq`**-slice discover directly when `helper/` absent (fixtures / ad-hoc); regenerate slice via:

```powershell
python automation/tools/epic_helper_affordances.py `
  --discover {EpicDir}dependencies/<KEY>-discover.json `
  --out {EpicDir}helper/affordances-slice.json `
  --strict-topology `
  --strict-principal
```

If **discover** missing: **STOP** — run `TEST-DISCOVER:` first.

## Allowed inputs (exception to production COVERAGE forbidden list)

| Input | Use |
|-------|-----|
| `-discover.json` | **jq slices only** — `verification_affordances` (incl. **`oracle_binding`**, **`topology_surface_id`**), `obligation_ledger`, `fixture_needs` (incl. **`linked_obligation_ids`**, **`derivation`**), `sources.principal_loaded`, `principal_provenance`, `environment.client_shell_impact`, `sources.topology_loaded` |
| `helper/affordances-slice.json` | Primary machine slice for reinforce |
| `helper/operator-feedback.md` | Human gaps (Order History, UI↔DB, surface parity, instrument tokens) |
| Existing `-coverage.json` / `.md` | **Merge base** — extend checks; do not drop row-complete obligations |

Contract: [`docs/coverage-obligation-contract.json`](../../docs/coverage-obligation-contract.json) `reinforce_allowed_inputs`.

## Forbidden inputs

- **CRTQA** Jira issues, **`.cursor/calibrate/`** gold
- **`-tests.json`**, **`-precon.json`**
- Full discover JSON loaded unfiltered into context (use **`jq`** per [automation/docs/jq.md](../../automation/docs/jq.md))

## Preconditions

- **user-mcp-atlassian** when Jira refresh needed for ambiguity only — reinforce is **coverage-grounded**, not a second EPIC-PREP.
- **Harness maps:** read [`docs/dxtrade5-harness/`](../../docs/dxtrade5-harness/) and [`docs/webbroker-harness/`](../../docs/webbroker-harness/) for widget/screen affordances cited in discover.
- **Smart Checklist norms:** same as [`coverage.md`](coverage.md) — **no meta prose** in executable `-` lines; use `>` for variants and discover depth.

**Ephemeral:** `{EpicDir}temp/` — delete before finish.

---

## Phases

### 1. Load merge base + slices

- **`jq`** project pass-1 **`-coverage.json`** obligations + checks; **`-discover.json`** affordances, ledger, fixtures, topology + principal fields; load **`affordances-slice.json`** (or regenerate); read **`operator-feedback.md`** when present.

**Principal jq slice** (when discover present):

```bash
jq '{
  provision_fixtures: [.fixture_needs[]? | select(.derivation == "ref_principal_provision" or ((.linked_obligation_ids | length) > 0)) | {id, kind, linked_check_ids, linked_obligation_ids, setup_depth, notes}],
  principal_loaded: .sources.principal_loaded,
  deferral_skips: [.validation_log[]? | select(.step == "phaseE_skipped_deferral_keyed")]
}' epics/<KEY>/dependencies/<KEY>-discover.json
```

- Build **reinforce work queue:** primary checks × linked affordances; collect delivery **`tooling_blocked`** ledger rows into **skip-deepen** set; collect deferral-keyed rows from **`phaseE_skipped_deferral_keyed`** into **skip-deepen** set.
- Record **`sources.reinforce_inputs[]`**: paths + `loaded_at`. Set **`sources.reinforce_topology_loaded: true`** when discover **`sources.topology_loaded`** consumed. Set **`sources.reinforce_principal_loaded: true`** when **`principal_loaded`** or provision fixtures present.
- Append **`validation_log`** step **`reinforce-1`**, **`reinforce-1-topology`** (surface/oracle bind counts), and **`reinforce-1-principal`** when principal loaded.
### 2. Map affordances → checks

For each **primary** check linked to discover affordances (batch by **`topology_surface_id`** when **`emit_layout: shell_first`**; by fixture/console batch when **`formula_first`**):

| Source | Reinforce action |
|--------|------------------|
| Affordance **`oracle_binding`** | Human **`Oracle`/`Harness`** hints in **`detail_lines`**; machine oracle enum in **`linker_trace_lines`** when needed; retain **`oracle_rule_id`** on check |
| Affordance **`artifacts[]`** / **`setup_depth: probe_executed`** | Human-readable tokens → **`detail_lines`**; sanitized probe tokens → **`linker_trace_lines`** when not operator-facing |
| Ledger **`tooling_blocked`** (delivery) | **Do not** add executable `-` lines; preserve pass-1 **`delivery_status`** + `[FAILED]`/excluded markers |
| **`fixture_needs`** with **`ref_principal_provision`** | Machine trace → **`linker_trace_lines`** (`> Discover:`, kind, fixture id, linked obligations); human setup from [`docs/coverage-operator-hints.json`](../../docs/coverage-operator-hints.json) **`fixture_kinds`** → **`detail_lines`** when missing (**`chk-s1`/`chk-s2`** on 594) |
| **`phaseE_skipped_deferral_keyed`** / deferral-keyed ledger | **Skip-deepen** — no new **`-`** lines on **`chk-def-*`**; optional deferral note in **`linker_trace_lines`** only |
| **`operator-feedback.md`** | Executable scenarios only — Order History, UI↔DB, cross-shell parity |
**Anti-patterns to fix on reinforce:**

- Generic widget-only lines without history/DB when discover cites fixtures
- Generic “tier-appropriate” when discover names **`first_tier_quote`** / **`text_configuration_closest_gte_qty`**
- Instrument litter (e.g. EURUSD) when epic/ref says FX Spot class — use `.spot` or ref instrument tokens
- Symmetric peer sections when `epic_verification_focus` is one-way
- Reopening delivery-blocked primaries as new executable checks
- Reopening deferral-keyed **`out_of_epic`** checks as new primary executable scenarios

Append **`validation_log`** **`reinforce-2-oracle`**, **`reinforce-2-skipped-delivery`**, **`reinforce-2-fixture-provision`** (fixture count), and **`reinforce-2-skipped-deferral-keyed`** when applicable.
### 3. Obligation row-complete (unchanged bar)

- Every **`primary_candidate`** in ref must remain **covered**, **deferred_in_check**, or **excluded_with_reason** in `obligations_coverage`.
- Run `coverage_verify.py --mode obligations` with `--ref`.

### 4. Emit

- Bump **`coverage_pass: 2`**, set **`reinforced_at`**, **`sources.reinforce_topology_loaded`** and **`sources.reinforce_principal_loaded`** when applicable.
- Regenerate **`-coverage.md`** via `coverage_verify.py --mode emit` (+ **`--strict-topology`** / **`--strict-principal`** when ref has topology/principal).
- Run **`coverage_verify.py --mode reinforce`** with **`--discover`** (+ **`--strict-topology`** / **`--strict-principal`** when trigger or ref/discover principal loaded).- Delete `{EpicDir}temp/`.
- Self-check: no `/temp/` paths in durable JSON.

**Downstream:** Legacy only — not in draft_truth_v3 helper chain. See [`.cursor/pipelines/test-precon.md`](test-precon.md) (calibrate/benchmark).

### 5. Helper handoff

**Not invoked from `/epic-helper` v4.** Opt-in manual trigger only; conflicts with `coverage_immutable` after human gate.

---

## Verifier

```text
python automation/tools/coverage_verify.py \
  --mode obligations \
  --coverage {EpicDir}dependencies/<KEY>-coverage.json \
  --ref {EpicDir}dependencies/<KEY>-ref.json

python automation/tools/coverage_verify.py \
  --mode emit --strict-topology \
  --coverage {EpicDir}dependencies/<KEY>-coverage.json \
  --ref {EpicDir}dependencies/<KEY>-ref.json \
  --md {EpicDir}<KEY>-coverage.md

python automation/tools/coverage_verify.py \
  --mode reinforce \
  --coverage {EpicDir}dependencies/<KEY>-coverage.json \
  --ref {EpicDir}dependencies/<KEY>-ref.json \
  --discover {EpicDir}dependencies/<KEY>-discover.json \
  --strict-topology \
  --strict-principal
```

Doc: [`automation/docs/coverage-verify.md`](../../automation/docs/coverage-verify.md).
