---
description: Roll up Jira TCD corpus vs AI-assisted work into per-user and team markdown reports.
---

# /epic-stats

Measure **time saved** on Test Case Development (TCD): **corpus** (manual baseline) vs **comparison** (AI-assisted Done TCD). Contract: [docs/epic-stats-contract.json](../../docs/epic-stats-contract.json).

## Runtime

- `mode=initial_assessment|incremental_update|full_refresh` (required)
- `jira_user=<username>` — required for `initial_assessment` and `full_refresh`; optional for `incremental_update`
- `users=<u1>,<u2>` — optional roster override for `incremental_update`

Use **`user-mcp-atlassian`** only; paginate searches (`limit` ≤ 50).

## Outputs

| Path | Git |
|------|-----|
| `stats/epic-stats/latest-<user>.md` | personal / gitignored |
| `stats/epic-stats/latest-team.md` | personal / gitignored |
| `stats/epic-stats/state/last-sync-<user>.json` | gitignored |
| `stats/epic-stats/epic-categories.json` | committed |

**Per-user finalize:**

```bash
python automation/tools/epic_stats_rollup.py --jira-user <user>
```

**Team finalize (incremental_update):**

```bash
python automation/tools/epic_stats_team_rollup.py
```

## Incremental_update flow

1. Run `team_readiness.py` → **AskQuestion** confirm baselines current.
2. Per user: `fetch_incremental.py` → show candidates → confirm scope → `process_incremental.py` → `epic_stats_rollup.py`.
3. `epic_stats_team_rollup.py` → `latest-team.md`.

See [automation/docs/epic-stats.md](../../automation/docs/epic-stats.md) for greenfield and full-refresh modes.
