# Corner Epic QA CI (dxCity / TeamCity)

**Visibility:** personal + team only — excluded from public export ([clean-publish-tier-matrix.json](../../docs/clean-publish-tier-matrix.json)).

**BLUF:** Comment **`Agent: Coverage`** on a **CRTQA** task triggers unattended harness work on dxCity: **EPIC-PREP → COVERAGE → Console gate → GROUND → ANALYSE**. Deliverables land in TeamCity artifacts **`epic-work`**; Jira gets a **comment only** (no API attachment in v1).

## Trigger

| Item | Value |
|------|--------|
| Jira project | **CRTQA** (QA task, not CRT epic) |
| Trigger phrase | `Agent: Coverage` (case-insensitive match in comment body) |
| Epic key source | Regex `\bCRT-\d+\b` from CRTQA **summary** (not Epic Link) |

## Repositories

| Role | Remote | Branch |
|------|--------|--------|
| CI checkout (Pipeline VCS) | Stash `AI/agentic-feature-helper` | **`team`** |
| Maintainer harness workspace | `cursor.corner` (local) | push `team` → Stash |

Push to Stash (when SSH configured):

```bash
git push stash refs/heads/team:refs/heads/team
```

## TeamCity build configurations

| Display name | Build configuration ID | Role |
|--------------|------------------------|------|
| Corner Epic QA Dispatch | `CornerTrader_QATooling_CornerEpicQaDispatch` | Poll Jira, dedup, queue Pipeline |
| Corner Epic QA Pipeline | `CornerTrader_QATooling_CornerEpicQaPipeline` | Full harness chain + Jira comment |
| Corner Epic QA Console Gate | *(optional standalone)* | Smoke OpenSSH console probe |

## Documentation map

| Doc | Contents |
|-----|----------|
| [architecture.md](architecture.md) | Components, data flow, vs `/epic-helper` |
| [teamcity-setup.md](teamcity-setup.md) | VCS, agents, cron, artifacts, parallelism |
| [pipeline-steps.md](pipeline-steps.md) | 12 steps → scripts + verifiers |
| [dispatch.md](dispatch.md) | JQL, dedup, REST queue, manual Run |
| [secrets-and-params.md](secrets-and-params.md) | Password/text parameters, anti-patterns |
| [jira-integration.md](jira-integration.md) | Success/fail comment templates |
| [artifacts.md](artifacts.md) | `epic-work` layout |
| [operations.md](operations.md) | Run Dispatch vs Pipeline, rerun, dedup reset |
| [troubleshooting.md](troubleshooting.md) | Known failures from v1 rollout |
| [decisions.md](decisions.md) | ADR: scope, comment-only, chain stop |

## Scripts (executable)

TeamCity wrappers live under [`automation/tools/teamcity/`](../tools/teamcity/). Dispatch reference copy: [`dispatch/poll-and-queue.sh`](dispatch/poll-and-queue.sh).

Console gate deep-dive (OpenSSH only): [`automation/docs/crtqa-console-ci.md`](../docs/crtqa-console-ci.md).

## Playbook normative source

Pipeline stages follow [`.cursor/pipelines/`](../../.cursor/pipelines/) (`EPIC-PREP:`, `COVERAGE:`, `GROUND:`, `ANALYSE:`). CI runs a **subset** without human coverage review or DISCOVER/PREP/CLOSE — see [decisions.md](decisions.md).

## v1 non-goals

- TEST-DISCOVER, TEST-PREP, CLOSE
- `COVERAGE fix_breadth=yes` loop after ANALYSE
- Human `coverage_frozen_at` / `scenario_groups[]` gate
- Jira REST file attachment
- Stash repo visibility for operators without AI project access
