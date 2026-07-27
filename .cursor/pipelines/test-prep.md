# Pipeline: test-prep (scenario intent drafts) v3.1

**Trigger**: user message starts with **`TEST-PREP:`** and includes a Jira **Epic key** (e.g. `TEST-PREP: CRT-639`). Optional tokens on the **same line**:

- **`map_only=yes`** — emit bundle shells + intent plan only; omit full draft prose.
- **`draft_profile=crtqa_outline`** — **legacy** calibrate/benchmark only (requires operator plan in temp/; no PRECON).

**Scope**: **one Epic** per run. **Router**: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc).

**Doctrine**: [docs/harness-principles.md](../../docs/harness-principles.md) §10 — default **`scenario_intent`** profile. Contract: [`docs/test-prep-scenario-intent-contract.json`](../../docs/test-prep-scenario-intent-contract.json). Groups: [`docs/scenario-groups-contract.json`](../../docs/scenario-groups-contract.json).

**No generation exploration:** **MUST NOT** run Phase 0 env gates, Chrome MCP, or cred tokens.

---

## Epic workspace (`{EpicDir}`)

Resolve **`{EpicDir}`** like [`epic-prep.md`](epic-prep.md).

### Prerequisites

| Artefact | Required |
|----------|----------|
| `{EpicDir}dependencies/<KEY>-coverage.json` | **Yes** — **`sources.coverage_frozen_at`** and **`scenario_groups[]`** must be set |
| `{EpicDir}dependencies/<KEY>-ref.json` | **Recommended** |
| `{EpicDir}dependencies/<KEY>-discover.json` | **Optional** — linker hints only |
| `{EpicDir}dependencies/<KEY>-analysis.json` | **Optional** — deferrals / suppressions |
| `{EpicDir}dependencies/<KEY>-precon.json` | **Must not load** in v3 production path |

If **`coverage_frozen_at`** or **`scenario_groups[]`** missing → **STOP** (instruct human **`coverage_review`** + **`COVERAGE:`** phase 8.6).

### Outputs

- **`{EpicDir}dependencies/<KEY>-tests.json`** — [`epics/templates/tests-ref.json`](../../epics/templates/tests-ref.json) **schema_version 4**.
- **`{EpicDir}dependencies/<KEY>-tests.md`** — mapping + draft bodies for human / Jira paste.

**Ephemeral**: **`{EpicDir}temp/`** only — **`test-prep-plan.json`**, **`test-prep-draft-<bundle_id>.json`**. **Delete** before run complete.

---

## Normative rules (MUST / MUST NOT)

### Greenfield

- **MUST NOT** use existing CRTQA Test issues for bundle design.
- **MUST NOT** run Jira CRTQA test search — **`jira_test_search.skipped: true`**, **`existing_tests_considered: []`**.
- **MUST NOT** emit **`[REQUIRES: CRTQA-*]`** in generation.

### Scenario intent (default)

- **One `test_bundles[]` row per `scenario_groups[]` row** — 1:1 **`group_id`** ↔ bundle mapping via **`covers_check_ids`**.
- **Actions:** plain English — what must be achieved. For **`variant_sequence`**, one numbered action per check variant in group order.
- **Results:** observable claim + **`[CRT-####]`** requirement tag. Formulas allowed with **`formula_provenance`**: **`agent_inferred`** (from requirement text) or **`ground_verified`** (from **`runtime_probes`**).
- **Forbidden in actions** unless check has **`grounding_certainty: observed`**: widget names, menu paths, harness oracle enums, click/navigate phrasing. See contract **`forbidden_ui_patterns`**.
- **Deferrals:** checks with **`delivery_status`** failed/excluded, analysis suppressions, or keyed deferrals → **`excluded_checks_with_reason`** only — **no** action rows.

### Preconditions

- **`shared_preconditions[]`** on **`-tests.json`** (once): summarize setup from coverage **`principal_coverage_threads`** environment/setup thread — not per-bundle console paste.

### Orchestration

- **MUST NOT** one-shot all bundles in one completion.
- Subprocesses: **8a** shells → **8a½** intent plan → **8b** draft per bundle → **8c** merge → **9** verify → **10** emit.

---

## Phases

### 1. Load (jq project first)

```bash
jq '{scenario_groups, sources: .sources | {coverage_frozen_at}}' epics/<KEY>/dependencies/<KEY>-coverage.json
jq '.checks[] | select(.verification_role=="primary") | {id, scenario_line, requirement_keys, delivery_status, runtime_probes, grounding_certainty}' epics/<KEY>/dependencies/<KEY>-coverage.json
```

Optional: discover linker slices, analysis **`exploration_suppressed[]`**, ref oracle rules for formula inference.

Build **`excluded_checks_with_reason[]`**: delivery failed/excluded, deferrals, out_of_epic.

### 2. Skip CRTQA search

Set **`jira_test_search.skipped: true`**, **`validation_log`**: **`6-skip-crtqa-search`**.

### 8a. Bundle shells

For each **`scenario_groups[]`** row:

- **`bundle_id`**: `tb-001`, … (sequential)
- **`proposed_title`**: copy **`title`**
- **`covers_check_ids`**: copy **`check_ids`** minus excluded primaries
- **`scenario_intent`**: one-line what this test proves
- **`scenario_group_ref`**: **`group_id`**
- **`combinatorics`**: from group

Skip bundles whose checks are all excluded.

### 8a½. Intent plan (light)

Per bundle in temp **`test-prep-plan-<bundle_id>.json`**:

- **`intent_steps[]`**: ordered strings from combinatorics + check **`scenario_line`** paraphrase (intent, not UI).
- Merge into **`temp/test-prep-plan.json`**.

### 8b. Draft subprocess (one per bundle)

Emit **`draft`**:

| Section | Content |
|---------|---------|
| **preconditions** | Reference **`shared_preconditions`** (cite setup thread title) |
| **actions** | From **`intent_steps[]`** |
| **results** | Requirement-linked claims; formulas when inferable |
| **peculiarities** | Formulas, rounding, deferral notes |

**Formula inference (4B):** derive from check **`scenario_line`**, ref **`pricing_oracle_rules`**, Yogi snippets — set **`formula_provenance: agent_inferred`**. When **`runtime_probes.verified_syntax`** present → **`ground_verified`**.

### 8c. Merge

Orchestrator merges temp drafts into **`-tests.json`**. Set **`sources.draft_profile: scenario_intent`**, **`sources.scenario_groups_loaded: true`**.

### 9. Verify

```powershell
python automation/tools/test_prep_verify.py --mode scenario_intent --ref {EpicDir}dependencies/<KEY>-ref.json --coverage {EpicDir}dependencies/<KEY>-coverage.json --tests {EpicDir}dependencies/<KEY>-tests.json
```

Fix failing bundles (max **3** epic iterations).

### 10. Emit

- Write **`-tests.json`** and **`-tests.md`** at epic root.
- Copy **`platform_reuse_annex`** into **`-tests.json`** when ref has **`platform_reuse_candidates`** — **omit** platform reuse section from **`-tests.md`** body (`emit_to_markdown: false` per [`docs/test-prep-topology-contract.json`](../../docs/test-prep-topology-contract.json)).
- **`reverse_validation.coverage_gaps`**: excluded primaries not in any bundle.
- Delete **`{EpicDir}temp/`**.

---

## Bundling (normative)

**Authority:** **`scenario_groups[]`** on frozen coverage ([`docs/scenario-groups-contract.json`](../../docs/scenario-groups-contract.json)). TEST-PREP **must not** invent groups — only consume and draft.

**Legacy `crtqa_outline`:** opt-in only; operator supplies **`case_outline[]`** in temp plan; not production default.

---

## Downstream

[`CLOSE:`](close.md) — documentation integrity + archive (no `-precon.json` required).
