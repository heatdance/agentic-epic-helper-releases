# Pipeline: test-prep (regression test drafting) v3

**Trigger**: user message starts with **`TEST-PREP:`** and includes a Jira **Epic key** (e.g. `TEST-PREP: CRT-639`). Optional tokens on the **same line**:

- **`map_only=yes`** / `true` / `1` — emit **shells** (phase **8a**) + **verification plan** (phase **8a½**) + plan verify only; **omit** full `draft` prose (placeholder arrays OK). **Skips** phase **8b**, **8b-verify**, **8c**, and **8c-verify**.
- **`draft_profile=teaching`** — legacy v2 teaching drafts (`illustration_budget` cap). **Default:** **`crtqa_outline`** (no token required).
- **`draft_split=per_check`** / **`per_bundle`** — override auto 8b split rule ([profiles](docs/test-prep-draft-profiles.json)).
- **`discover_override=yes`** — when **`test_prep_gates.blocked: true`** on **`-discover.json`**; set **`sources.discover_blocked_acknowledged: true`**.
- **`dxtrade5_creds=<user>/<password>`** / **`webbroker_creds=<user>/<password>`** — transient only (**MUST NOT** enter durable JSON).
- **`fe_exploration_waived=yes`** — only after Phase **0b** FE stop + operator ack (caps FE at **`shell_only`**).
- **`proceed`** — after Phase **0** hard stop; re-run Phase **0** then continue fresh.
- **`skip_cold_gate=yes`** — waive machine gates; log waiver in **`validation_log`**.

**Scope**: **one Epic** per run. **Router**: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc).

**Doctrine**: [docs/harness-principles.md](../../docs/harness-principles.md) §3–§10 — **generation (greenfield)** assumes **no live CRTQA Jira fetch**; humans create Jira tests **after** drafts. **Default output:** **CRTQA-shaped executable outlines** ([`docs/test-prep-draft-profiles.json`](../../docs/test-prep-draft-profiles.json) **`crtqa_outline`**) — full **case_outline** expansion with human-fill session placeholders only ([`docs/test-prep-tbd-contract.json`](../../docs/test-prep-tbd-contract.json)).

**Exploration depth (DISCOVER → PRECON → PREP):**

| Pipeline | Dive | Role |
|----------|------|------|
| **TEST-DISCOVER** | 1 — surface | Obligations, affordances, fixture depth |
| **TEST-PRECON** | 2 — abstraction | Environment setup + **`test_skeleton[]`** + **`case_outline[]`** |
| **TEST-PREP** | 3 — verification outlines | Expand outlines into Actions/Results (`-tests.json`/`.md`) |

---

## Epic workspace (`{EpicDir}`)

Resolve **`{EpicDir}`** like [`epic-prep.md`](epic-prep.md).

**Prerequisite**: **`{EpicDir}<KEY>-coverage.json`** (from **`COVERAGE:`**, **schema v2** with **`obligations_coverage`**). If missing: **stop** → instruct **`COVERAGE: <KEY>`**.

**Obligation gate**: If **`-ref.json`** **`obligations_proposed[]`** has **`primary_candidate`** rows not **`covered`** or **`excluded_with_reason`** in **`obligations_coverage`**, **STOP** (or use **`map_only=yes`** with operator ack) — do not invent checks to fill coverage gaps ([`docs/harness-principles.md`](../../docs/harness-principles.md)).

### JSON inspection (inspect only)

Before loading **`-coverage.json`** (required), **`-precon.json`**, **`-discover.json`**, **`-ref.json`**, or **`-analysis.json`** for **inspection**: **MUST** project with `jq` per [automation/docs/jq.md](../../automation/docs/jq.md); do not load full epic JSON into context for multi-field reasoning. **Read** only slices needed for **edit/emit**. For **`{EpicDir}temp/test-prep-plan.json`** and per-bundle plan drafts during merge: **SHOULD** `jq` key slices (`bundles`, `verification_plan`) before full Read when files grow large.

### Optional discovery (`{EpicDir}<KEY>-discover.json`)

- **SHOULD** load before bundle planning (after **`jq`** projection per [JSON inspection](#json-inspection-inspect-only)); honour **`test_prep_gates.blocked`** unless **`discover_override=yes`** (same as v1).
- **MUST NOT** emit **`[REQUIRES: CRTQA-*]`** from discover when **`crtqa_index_enabled`** is false.
- Use **`fixture_needs`**, **`obligation_ledger`**, **`verification_affordances`** for modality hints only—not step text.

### Optional precondition (`{EpicDir}<KEY>-precon.json`)

- **SHOULD** load before phase **8a** (after **`jq`** projection per [JSON inspection](#json-inspection-inspect-only)).
- **Phase 8a**: adopt **`test_skeleton[]`** into **`test_bundles[]`** shells when present.
- **Phase 8b preconditions**: **thin** — cite **`-precon.md`** cluster; **must not** paste full console/WebBroker blocks per bundle.

**Outputs**:

- **`{EpicDir}<KEY>-tests.json`** — [`epics/templates/tests-ref.json`](../../epics/templates/tests-ref.json) **schema_version 4**.
- **`{EpicDir}<KEY>-tests.md`** — mapping + draft bodies for human / Jira paste.

**Ephemeral**: **`{EpicDir}temp/`** only — **`test-prep-plan.json`**, **`test-prep-plan-<bundle_id>.json`**, **`test-prep-draft-<bundle_id>.json`**, **`test-prep-draft-<bundle_id>-<check_id>.json`**, optional **`test-prep-fe-probe.json`**. **Delete** before run complete. **Never** persist **`/temp/`** in durable JSON.

**Exploration depth:** Phase **0c** = **`smoke` only** ([`docs/exploration-depth-ladder.json`](../../docs/exploration-depth-ladder.json)). Phase **8a¾** = **`prep_verify_view`**. **Out of scope**: mutating console/DB, Playwright, **live** **`execution trade`** execution during PREP — **literary templates** with placeholders **are required** for **`stateful_ladder`** in **`crtqa_outline`**.

**Downstream**: [`CLOSE:`](close.md) optional (documentation integrity + archive).

---

## Normative rules (MUST / MUST NOT)

### Greenfield (generation)

- **MUST NOT** use **existing CRTQA Test** issues for bundle design, preconditions chains, or Actions/Results prose.
- **MUST NOT** run Jira test search/fetch in generation (phase **6** logs skip); **`existing_tests_considered: []`**, **`jira_test_search.skipped: true`**.
- **MUST NOT** emit **`[REQUIRES: CRTQA-*]`** in generation (use **`crtqa_index=yes`** on **TEST-DISCOVER** only when operator opts in).

### CRTQA outline (default `draft_profile=crtqa_outline`)

- **Actions / Results**: numbered **1:1** pairs — **one** top-level pair per **`case_outline[]`** row from plan (merged from PRECON + 8a½). **Anti-pattern (v3.1):** do **not** emit one numbered pair per line of **`command_patterns.ladder_step`** — those lines are **sub-bullets inside** the single action for that row ([`docs/test-prep-tbd-contract.json`](../../docs/test-prep-tbd-contract.json) **`expansion_policy.single_pair_per_case_outline_row`**; applies to **`stateful_ladder`**, **`rounding_matrix`**, **`pattern_ref: ladder_step`**).
- **`[TBD]`**: only session literals (`<account_code>`, …) and tagged gaps (`[oracle:TBD]`, `[attach:TBD]`) per [`docs/test-prep-tbd-contract.json`](../../docs/test-prep-tbd-contract.json). **Forbidden:** whole-scenario deferrals (`[TBD: ladder]`, bare `[TBD]`).
- **`stateful_ladder`**: use **`command_patterns.ladder_step`** from **`-precon.json`** with placeholders inside each row’s action; include **`execution trade`** template lines (not executed by agent).
- **Plan class:** `verification_plan[].verification_class` must match machine rules in [`docs/test-verification-classes.json`](../../docs/test-verification-classes.json) **`selection_rules_machine`** unless **`selection_override_reason`** is set; document **`selection_rule_priority`**.
- **Yogi / requirement tags** — **only** in **`draft.results[]`**; orchestrator passes **`results_only_context`** to subprocess.
- **Peculiarities**: formulas; FE labels from **8a¾** `metric_columns` / `widgets_seen`; no Yogi tags.

### Teaching (legacy `draft_profile=teaching`)

- **Actions**: ≤ **`illustration_budget`** (default **2**); remainder **`[TBD: …]`** per coverage.
- Same Yogi / path / orchestration rules as v2.

### Path hygiene, traceability, orchestration

- No **`/temp/`** in durable JSON; **8a½** one subprocess per bundle; **8b** one subprocess per bundle **or** per **`check_id`** when [split rule](docs/test-prep-draft-profiles.json) fires (unless **`draft_split=`** override); **8c** orchestrator merge; **no one-shot** all-bundle drafts.

### Step format

- **Preconditions → Actions → Results → Peculiarities** per [`tests-ref.json`](../../epics/templates/tests-ref.json) **format_norms** and [`docs/temp/tc-template.txt`](../../docs/temp/tc-template.txt).

---

## Verification ladder (phase 8a½)

**Registry**: [`docs/test-verification-classes.json`](../../docs/test-verification-classes.json).

**Temp plan only**: **`{EpicDir}temp/test-prep-plan.json`** — **never** full **`verification_plan[]`** rows in committed **`-tests.json`** (optional **`verification_classes_summary[]`** on bundles for humans).

**Per bundle `verification_plan[]` row** (agent merges from subprocess):

| Field | Source |
|-------|--------|
| **`check_id`** | `covers_check_ids` |
| **`verification_class`** | Rule-ordered selection from registry |
| **`observation_surfaces`** | coverage + discover modality |
| **`min_case_count`** | from registry + [`test-prep-draft-profiles.json`](../../docs/test-prep-draft-profiles.json) matrix |
| **`case_outline[]`** | merge PRECON skeleton outlines; add rows until **`min_case_count`** met |
| **`draft_profile`** | `crtqa_outline` (default) or `teaching` |
| **`coverage_anchor`** | short excerpt from `scenario_line` |
| **`discover_modality`** | disposition / affordance note when discover loaded |
| **`selection_rule_priority`** | which registry rule matched |

**Self-heal — plan loop** (max **3** epic iterations):

1. Run **8a½** subprocess per bundle → merge **`temp/test-prep-plan-<bundle_id>.json`** into **`test-prep-plan.json`**.
2. **`python automation/tools/test_prep_verify.py --mode plan --coverage … --plan …`**
3. On fail: fix plan subprocesses for affected bundles; goto 1.

---

## Phase 0 (after shells, before 8a½)

Runs **after** phase **8a** so FE surfaces derive from **`test_bundles[]`** + skeleton **`surfaces`**.

Contract: [`docs/fe-ui-probe-contract.json`](../../docs/fe-ui-probe-contract.json).

### 0a — Machine gates

When any bundle needs console/postgres ( **`ladder_in_test`** on skeleton, console in **`covers_check_ids`** surfaces, or discover tooling intent):

- **`crtqa_env_probe.py --coverage`**
- MCP **`list_tables`** if postgres required
- **`Get-CrtqaConsoleStatus.ps1`** if console required

### 0b — FE credential gate

**`required_fe_surfaces`**: union of bundle/skeleton **`surfaces`** + registry **`fe_probe_surfaces`** for planned classes + Adaptive when ref **`client_shell_impact.adaptive`** is **`affected`** / **`likely_affected`**.

Missing creds and no **`fe_exploration_waived=yes`** → **STOP** + **`operator_recovery`** (chat only).

### 0c — Post-login smoke (read-only Chrome)

**Depth `smoke` only** — login gate; **does not** satisfy verification exploration.

Record **`fe_ui_sessions`** in **`temp/test-prep-plan.json`**; copy to **`sources.fe_ui_sessions`** on emit.

**Hard stop** on auth fail when creds supplied.

---

## Phases (complete unless N/A)

### 1–5. Resolve, load, epic refresh, exclusions

Same as v1 (steps **1**–**5**): load coverage (required), analysis/ref optional — **MUST** `jq` project each present artifact per [JSON inspection](#json-inspection-inspect-only) before loading full files; when **`-analysis.json`** (v2) present, `jq '.exploration_suppressed[]'` — do not re-explore suppressed **`check_id`** rows; **`jira_get_issue`** for **Epic `<KEY>`** only (not CRTQA tests), build **`excluded_checks_with_reason[]`**.

### 6. Generation — skip CRTQA test search

- Set **`jira_test_search.at`** (ISO-8601), **`jira_test_search.skipped: true`**, **`jira_test_search.note`**: `generation_mode_greenfield`.
- **`jira_test_search.queries: []`**
- **`existing_tests_considered: []`**
- **Do not** run **`jira_search`** for CRTQA tests in generation.
- Append **`validation_log`**: **`6-skip-crtqa-search`**.

### 8a. Bundle shells

- Adopt **`test_skeleton[]`** when **`-precon.json`** loaded; else bundle from [Bundling](#bundling-normative).
- **`related_existing_tests: []`** always in generation.
- **`precon_cluster_refs[]`** from skeleton when present.
- **`draft`**: empty `[]` or single-line pending placeholders unless **`map_only`**.
- Set **`sources.tests_run_started_at`** (ISO-8601).
- Append **`validation_log`**: **`8a`**.

### Phase 0 (after 8a)

Complete **0a**–**0c** above. Append **`validation_log`**: **`phase0`**, **`phase0b`**, **`phase0c`** as applicable.

### 8a½. Verification plan (one subprocess per bundle)

**Input to subprocess**: coverage slice, discover slice (if loaded), registry path, bundle shell, **`-precon.json`** **`case_outline[]`** + **`session_placeholders`** / **`command_patterns`**, **`fe_ui_sessions`**, ref **`client_shell_impact`**, **`draft_profile`**.

**Output**: **`{EpicDir}temp/test-prep-plan-<bundle_id>.json`** with **`verification_plan[]`** (each row includes **`case_outline[]`**, **`min_case_count`**, **`draft_profile`**), **`plan_status`**, **`fe_probe_surfaces`**, **`ladder_dependency_declared`** when class is **`stateful_ladder`**.

**Merge:** set epic-level **`draft_profile`** on **`temp/test-prep-plan.json`** (default **`crtqa_outline`**).

Orchestrator merges into **`{EpicDir}temp/test-prep-plan.json`**.

Append **`validation_log`**: **`8a-half-<bundle_id>`**.

### 8a½-verify. Plan verifier gate

```powershell
python automation/tools/test_prep_verify.py --mode plan `
  --coverage {EpicDir}<KEY>-coverage.json `
  --plan {EpicDir}temp/test-prep-plan.json
```

- Max **3** epic iterations on non-zero exit.
- On pass: set each bundle **`plan_status: verified`** in temp plan.

Append **`validation_log`**: **`8a-half-verify`**.

### 8a¾. Verification exploration (one subprocess per bundle)

**After plan verify, before 8b.** Contract: [`docs/exploration-depth-ladder.json`](../../docs/exploration-depth-ladder.json) **`prep_requires`**.

**Input:** plan slice, **`-precon.json`** `exploration_log` summary, optional **`-discover.json`**, **`fe_ui_sessions`**, coverage metric keywords.

**Task:** reach **`prep_verify_view`** per **`verification_class`** — open verification-target grids (Position Book, Positions widget, Adaptive portfolio metrics, console metric help family for **`stateful_ladder`**).

**Output:** merge into **`temp/test-prep-plan.json`** per bundle:

```json
{
  "bundle_id": "tb-003",
  "verification_exploration": [
    {
      "surface": "dxtrade5",
      "depth_level": "prep_verify_view",
      "view_id": "positions_widget_metrics",
      "metric_columns": ["Open P/L", "% PL Gross"],
      "widgets_seen": [],
      "precon_depth_ok": true
    }
  ]
}
```

**MUST** use Chrome MCP navigation beyond login; **≥1** row per **`observation_surfaces`** on parity classes.

**Optional split:** one subprocess per **surface** when plan lists multiple FE surfaces.

Append **`validation_log`**: **`8a-three-quarter-<bundle_id>`**.

### 8a¾-verify. Exploration verifier (per bundle, max 2 iterations)

```powershell
python automation/tools/test_prep_verify.py --mode explore `
  --coverage {EpicDir}<KEY>-coverage.json `
  --plan {EpicDir}temp/test-prep-plan.json `
  --precon {EpicDir}<KEY>-precon.json `
  --bundle-id tb-003
```

Epic cap: **5** bundle explore failures → set **`test_prep_gates.blocked: true`** on temp plan + **STOP** with operator recovery (chat).

On fail: re-run **8a¾** for that bundle only.

Append **`validation_log`**: **`8a-three-quarter-verify-<bundle_id>`**.

### 8b. Draft (skip if `map_only`)

**Split rule** ([`docs/test-prep-draft-profiles.json`](../../docs/test-prep-draft-profiles.json)): **per-check** subprocess when bundle has class in `{stateful_ladder, derived_metric, invariant_under_change, rounding_matrix}` **and** (`len(covers_check_ids) > 1` **or** `min_case_count > 4`). Else **per-bundle**. Override with **`draft_split=`** on trigger.

**MUST NOT** one-shot all bundles or all checks in parent chat.

**Orchestrator → subprocess** (bounded pack):

1. `epic_key`, `bundle_id`, `check_id` (when per-check), `proposed_title`, `draft_profile`.
2. Coverage slice; **plan slice** including **`case_outline[]`** for target check(s).
3. **`-precon.json`**: **`session_placeholders`**, **`command_patterns`**, thin precon cite text.
4. **`verification_exploration[]`** / **`metric_columns`** from plan (**8a¾**).
5. **`results_only_context`** (Yogi — **Results only**).
6. [test-verification-classes.json](../../docs/test-verification-classes.json), [test-prep-tbd-contract.json](../../docs/test-prep-tbd-contract.json).

**Output**:

- Per-bundle: **`temp/test-prep-draft-<bundle_id>.json`**
- Per-check: **`temp/test-prep-draft-<bundle_id>-<check_id>.json`**

Append **`validation_log`**: **`8b-<bundle_id>`** or **`8b-<bundle_id>-<check_id>`**.

### 8c. Merge drafts (orchestrator; skip if `map_only`)

1. For each bundle: concatenate per-check draft arrays in **`case_id`** order into one **`draft`** on **`test_bundles[]`**.
2. Set **`authoring.subprocess_completed: true`**, **`verification_classes_summary[]`**.
3. **`python automation/tools/test_prep_verify.py --mode merge --tests … --plan …`**
4. Append **`validation_log`**: **`8c`**.

### 8c-verify. Path scrub (skip if `map_only`)

Same as v2 path scrub on durable-bound staging; append **`validation_log`**: **`8c-scrub`**.

### 8b-verify. Draft verifier (per bundle, max 2 retries)

**Requires `--plan`** (v3.1: outline cardinality + duplicate-action gates for ladder/rounding bundles).

```powershell
python automation/tools/test_prep_verify.py --mode draft `
  --coverage {EpicDir}<KEY>-coverage.json `
  --tests <in-memory or temp staging> `
  --bundle-id tb-001 `
  --plan {EpicDir}temp/test-prep-plan.json
```

On fail: re-run **8b** for that bundle only (fix expansion: one pair per **`case_outline`** row, not per **`ladder_step`** line).

### 9–10. Reverse validation and anti-patterns

Same as v1; add anti-pattern **`crtqa_structural_dependency_in_generation`**, **`verification_plan_missing`**.

### 11. Emit

**Pre-write**:

```powershell
python automation/tools/test_prep_verify.py --mode tests `
  --coverage {EpicDir}<KEY>-coverage.json `
  --tests {EpicDir}<KEY>-tests.json `
  --plan {EpicDir}temp/test-prep-plan.json
```

(Use the same **`test-prep-plan.json`** used for **8a½**–**8c**; **required** for **`crtqa_outline`** emit — exclusion ↔ **`coverage_gaps[]`**, outline cardinality.)

Write **`-tests.md`** and **`-tests.json`**. When **`map_only`**: include verification plan summary table from temp plan; note map-only.

**`sources.fe_ui_sessions`**, **`sources.fe_exploration_waived`**, **`sources.generation_mode: true`**, **`sources.draft_profile`**, optional **`sources.shape_ref`** on emit.

### 12. Cleanup

**Delete** **`{EpicDir}temp/`** entirely.

---

## Subprocess contracts

### Plan subprocess (`8a½`)

Write **`temp/test-prep-plan-<bundle_id>.json`**:

```json
{
  "bundle_id": "tb-002",
  "draft_profile": "crtqa_outline",
  "verification_plan": [
    {
      "check_id": "chk-002",
      "verification_class": "stateful_ladder",
      "min_case_count": 6,
      "case_outline": [
        {
          "case_id": "c01",
          "check_id": "chk-002",
          "title": "Multi-buy then sell through zero with remainder",
          "intent": "opening-side avg; realized on close",
          "pattern_ref": "ladder_step"
        }
      ],
      "observation_surfaces": ["console"],
      "coverage_anchor": "…",
      "selection_rule_priority": 40
    }
  ],
  "plan_status": "pending",
  "ladder_dependency_declared": true,
  "fe_probe_surfaces": []
}
```

### Draft subprocess (`8b`)

Write **`temp/test-prep-draft-<bundle_id>.json`** or **`temp/test-prep-draft-<bundle_id>-<check_id>.json`**:

```json
{
  "bundle_id": "tb-002",
  "check_id": "chk-002",
  "draft": { "preconditions": [], "actions": [], "results": [], "peculiarities": [] },
  "verification_classes_summary": ["stateful_ladder"],
  "authoring_notes": []
}
```

---

## Bundling (normative)

Unchanged from v1: merge by shared surface/session/preconditions; split on reset/persona; copy **`covers_sections`** from **`-coverage.md`**.

---

## Pitfalls

| Pattern | Severity |
|---------|----------|
| One-shot all-bundle drafts | **Violation** |
| CRTQA search or reuse in generation | **Violation** |
| Yogi tags outside **Results** | **Violation** |
| Skip plan verify before **8b** | **Violation** |
| Full **verification_plan** in durable **`-tests.json`** | **Violation** |
| Phase **0** after plan without creds when FE required | **Violation** |
| Skip **8a¾** before **8b** when plan class needs `prep_verify_view` | **Violation** |
| **8b** Peculiarities labels not from **8a¾** `metric_columns` / `widgets_seen` | **Violation** |
| Whole-scenario `[TBD]` in **crtqa_outline** | **Violation** |
| CRTQA keys in durable draft (generation) | **Violation** |
| **teaching**: invented `execution trade` without vignette/TBD | **Violation** |
| **crtqa_outline**: `stateful_ladder` without ladder template markers | **Violation** |
| Skip **8c** merge after per-check **8b** | **Violation** |

---

## Related

| Item | Path |
|------|------|
| Template | [`epics/templates/tests-ref.json`](../../epics/templates/tests-ref.json) |
| Verification classes | [`docs/test-verification-classes.json`](../../docs/test-verification-classes.json) |
| Draft profiles | [`docs/test-prep-draft-profiles.json`](../../docs/test-prep-draft-profiles.json) |
| TBD contract | [`docs/test-prep-tbd-contract.json`](../../docs/test-prep-tbd-contract.json) |
| Verifier | [`automation/tools/test_prep_verify.py`](../../automation/tools/test_prep_verify.py) · [doc](../../automation/docs/test-prep-verify.md) (`plan`, `explore`, `draft`, `merge`, `tests`) |
| Calibrate (post-hoc) | [`.cursor/pipelines/calibrate.md`](calibrate.md) |
| Exploration depth | [`docs/exploration-depth-ladder.json`](../../docs/exploration-depth-ladder.json) |
| FE contract | [`docs/fe-ui-probe-contract.json`](../../docs/fe-ui-probe-contract.json) |
| Precon | [`test-precon.md`](test-precon.md) |
| Discover | [`test-discover.md`](test-discover.md) |
| Coverage | [`coverage.md`](coverage.md) |
