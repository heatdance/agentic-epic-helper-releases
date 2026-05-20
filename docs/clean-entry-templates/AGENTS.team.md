# AGENTS.md — team harness (contributors)

Short map for coding agents on the **team** repository. **Progressive disclosure** — follow links, do not load the whole tree.

## Project

**Corner Trader QA workspace** (templates, harness, automation). Product context: use **`docs/project.example.json`** locally (Confluence-backed fields are not committed here).

## Where things live

### Canonical JSON

| Area | Path |
|------|------|
| Product / fork (example) | [docs/project.example.json](docs/project.example.json) |
| Corner QA scope (example) | [docs/qa-project.example.json](docs/qa-project.example.json) |
| Environments / repos (example) | [docs/corner-platform-map.example.json](docs/corner-platform-map.example.json) |
| Tiered context | [docs/harness-map.json](docs/harness-map.json) |
| Harness doctrine | [docs/harness-principles.md](docs/harness-principles.md) |
| Calibrate contract | [docs/calibrate-contract.json](docs/calibrate-contract.json) |
| Publish tier matrix (reference) | [docs/clean-publish-tier-matrix.md](docs/clean-publish-tier-matrix.md) |

### Pipelines (agent playbooks)

| Area | Path |
|------|------|
| Epic pipelines | [`.cursor/pipelines/`](.cursor/pipelines/) — `EPIC-PREP:`, `COVERAGE:`, `ANALYSE:`, `TEST-DISCOVER:`, `TEST-PRECON:`, `TEST-PREP:`, `CLOSE:` |
| Calibrate (slash only) | [crtqa-calibrate.md](.cursor/commands/crtqa-calibrate.md) · [calibrate.md](.cursor/pipelines/calibrate.md) |

**No** publish playbook in this repo — maintainer-only upstream.

### Epics

Templates: [epics/templates/](epics/templates/). Per-epic work under `epics/<KEY>/` (your clones; not committed to team remote).

### Automation tools

Verifiers under [automation/tools/](automation/tools/) — see [automation/docs/](automation/docs/).

| Tool | Path |
|------|------|
| `/crtqa-env` | [automation/docs/crtqa-env.md](automation/docs/crtqa-env.md) |
| `/crtqa-console` | [automation/tools/crtqa-console/README.md](automation/tools/crtqa-console/README.md) |
| `/crtqa-calibrate` | [automation/docs/calibrate.md](automation/docs/calibrate.md) · [calibrate_verify.py](automation/tools/calibrate_verify.py) |
| jq inspection | [automation/docs/jq.md](automation/docs/jq.md) |

## How to start a session

1. Read [HOW-TO.md](HOW-TO.md) for the task at hand.
2. For pipelines or calibrate, read [docs/harness-principles.md](docs/harness-principles.md) once per session.
3. Use [docs/harness-map.json](docs/harness-map.json) keyword packages — do not open every doc by default.

## MCP

- **Templates (no secrets):** [`.cursor/mcp.json.example`](../.cursor/mcp.json.example) (postgres + chrome) and [`.cursor/mcp.json.team.example`](../.cursor/mcp.json.team.example) (full stack with `YOUR_*` placeholders).
- **Jira / Confluence / Stash:** `user-mcp-atlassian` — see [docs/mcp-atlassian-tools.md](docs/mcp-atlassian-tools.md). Configure in **gitignored** `.cursor/mcp.json` and/or global `~/.cursor/mcp.json`.
- **Optional:** postgres-ctqa, chrome-devtools, Figma — see [HOW-TO.md](HOW-TO.md) and [automation/tools/tunnel/README.md](../automation/tools/tunnel/README.md).

## Rules

[.cursor/rules/](.cursor/rules/) — `pipeline-router`, `qa-artifacts`, `harness-context`, `jq-json`, `mcp-atlassian-search`, optional UI harness rules.
