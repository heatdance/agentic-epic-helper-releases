# CRTQA stats (v4)

Management rollups for **Test Case Development** time: **manual corpus** vs **AI-assisted comparison**, with **draft-hour** sizing and honest **attribution**.

| Doc | Role |
|-----|------|
| [`/crtqa-stats`](../../.cursor/commands/crtqa-stats.md) | Agent playbook (Jira ingest, attestation, schema v4) |
| [HOW-TO.md §1](../../HOW-TO.md) | Human operator steps and read order |
| [automation/docs/crtqa-stats.md](../../automation/docs/crtqa-stats.md) | Rollup script (`crtqa_stats_rollup.py`) |

## Model

| Role | Use |
|------|-----|
| **corpus** | Manual baseline — medians for “expected hours” when n≥4 |
| **comparison** | AI-assisted (agentic epic helper) — vs corpus and/or draft |

**Draft estimate:** Jira **`customfield_11250`** (hours). **Logged:** `timetracking.time_spent` (8h = 1 Devex day). **Do not** use `original_estimate` for draft or SP bands.

**Devex SP** = draft ÷ 8. Size bands: &lt;1 SP (&lt;8h), 1–2 SP (8–16h), 3+ SP (&gt;16h).

**Attribution (comparison rows):** `estimate_only` (under draft, no corpus yet), `corpus_benchmark`, `corpus_and_estimate`, `none` (corpus rows).

## Modes

| Mode | Use |
|------|-----|
| `initial_assessment` | First time: full done-TCD cohort + per-epic AI attestation |
| `incremental_update` | New done tasks only; rollup still refreshes `latest.md` if there are no new keys |
| `full_refresh` | Re-fetch Jira for existing keys — **redo assessment** with same epic decisions, or fix draft/logged after v4 upgrade |

Example:

```text
/crtqa-stats mode=initial_assessment jira_user=<you>
```

Then (agent or terminal):

```bash
python automation/tools/crtqa_stats_rollup.py --append-longitudinal
```

## Report profiles (dynamic)

Recomputed on **every** rollup from current `rows`:

| Profile | Typical situation |
|---------|-------------------|
| `task_detail` | Few tasks or no corpus n≥4 — read **Task-level** + draft vs logged chart first |
| `directional` | Some manual history (corpus 1–3 per category), benchmark not stable |
| `benchmark` | At least one category×size with ≥4 corpus tasks — corpus % saved in tables |

**Read order:** header (profile) → **Task-level** → charts → benchmark tables → footer (attribution legend).

## Cohort (Jira)

- Epics: `project = CRT AND issuetype = Epic AND "test lead" = <user>`
- Tasks: `project = CRTQA AND issuetype = "Test Execution" AND summary ~ "Test Case Development" AND "Epic Link" = <CRT-KEY> AND statusCategory = Done`

## Files

| Path | Git |
|------|-----|
| `latest.md` | committed — management report |
| `temp/categories.json` | committed — taxonomy v3 (draft-hour bands) |
| `state/last-sync.json` | gitignored — schema v4 cumulative state |
| `state/longitudinal.json` | gitignored — per-run snapshots |
| `raw/run-*.jsonl` | gitignored — audit trail |

Association, not causation.
