# CRTQA stats rollup (`crtqa_stats_rollup.py`) — schema v4

Deterministic enrich, `report_profile`, medians, attribution, and `latest.md` for [`/crtqa-stats`](../../.cursor/commands/crtqa-stats.md).

## When to run

After every stats run once `stats/crtqa-stats/state/last-sync.json` exists:

```bash
python automation/tools/crtqa_stats_rollup.py --append-longitudinal
```

## v3 → v4 migration

Existing v3 state is rejected unless:

```bash
python automation/tools/crtqa_stats_rollup.py --allow-v3-migrate --repair-draft-from-estimate
```

This only copies `estimate_hours` → `draft_estimate_hours` when `estimate_hours >= 8` (avoids the 1.92h `original_estimate` mistake). **Recommended:** `/crtqa-stats mode=full_refresh jira_user=…` to reload `customfield_11250` from Jira, then rollup.

## Jira fields (ingest — agent, not this script)

| Purpose | Field |
|---------|--------|
| Draft estimate (hours) | `customfield_11250` → `draft_estimate_hours` |
| Logged time | `timetracking.time_spent` → `hours_logged` |
| Do **not** use | `timetracking.original_estimate` for draft/size |

Devex SP: `devex_sp = draft_estimate_hours / 8`. Size bands: &lt;8h, 8–16h, &gt;16h.

## Rollup outputs

| Output | Action |
|--------|--------|
| `state/last-sync.json` | Updates `corpus_cells`, enriches `rows`, sets `report_profile`, `report_meta`, `schema_version` 4 |
| `latest.md` | Overwritten (dynamic sections) |
| `state/longitudinal.json` | Optional append (`--append-longitudinal`) |

## Report profiles

| Profile | Layout emphasis |
|---------|-----------------|
| `task_detail` | Task table + draft/logged chart; benchmark tables show “pending” |
| `directional` | Above + category charts when partial corpus |
| `benchmark` | Corpus vs comparison medians where n≥4 |

Profiles recompute on every rollup, including `rollup_only` incremental runs.

## Options

```bash
python automation/tools/crtqa_stats_rollup.py
python automation/tools/crtqa_stats_rollup.py --state stats/crtqa-stats/state/last-sync.json
python automation/tools/crtqa_stats_rollup.py --append-longitudinal
python automation/tools/crtqa_stats_rollup.py --allow-v3-migrate --repair-draft-from-estimate
```

Exit **1** on schema mismatch or missing state file.

## Longitudinal entry (v4)

Includes: `report_profile`, `total_hours_vs_draft_comparison`, `corpus_n`, `comparison_n`, `representable_cells`, `saved_pct_by_category`.
