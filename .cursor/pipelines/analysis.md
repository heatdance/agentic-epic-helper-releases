# Pipeline: analysis (ANALYSE v2)

**Trigger**: user message starts with `ANALYSE:` and includes a Jira **Epic key** (e.g. `ANALYSE: CRT-642`). Optional tokens on the **same line**:

- **`known_issues=yes`** — run phases **6–8** (Jira search + optional coverage `>` mutation). **Default: off** (empty `known_issues[]`, no coverage mutation).
- **`include_closed=yes`** — only when **`known_issues=yes`**; allow recent **closed** issues for `>` regression anchors (≤ 90 days when `updated` available).
- **`resolve=no`** — audit-only: skip phase **4b** Confluence resolve subprocesses. **Default: resolve on** (omit token or `resolve=yes`).

**Version note (v2):** Coverage-grounded **gap auditor** + bounded Confluence resolve + **`exploration_suppressed[]`** for downstream. Contract: [`docs/analysis-gap-contract.json`](../../docs/analysis-gap-contract.json). Verifier: [`automation/docs/analysis-verify.md`](../../automation/docs/analysis-verify.md). Template: [`epics/templates/analysis-ref.json`](../../epics/templates/analysis-ref.json) **schema v2**.

**Scope**: **one Epic** per run. **Router**: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc).

**Not human BA** — no hypothesis questions, no persona role-play, no CRTQA Jira as gap sources.

## Epic workspace (`{EpicDir}`)

Resolve **`{EpicDir}`** like [`epic-prep.md`](epic-prep.md).

**Outputs**:

- `{EpicDir}<KEY>-analysis.json` — machine contract (authoritative for downstream).
- `{EpicDir}<KEY>-analysis.md` — **gaps-first** human view (+ optional **Actions**, **Known issues** when token set).

**Side effects** (tool-backed only, phase **9**):

- May fill **`nested_requirement_refs`** on `-coverage.json` after successful resolve.
- May append **`> Known issue:`** lines when **`known_issues=yes`** and mapping is unambiguous.
- **Never** edit top-level **`-`** scenario lines on coverage checks.

**Ephemeral**: `{EpicDir}temp/` — e.g. `analysis-resolve-<gap-id>.json`, optional `jira-search-*.json`. **Delete** before finish.

---

## Preconditions

- **Required:** `{EpicDir}<KEY>-coverage.json` from **`COVERAGE:`**. If missing → **STOP** → instruct `COVERAGE: <KEY>`.
- **Required:** `{EpicDir}<KEY>-ref.json` when gaps need requirement/snippet context (almost always).
- **user-mcp-atlassian** for optional known-issues search and Confluence resolve in **4b**.
- **Yogi** (optional): [`automation/docs/yogi-url-resolve.md`](../../automation/docs/yogi-url-resolve.md) for phase **4b** `--storage-file` path.
- **jq** before loading full ref/coverage: [automation/docs/jq.md](../../automation/docs/jq.md).

**Forbidden (production):** CRTQA keys in durable analysis JSON; bench JSON as gap source; inventing Jira/Confluence text.

---

## Folder lifecycle

1. Ensure `{EpicDir}` exists.
2. Create `{EpicDir}temp/` when resolve or known-issues runs need scratch.
3. Merge into `-analysis.json` / `-analysis.md`; optional coverage write-back (phase **9**).
4. Run **`analysis_verify.py`** (phase **10**).
5. **Delete** `{EpicDir}temp/`.
6. No `/temp/` in durable JSON or coverage after write-back.

---

## Phases

### 1. Resolve inputs

- Parse `<KEY>`, **`known_issues=yes`**, **`include_closed=yes`**, **`resolve=no`**.
- Set `sources.known_issues_enabled`, `sources.resolve_enabled` on the analysis artifact.
- **MUST** `jq` project `-coverage.json` and `-ref.json` before full load.
- Set `sources.coverage_loaded`, `sources.ref_loaded`, paths, `epic_key`.
- If coverage missing → **STOP**. If ref missing → log gap `snippet_missing` risk; continue only for coverage-only mechanical gaps.
- Append `validation_log` step `1`.

### 2. Build work queue

Deterministic scan per [`docs/analysis-gap-contract.json`](../../docs/analysis-gap-contract.json) **`work_queue_sources`**:

| Signal | Gap kind (typical) |
|--------|-------------------|
| `checks[]` with `calculation_contract: deferred_ambiguous` or `ambiguity` set | `deferred_check` |
| `grounding_audit.ungrounded_check_ids[]` | `ungrounded_check` |
| `nested_requirement_refs[]` with null `page_id` / `short_url` | `nested_req_unresolved` |
| ref `requirements[]` `snippet_status` missing/failed | `snippet_missing` |
| ref `obligations_proposed` vs `obligations_coverage` (only if coverage schema &lt; 2 or obvious row gap) | `obligation_uncovered` |
| `anti_pattern_findings[]` | `anti_pattern` |

Dedupe by `(kind, check_id, requirement_key, obligation_id)`. Assign provisional **`gap-001`**… ids. Store queue in `temp/` only until merged into `gaps[]` in phase **3** — do not leave queue-only files in durable JSON.

Append `validation_log` step `2` (queue count).

### 3. Mechanical gaps (high confidence)

For each queue item, append **`gaps[]`** with:

- `kind`, `confidence: high`, `status: open` (or `confirmed_gap` if clearly intentional deferral with `obligation_ids` on check)
- `pointers`: `check_id` / `obligation_id` / `requirement_key` as applicable
- `evidence`: field path only (e.g. `checks[chk-015].calculation_contract`)
- `recommended_action`: per contract **`recommended_action_by_kind`** (override only with `validation_log` reason)

**Obligation reconciliation:** When coverage **`schema_version` ≥ 2** and `obligations_coverage` is row-complete per [`coverage_verify.py`](../../automation/tools/coverage_verify.py), **do not** emit duplicate `obligation_uncovered` gaps.

**No hypothesis questions** — `questions[]` remains **empty** in v2 generation emit.

Optional **`summary.text`**: **one line** max, verbatim from `coverage.epic_verification_focus.statement` only; `derived_from: ["coverage.epic_verification_focus"]`.

Populate **`actions`**: `rerun_coverage`, `rerun_epic_prep`, `focus_hint` from gap actions aggregate.

Append `validation_log` step `3`.

### 4a. Short-circuit

If **`gaps[]`** empty after phase **3** and no resolve queue → skip to phase **5** (suppression may still be empty) → phase **10** emit.

### 4b. Per-gap resolve subprocess (when `resolve` enabled)

**Parent MUST NOT** resolve all gaps in one chat turn.

For each gap with `recommended_action: confluence_resolve` (and kind `nested_req_unresolved` or `snippet_missing` with resolvable key), up to **`max_resolve_attempts_per_run`** (8 per contract):

1. **Input pack:** one gap + linked `requirements[]` row + optional `checks[]` slice.
2. **One attempt:** narrow MCP `confluence_search` / `confluence_get_page` (storage) + `yogi_snippet.py --storage-file` **or** Yogi live per [yogi-url-resolve.md](../../automation/docs/yogi-url-resolve.md).
3. **Output:** `temp/analysis-resolve-<gap-id>.json` with `{ "gap_id", "found": true|false, "snippet_excerpt", "page_id", "requirement_key" }`.
4. **Merge:**
   - **found** → move to **`resolved_gaps[]`** (`resolution: confluence_snippet`); remove from open `gaps[]` or set `status: resolved`.
   - **not found** → set `confidence: medium`, `status: confirmed_gap`, keep `recommended_action: human_ba`.

Overflow queue items → `confirmed_gap` + `human_ba` without tool calls.

Append `validation_log` step `4b` (attempt count).

### 5. Exploration suppression

For gaps with kind **`deferred_check`** or `recommended_action: ignore_for_discover`, append **`exploration_suppressed[]`**:

```json
{
  "check_id": "chk-015",
  "reason": "deferred_in_check | keyed deferral per obligations_coverage",
  "blocks_fixture_probe": true,
  "until_action": "rerun_coverage | human_ba"
}
```

Align with [`test-discover.md`](test-discover.md): do **not** instruct discover to `scope_gap` on `!`-only lines when coverage documents keyed deferral.

Append `validation_log` step `5`.

### 6–8. Known issues (only if `known_issues=yes`)

**If token absent:** leave `known_issues[]`, `known_issues_search`, `unmapped_known_issues`, `coverage_mutations` empty; skip to phase **9**.

**When enabled:**

#### 6. Known issues search (Jira)

- MCP `jira_get_issue` for epic if not already fresh; set `known_issues_search.at`.
- Run **multiple** `jira_search` calls; record in `known_issues_search.queries[]`.

**JQL strategy** (try in order):

1. **Epic linkage** (`epic_link`): `parent = <KEY>` or `"Epic Link" = <KEY>` or `issue in childIssuesOf("<KEY>")`.
2. **Epic key text** (`epic_text`): `text ~ "<KEY>" AND project in (...)` per [`docs/qa-project.json`](../../docs/qa-project.json).
3. **Keyword semantic** (`keyword_semantic`): only if phases 1–2 yield &lt; 10 hits — tokenize epic summary + ref keywords; cap total issues **≤ 80**.

- For each issue: key, summary, status, url, `relevance`, `status_category` (`open` | `closed` | `aborted_other`).
- **Do not** invent issues. **Do not** persist CRTQA keys in analysis JSON when avoidable — use issue keys from Jira only in `known_issues[]` (verifier forbids CRTQA in generation artifacts; prefer XT/CAN/CRT defect keys for mutation targets).

Append `validation_log` step `6`.

#### 7. Coverage reconciliation (known issues)

**Skip** if coverage not loaded: verdict `skipped_no_coverage` on each issue.

**When loaded:** For each `known_issues[]` item, set **`coverage_reconciliation.verdict`**: `in_scope_relevant` | `out_of_epic` | `questionable` using `epic_verification_focus`, matrix, checks, `explicitly_out_of_scope`.

Append `validation_log` step `7`.

#### 8. Coverage mutation (known issues)

Per prior v1 rules (eligibility, dedupe, single best `check_id`):

1. Only `in_scope_relevant`.
2. Default **open** only; **`include_closed=yes`** allows recent closed.
3. Line format: `> Known issue: <KEY> — <summary> (status: <Status>)`.
4. Ambiguous mapping → `unmapped_known_issues[]`, no append.
5. Record in **`coverage_mutations[]`** and **`coverage_writebacks[]`**.

**Never** edit top-level `-` scenario lines.

Append `validation_log` step `8`.

### 9. Coverage write-back (resolve + known issues)

**Tool-backed only:**

- **nested_requirement_refs:** When phase **4b** found `page_id` / `short_url`, update `-coverage.json` row; log **`coverage_writebacks[]`**.
- **Known issue `>` lines:** From phase **8** only.
- Regenerate or patch `-coverage.md` `>` blocks for touched checks; sync `smart_checklist_markdown` when present.

Append `validation_log` step `9`.

### 10. Emit

1. Write `{EpicDir}<KEY>-analysis.json` (`schema_version: 2`).
2. Write `{EpicDir}<KEY>-analysis.md`:

```markdown
## Gaps

- `gap-001` [high] nested_req_unresolved — CRT-1481 — … — action: confluence_resolve

## Actions

- rerun_coverage: yes | no
- rerun_epic_prep: no
- focus_hint: null | free text

## Known issues

(only when known_issues=yes — subsections per v1: In scope, Out of scope, Unmapped)
```

**Forbidden in default emit:** `## Summary`, `## Questions`.

3. Run:

```text
python automation/tools/analysis_verify.py --mode gaps --analysis {EpicDir}<KEY>-analysis.json
python automation/tools/analysis_verify.py --mode downstream --analysis {EpicDir}<KEY>-analysis.json
python automation/tools/analysis_verify.py --mode emit --analysis {EpicDir}<KEY>-analysis.json --md {EpicDir}<KEY>-analysis.md
```

Block finish until all exit **0**. If open gaps &gt; 15, add `validation_log` entry `gap_cap_deferral` or split run.

4. **Delete** `{EpicDir}temp/`.

---

## Pitfalls

- **ANALYSE before green COVERAGE** — yields rework noise; run `coverage_verify` first.
- **Hypothesis questions** — forbidden in v2 generation.
- **Keyword JQL without `known_issues=yes`** — do not run phase 6 by default.
- **Rewriting coverage `-` lines** — only `>` detail and `nested_requirement_refs`.
- **One-shot resolve** — violates subprocess contract; cap 8 attempts.
- **CRTQA in durable JSON** — verifier fails generation artifacts.

---

## Related

- Template: [`epics/templates/analysis-ref.json`](../../epics/templates/analysis-ref.json)
- Gap contract: [`docs/analysis-gap-contract.json`](../../docs/analysis-gap-contract.json)
- Verifier: [`automation/docs/analysis-verify.md`](../../automation/docs/analysis-verify.md)
- Coverage: [`coverage.md`](coverage.md)
- Doctrine: [`docs/harness-principles.md`](../../docs/harness-principles.md) §5
- Discover / precon consumption: [`test-discover.md`](test-discover.md), [`test-precon.md`](test-precon.md)
