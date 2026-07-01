# Epic stats (v5)

Per-engineer rollups for **Test Case Development** and related QA work: **manual corpus** vs **AI-assisted comparison**, with draft-hour sizing and honest attribution.

| Doc | Role |
|-----|------|
| [`/epic-stats`](../../.cursor/commands/epic-stats.md) | Slash entry |
| [docs/epic-stats-contract.json](../../docs/epic-stats-contract.json) | Normative JQL, paths, gates |
| [automation/docs/epic-stats.md](../../automation/docs/epic-stats.md) | Rollup CLI |
| [HOW-TO.md § stats](../../HOW-TO.md) | Human operator steps |

## Model (v5)

| Role | Use |
|------|-----|
| **corpus** | Manual baseline — user worklogs on cross-project QA tasks; epic gate: user QA logged > 0 |
| **comparison** | AI-assisted Done TCD (incremental) — vs corpus medians |

**Discovery:** CRTQA **Tests** reported by user → epics → **any project** QA tasks on Epic Link (incl. BROQA Release notes).

**Draft:** `customfield_11250` (hours), then original estimate, then 8h default. **Logged:** user worklogs only (not issue `time_spent`).

**Size:** `small_tcd` ≤16h, `big_tcd` >16h (from draft hours).

## Modes

| Mode | Use |
|------|-----|
| `initial_assessment` | First time: tests → epics → QA corpus + state |
| `incremental_update` | Team workflow: new Done TCD rows vs existing corpus |
| `full_refresh` | Rebuild state from scratch |

## Outputs (gitignored on personal)

- `stats/epic-stats/latest-<user>.md`
- `stats/epic-stats/latest-team.md`
- `stats/epic-stats/state/last-sync-<user>.json`

Committed: `stats/epic-stats/epic-categories.json`

## Rollup commands

```bash
python automation/tools/epic_stats_rollup.py --jira-user <user>
python automation/tools/epic_stats_team_rollup.py
```

See [automation/docs/epic-stats.md](../../automation/docs/epic-stats.md) for greenfield harvest and incremental phases.

**CLEAN Phase T:** team strip deletes `stats/epic-stats/**`. Run `python automation/tools/clean_stats_personal.py backup` on **`personal`** before Phase T and **`restore`** after returning to **`personal`**.
