---
description: CRTQA stats v5 — test-first corpus, per-user latest-<username>.md, team incremental, latest-team.md
---

# /crtqa-stats

Measure **time saved** on Test Case Development (TCD): **corpus** (manual baseline) vs **comparison** (AI-assisted Done TCD).

**Canonical playbook:** [`.cursor/skills/crtqa-stats/SKILL.md`](../skills/crtqa-stats/SKILL.md) — greenfield, modes, metrics.  
**Contract:** [docs/crtqa-stats-contract.json](../../docs/crtqa-stats-contract.json)

## Runtime

- `mode=initial_assessment|incremental_update|full_refresh` (required)
- `jira_user=<username>` — required for `initial_assessment` and `full_refresh`; **optional** for `incremental_update` (all roster users with state)
- `users=<u1>,<u2>` — optional roster override for `incremental_update`

## MCP

- **`user-mcp-atlassian`** only; paginate searches (`limit` ≤ 50).
- Do not invent worklogs or draft hours.

## Outputs

| Path | Git |
|------|-----|
| `stats/crtqa-stats/latest-<user>.md` | personal / gitignored |
| `stats/crtqa-stats/latest-team.md` | personal / gitignored |
| `stats/crtqa-stats/state/last-sync-<user>.json` | gitignored |
| `stats/crtqa-stats/epic-categories.json` | committed (shared categories) |

**Per-user finalize:**

```bash
python automation/tools/crtqa_stats_rollup.py --jira-user <user>
```

**Team finalize (incremental_update Phase 3):**

```bash
python automation/tools/crtqa_stats_team_rollup.py
```

## Report shape (summary)

**Per user:** header, collapsed rollup, category rollup, epic breakdown, AI epic breakdown — see SKILL.

**Team (`latest-team.md`):** Generated, Users, Scope; **collapsed rollup** (Small + Big; team Saved % from team row medians); **per-user rollup** table below (individual Saved %).

## Modes (pointer)

| Mode | SKILL section |
|------|----------------|
| `initial_assessment` | Greenfield checklist |
| `incremental_update` | Incremental update (team workflow — 3 phases) |
| `full_refresh` | Full refresh |

## Incremental_update agent flow

1. Run `team_readiness.py` → **AskQuestion** confirm baselines current.
2. Per user: `fetch_incremental.py` → show candidates → **AskQuestion** confirm scope → `process_incremental.py` → `crtqa_stats_rollup.py`.
3. `crtqa_stats_team_rollup.py` → `latest-team.md`.
