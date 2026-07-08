# AGENTS.md — team harness (contributors)

Short map for coding agents on the **team** repository. **Progressive disclosure** — follow links, do not load the whole tree.

## Project

**Corner Trader QA workspace** (templates, harness, automation). Org context maps are **committed on this branch** — point MCP and pipelines at them after you add credentials.

## Where things live

### Canonical JSON

| Area | Path |
|------|------|
| Product / fork | [docs/project.json](docs/project.json) |
| Corner QA scope | [docs/qa-project.json](docs/qa-project.json) |
| Environments / repos | [docs/corner-platform-map.json](docs/corner-platform-map.json) |
| Tiered context | [docs/harness-map.json](docs/harness-map.json) |
| Harness doctrine | [docs/harness-principles.md](docs/harness-principles.md) |
| Epic orchestrator | [docs/epic-helper-contract.json](docs/epic-helper-contract.json) |
| Calibrate contract | [docs/calibrate-contract.json](docs/calibrate-contract.json) |

### Pipelines (agent playbooks)

| Area | Path |
|------|------|
| Epic orchestrator | [epic-helper.md](.cursor/commands/epic-helper.md) |
| Epic pipelines | [`.cursor/pipelines/`](.cursor/pipelines/) — `EPIC-PREP:`, `COVERAGE:`, `COVERAGE-REINFORCE:`, `ANALYSE:`, `TEST-DISCOVER:`, `TEST-PRECON:`, `TEST-PREP:`, `CLOSE:` |
| Calibrate (slash only) | [epic-calibrate.md](.cursor/commands/epic-calibrate.md) · [calibrate.md](.cursor/pipelines/calibrate.md) |

**No** publish playbook or stats in this repo — maintainer-only upstream.

### Epics

Templates: [epics/templates/](epics/templates/). Per-epic work under `epics/<KEY>/` (your clones; not committed to team remote).

### Automation tools

Verifiers under [automation/tools/](automation/tools/) — see [automation/docs/](automation/docs/).

| Tool | Path |
|------|------|
| Corner Epic QA CI (dxCity) | [automation/CI/README.md](automation/CI/README.md) · [rollout-learnings](automation/CI/rollout-learnings.md) · [scripts-reference](automation/CI/scripts-reference.md) · [teamcity scripts](automation/tools/teamcity/) |
| `/crtqa-console` | [automation/tools/crtqa-console/README.md](automation/tools/crtqa-console/README.md) |
| Console gate probe | [crtqa_console_probe.py](automation/tools/crtqa_console_probe.py) |
| `/epic-helper` affordances | [epic_helper_affordances.py](automation/tools/epic_helper_affordances.py) |
| `/epic-calibrate` | [automation/docs/calibrate.md](automation/docs/calibrate.md) · [calibrate_verify.py](automation/tools/calibrate_verify.py) |
| jq inspection | [automation/docs/jq.md](automation/docs/jq.md) |

**Not in this repo:** release-notes command, `releases/**`, epic-stats (maintainer personal branch only).

## How to start a session

1. Read [HOW-TO.md](HOW-TO.md) for the task at hand.
2. For pipelines or calibrate, read [docs/harness-principles.md](docs/harness-principles.md) once per session.
3. Use [docs/harness-map.json](docs/harness-map.json) keyword packages — do not open every doc by default.

## MCP

- **Templates (no secrets):** [`.cursor/mcp.json.team.example`](../.cursor/mcp.json.team.example) (full stack with `YOUR_*` placeholders).
- **Jira / Confluence / Stash:** `user-mcp-atlassian` — see [docs/mcp-atlassian-tools.md](docs/mcp-atlassian-tools.md). Configure in **gitignored** `.cursor/mcp.json` and/or global `~/.cursor/mcp.json`.
- **Optional:** chrome-devtools, Figma — see [HOW-TO.md](HOW-TO.md).

## Rules

[.cursor/rules/](.cursor/rules/) — `pipeline-router`, `qa-artifacts`, `harness-context`, `jq-json`, `mcp-atlassian-search`, optional UI harness rules.
