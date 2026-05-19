---
description: CRTQA TCD time stats — corpus baseline vs AI-assisted comparison; category and SP strata; n≥4 representability
---

# /crtqa-stats

Measure **% time saved** for Test Case Development work when using the **agentic epic helper** (this workspace), against a **manual baseline corpus** from historical done tasks. Reporting is **associative, not causal**.

## Tools and limits

- Use **`user-mcp-atlassian`** only (`jira_search`, `jira_get_issue`).
- Do not invent Jira fields, links, story points, or worklog values.
- Page Jira searches (`limit <= 50`, increment `start_at` until exhausted).

## Output files

| Path | Git |
|------|-----|
| `stats/crtqa-stats/latest.md` | committed |
| `stats/crtqa-stats/temp/categories.json` | committed (taxonomy) |
| `stats/crtqa-stats/state/last-sync.json` | gitignored |
| `stats/crtqa-stats/state/longitudinal.json` | gitignored |
| `stats/crtqa-stats/raw/run-<UTC>.jsonl` | gitignored |

## Runtime config

- `mode=initial_assessment|incremental_update|full_refresh` (required)
- `jira_user=<username|email|accountId>` (required)

## Analytic model

| Role | Meaning | When assigned |
|------|---------|----------------|
| **corpus** | Manual baseline (pre-harness or not AI-assisted) | Epic attested **not** AI-assisted on first run; rare manual-only on incremental |
| **comparison** | AI-assisted TCD | Epic attested AI-assisted on first run; default for new done tasks on incremental |

**Saved %** (per cell): `(corpus_median − comparison_median) / corpus_median × 100` when corpus **representable** (`corpus_n ≥ 4` in that cell).

## Cohort rules

1. Resolve Jira user (`jira_user`).
2. Epics:

```text
project = CRT AND issuetype = Epic AND "test lead" = <jira_user> ORDER BY key ASC
```

3. Per Epic, done TCD tasks:

```text
project = CRTQA AND issuetype = "Test Execution" AND summary ~ "Test Case Development" AND "Epic Link" = <CRT-KEY> AND statusCategory = Done ORDER BY key ASC
```

4. Membership is **Epic Link only** — no summary-based cohort fallback.

## Modes

### initial_assessment

1. Build full cohort; propose `included_issue_keys`; **human confirms** list.
2. **Per Epic** with ≥1 included task: ask **“Already AI-assisted (agentic epic helper)?”**
   - **Yes** → `attestation_by_epic[CRT].ai_assisted=true`, `role=comparison` for all tasks under epic.
   - **No** → `ai_assisted=false`, `role=corpus`.
3. Fetch issue details (worklogs → `hours_logged`, estimate, dates).
4. Resolve **Story Points** field once via `jira_get_issue` on a sample CRTQA TCD; store in `jira_field_map.story_points` (do not invent).
5. Classify each row (see **Classification**).
6. Write `state/last-sync.json` schema **v3** (overwrite).
7. Append raw audit `raw/run-<UTC>.jsonl`.
8. Run rollup (see **Finalize**).

### incremental_update

1. Recompute cohort from Jira.
2. `new_keys = cohort_keys − state.included_issue_keys`.
3. If `new_keys` empty: set `rollup_only=true`, skip fetch; **Finalize** only.
4. Else: confirm `new_keys`; **per new task** ask **“AI-assisted for this TCD?”** (default **yes** → `comparison`; **no** → `corpus`).
5. Fetch and classify new rows only; upsert `rows` and `included_issue_keys`.
6. Set `new_keys_this_run`; **Finalize**.

### full_refresh

1. Re-fetch and reclassify all `included_issue_keys`.
2. **Do not** change epic `role` without human re-attestation.
3. **Finalize**.

## Classification

Source: [`stats/crtqa-stats/temp/categories.json`](../stats/crtqa-stats/temp/categories.json).

**Order:**

1. Epic workspace refs when present: `epics/<CRT>/<CRT>-ref.json` (surfaces, obligation kinds).
2. Summary + category `mapping_hints`.
3. `other` with `category_confidence=low` if uncertain.

**Size band** from `story_points` on the issue:

| `size_band_id` | Rule |
|----------------|------|
| `sp_lt_1` | SP &lt; 1 |
| `sp_1_2` | 1 ≤ SP ≤ 2 |
| `sp_3_plus` | SP ≥ 3 |
| `sp_unknown` | missing or unmapped |

## State schema v3 (`last-sync.json`)

Required top-level fields:

- `schema_version` (must be `3`)
- `run_mode`, `generated_at`, `snapshot_run_id`, `rollup_only`
- `resolved_user`, `included_issue_keys`, `skipped_epics`, `jql_fragments`
- `attestation_by_epic`, `rows`, `corpus_cells`
- `category_schema_version`, `category_schema_hash`
- `jira_field_map` (e.g. `story_points` field id after discovery)
- `new_keys_this_run` (array; empty if none)

### `attestation_by_epic`

```json
"CRT-639": { "ai_assisted": true, "role": "comparison" },
"CRT-632": { "ai_assisted": false, "role": "corpus" }
```

### `rows[]` (each element)

```json
{
  "issue": "CRTQA-12345",
  "epic_link": "CRT-999",
  "summary": "text",
  "role": "corpus",
  "category_id": "fe",
  "size_band_id": "sp_1_2",
  "category_confidence": "high",
  "story_points": 2,
  "hours_logged": 12.5,
  "estimate_hours": 16.0,
  "created": "2026-01-01T00:00:00.000+0000",
  "resolutiondate": "2026-01-15T00:00:00.000+0000"
}
```

### `corpus_cells[]` (rollup-written)

Computed by [`crtqa_stats_rollup.py`](../../automation/tools/crtqa_stats_rollup.py). Each cell:

- `category_id`, `size_band_id`, `corpus_n`, `median_hours_logged`, `representable` (`corpus_n >= 4`)
- Optional `borrowed_from`: `category_only` when size band sparse but category pool has n≥4

## Finalize (required every run)

```bash
python automation/tools/crtqa_stats_rollup.py --append-longitudinal
```

- Refreshes `corpus_cells[]` in state.
- Overwrites `stats/crtqa-stats/latest.md`.
- Appends one entry to `state/longitudinal.json`.

Do **not** hand-edit medians or saved % in `latest.md`.

## Reporting (`latest.md`)

1. **Header:** mode, user, timestamp, `corpus_n`, `comparison_n`, representable cell count.
2. **Chart:** mermaid xychart — category-only rows where corpus n≥4 (corpus vs comparison median hours).
3. **Primary table:** Category × Size — saved % only when representable; else `benchmark pending (need N more corpus tasks)`.
4. **Category-only rollup** table.
5. **Footer:** caveat, new keys, skipped epics, epics marked comparison on first run.

### Evidence labels

| Label | Rule |
|-------|------|
| `representable` | corpus_n ≥ 4 in cell (or borrowed category pool) |
| `directional` | corpus_n 1–3 or borrowed pool |
| `comparison_weak` | saved % shown but comparison n &lt; 3 |
| `pending` | no corpus data in cell |

## Human checklist

### First run

- [ ] `/crtqa-stats mode=initial_assessment jira_user=…`
- [ ] Confirm included CRTQA keys
- [ ] Per epic: already AI-assisted? → comparison vs corpus
- [ ] Run rollup; open `latest.md`

### Incremental

- [ ] `/crtqa-stats mode=incremental_update jira_user=…`
- [ ] Confirm new keys; per task AI-assisted? (default yes)
- [ ] Run rollup

## Validation

- Empty state + `initial_assessment` must succeed.
- `incremental_update` with no new keys → `rollup_only=true`, report regenerates.
- Corpus n≥4 enables saved % for that category/cell; sparse cells do not block other rows.
- No `assistance`, `human_manual_benchmark_hours`, or legacy v2-only fields.

## References

- Operator summary: [`stats/crtqa-stats/README.md`](../../stats/crtqa-stats/README.md)
- Rollup tool: [`automation/docs/crtqa-stats.md`](../../automation/docs/crtqa-stats.md)
