# Corner Trader — QA workspace

Devexperts QA working area for **Corner Trader**: templates, automation docs, and a Cursor harness for agent-assisted work (this repo is not necessarily the application source tree).

## Branches (GitHub: [agentic-epic-helper](https://github.com/heatdance/agentic-epic-helper))

| Branch | Role |
|--------|------|
| **`main`** | **Default** on GitHub — **stable** snapshots. Merge from `develop` (e.g. via PR) when a harness change set is ready to publish. |
| **`develop`** | Integration branch for **new work**; commit and push here first, then promote to `main` when stable. |

## Start here

| Who | First reads |
|-----|-------------|
| **Humans** | [qa-handoff.md](qa-handoff.md) (session focus), [.cursor/HOW-TO.md](.cursor/HOW-TO.md) (Cursor: pipelines, MCP, CTQA Postgres tunnel) |
| **AI agents** | [AGENTS.md](AGENTS.md) (map + MCP policy), [docs/harness-map.json](docs/harness-map.json) (keyword → which files to open; tiers T0–T2) |

## Product and QA context (JSON)

- [docs/project.json](docs/project.json) — product / **fork-of DXtrade XT** Confluence anchors (CT / XT), Bitbucket defaults.
- [docs/qa-project.json](docs/qa-project.json) — Corner QA scope (QAPORTAL Corner subtree), environments, Jira mapping (functional summaries only).

## Pipelines (chat triggers)

All playbooks: [.cursor/pipelines/](.cursor/pipelines/)

| Trigger | Playbook |
|---------|----------|
| `EPIC-PREP:` + Epic key | [epic-prep.md](.cursor/pipelines/epic-prep.md) |
| `COVERAGE:` + Epic key | [coverage.md](.cursor/pipelines/coverage.md) |
| `ANALYSE:` + Epic key | [analysis.md](.cursor/pipelines/analysis.md) |
| `TEST-PREP:` + Epic key | [test-prep.md](.cursor/pipelines/test-prep.md) |

Router: [.cursor/rules/pipeline-router.mdc](.cursor/rules/pipeline-router.mdc).

## Epics and templates

- Layout and workflow: [epics/README.md](epics/README.md).
- Schemas: [epics/templates/](epics/templates/) (`epic-ref.json`, `coverage-ref.json`, `analysis-ref.json`, `tests-ref.json`).
- Per-Epic artifacts live under `epics/<KEY>/`.

## Automation

- Tool docs: [automation/docs/](automation/docs/) (e.g. [yogi-url-resolve.md](automation/docs/yogi-url-resolve.md), [figma-mcp.md](automation/docs/figma-mcp.md)).
- Runnable tools: [automation/tools/](automation/tools/) — **CTQA Postgres SSH tunnel / probe**: [automation/tools/tunnel/README.md](automation/tools/tunnel/README.md) (`ctqa_pg.py`, PuTTY plink default on Windows).
- Scratch: [automation/temp/](automation/temp/) (short-lived; see [automation/temp/README.md](automation/temp/README.md)).

## Rules, prompts, MCP config

- Rules: [.cursor/rules/](.cursor/rules/).
- Prompt scaffolds: [.cursor/prompts/](.cursor/prompts/).
- Optional **postgres-ctqa** MCP: copy [.cursor/mcp.json.example](.cursor/mcp.json.example) to `.cursor/mcp.json` — see [.cursor/HOW-TO.md](.cursor/HOW-TO.md) (*MCP — PostgreSQL*); SSH tunnel + local URI; no secrets in git.

## Reference docs

- Test case format: [docs/tc-ref](docs/tc-ref).
- Defect report format: [docs/dr-ref](docs/dr-ref).

Template references under [docs/](docs/). Automation under [automation/](automation/).
