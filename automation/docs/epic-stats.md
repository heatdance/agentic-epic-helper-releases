# Epic stats (`automation/tools/epic_stats/`) — schema v5

Per-user rollups: **corpus** vs **comparison**, categories, epic breakdown. Team incremental → **`latest-team.md`**. Slash: [`/epic-stats`](../../.cursor/commands/epic-stats.md). Contract: [docs/epic-stats-contract.json](../../docs/epic-stats-contract.json).

## Greenfield (from zero)

1. **Harvest** — MCP or `fetch_initial_assessment.py` → `stats/epic-stats/temp/initial-<user>/`
2. **State** — `process_initial_assessment.py` with `--epic-meta` → `state/last-sync-<user>.json`
3. **Meta** — `fetch_epic_meta.py --jira-user <user>` if summaries missing
4. **Categories** — [stats/epic-stats/epic-categories.json](../../stats/epic-stats/epic-categories.json) via `set_epic_category.py`
5. **Report** — `epic_stats_rollup.py --jira-user <user>` → `latest-<user>.md`

## Incremental update (team — 3 phases)

1. **Baseline gate** — `team_readiness.py`
2. **Per user** — `fetch_incremental.py` → confirm scope → `process_incremental.py` → `epic_stats_rollup.py`
3. **Team** — `epic_stats_team_rollup.py` → `latest-team.md`

## Scripts

| Script | When |
|--------|------|
| [`fetch_initial_assessment.py`](../tools/epic_stats/fetch_initial_assessment.py) | Jira REST harvest |
| [`process_initial_assessment.py`](../tools/epic_stats/process_initial_assessment.py) | Build v5 state |
| [`fetch_incremental.py`](../tools/epic_stats/fetch_incremental.py) | Done TCD candidates |
| [`process_incremental.py`](../tools/epic_stats/process_incremental.py) | Append comparison rows |
| [`team_readiness.py`](../tools/epic_stats/team_readiness.py) | Baseline checklist |
| [`epic_stats_rollup.py`](../tools/epic_stats_rollup.py) | Render `latest-<user>.md` |
| [`epic_stats_team_rollup.py`](../tools/epic_stats_team_rollup.py) | Render `latest-team.md` |
