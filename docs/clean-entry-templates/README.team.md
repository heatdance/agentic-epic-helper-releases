# Agentic epic helper — team harness

Runnable **Corner Trader QA** harness for contributors: epic pipelines, verifiers, templates, org maps, `/crtqa-stats`, and optional calibrate — **without** maintainer epics, release-notes tooling, personal stats reports, or publish tooling.

## Repository

| Item | Value |
|------|--------|
| **Remote** | [{{TEAM_REPO_SLUG}}]({{TEAM_REPO_URL}}) |
| **Branch** | **`{{TEAM_BRANCH}}`** |

**Clone:**

```bash
git clone {{TEAM_REPO_URL}} -b {{TEAM_BRANCH}}
```

Updates land via **pull requests** to `{{TEAM_BRANCH}}` (do not push directly unless you are the repo admin).

## Start here

| Who | First reads |
|-----|-------------|
| **Humans** | [HOW-TO.md](HOW-TO.md) (pipelines, calibrate, CTQA prep) |
| **AI agents** | [AGENTS.md](AGENTS.md), [docs/harness-principles.md](docs/harness-principles.md), [docs/harness-map.json](docs/harness-map.json) |

## Pipelines (chat triggers)

Playbooks: [.cursor/pipelines/](.cursor/pipelines/)

| Trigger | Playbook |
|---------|----------|
| `EPIC-PREP:` + Epic key | [epic-prep.md](.cursor/pipelines/epic-prep.md) |
| `COVERAGE:` + Epic key | [coverage.md](.cursor/pipelines/coverage.md) |
| `ANALYSE:` + Epic key | [analysis.md](.cursor/pipelines/analysis.md) |
| `TEST-DISCOVER:` + Epic key | [test-discover.md](.cursor/pipelines/test-discover.md) |
| `TEST-PRECON:` + Epic key | [test-precon.md](.cursor/pipelines/test-precon.md) |
| `TEST-PREP:` + Epic key | [test-prep.md](.cursor/pipelines/test-prep.md) |
| `CLOSE:` + Epic key | [close.md](.cursor/pipelines/close.md) |
| `/crtqa-calibrate` | [crtqa-calibrate.md](.cursor/commands/crtqa-calibrate.md) — prod vs gold (gold folders are local; not in this repo) |

Router: [.cursor/rules/pipeline-router.mdc](.cursor/rules/pipeline-router.mdc).

## Context JSON

Committed org maps (update only if your team agrees): [docs/project.json](docs/project.json), [docs/qa-project.json](docs/qa-project.json), [docs/corner-platform-map.json](docs/corner-platform-map.json). Add **gitignored** `.cursor/mcp.json` from the MCP examples below.

## Epics and automation

- [epics/README.md](epics/README.md) · [epics/templates/](epics/templates/)
- [automation/docs/](automation/docs/) · [automation/tools/](automation/tools/)

Publish tier matrix (maintainer reference on upstream): not applicable in this repo.
