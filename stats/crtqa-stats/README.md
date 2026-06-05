# CRTQA stats (v5)

Per-engineer rollups for **Test Case Development** and related QA work: **manual corpus** vs **AI-assisted comparison**, with draft-hour sizing and honest attribution.

| Doc | Role |
|-----|------|
| [`/crtqa-stats`](../../.cursor/commands/crtqa-stats.md) | Slash entry |
| [`.cursor/skills/crtqa-stats/SKILL.md`](../../.cursor/skills/crtqa-stats/SKILL.md) | **Canonical agent playbook** (greenfield, modes, metrics) |
| [docs/crtqa-stats-contract.json](../../docs/crtqa-stats-contract.json) | Normative JQL, paths, gates |
| [HOW-TO.md § stats](../../HOW-TO.md) | Human operator steps |
| [automation/docs/crtqa-stats.md](../../automation/docs/crtqa-stats.md) | Rollup CLI |

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
| `incremental_update` | Phase 1 baseline gate → scoped Done TCD per user → `latest-team.md` |
| `full_refresh` | Re-fetch keys; roles unchanged without entrust |

Example:

```text
/crtqa-stats mode=initial_assessment jira_user=mshpak
/crtqa-stats mode=incremental_update
```

Rollup (per user):

```bash
python automation/tools/crtqa_stats_rollup.py --jira-user mshpak
python automation/tools/crtqa_stats_rollup.py --jira-user mshpak --append-longitudinal
```

Team rollup (after incremental):

```bash
python automation/tools/crtqa_stats_team_rollup.py
```

If `jira_user` is omitted on **`initial_assessment`** or **`full_refresh`**, the agent asks via **AskQuestion**. **`incremental_update`** uses contract `team_users[]` (or `users=` override).

## Generate from zero

Follow [`.cursor/skills/crtqa-stats/SKILL.md`](../../.cursor/skills/crtqa-stats/SKILL.md) § Greenfield:

1. MCP harvest (or `fetch_initial_assessment.py`) → temp JSON  
2. `process_initial_assessment.py` + `--epic-meta` → `state/last-sync-<user>.json`  
3. `fetch_epic_meta.py` if needed  
4. `epic-categories.json` via `set_epic_category.py` per epic  
5. `crtqa_stats_rollup.py --jira-user <user>` → `latest-<user>.md`

## Report

`stats/crtqa-stats/latest-<username>.md` — header, display tier, **collapsed rollup**, **category rollup**, **Epic breakdown**, **AI Epic breakdown**.

`stats/crtqa-stats/latest-team.md` — **Generated**, **Users**, **Scope**; **collapsed rollup** (team Saved % from team row medians); **per-user rollup** (individual Saved % per Small/Big band).

Optional **`epic_meta`** in state; **`epic-categories.json`** for FE/BE/API/Other (rollup applies before render).

## Git / CLEAN

| Path | personal | team / public |
|------|----------|----------------|
| `latest-*.md` (incl. `latest-team.md`) | local / optional commit on personal | **omitted** |
| `state/`, `raw/` | gitignored | omitted |
| `README.md`, `temp/categories.json`, command, rollup script | kept on team | stats tree omitted on public |

Association, not causation.
