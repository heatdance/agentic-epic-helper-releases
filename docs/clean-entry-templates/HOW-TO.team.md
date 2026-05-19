# Corner QA — how to run the main processes (team harness)

This repository is the **team** share of the agentic epic helper: run epic pipelines and optional calibrate on your machine. **Workspace rules load automatically** in Cursor.

**Detail map:** [AGENTS.md](AGENTS.md) · [epics/README.md](epics/README.md) · [docs/harness-map.json](docs/harness-map.json) · [docs/harness-principles.md](docs/harness-principles.md)

### Operator prerequisites

- **jq** (recommended): [automation/docs/jq.md](automation/docs/jq.md) — `winget install --id jqlang.jq -e` on Windows.
- **MCP:** configure `user-mcp-atlassian` and optional CTQA tools per [AGENTS.md](AGENTS.md).

---

## 1. Pipelines (QA work per Epic)

**Purpose:** Build a reusable artifact chain per Epic. Run **one Epic per chat**.

| Step | Trigger | Main output |
|------|---------|-------------|
| 1 | `EPIC-PREP:` | `epics/<KEY>/<KEY>-ref.json` |
| 2 | `COVERAGE:` | `-coverage.json` / `-coverage.md` |
| 3 | `ANALYSE:` (optional) | `-analysis.json` / `-analysis.md` |
| 4 | `TEST-DISCOVER:` | `-discover.json` |
| 5 | `TEST-PRECON:` (optional) | `-precon.json` / `-precon.md` |
| 6 | `TEST-PREP:` | `-tests.json` / `-tests.md` |
| 7 | `CLOSE:` (optional) | JSON → `context/`; four `.md` at epic root |

### Trigger reference

| Trigger | Needs (under `epics/<KEY>/`) | Optional on same line |
|---------|------------------------------|----------------------|
| `EPIC-PREP:` *KEY* | — | `repo=`, `focus=` |
| `COVERAGE:` *KEY* | `-ref.json` | `repo=`, `focus=` |
| `ANALYSE:` *KEY* | `-coverage.json` | `known_issues=yes`, `resolve=no` |
| `TEST-DISCOVER:` *KEY* | `-ref.json`, `-coverage.json` | FE creds, `proceed`, `crtqa_index=yes` |
| `TEST-PRECON:` *KEY* | `-coverage.json` | Same FE tokens |
| `TEST-PREP:` *KEY* | `-coverage.json` | `map_only=yes`, `draft_profile=teaching` |
| `CLOSE:` *KEY* | full artifact set at epic root | `heal=no` |

Playbooks: [.cursor/pipelines/](.cursor/pipelines/).

### Operator prep (Discovery, Precondition, Prep)

1. Postgres tunnel: [automation/tools/tunnel/README.md](automation/tools/tunnel/README.md)
2. `/crtqa-console start` then `/crtqa-env`
3. **chrome-devtools** MCP when UI is in scope

FE credentials on the trigger line only — never commit secrets.

---

## 2. Calibrate (prod vs operator gold)

**When:** After epic work and local gold under `.cursor/calibrate/<KEY>-gold/` (not shipped in this repo).

1. Run **`/crtqa-calibrate`** in Cursor.
2. Compare `epics/<KEY>/` to your local gold.
3. Apply harness edits in a **separate** chat if needed.

Docs: [automation/docs/calibrate.md](automation/docs/calibrate.md) · [.cursor/calibrate/README.md](.cursor/calibrate/README.md)

---

## 3. Stats (optional, local)

Team repo may include [stats/crtqa-stats/README.md](stats/crtqa-stats/README.md) for methodology; **`latest.md` and state are not published here.** Use `/crtqa-stats` only when your maintainer has configured Jira access locally.
