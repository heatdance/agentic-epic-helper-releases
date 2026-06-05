---
name: crtqa-stats
description: CRTQA stats v5 — test-first corpus, per-user latest-<user>.md, categories, epic breakdown. Use for /crtqa-stats or rebuilding statistics from zero.
paths: stats/crtqa-stats/**
---

# CRTQA stats (v5)

**Normative contract:** [docs/crtqa-stats-contract.json](../../docs/crtqa-stats-contract.json)  
**Slash entry:** [`.cursor/commands/crtqa-stats.md`](../../commands/crtqa-stats.md)  
**Rollup CLI:** [automation/docs/crtqa-stats.md](../../automation/docs/crtqa-stats.md)

## Modes

| Mode | Trigger |
|------|---------|
| `initial_assessment` | First-time corpus for a Jira user |
| `incremental_update` | New Done TCD → `comparison` (requires state) |
| `full_refresh` | Re-fetch included keys; do not change roles without entrust |

If `jira_user=` is missing on the slash line, **AskQuestion** once, then resolve user via MCP.

## Greenfield — generate from zero

Use this checklist for a **new engineer** or after deleting `state/last-sync-<user>.json`.

### 1. Discover corpus (Jira MCP)

1. Paginate tests: `project = CRTQA AND issuetype = Test AND reporter = {user}` (contract template; `limit` ≤ 50, advance `start_at`).
2. From each test: `issuelinks` + summary regex → CRT epic keys ([`gather.extract_epics_from_issue`](../../automation/tools/crtqa_stats/gather.py)).
3. Per epic: cross-project QA JQL (`task_jql_template`) — TCD, Epic Testing/Validation, Release notes, Update test; apply `exclude_from_qa`.
4. Per task: `worklog`, `timetracking`, `customfield_11250`, Epic Link, summary, status.

Optional harvest CLI (same creds as MCP, writes under `stats/crtqa-stats/temp/`):

```bash
python automation/tools/crtqa_stats/fetch_initial_assessment.py --jira-user <user> --out-dir stats/crtqa-stats/temp/initial-<user>
```

### 2. Build state

```bash
python automation/tools/crtqa_stats/process_initial_assessment.py \
  --jira-user <user> \
  --tests-count <N> \
  --qa-list stats/crtqa-stats/temp/initial-<user>/qa-search.json \
  --issues-dir stats/crtqa-stats/temp/initial-<user>/issues \
  --epic-meta stats/crtqa-stats/temp/initial-<user>/epic-meta.json
```

- **Corpus gate:** epics with sum(user QA worklogs) = 0 are dropped.
- Rows default `role=corpus`. Optional `--exclude-epics CRT-594` → `attestation_by_epic` (AI-assisted, not corpus).
- Classify **after** `epic-meta.json` is loaded; then apply registry.

### 3. Epic summaries (`epic_meta`)

```bash
python automation/tools/crtqa_stats/fetch_epic_meta.py --jira-user <user>
```

Required for Epic breakdown Note line 1. Idempotent merge into state.

### 4. Epic categories (FE / BE / API / Other)

**SoT:** [stats/crtqa-stats/epic-categories.json](../../stats/crtqa-stats/epic-categories.json) (shared across users).

Research rubric (major work only):

| Category | Signal |
|----------|--------|
| **fe** | Client UI — dxTrade5, WebBroker, charts, OE |
| **be** | Server logic, metrics, jobs, risk, settlement |
| **api** | External integration, FIX/REST, feeds |
| **other** | Rare — none dominates |

Per new epic:

```bash
python automation/tools/crtqa_stats/set_epic_category.py \
  --epic CRT-KEY --category fe --rationale "..." --evidence CRT-123
```

Bulk seed from existing states (maintainer): `seed_epic_categories_from_states.py`; patches: `patch_epic_categories.py`.

### 5. Render report (always)

```bash
python automation/tools/crtqa_stats_rollup.py --jira-user <user>
python automation/tools/crtqa_stats_rollup.py --jira-user <user> --append-longitudinal
```

Rollup calls `apply_epic_categories_to_state` then writes `stats/crtqa-stats/latest-<user>.md`.

### 6. Optional raw audit

Append `stats/crtqa-stats/raw/<user>/run-<UTC>.jsonl` during ingest (agent/MCP trace).

---

## Incremental update (team workflow)

Three phases. **`jira_user=` optional** — omit to run for all roster users with state; `users=` on slash line overrides contract [`team_users`](../../docs/crtqa-stats-contract.json).

### Phase 1 — Baseline readiness (hard stop)

```bash
python automation/tools/crtqa_stats/team_readiness.py
python automation/tools/crtqa_stats/team_readiness.py --json
```

List each user's `latest-<user>.md` Generated timestamp vs `state/last-sync-<user>.json` `last_sync_utc`. **AskQuestion:** “Are all listed latest-* files current?” — proceed only on explicit yes.

Roster default: contract `team_users[]`; discover anyone with `state/last-sync-*.json`. Skip users without state (warn).

### Phase 2 — Scoped AI incremental (per user)

For each user in scope:

```bash
python automation/tools/crtqa_stats/fetch_incremental.py \
  --jira-user <user> \
  --out-dir stats/crtqa-stats/temp/incremental-<user>

python automation/tools/crtqa_stats/process_incremental.py \
  --jira-user <user> \
  --candidates stats/crtqa-stats/temp/incremental-<user>/candidates.json \
  --all
# or: --include-keys CRTQA-10132 CRTQA-…
```

- Candidates: Done TCD **not** in `included_issue_keys`; user worklog > 0; epic in `corpus_epic_keys` or `attestation_by_epic`.
- **AskQuestion:** confirm scope (all candidates or subset) before `process_incremental.py`.
- Per-user finalize: `python automation/tools/crtqa_stats_rollup.py --jira-user <user>`

### Phase 3 — Team rollup

```bash
python automation/tools/crtqa_stats_team_rollup.py
python automation/tools/crtqa_stats_team_rollup.py --users mshpak,amukanova
```

Writes [`stats/crtqa-stats/latest-team.md`](../../stats/crtqa-stats/latest-team.md) — header: Generated, Users, Scope; **collapsed rollup** (Small + Big; team **Saved %** = `(team median logged − team AI logged avg) / team median logged`); **per-user rollup** table with the same columns per engineer.

## Full refresh

Re-fetch all `included_issue_keys`; do **not** change `role` or corpus membership without operator entrust. Finalize rollup.

---

## Report shape (`latest-<user>.md`)

1. Header — counts, display tier (`full` | `partial` | `collapsed`).
2. **Collapsed rollup** — if **both** Small and Big bands have ≥4 **corpus epics**, two rows (`Small TCD ≤16h`, `Big TCD >16h`); else one all-corpus row.
3. **Category rollup** — FE/BE/API/Other × Small/Big.
4. **Epic breakdown** — corpus epics; `FE+S` / `BE+B`; Draft/Logged sums; Note = summary + category rationale.
5. **AI Epic breakdown** — attested (`attestation_by_epic`) ∪ comparison epics.

## Metrics (same formulas per scope)

| Metric | Collapsed (single row) | Collapsed (split) | Category row |
|--------|------------------------|-------------------|--------------|
| Median draft / logged | All corpus rows | Corpus rows in that size band | Corpus in category×size |
| AI epics | Attested ∪ comparison in scope | Per size band | Per category×size |
| AI logged avg | Mean comparison logged in scope | Same, per band | Same, per cell |
| Saved % | `(median_corpus_logged − ai_avg) / median_corpus_logged` | Same | Same |

Attested-only AI epics count in **AI epics** but not avg/Saved until a logged comparison TCD exists.

## Outputs (git)

| Path | personal |
|------|----------|
| `latest-<user>.md` | gitignored pattern |
| `latest-team.md` | gitignored (`paths.latest_team`) |
| `state/`, `raw/` | gitignored |
| `epic-categories.json`, `temp/categories.json`, README, skill, command | committed on team |

Do **not** write `latest.md` (removed v5).

## Tools map

| Script | Role |
|--------|------|
| `fetch_initial_assessment.py` | Jira REST harvest → temp JSON + `epic-meta.json` |
| `process_initial_assessment.py` | QA list + issues → `last-sync-<user>.json` |
| `fetch_epic_meta.py` | Backfill `epic_meta` on existing state |
| `set_epic_category.py` | One manual category review |
| `seed_epic_categories_from_states.py` | Bulk registry from state files |
| `patch_epic_categories.py` | Maintainer category corrections |
| `crtqa_stats_rollup.py` | Apply categories + render `latest-<user>.md` |
| `fetch_incremental.py` | Done TCD candidates for incremental |
| `process_incremental.py` | Append scoped comparison rows to state |
| `team_readiness.py` | Phase 1 baseline checklist |
| `crtqa_stats_team_rollup.py` | Render `latest-team.md` from user states |

## MCP rules

- **user-mcp-atlassian** only for Jira; read tool schemas before calls.
- Do not invent worklogs, links, or draft hours.
- No secrets in repo files.
