# Pipeline: test-prep (regression test drafting)

**Trigger**: user message starts with `TEST-PREP:` and includes a Jira **Epic key** (e.g. `TEST-PREP: CRT-639`). Optional tokens on the same line:

- **`map_only=yes`** / `true` / `1` — emit **mapping** (`test_bundles[]` with `proposed_title`, `covers_check_ids`, `covers_sections`) and **Jira search audit** only; **omit** full `draft.preconditions` / `actions` / `results` / `peculiarities` prose (use empty arrays or single placeholder line per array documenting map-only). Use for fast traceability review before full authoring.

**Scope**: **one Epic** per run. **Router rule**: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc).

**Prerequisite**: `epics/<KEY>/<KEY>-coverage.json` **must** exist (from [`COVERAGE:`](coverage.md)). If missing: **stop** and instruct the user to run `COVERAGE: <KEY>` first. Do not fabricate checklist checks.

**Outputs**:

- `epics/<KEY>/<KEY>-tests.json` — structured artifact (from [`epics/templates/tests-ref.json`](../../epics/templates/tests-ref.json)).
- `epics/<KEY>/<KEY>-tests.md` — human-readable mapping table + draft test bodies for review / Jira paste.

**Authoring model**: Full **`draft`** prose (when not `map_only`) is produced **one bundle per subprocess** (phase **8b**), not in a single one-shot generation — see [Orchestration](#orchestration-no-one-shot-drafts).

**Explicitly out of scope (v1)**: Playwright MCP, QA database access, SSH / dxCore console execution. Operational examples (SQL, console commands, sample outputs) **must not** be invented; use **`[TBD]`** or **`[REQUIRES: <source>]`** unless text is **copied** from a **fetched** Jira issue field or an attached runbook excerpt the user provided in-chat (then cite source).

**Ephemeral**: `epics/<KEY>/temp/` — **must be deleted** before the run is considered complete (success or abort). Durable files must **not** contain the substring `/temp/`.

---

## Normative rules (MUST / MUST NOT)

### Mental model and taxonomy

- **MUST** treat **compliance / coverage** (`-coverage.json` / Smart Checklist) as the **matrix** to satisfy. **Regression** test cases in Jira are **client-facing taxonomy**; internally they are **E2E combinatoric bundles** that let a human execute the checklist efficiently.
- **MUST** minimize the **number** of test cases without dropping **effectiveness**: group many checklist lines into **one bundle** when they share **surface**, **user journey**, and **preconditions** (see [Bundling](#bundling-normative)).
- **MUST NOT** default to **one Jira test per checklist bullet** when bullets share the same session (see worked pattern: [`docs/temp/coverage-to-tests.txt`](../../docs/temp/coverage-to-tests.txt) — CRT-632 style).
- **Policy anchor** (human): [QAPORTAL — Test Repository](https://confluence.in.devexperts.com/spaces/QAPORTAL/pages/497097317/Test+Repository) — cite for taxonomy; do not duplicate full Confluence body in-repo.

### Step format

- **MUST** structure each bundle’s executable text as **Preconditions → Actions → Results → Peculiarities**, per [docs/tc-ref](../../docs/tc-ref) and the inline example [`docs/temp/tc-template.txt`](../../docs/temp/tc-template.txt): cross-reference Preconditions/Actions to Peculiarities (`see Peculiarities N`).
- **MUST** put formulas, Figma/Slack links, scope caveats, setup detail, and copy-paste **evidence** in **Peculiarities**, not in the main **Actions** list when that keeps Actions linear.

### Jira reuse (anti-hallucination)

- **MUST** use **user-mcp-atlassian** (`jira_search`, `jira_get_issue`) for **discovery and retrieval** — read tool schemas before calls; follow [`.cursor/rules/mcp-atlassian-search.mdc`](../rules/mcp-atlassian-search.mdc).
- **MUST NOT** invent test steps, expected results, SQL, or console commands **from issue titles or from memory**. If `jira_get_issue` was **not** run for an issue, **do not** claim its steps — set `steps_provenance: not_fetched` and use **`[GAP: pull steps from CRTQA-xxxx or author manually]`** in the draft where reuse was intended.
- **MUST** record JQL and `result_count` per query in `jira_test_search.queries[]`.
- **MUST** set `existing_tests_considered[].reuse_recommendation` only when **`steps_provenance == fetched_from_issue`**; otherwise `none` or omit recommendation with note.

### Unknowns and operational detail

- **MUST** use **`[TBD]`** or **`[REQUIRES: <specific source>]`** when the agent lacks **tool-backed** or **user-supplied** text for a label, command, query, or expected output.
- **MUST** treat **hesitation** as **unknown** — same as missing data.
- **MUST NOT** output **plausible** dxCore commands, SQL, or example outputs without a **fetched** or **user-pasted** source.

### Exclusions

- **MUST NOT** author bundles whose sole purpose is to cover checks that are **excluded** per coverage **`explicitly_out_of_scope`**, unless the user explicitly overrides in the trigger (default: no override).
- **MUST** skip checks with **`checks[].ambiguity`** set (Smart Checklist **`!`**) **unless** the user adds an explicit waiver in the trigger line (e.g. `include_ambiguous=yes`) — default **skip** and list under **`excluded_checks_with_reason`**.
- **SHOULD** use **`-analysis.json`** when present: skip or flag checks tied to **`gaps[]`** with `type: unverifiable` (or similar) the same way — record in **`excluded_checks_with_reason`** with `reason: analysis_gap` and evidence pointer.

### Traceability and reverse validation

- **MUST** assign every **included** primary-relevant check (see below) to **exactly one** `test_bundles[].covers_check_ids` entry, **or** document waiver in **`excluded_checks_with_reason`**.
- **MUST** populate **`reverse_validation.coverage_gaps[]`** for every **`checks[].id`** that is **`verification_role: primary`** or **`null`** (treat null as in-scope for traceability when not excluded) and **not** covered by any bundle **and** not excluded — **coverage_gaps must be empty** when healthy, or each gap explained.
- **MUST** populate **`draft_red_flags[]`** when: a bundle has **empty** `covers_check_ids`; the same `check_id` appears in **multiple** bundles without explicit rationale in `reverse_validation.notes`; or self-review detects **ungrounded operational detail** risk.
- **SHOULD** list **`reverse_validation.orphan_bundles[]`** for bundles with zero `covers_check_ids` after phase 8a.

**Primary-relevant checks**: Prefer `checks[].verification_role == primary` or matrix-aligned primary rows; for **`supporting`** / **`out_of_epic`**, bundle **with** their primary scenario in the same test session when they are **`detail_lines`**-only for the same user journey; otherwise exclude per coverage norms or list under exclusions with rationale.

### Orchestration (no one-shot drafts)

- **MUST** use a **single user trigger** `TEST-PREP:` — the human does **not** re-prompt per test. The **orchestrator** (the agent handling the trigger) runs planning **once**, then runs **one subprocess per bundle** for full draft prose.
- **MUST NOT** generate **full** `draft.preconditions` / `actions` / `results` / `peculiarities` for **more than one** `bundle_id` in a **single** model completion / turn when `sources.map_only` is **false**. Treat **batching all bundle drafts** in one shot as a **pipeline violation** (same severity as inventing Jira text).
- **MUST** complete **phase 8a** (bundle **shells** only: ids, titles, `covers_check_ids`, `covers_sections`, `related_existing_tests`; `draft` empty or single-line placeholders) **before** starting **phase 8b** subprocesses.
- **MUST** run **phase 8b** as **N sequential subprocesses** (N = number of bundles), **one bundle per subprocess**. Recommended: Cursor **Task** tool with `subagent_type: generalPurpose` (or any equivalent **isolated** agent run). Each subprocess **only** authors **that** bundle’s `draft`.
- **When `map_only` is true**: **skip** phase **8b** entirely; shells may carry map-only placeholder `draft` lines only.

---

## Subprocess prompt contract (normative)

**Mechanism**: One **dedicated subprocess** per `test_bundles[].bundle_id`. **Do not** pass the entire epic coverage JSON if avoidable — pass a **minimal slice**.

**Orchestrator → subprocess — include explicitly**:

1. `epic_key`, `bundle_id`, `proposed_title`.
2. **Coverage slice**: for each id in `covers_check_ids`, the full matching **`checks[]`** object from `-coverage.json` (`id`, `section`, `subsection`, `scenario_line`, `detail_lines`, `verification_role`, `ambiguity`, `requirement_keys`).
3. **`existing_tests_considered[]`** rows whose `key` appears in `related_existing_tests` — include **verbatim** fetched step/description fields when `steps_provenance == fetched_from_issue`; otherwise one line per key: not fetched, do not invent.
4. Pointers: [docs/tc-ref](../../docs/tc-ref), [docs/temp/tc-template.txt](../../docs/temp/tc-template.txt), and this playbook’s **Jira reuse**, **Unknowns**, **Exclusions** bullets (or a one-line “obey test-prep.md MUST NOT invent”).
5. Output schema (subprocess must return or write — see below).

**Subprocess → orchestrator — output**:

- A JSON object:  
  `{ "bundle_id": "<same as input>", "draft": { "preconditions": [], "actions": [], "results": [], "peculiarities": [] }, "authoring_notes": [] }`  
  `authoring_notes` optional (e.g. why a line is `[TBD]`).

**Preferred persistence (robust merge)**: Subprocess writes **`epics/<KEY>/temp/test-prep-draft-<bundle_id>.json`** with the object above (sanitize `bundle_id` for the filename, e.g. replace unsafe chars). Orchestrator **reads** each file after the subprocess returns, **merges** `draft` into the matching `test_bundles[]` entry, sets **`authoring.subprocess_completed`** and **`authoring.completed_at`** (ISO-8601), leaves **`authoring.temp_draft_file`** **null** in **durable** `-tests.json` (never persist `/temp/` paths in committed output).

**Alternative**: Subprocess returns the JSON object only in the Task transcript — acceptable if the orchestrator **parses** it reliably; **prefer temp files** when unsure.

**Caps**: Subprocess **may** call `jira_get_issue` only for keys listed in `related_existing_tests` if orchestrator did not already fetch body text — keep extra fetches **minimal** (orchestrator should prefetch in phase 7).

---

## Bundling (normative)

1. **Merge** when: same **surface** (e.g. same app / same major screen), continuous **navigation**, shared **preconditions** (same user, account, instrument setup), and executing **Action N** does not invalidate **Result** of prior checks in the bundle.
2. **Split** when: different **persona** or **account**, **backend reset** required between scenarios, or a **long** unrelated journey (different major `##` section with different setup).
3. **Allow** one proposed Jira test to span **multiple `###` subsections** when one session validates all (pattern: shared **CRTQA** key across Instrument page subsections in [`docs/temp/coverage-to-tests.txt`](../../docs/temp/coverage-to-tests.txt)).
4. **Copy** `covers_sections` from **`-coverage.md`** `##` / `###` headings where possible for human orientation.

---

## Preconditions

- **user-mcp-atlassian**: Jira tools — schema before calls.
- **Inputs**: **`epics/<KEY>/<KEY>-coverage.json`** (required), **`epics/<KEY>/<KEY>-coverage.md`** (recommended for headings), **`epics/<KEY>/<KEY>-analysis.json`** (optional), **`epics/<KEY>/<KEY>-ref.json`** (optional — `client_shell_impact`, `synthesis`).
- **Context**: [`docs/qa-project.json`](../../docs/qa-project.json) for Jira project lists (CRTQA, CRT, CRTBL, SUPXT, CAN, etc.).

---

## Folder lifecycle

1. Ensure `epics/<KEY>/` exists.
2. Create `epics/<KEY>/temp/` when saving raw Jira exports **or** per-bundle draft fragments.
3. **Allowed in `temp/` only**: e.g. `jira-epic.json`, `jira-test-search-*.json`, **`test-prep-draft-<bundle_id>.json`** (phase 8b). **No cookies or tokens** in committed files.
4. Merge durable facts into `epics/<KEY>/<KEY>-tests.json` and write `epics/<KEY>/<KEY>-tests.md`.
5. **Delete** `epics/<KEY>/temp/` recursively before finishing.
6. **Self-check**: `<KEY>-tests.json` and `.md` must **not** contain `/temp/`.

---

## Phases (complete all unless N/A — document skip in `validation_log`)

### 1. Resolve trigger and paths

- Parse `<KEY>` and optional **`map_only`** (`yes`/`true`/`1` → `sources.map_only: true`).
- Set `epic_key`, `sources.*_path`, append `validation_log` step `1`.

### 2. Load coverage (required)

- Read `epics/<KEY>/<KEY>-coverage.json`. If missing: **stop**; log and instruct `COVERAGE: <KEY>`.
- Set `sources.coverage_loaded: true`, timestamp if useful.
- Read `epics/<KEY>/<KEY>-coverage.md` when present for section headings.
- Append `validation_log`: step `2`.

### 3. Load optional inputs

- Read `epics/<KEY>/<KEY>-analysis.json` → `sources.analysis_loaded`.
- Read `epics/<KEY>/<KEY>-ref.json` → `sources.ref_loaded`.
- Append `validation_log`: step `3`.

### 4. Refresh Epic (Jira)

- MCP `jira_get_issue` for `<KEY>`; optional save raw JSON to `temp/jira-epic.json`.
- Set `sources.jira_fetched_at` (ISO-8601).
- Append `validation_log`: step `4`.

### 5. Build exclusion set

- From **`-coverage.json`**: all **`explicitly_out_of_scope`** themes; each **`checks[]`** with non-null **`ambiguity`** (unless user `include_ambiguous=yes` in trigger).
- From **`-analysis.json`** when loaded: map **`gaps[]`** with `type` in `unverifiable`, `snippet_missing` (optional team policy — default exclude or flag per gap evidence).
- Populate **`excluded_checks_with_reason[]`** with `check_id`, `reason`, `evidence` (field path).
- Append `validation_log`: step `5`.

### 6. Jira search — existing tests

- Set `jira_test_search.at` (ISO-8601).
- Run **multiple** `jira_search` calls; record `jql`, `purpose`, `result_count` in `jira_test_search.queries[]`.

**JQL strategy** (adapt to instance; try in order):

1. **Epic linkage** (`epic_link`): e.g. `"Epic Link" = <KEY>` or `parent = <KEY>` or `issue in childIssuesOf("<KEY>")` if supported — scope to **Test** / **CRTQA** issue types **only if** `issuetype` names are confirmed from a sample query; otherwise broader project filter.
2. **Epic key text** (`epic_key_text`): `text ~ "<KEY>" AND project in (CRTQA, ...)` per qa-project.
3. **Summary keywords** (`summary_keyword`): 1–2 queries from epic summary tokens + `epic_verification_focus.keywords` when present.

- Cap total issues considered (e.g. **≤ 50** keys) before selective `jira_get_issue`.
- Append `validation_log`: step `6`.

### 7. Fetch candidate tests

- For the **most relevant** subset of search hits (epic-linked first, then keyword), run **`jira_get_issue`** to retrieve description / test-step fields.
- Populate **`existing_tests_considered[]`** with `key`, `summary`, `status`, `issuetype`, `url`, `steps_provenance`, `fields_used`, `reuse_recommendation` per template rules.
- Append `validation_log`: step `7`.

### 8a. Compose test bundle shells (orchestrator only)

- Cluster **`checks[]`** (minus exclusions) using [Bundling](#bundling-normative) rules.
- Assign **`bundle_id`** (`tb-001`…), **`proposed_title`**, **`covers_check_ids`**, **`covers_sections`**, **`related_existing_tests`** (keys from phase 7 that overlap thematically — **do not** imply steps were reused unless fetched).
- Initialize **`authoring`**: `subprocess: true`, `subprocess_completed: false`, `completed_at: null`, `temp_draft_file: null` (see template). If **`map_only`**: set **`authoring.subprocess: false`**, keep **`subprocess_completed: false`**; **skip phase 8b**.
- If **`map_only`**: set `draft` arrays to minimal placeholders documenting map-only only; **skip phase 8b**.
- If **not** `map_only`: set **`draft`** to **empty arrays** `[]` **or** a **single** placeholder string per array (e.g. `"1. [PENDING subprocess tb-001]"`) — **do not** write full Preconditions/Actions/Results/Peculiarities prose in this phase.
- Append `validation_log`: step `8a`.

### 8b. Draft each bundle via subprocess (skip if `map_only`)

- For **each** `test_bundles[]` entry in order:
  1. Invoke a **dedicated subprocess** per [Subprocess prompt contract](#subprocess-prompt-contract-normative) (e.g. **Task** `generalPurpose`).
  2. Subprocess produces **`draft`** only for **this** `bundle_id`.
  3. Merge: read `temp/test-prep-draft-<bundle_id>.json` **or** parse subprocess return → copy `draft` into `test_bundles[]` for matching `bundle_id`.
  4. Set **`authoring.subprocess_completed: true`**, **`authoring.completed_at`** (ISO-8601). **Do not** write **`temp_draft_file`** paths into durable JSON.
  5. Append `validation_log`: e.g. step `8b-tb-001` … or one entry per bundle with `action: merged draft for tb-00N`.
- **MUST NOT** substitute 8b by generating all drafts in the orchestrator in one completion — see [Orchestration](#orchestration-no-one-shot-drafts).

### 9. Reverse validation

- Compute **`reverse_validation.coverage_gaps`** for uncovered primary-relevant checks.
- Detect **duplicate** `check_id` across bundles → **`draft_red_flags`** + **`reverse_validation.notes`**.
- Detect bundles with **empty** `covers_check_ids` → **`orphan_bundles`** / **`draft_red_flags`**.
- Append `validation_log`: step `9`.

### 10. Anti-pattern scan

- Populate **`anti_pattern_findings[]`** for: one-bullet-one-test explosion without justification; missing traceability; suspected invented operational detail (self-check).
- Append `validation_log`: step `10`.

### 11. Emit markdown

- Write **`epics/<KEY>/<KEY>-tests.md`**:
  - **Epic** line and optional focus from coverage.
  - **Mapping table**: `bundle_id` | `proposed_title` | `covers_check_ids` (comma-separated) | `covers_sections` (short).
  - **Existing tests considered** (bullets: key — summary — reuse note).
  - **Per bundle**: full draft text (Preconditions / Actions / Results / Peculiarities) **or** map-only notice.
  - **Reverse validation** summary: gaps (must be empty or listed), red flags, notes.
  - **Excluded checks** summary when non-empty.

- Write **`epics/<KEY>/<KEY>-tests.json`** from template, all sections filled.

- Append `validation_log`: step `11`.

### 12. Cleanup

- **Delete** `epics/<KEY>/temp/`.
- Append `validation_log`: step `12` (complete).

---

## Pitfalls

- **One-shot all-bundle drafts** — Violates [Orchestration](#orchestration-no-one-shot-drafts); use phase **8b** per bundle.
- **Inventing Jira steps** — Titles are not evidence; fetch or `[GAP]`.
- **Inventing SQL/console** — Use `[TBD]` / `[REQUIRES: …]`.
- **Ignoring `!` ambiguity** — Default skip + `excluded_checks_with_reason`.
- **Traceability holes** — `coverage_gaps` must be reconciled or waived in writing.
- **Temp leakage** — Mandatory delete + substring self-check; never persist `/temp/` paths in `-tests.json`.

---

## Related

- Template: [`epics/templates/tests-ref.json`](../../epics/templates/tests-ref.json)
- Coverage playbook: [`coverage.md`](coverage.md)
- Analysis playbook: [`analysis.md`](analysis.md)
- Epic ref: [`epic-prep.md`](epic-prep.md), [`epics/README.md`](../../epics/README.md)
- Router: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc)
