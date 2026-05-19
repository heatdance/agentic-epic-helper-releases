# CRTQA stats rollup (`crtqa_stats_rollup.py`)

Deterministic medians, representability (corpus **n ≥ 4**), and `latest.md` generation for [`/crtqa-stats`](../../.cursor/commands/crtqa-stats.md).

## When to run

After every successful stats run, once `stats/crtqa-stats/state/last-sync.json` exists with **schema v3**:

```bash
python automation/tools/crtqa_stats_rollup.py --append-longitudinal
```

The agent playbook **must** run this before committing `latest.md`. Do not compute saved % or medians by hand in chat.

## Inputs / outputs

| Path | Role |
|------|------|
| `stats/crtqa-stats/state/last-sync.json` | Input; `corpus_cells[]` updated in place |
| `stats/crtqa-stats/latest.md` | Overwritten |
| `stats/crtqa-stats/state/longitudinal.json` | One entry appended when `--append-longitudinal` |

## Options

```bash
python automation/tools/crtqa_stats_rollup.py
python automation/tools/crtqa_stats_rollup.py --state stats/crtqa-stats/state/last-sync.json
python automation/tools/crtqa_stats_rollup.py --append-longitudinal
```

Exit code **0** on success; **1** on missing file, invalid JSON, or schema validation errors.

## Logic summary

- **Corpus** rows: `role=corpus`; **comparison** rows: `role=comparison`.
- Cells keyed by `(category_id, size_band_id)`.
- `representable` when `corpus_n >= 4`.
- **Borrow rule:** if a size band has `corpus_n < 4` but the category-only pool has `corpus_n >= 4`, the cell uses the category median and sets `borrowed_from=category_only` (report evidence `directional`).
- **Saved %:** `(corpus_median - comparison_median) / corpus_median * 100` when representable.

## Longitudinal entry shape

Each append includes: `run_id`, `generated_at`, `run_mode`, `new_issues_this_run`, `corpus_n`, `comparison_n`, `representable_cells`, `comparison_hours_sum`, `saved_pct_by_category`.

## Jira

This script does **not** call Jira. Cohort fetch and classification stay in the agent + MCP flow.
