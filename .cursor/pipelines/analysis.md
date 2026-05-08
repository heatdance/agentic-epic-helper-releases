# Pipeline: analysis

**Trigger**: user message starts with `ANALYSE:` and includes a Jira **Epic key** (e.g. `ANALYSE: CRT-639`). Optional tokens on the same line:

- **`include_closed=`** — when set to `yes` / `true` / `1`, allow **recent closed** issues (e.g. resolved within 90 days) to be appended as **`>`** detail lines in coverage when `in_scope_relevant` and they serve as a **regression anchor**. **Default**: **OPEN issues only** for coverage mutation.
- **`benchmark_suite=<suite_id>`** / **`benchmark_attempt=<n>`** — optional shadow `{EpicDir}` ([`docs/benchmark-contract.md`](../../docs/benchmark-contract.md)); must match prior **EPIC-PREP**/**COVERAGE** tokens for this attempt.

**Scope**: **one Epic** per run. **Router rule**: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc).

## Epic workspace (`{EpicDir}`)

Resolve **`{EpicDir}`** like [`epic-prep.md`](epic-prep.md) (`benchmark_suite=` + `benchmark_attempt=` vs production `epics/<KEY>/`).

**Outputs**:

- `{EpicDir}<KEY>-analysis.json` — structured artifact (from [`epics/templates/analysis-ref.json`](../../epics/templates/analysis-ref.json)).
- `{EpicDir}<KEY>-analysis.md` — human-readable summary (four sections; simple markdown).

**Side effects (when `-coverage.json` is loaded and reconciliation applies)**:

- May **append** `checks[].detail_lines` in `{EpicDir}<KEY>-coverage.json` and sync **`>`** lines in `{EpicDir}<KEY>-coverage.md` per [Coverage mutation](#coverage-mutation-normative). Does **not** remove or rewrite existing scenario **`-`** lines.

**Ephemeral**: `{EpicDir}temp/` — **must be deleted** before the run is considered complete (success or abort). Durable files must **not** contain the substring `/temp/`.

---

## Preconditions

- **user-mcp-atlassian**: `jira_get_issue`, `jira_search` — read each tool’s schema before calls.
- **Context anchors**: [`docs/project.json`](../../docs/project.json), [`docs/qa-project.json`](../../docs/qa-project.json), [`docs/corner-platform-map.json`](../../docs/corner-platform-map.json) — Jira projects and dashboards per **`jira_index`** / **`jira_dashboards`** in the platform map (and `qa-project.json` pointer); use for JQL scoping, not invented ticket text.
- **Optional repo inputs** (grounding): `{EpicDir}<KEY>-ref.json`, `{EpicDir}<KEY>-coverage.json`. **If paths exist on disk**, load them without asking the user. If **missing**, append **`validation_log`**, **prompt once** to run `EPIC-PREP:` / `COVERAGE:` or provide files, and **stop** unless the user explicitly agrees to **Jira-only** degraded analysis (then set `coverage_loaded` / `ref_loaded` false and skip phases 7–8).

**Format norms for appended coverage lines**: [`.cursor/pipelines/coverage.md`](coverage.md) — **`>`** = details under a scenario; do not break Smart Checklist structure.

---

## Folder lifecycle

1. Ensure `{EpicDir}` exists.
2. Create `{EpicDir}temp/` only if raw Jira exports are saved (optional).
3. **Allowed in `temp/` only**: e.g. `jira-epic.json`, `jira-search-*.json` scratch. **No cookies or tokens** in committed files.
4. Merge durable facts into `{EpicDir}<KEY>-analysis.json` and write `{EpicDir}<KEY>-analysis.md`.
5. If coverage mutation runs: update `{EpicDir}<KEY>-coverage.json` and `{EpicDir}<KEY>-coverage.md` in place.
6. **Delete** `{EpicDir}temp/` recursively before finishing.
7. **Self-check**: `<KEY>-analysis.json`, `<KEY>-analysis.md`, and (if touched) `<KEY>-coverage.json` / `.md` must **not** contain `/temp/`.

---

## Phases (complete all unless N/A — document skip in `validation_log`)

### 1. Resolve inputs

- Parse `<KEY>` and optional **`include_closed=`** from the user message.
- Set `epic_key`, `sources.ref_path`, `sources.coverage_path`.
- Attempt to read `{EpicDir}<KEY>-ref.json` → set `sources.ref_loaded` true/false; `sources.epic_ref_loaded_at` or merge into `validation_log` if missing.
- Attempt to read `{EpicDir}<KEY>-coverage.json` → set `sources.coverage_loaded` true/false.
- If both JSON inputs missing: prompt user; stop or degraded mode per [Preconditions](#preconditions).
- Append `validation_log`: step `1`.

### 2. Refresh Epic (Jira)

- MCP `jira_get_issue` for `<KEY>`; optional save raw JSON to `temp/jira-epic.json`.
- Set `sources.jira_fetched_at` (ISO-8601).
- Append `validation_log`: step `2`.

### 3. Mine ref + coverage for gaps

Populate **`gaps[]`** (structured `id`, `summary`, `source`, `type`, optional `evidence`). **Sources**:

- **From ref** (when loaded): `requirements[]` with `snippet_status` `missing`/`failed`; `client_shell_impact` with `unknown`; notable `validation_log` / deferrals; empty or weak `synthesis`.
- **From coverage** (when loaded): `checks[].ambiguity`; `anti_pattern_findings`; `explicitly_out_of_scope` items that imply testability risk; `calculation_contract: deferred_ambiguous`; `grounding_audit.ungrounded_check_ids`; `validation_log` entries that indicate blocked verification.

Do **not** fabricate evidence strings; pointers only (field paths, keys).

- Append `validation_log`: step `3`.

### 4. Questions

- Populate **questions[]** (cap **20** unless user widens scope): each item has `id`, `text`, `kind` **`grounded`** | **`hypothesis`**, `dimension` (`testability` | `completeness` | `consistency` | `cross_surface` | `operational` | `other`), `evidence` (required for **grounded** — excerpt or artifact reference; null for **hypothesis**).
- Use narrow dimensions (ISTQB-style intent) without dumping generic role-play.
- Append `validation_log`: step `4`.

### 5. Summary

- Fill **`summary`**: `text` = **1–4 sentences** — what we test and **why** (practical), from Jira summary/description, acceptance tables, and ref `synthesis` / `business_context` when present.
- `derived_from[]`: list which inputs contributed (e.g. `jira_description`, `ref.synthesis`).
- Append `validation_log`: step `5`.

### 6. Known issues (Jira search)

- Set `known_issues_search.at` (ISO-8601). Run **multiple** `jira_search` calls; record each in `known_issues_search.queries[]` with `jql`, `purpose`, `result_count`.

**JQL strategy (try in order; adapt to instance fields)**:

1. **Epic linkage** (purpose `epic_link`): e.g. `parent = <KEY>` **or** `"Epic Link" = <KEY>` **or** `issue in childIssuesOf("<KEY>")` if supported. If unknown field shape, fall back to next rows.
2. **Epic key text** (purpose `epic_text`): `text ~ "<KEY>" AND project in (CRTQA, CRTBL, SUPXT, CAN)` — adjust project list per [`docs/qa-project.json`](../../docs/qa-project.json); keep limits modest.
3. **Keyword semantic** (purpose `keyword_semantic`): tokenize epic `summary` + ref `synthesis.keywords` (drop stop words); 1–2 queries with `summary ~ "token1" AND summary ~ "token2"` scoped to defect/feedback projects **only if** `issuetype` names are confirmed from a sample search — do not guess type names; use broader project filter if needed.

- **Pagination**: `limit` ≤ 50 per call; use `start_at` until cap (e.g. **≤ 80 total issues** across queries) or diminishing returns.
- For each issue: `key`, `summary`, `status`, `issuetype`, `resolution` if present, `url`, `relevance` (`epic_mention` | `keyword` | `linked` | `jql_hit`), `status_category` (`open` | `closed` | `aborted_other` — map “Aborted”, “Cancelled”, etc. to `aborted_other` when applicable).
- **Do not** copy secrets. **Do not** invent issues.

- Append `validation_log`: step `6`.

### 7. Coverage reconciliation

**Skip** if `sources.coverage_loaded` is false: set each known issue’s `coverage_reconciliation.verdict` to **`skipped_no_coverage`** with rationale; list a **gap** that coverage was missing for reconciliation; proceed to phase 9 (emit analysis files only).

**When coverage is loaded**:

- For each **`known_issues[]`** item, compare to **`epic_verification_focus`**, **`coverage_matrix[]`**, **`checks[]`** (`scenario_line`, `detail_lines`, `requirement_keys`), and **`explicitly_out_of_scope`**; use ref `synthesis` / requirement keys when helpful.
- Set **`coverage_reconciliation`**:
  - **`in_scope_relevant`** — issue plausibly affects a **primary** or **supporting** capability under epic focus; not contradicted by `explicitly_out_of_scope` for that theme.
  - **`out_of_epic`** — clearly another subsystem/epic, or matches an **explicitly_out_of_scope** rationale, or contradicts **epic_verification_focus**.
  - **`questionable`** — insufficient signal to map safely (needs human).

- Append `validation_log`: step `7`.

### 8. Update coverage artifacts (coverage mutation)

**Normative rules**:

1. **Eligibility**: Only issues with `coverage_reconciliation.verdict == in_scope_relevant`. **Never** append for `out_of_epic` or `questionable`.
2. **Status filter**: By default, only **`status_category == open`** may receive **`>`** lines. If trigger **`include_closed=yes`** (or `true`/`1`), also allow **`closed`** issues whose `updated` (if available in search fields) or resolution is **recent** (e.g. ≤ 90 days — if `updated` missing, skip closed for mutation unless user override).
3. **Line format** (single prefix for dedupe):  
   `> Known issue: <ISSUE-KEY> — <short summary> (status: <Status>)`  
   Summary must be **one line**, truncated if needed; no secrets.
4. **Mapping**: Choose the **single best** `checks[].check_id` by overlap of requirement keys, capability text, and scenario line keywords. If **two or more** checks tie with no clear winner → **do not** append; add to **`unmapped_known_issues[]`** with `suggested_check_ids` and `reason: ambiguous_mapping`. If **none** fit → `unmapped_known_issues[]` with `reason: no_check_overlap`.
5. **Dedupe**: Before append, if **any** `detail_lines` entry for that check already contains the substring `Known issue: <ISSUE-KEY>` (same key), **skip** append; record key in `coverage_mutations[].skipped_duplicates`.
6. **Apply**: Append new strings to **`checks[].detail_lines`** in `-coverage.json`. **Regenerate or surgically patch** `-coverage.md` so **`>`** blocks under the corresponding scenario match JSON order for that check (preserve existing **`-`** / `##` structure per [coverage.md](coverage.md)).
7. If **`smart_checklist_markdown`** exists on `-coverage.json`, update it to stay consistent with emitted `.md` body when practical.
8. Append `validation_log`: step `8`; populate **`coverage_mutations[]`** with `{ check_id, appended_lines[], skipped_duplicates[] }`.

### 9. Emit analysis markdown

Write **`{EpicDir}<KEY>-analysis.md`** with **exactly four top-level sections** (use `##` headings):

1. **Summary** — `summary.text` only (no tables).
2. **Gaps** — bullets from `gaps[]` (optional prefix `` `gap-00N` ``).
3. **Questions** — bullets; prefix **`(G)`** for grounded, **`(H)`** for hypothesis per `questions[].kind`.
4. **Known issues** — split for readability:
   - **In scope (relevant)** — issues with `in_scope_relevant` (note OPEN vs CLOSED in text: `(OPEN)` / `(CLOSED)` / `(ABORTED_OR_OTHER)`).
   - **Out of scope / questionable** — `out_of_epic` and `questionable` (and `skipped_no_coverage` if any).
   - **Unmapped (checklist candidates)** — bullets from `unmapped_known_issues[]` when non-empty.

Optional: minimal HTML `<span style="color:...">` for severity **only** if the team’s viewer supports it; **default** to semantic text tags above.

Write **`{EpicDir}<KEY>-analysis.json`** (validate JSON).

**Delete** `{EpicDir}temp/`.

---

## Pitfalls

- **Inventing gaps** — Every gap should trace to a loaded artifact field or Jira text path.
- **Coverage mutation without coverage** — Phase 7–8 skipped; never write partial coverage.
- **Ambiguous mapping** — Prefer **unmapped_known_issues** over wrong check attachment.
- **Temp leakage** — Mandatory delete + substring self-check.
- **JQL variance** — Document failed fields in `validation_log`; use fallbacks.

---

## Related

- Template: [`epics/templates/analysis-ref.json`](../../epics/templates/analysis-ref.json)
- Coverage playbook: [`coverage.md`](coverage.md)
- Epic ref: [`epic-prep.md`](epic-prep.md), [`epics/README.md`](../../epics/README.md)
- Router: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc)
