---
description: CRTQA TCD stats v4 — draft-hour sizing, dynamic report profiles, corpus vs comparison with attribution
---

# /crtqa-stats

Measure **% time saved** for Test Case Development when using the **agentic epic helper**, against a **manual baseline corpus**. Reporting is **associative, not causal**. Schema **v4** adds **draft estimate hours** (Devex sizing), **per-task** tables, and **dynamic** `latest.md` layouts.

## Tools and limits

- Use **`user-mcp-atlassian`** only (`jira_search`, `jira_get_issue`).
- Do not invent Jira fields, links, or worklog values.
- Page Jira searches (`limit <= 50`, increment `start_at` until exhausted).

## Output files

| Path | Git |
|------|-----|
| `stats/crtqa-stats/latest.md` | committed |
| `stats/crtqa-stats/temp/categories.json` | committed (taxonomy v3) |
| `stats/crtqa-stats/state/last-sync.json` | gitignored (schema v4) |
| `stats/crtqa-stats/state/longitudinal.json` | gitignored |
| `stats/crtqa-stats/raw/run-<UTC>.jsonl` | gitignored |

## Runtime config

- `mode=initial_assessment|incremental_update|full_refresh` (required)
- `jira_user=<username|email|accountId>` (required)

## Analytic model

| Role | Meaning |
|------|---------|
| **corpus** | Manual baseline — epic **not** AI-assisted on first run |
| **comparison** | AI-assisted — epic AI-assisted on first run, or new tasks (default) |

**Sizing (Devex):** `draft_estimate_hours` from Jira **`customfield_11250`**; `devex_sp = draft / 8`; size band from draft hours (see taxonomy).

**Do not** use `timetracking.original_estimate` for draft or size (often ~2h on TCD; draft is typically 8–16+ hours).

**Logged hours:** parse `timetracking.time_spent` (e.g. `1d 5h` → 13h).

## Cohort rules

1. Resolve Jira user (`jira_user`).
2. Epics: `project = CRT AND issuetype = Epic AND "test lead" = <jira_user> ORDER BY key ASC`
3. Per Epic, done TCD: `project = CRTQA AND issuetype = "Test Execution" AND summary ~ "Test Case Development" AND "Epic Link" = <CRT-KEY> AND statusCategory = Done ORDER BY key ASC`
4. Membership is **Epic Link only**.

## Modes

### initial_assessment

1. Build cohort; **human confirms** `included_issue_keys`.
2. **Per Epic:** “Already AI-assisted?” → `role=comparison` or `corpus` for all tasks under epic.
3. Fetch per issue:
   - **`customfield_11250`** → `draft_estimate_hours` (store field id in `jira_field_map.draft_estimate_hours`)
   - **`timetracking.time_spent`** → `hours_logged`
   - `created`, `resolutiondate`, `summary`
4. Set `estimate_hours` = `draft_estimate_hours` (alias; not `original_estimate`).
5. Classify `category_id` (see **Classification**).
6. Write `last-sync.json` **schema v4**; raw `jsonl`; **Finalize**.

### incremental_update

1. Recompute cohort; `new_keys = cohort − included_issue_keys`.
2. If empty: `rollup_only=true` → **Finalize** only (report profile recomputes).
3. Else: confirm keys; per new task: AI-assisted? (default yes) → `comparison` or rare `corpus`.
4. Fetch/classify new rows; upsert; **Finalize**.

### full_refresh

1. Re-fetch all `included_issue_keys` (fixes draft after v4 upgrade).
2. Do not flip epic roles without re-attestation.
3. **Finalize**.

**After v4 upgrade:** run **`full_refresh`** once so rows get correct `customfield_11250` (e.g. CRTQA-10132 draft 16h, not 1.92h from wrong field).

## Classification

[`stats/crtqa-stats/temp/categories.json`](../stats/crtqa-stats/temp/categories.json) — order: epic `epics/<CRT>/*-ref.json` → summary + `mapping_hints` → `other` (low confidence).

## Size bands (from draft hours)

| `size_band_id` | Draft hours | Devex SP |
|----------------|-------------|----------|
| `sp_lt_1` | &lt; 8 | &lt; 1 |
| `sp_1_2` | 8–16 | 1–2 |
| `sp_3_plus` | &gt; 16 | 3+ |
| `sp_unknown` | missing | — |

Rollup may recompute `size_band_id` and `devex_sp` from `draft_estimate_hours`.

## State schema v4

Top-level: `schema_version` **4**, `report_profile`, `report_meta`, `corpus_cells`, plus v3 fields (`attestation_by_epic`, `rows`, …).

### `rows[]`

```json
{
  "issue": "CRTQA-10132",
  "epic_link": "CRT-639",
  "summary": "...",
  "role": "comparison",
  "category_id": "be",
  "size_band_id": "sp_1_2",
  "category_confidence": "high",
  "draft_estimate_hours": 16.0,
  "devex_sp": 2.0,
  "hours_logged": 13.0,
  "estimate_hours": 16.0,
  "hours_vs_draft": 3.0,
  "savings_hours_estimate": 3.0,
  "savings_hours_corpus": null,
  "savings_attribution": "estimate_only",
  "created": "...",
  "resolutiondate": "..."
}
```

### `savings_attribution` (rollup)

| Value | When |
|-------|------|
| `none` | corpus row |
| `insufficient` | missing draft or logged |
| `estimate_only` | comparison; no representable corpus in cell |
| `corpus_benchmark` | comparison; corpus n≥4 in cell |
| `corpus_and_estimate` | under draft and below corpus median |

### `report_profile` (rollup)

| Profile | When |
|---------|------|
| `task_detail` | total &lt; 4 or no representable cells |
| `directional` | corpus 1–3 in some category, no global benchmark |
| `benchmark` | ≥1 cell corpus n≥4 |

## Finalize (required)

```bash
python automation/tools/crtqa_stats_rollup.py --append-longitudinal
```

One-shot v3→4 without Jira re-fetch (draft from `estimate_hours` only if ≥8):

```bash
python automation/tools/crtqa_stats_rollup.py --allow-v3-migrate --repair-draft-from-estimate
```

Prefer **`full_refresh`** to fix wrong estimates (e.g. 1.92h).

## Reporting (`latest.md`)

1. Header — profile, counts, what the report can claim.
2. **Task-level table** (always).
3. **Chart: draft vs logged** (per issue, when draft present).
4. **Chart: corpus vs comparison** (when benchmark/directional with n≥4 category).
5. **Chart: longitudinal** (≥2 runs in `longitudinal.json`).
6. Primary table (category × size); category rollup.
7. Footer — caveats, attribution legend, migration note.

## Validation

- CRTQA-10132: draft 16, logged 13, `sp_1_2`, `hours_vs_draft` 3, `estimate_only` if no BE corpus.
- 2 tasks → `task_detail`, task table + draft chart present.
- `incremental_update` with no new keys regenerates profile when corpus grows.

## References

- [`stats/crtqa-stats/README.md`](../../stats/crtqa-stats/README.md)
- [`automation/docs/crtqa-stats.md`](../../automation/docs/crtqa-stats.md)
