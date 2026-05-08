---
description: Rebuilt CRTQA stats command with two modes, category mapping, and low-n visible reporting
---

# /crtqa-stats

Generate per-engineer CRTQA Test Case Development time stats from Jira, then render a simple `latest.md` with one chart and one primary table.

## Tools and limits

- Use `user-mcp-atlassian` only (`jira_search`, `jira_get_issue`).
- Do not invent Jira fields, links, or values.
- Page Jira searches (`limit <= 50`, increment `start_at` until exhausted).

## Output files

- `stats/crtqa-stats/latest.md` (committed)
- `stats/crtqa-stats/raw/run-<UTC>.jsonl` (gitignored)
- `stats/crtqa-stats/state/last-sync.json` (gitignored)
- `stats/crtqa-stats/state/longitudinal.json` (gitignored)
- `stats/crtqa-stats/temp/categories.json` (taxonomy input)

## Runtime config (human-facing)

- `mode=initial_assessment|incremental_update|full_refresh`
- `jira_user=<username|email|accountId>`
- `category_policy=static_core|hybrid` (default: `hybrid`)
- `allow_category_extension=yes|no` (default: `no`)
- `extension_threshold_n=<int>` (default: `3`)
- `unknown_assist_policy=show_separately` (default)

## Cohort rules

1. Resolve explicit Jira user identity (`jira_user`).
2. Fetch Epics by Test Lead:

```sql
project = CRT AND issuetype = Epic AND "test lead" = <jira_user> ORDER BY key ASC
```

3. For each Epic, fetch done TCD tasks:

```sql
project = CRTQA AND issuetype = "Test Execution" AND summary ~ "Test Case Development" AND "Epic Link" = <CRT-KEY> AND statusCategory = Done ORDER BY key ASC
```

4. Cohort membership is Epic Link only. Do not use text matching as membership fallback.

## Modes

### initial_assessment

- Build baseline from full current cohort.
- Ask for confirmation of included keys.
- Ask for assisted/manual attestation per Epic in the included set.
- Fetch issue details/worklogs for all included keys.
- Classify all included keys using `temp/categories.json`.
- Overwrite state with fresh baseline.

### incremental_update

- Recompute full cohort from Jira.
- `new_keys = cohort_keys - state.included_issue_keys`.
- If `new_keys` is empty: regenerate report from state (`rollup_only=true`).
- Else: confirm keys, fetch details for new keys, classify new keys, upsert state.

### full_refresh

- Recompute and re-fetch all included keys.
- Reclassify all included keys.
- Keep same state schema; refresh all derived metrics.

## Required per-issue row fields

Each `rows[]` element in `state/last-sync.json`:

```json
{
  "issue": "CRTQA-12345",
  "epic_link": "CRT-999",
  "summary": "text",
  "hours_logged": 0.0,
  "assistance": "assisted|manual|unknown",
  "category_id": "functional_order_entry|unknown_or_other",
  "category_confidence": "high|medium|low",
  "estimate_hours": null,
  "human_manual_benchmark_hours": null,
  "created": null,
  "resolutiondate": null
}
```

## Category mapping

- Use `stats/crtqa-stats/temp/categories.json` as source of truth.
- Map each issue to one `category_id`.
- If mapping is uncertain or unmappable, use `unknown_or_other` and set `category_confidence=low`.
- If `allow_category_extension=yes` and unknown patterns repeat (`>= extension_threshold_n`), append proposal objects to `category_extension_proposals` in state. Do not mutate taxonomy automatically.

## Attestation rules

- Ask human whether each Epic is assisted or manual.
- Store merged epic map in `attestation_by_epic`.
- Derive row-level `assistance` from row `epic_link` using this map.
- If epic not attested, row assistance is `unknown`.

## Low-n policy

- Always show statistics even for tiny samples (including 1 vs 1).
- Never suppress comparisons due to low n.
- Label evidence strength:
  - `weak`: either arm has `n < 3`
  - `medium`: both arms `n >= 3` and one arm `< 5`
  - `strong`: both arms `n >= 5`

## latest.md format (simple glance)

1. Header strip:
   - mode, user, generated time
   - `assisted_n`, `manual_n`, `unknown_n`
   - overall evidence label
2. Single chart:
   - per-category assisted vs manual median logged hours (mermaid xychart)
3. Single primary table:
   - `Category | Assisted n | Manual n | Unknown n | Assisted median h | Manual median h | Delta % | Evidence`
4. Footer:
   - caveat: association, not causation
   - skipped epics
   - new keys this run

## State write contract

`state/last-sync.json` required fields:

- `schema_version`, `run_mode`, `generated_at`, `snapshot_run_id`
- `resolved_user`, `included_issue_keys`
- `skipped_epics`, `jql_fragments`
- `attestation_by_epic`
- `rows`
- `category_schema_version`, `category_schema_hash`
- `category_extension_proposals`
- `rollup_only` (boolean)

`state/longitudinal.json` append one run per successful execution:

- `run_id`, `generated_at`, `run_mode`
- `new_issues_this_run`
- `assisted_n`, `manual_n`, `unknown_n`
- `evidence`
- `hours_sum_this_fetch`

## Validation checklist (must pass)

- No legacy values reused from deleted files.
- `initial_assessment` works with empty state.
- `incremental_update` correctly handles no-new-keys.
- 1 assisted + 1 manual still produces table and chart with `evidence=weak`.
