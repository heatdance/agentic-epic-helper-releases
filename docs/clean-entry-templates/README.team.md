# Agentic epic helper — team harness

Runnable **Corner Trader QA** harness for contributors: epic pipelines, **`/crtqa-helper`**, verifiers, templates, org maps, and calibrate — **without** maintainer epics, release-notes tooling, stats, coaches, teach, or publish tooling.

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
| **Humans** | [HOW-TO.md](HOW-TO.md) (orchestrator, pipelines, calibrate, CTQA prep) |
| **AI agents** | [AGENTS.md](AGENTS.md), [docs/harness-principles.md](docs/harness-principles.md), [docs/harness-map.json](docs/harness-map.json) |

## Pipelines (chat triggers)

Playbooks: [.cursor/pipelines/](.cursor/pipelines/)

| Entry | When |
|-------|------|
| **`/crtqa-helper`** + Epic key | Full chain — one stage per turn ([crtqa-helper.md](.cursor/commands/crtqa-helper.md)) |
| `EPIC-PREP:` … `CLOSE:` | Individual stages — see [HOW-TO.md](HOW-TO.md) pipeline table |
| `/crtqa-calibrate` | Prod vs gold ([crtqa-calibrate.md](.cursor/commands/crtqa-calibrate.md); gold folders are local) |

Router: [.cursor/rules/pipeline-router.mdc](.cursor/rules/pipeline-router.mdc).

## Context JSON

Committed org maps (update only if your team agrees): [docs/project.json](docs/project.json), [docs/qa-project.json](docs/qa-project.json), [docs/corner-platform-map.json](docs/corner-platform-map.json). Add **gitignored** `.cursor/mcp.json` from the MCP examples below.

## Epics and automation

- [epics/README.md](epics/README.md) · [epics/templates/](epics/templates/)
- [automation/docs/](automation/docs/) · [automation/tools/](automation/tools/)

Publish tier matrix (maintainer reference on upstream): not applicable in this repo.
