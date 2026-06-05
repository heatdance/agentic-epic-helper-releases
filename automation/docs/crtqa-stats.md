# CRTQA stats (`automation/tools/crtqa_stats/`) — schema v5

Per-user rollups: **corpus** vs **comparison**, categories, epic breakdown. Team incremental → **`latest-team.md`**. Agent playbook: [`.cursor/skills/crtqa-stats/SKILL.md`](../../.cursor/skills/crtqa-stats/SKILL.md). Slash: [`/crtqa-stats`](../../.cursor/commands/crtqa-stats.md). Contract: [docs/crtqa-stats-contract.json](../../docs/crtqa-stats-contract.json).

## Greenfield (from zero)

1. **Harvest** — MCP or `fetch_initial_assessment.py` → `stats/crtqa-stats/temp/initial-<user>/` (`qa-search.json`, `issues/`, `epic-meta.json`).
2. **State** — `process_initial_assessment.py` with `--epic-meta` → `state/last-sync-<user>.json`.
3. **Meta** — `fetch_epic_meta.py --jira-user <user>` if summaries missing.
4. **Categories** — [stats/crtqa-stats/epic-categories.json](../../stats/crtqa-stats/epic-categories.json) via `set_epic_category.py` (research FE/BE/API/Other per epic).
5. **Report** — `crtqa_stats_rollup.py --jira-user <user>` → `latest-<user>.md`.

## Incremental update (team — 3 phases)

1. **Baseline gate** — `team_readiness.py` (operator confirms all `latest-*` current).
2. **Per user** — `fetch_incremental.py` → operator confirms scope → `process_incremental.py` (`--all` or `--include-keys`) → `crtqa_stats_rollup.py --jira-user <user>`.
3. **Team** — `crtqa_stats_team_rollup.py` → `latest-team.md`.

Requires existing per-user state from greenfield.

## Scripts

| Script | When |
|--------|------|
| [`fetch_initial_assessment.py`](../tools/crtqa_stats/fetch_initial_assessment.py) | Jira REST harvest → temp dir |
| [`process_initial_assessment.py`](../tools/crtqa_stats/process_initial_assessment.py) | Build v5 state from harvest |
| [`fetch_incremental.py`](../tools/crtqa_stats/fetch_incremental.py) | Done TCD candidates not in state |
| [`process_incremental.py`](../tools/crtqa_stats/process_incremental.py) | Append scoped comparison rows |
| [`team_readiness.py`](../tools/crtqa_stats/team_readiness.py) | Phase 1 baseline checklist |
| [`fetch_epic_meta.py`](../tools/crtqa_stats/fetch_epic_meta.py) | Backfill `epic_meta` on state |
| [`set_epic_category.py`](../tools/crtqa_stats/set_epic_category.py) | Record one epic category review |
| [`seed_epic_categories_from_states.py`](../tools/crtqa_stats/seed_epic_categories_from_states.py) | Bulk registry from state files |
| [`patch_epic_categories.py`](../tools/crtqa_stats/patch_epic_categories.py) | Maintainer category patches |
| [`crtqa_stats_rollup.py`](../tools/crtqa_stats_rollup.py) | Apply categories + render `latest-<user>.md` |
| [`crtqa_stats_team_rollup.py`](../tools/crtqa_stats_team_rollup.py) | Render `latest-team.md` |

## Library modules

| Module | Role |
|--------|------|
| `gather.py` | Jira parse, lanes, worklogs, estimates |
| `categories.py` | Hint classifier + size bands |
| `apply_categories.py` | Registry → state rows |
| `ingest.py` | State I/O, team discovery, readiness |
| `render_report.py` | Per-user markdown; `pack_user_collapsed_bands` |
| `render_team_report.py` | Team collapsed rollup |
| `epic_breakdown.py` | Epic / AI epic tables |
| `jira_rest.py` | Shared Jira REST + normalize_issue |

## Rollup

```bash
python automation/tools/crtqa_stats_rollup.py --jira-user mshpak
python automation/tools/crtqa_stats_rollup.py --jira-user mshpak --append-longitudinal
python automation/tools/crtqa_stats_team_rollup.py
python automation/tools/crtqa_stats_team_rollup.py --users mshpak,amukanova
python automation/tools/crtqa_stats/team_readiness.py
```

Applies `apply_epic_categories_to_state` before render. Exit **1** on missing state or schema mismatch (`team_readiness.py` exits **1** when baselines incomplete).

## State (v5)

`stats/crtqa-stats/state/last-sync-<jira_user>.json` (gitignored): `rows[]`, `corpus_epic_keys[]`, `epic_classifications[]`, `epic_meta`, `attestation_by_epic`, `report_meta`. v4 state is not migrated.

## Report sections

**Per user (`latest-<user>.md`):**

- **Collapsed rollup** — two Small/Big rows when both size bands have ≥4 corpus epics; else one row (or micro corpus layout).
- **Category rollup** — FE/BE/API/Other × Small/Big TCD.
- **Epic breakdown** / **AI Epic breakdown** — per-epic sums, Jira links, `FE+S` labels.

**Team (`latest-team.md`):** header (Generated, Users, Scope); **collapsed rollup** — always Small + Big rows; team **Saved %** from team `median logged` and `AI logged avg` on that row; **per-user rollup** — same columns per user×band with individual Saved %.

**Metrics:** medians from corpus rows in scope; AI logged avg = mean comparison logged; Saved % = `(median_corpus_logged − ai_avg) / median_corpus_logged`. Team row uses **means of per-user band metrics** (see contract).
