# Agentic epic helper — team harness

Runnable **Corner Trader QA** harness for contributors: epic pipelines, **`/epic-helper`**, verifiers, templates, org maps, and calibrate — **without** maintainer epics, release-notes tooling, stats, or publish tooling.

## Repository

| Item | Value |
|------|--------|
| **Remote** | [agentic-epic-helper-team](https://github.com/heatdance/agentic-epic-helper-team.git) |
| **Branch** | **`team`** |

**Clone:**

```bash
git clone https://github.com/heatdance/agentic-epic-helper-team.git -b team
```

Updates land via **pull requests** to `team` (do not push directly unless you are the repo admin).

## Start here

| Who | First reads |
|-----|-------------|
| **Humans** | [HOW-TO.md](HOW-TO.md) (orchestrator, pipelines, calibrate, CTQA prep) |
| **AI agents** | [AGENTS.md](AGENTS.md), [docs/harness-principles.md](docs/harness-principles.md), [docs/harness-map.json](docs/harness-map.json) |

## Pipelines (chat triggers)

Playbooks: [.cursor/pipelines/](.cursor/pipelines/)

| Entry | When |
|-------|------|
| **`/epic-helper`** + Epic key | Full chain — one stage per turn ([epic-helper.md](.cursor/commands/epic-helper.md)) |
| `EPIC-PREP:` … `CLOSE:` | Individual stages — see [HOW-TO.md](HOW-TO.md) pipeline table |
| `/epic-calibrate` | Prod vs gold ([epic-calibrate.md](.cursor/commands/epic-calibrate.md); gold folders are local) |

Router: [.cursor/rules/pipeline-router.mdc](.cursor/rules/pipeline-router.mdc).

## Context JSON

Committed org maps (update only if your team agrees): [docs/project.json](docs/project.json), [docs/qa-project.json](docs/qa-project.json), [docs/corner-platform-map.json](docs/corner-platform-map.json). Add **gitignored** `.cursor/mcp.json` from the MCP examples below.

## Epics and automation

- [epics/README.md](epics/README.md) · [epics/templates/](epics/templates/)
- [automation/docs/](automation/docs/) · [automation/tools/](automation/tools/)
- [automation/CI/](automation/CI/) — Corner Epic QA on dxCity (team/personal only)

Publish tier matrix (maintainer reference on upstream): not applicable in this repo.
