# Corner QA — how to run the main processes

This workspace is a **Corner Trader QA harness** for humans and AI agents: prepare epics, draft coverage and tests, and archive artefacts under `epics/<KEY>/`. **Workspace rules load automatically** in Cursor.

**Organization-wide Cursor MCP** (tokens, server layout, global settings): [AI with Cursor](https://confluence.in.devexperts.com/spaces/QAPORTAL/pages/497112528/AI+with+Cursor) on QAPORTAL.

### Operator prerequisites

- **jq** (recommended for agent-assisted epic work): install on system **PATH**. **Windows:** `winget install --id jqlang.jq -e`. **macOS:** `brew install jq`. Details: [automation/docs/jq.md](automation/docs/jq.md).
- **MCP:** configure `user-mcp-atlassian` and optional CTQA tools per [AGENTS.md](AGENTS.md).

**Where detail lives:** [AGENTS.md](AGENTS.md) · [epics/README.md](epics/README.md) · [docs/harness-map.json](docs/harness-map.json) · [docs/harness-principles.md](docs/harness-principles.md) · playbooks under [.cursor/pipelines/](.cursor/pipelines/)

---

## 1. Stats (CRTQA Test Case Development time) — personal only

| Mode | When |
|------|------|
| `initial_assessment` | First time: build corpus + `state/last-sync-<you>.json` |
| `incremental_update` | Team workflow: confirm baselines → scoped AI TCD → `latest-team.md` |
| `full_refresh` | Re-fetch existing keys; roles unchanged unless you re-attest |

**How to run**

```text
/crtqa-stats mode=initial_assessment jira_user=<you>
/crtqa-stats mode=incremental_update
/crtqa-stats mode=incremental_update users=mshpak,amukanova
/crtqa-stats mode=full_refresh jira_user=<you>
```

**Incremental (team):** Phase 1 — `python automation/tools/crtqa_stats/team_readiness.py` (confirm all `latest-*` current). Phase 2 — per user `fetch_incremental.py` → confirm scope → `process_incremental.py` → `crtqa_stats_rollup.py`. Phase 3 — `python automation/tools/crtqa_stats_team_rollup.py` → `stats/crtqa-stats/latest-team.md`.

Skill: [`.cursor/skills/crtqa-stats/SKILL.md`](.cursor/skills/crtqa-stats/SKILL.md) · Command: [`.cursor/commands/crtqa-stats.md`](.cursor/commands/crtqa-stats.md) · Contract: [docs/crtqa-stats-contract.json](docs/crtqa-stats-contract.json) · Rollup: [automation/docs/crtqa-stats.md](automation/docs/crtqa-stats.md)

---

## 2. Pipelines (QA work per Epic)

### Epic orchestrator (`/crtqa-helper`)

Recommended entry for a full epic chain — **one pipeline stage per agent turn**.

| Command | When |
|---------|------|
| **`/crtqa-helper CRT-1234`** | Bind epic key; run env probe then first stage when env passes |
| **`/crtqa-helper resume`** | Advance one stage or clear a gate; optional comment → `epics/<KEY>/helper/operator-feedback.md` |

**Human gates:** env (tunnel/console) · coverage review (edit `-coverage.md` and/or comment on resume) · discover creds (tokens on resume line only — never in session files).

Scratch: `epics/<KEY>/helper/` (gitignored) archives to `context/helper/` on **`CLOSE:`**. Contract: [docs/crtqa-helper-contract.json](docs/crtqa-helper-contract.json).

You can still run individual triggers below without the orchestrator.

### Pipeline reference

Run **one Epic per chat**. Paste trigger + key on the first line (e.g. `COVERAGE: CRT-639`).

| Trigger | Purpose | Prep |
|---------|---------|------|
| `EPIC-PREP:` | Requirement map + proposed obligations | Jira/Confluence MCP |
| `COVERAGE:` | First-pass Smart Checklist | `-ref.json`; harness maps optional |
| `ANALYSE:` | Coverage-grounded gap audit | `-coverage.json` |
| `TEST-DISCOVER:` | Obligation closure + verification affordances | Postgres tunnel + `/crtqa-console start` + `/crtqa-env`; chrome-devtools MCP; FE creds on trigger line |
| `COVERAGE-REINFORCE:` | Deepen checklist from discover + operator feedback | `-discover.json`, `helper/affordances-slice.json`, `operator-feedback.md` |
| `TEST-PRECON:` | Preconditions + session placeholders | Same env prep as discover |
| `TEST-PREP:` | Regression test draft bundles | Same env prep; `-coverage.json` obligations |
| `CLOSE:` | Integrity ladder + archive | Full artefact set at epic root |

Playbooks: [.cursor/pipelines/](.cursor/pipelines/) · Layout: [epics/README.md](epics/README.md)

---

## 3. Calibrate (prod vs operator gold)

**When:** After the full epic workflow (through **`CLOSE:`** when you close) and after you curate **gold** under **`.cursor/calibrate/<KEY>-gold/`** (required: **`<KEY>-coverage.json`** and **`<KEY>-tests.json`**).

**How:**

1. Run **`/crtqa-calibrate`** in Cursor (no CLI args on the slash command).
2. Answer the **questionnaire** (epic key).
3. Mechanical gates: gold must include **`gold_as_of:`** in README; **`gold_distinct`** rejects gold that merely copies `context/`; **`compare`** emits `NO_ACTIONABLE_DELTA` or `DELTA_REVIEW`.
4. **`NO_ACTIONABLE_DELTA`** — **success**: no harness suggestions; you are done until gold or prod changes.
5. **`DELTA_REVIEW`** only — agent may propose up to **3** harness changes, each tied to a compare signal; discuss in a **separate** chat to apply — calibrate does **not** auto-merge playbook patches.

**Where gold lives:** [`.cursor/calibrate/<KEY>-gold/`](.cursor/calibrate/README.md)

**What you get:** A suggestion list and optional report under **`.cursor/calibrate/reports/<KEY>-latest.md`** — not automatic harness commits.

**Docs:** [automation/docs/calibrate.md](automation/docs/calibrate.md) · [epics/README.md](epics/README.md) (calibrate bullet)

---

## Maintainer publish (`CLEAN:`) — personal branch only

Align harness and push tiers: **`CLEAN:`** on branch **`personal`** only — `scope=full` (default) pushes `origin/personal`, `team/team`, and `releases/public-M.N`. Playbook: [`.cursor/pipelines/clean.md`](.cursor/pipelines/clean.md). Tier matrix: [docs/clean-publish-tier-matrix.md](docs/clean-publish-tier-matrix.md).
