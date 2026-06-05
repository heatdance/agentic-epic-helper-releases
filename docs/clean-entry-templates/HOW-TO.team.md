# Corner QA — how to run the main processes

This workspace is a **Corner Trader QA harness** for humans and AI agents: prepare epics, draft coverage and tests, and archive artefacts under `epics/<KEY>/`. **Workspace rules load automatically** in Cursor.

**Organization-wide Cursor MCP** (tokens, server layout, global settings): [AI with Cursor](https://confluence.in.devexperts.com/spaces/QAPORTAL/pages/497112528/AI+with+Cursor) on QAPORTAL.

### Operator prerequisites

- **jq** (recommended for agent-assisted epic work): install on system **PATH**. **Windows:** `winget install --id jqlang.jq -e`. **macOS:** `brew install jq`. Details: [automation/docs/jq.md](automation/docs/jq.md).
- **MCP:** configure `user-mcp-atlassian` and optional CTQA tools per [AGENTS.md](AGENTS.md).

**Where detail lives:** [AGENTS.md](AGENTS.md) · [epics/README.md](epics/README.md) · [docs/harness-map.json](docs/harness-map.json) · [docs/harness-principles.md](docs/harness-principles.md) · playbooks under [.cursor/pipelines/](.cursor/pipelines/)

---

## 1. Pipelines (QA work per Epic)

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

## 2. Calibrate (prod vs operator gold)

**When:** After the full epic workflow (through **`CLOSE:`** when you close) and after you curate **gold** under **`.cursor/calibrate/<KEY>-gold/`** (required: **`<KEY>-coverage.json`** and **`<KEY>-tests.json`**; gold folders are local — not in this repo).

**How:**

1. Run **`/crtqa-calibrate`** in Cursor (no CLI args on the slash command).
2. Answer the **questionnaire** (epic key).
3. **`NO_ACTIONABLE_DELTA`** — success; **`DELTA_REVIEW`** — discuss harness edits in a **separate** chat (calibrate does not auto-merge playbook patches).

**Docs:** [automation/docs/calibrate.md](automation/docs/calibrate.md) · [.cursor/calibrate/README.md](.cursor/calibrate/README.md)
