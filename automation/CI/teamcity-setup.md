# TeamCity setup — Corner Epic QA

## Build configurations

| Name | ID | VCS | Agent |
|------|-----|-----|-------|
| Corner Epic QA Dispatch | `CornerTrader_QATooling_CornerEpicQaDispatch` | Optional (script can be pasted) or Stash `team` | Linux `dxAgent*` |
| Corner Epic QA Pipeline | `CornerTrader_QATooling_CornerEpicQaPipeline` | **Required** — Stash `AI/agentic-feature-helper` **`team`** | Linux `dxAgent*` |
| Corner Epic QA Console Gate | *(operator-defined)* | Optional Stash `team` | Linux `dxAgent*` |

Place both under **QA Tooling** project on dxCity (`https://dxcity.in.devexperts.com`).

## Pipeline settings

| Setting | Recommended value |
|---------|-------------------|
| Build timeout | **180 minutes** |
| Max parallel builds | **1** (queue multiple epics sequentially) |
| Artifact paths | `epics/%EPIC_KEY% => epic-work` |
| Publish artifacts | **Even if build fails** |
| Agent requirement | Linux (OpenSSH console gate) |
| **Failure conditions** | **Stop build on failure** (must stop downstream steps on first failing step, except step 12 notify path) |

Without stop-on-failure, failed steps can still trigger downstream chain execution — confusing logs and wasted agent time.

## Dispatch settings

| Setting | Recommended value |
|---------|-------------------|
| Schedule trigger | `0 0 7-17 * * ?` (hourly 07:00–17:00 UTC) |
| `DISPATCH_LOOKBACK_MINUTES` | **`120`** |
| VCS trigger | **Off** — «Trigger only if there are pending changes» disabled |
| Build step | Command Line — [`dispatch/poll-and-queue.sh`](dispatch/poll-and-queue.sh) |
| Artifact publish | `dispatch-state => dispatch-state` (via service message in script) |

### Dispatch artifact dependency (after first green run)

- **Depend on:** same build config (`CornerEpicQaDispatch`)
- **From:** Latest successful build
- **Rule:** `dispatch-state/** => dispatch-state.in`

First run: dependency may 404 if no prior successful build — run once without dependency, then add dependency.

**Do not** depend on Pipeline artifacts for dispatch state.

## VCS root (Pipeline)

- Repository: Stash `AI/agentic-feature-helper`
- Branch: **`team`**
- Checkout directory: agent default (harness root = `AGENTS.md` at `$PWD`)

Step 1 [`verify-checkout.sh`](../tools/teamcity/verify-checkout.sh) asserts tree layout.

## Parameters summary

See [secrets-and-params.md](secrets-and-params.md) for full list.

**Dispatch:** `JIRA_API_TOKEN`, `PIPELINE_BUILD_TYPE_ID`, `DISPATCH_LOOKBACK_MINUTES`, `TRIGGER_PHRASE`, `TC_REST_TOKEN`, optional `TC_SERVER_URL`.

**Pipeline:** `EPIC_KEY`, `QA_TASK_KEY`, `COMMENT_ID`, `CURSOR_API_KEY`, `JIRA_API_TOKEN`, `AGENT_MAX_WAIT_MINUTES`, CRTQA OpenSSH params, plus TeamCity built-in `teamcity.build.url` (auto-resolved to `TEAMCITY_BUILD_URL` by [`jira-env.sh`](../tools/teamcity/jira-env.sh) — see D13).

### Expose secrets to all steps (required for MCP patch)

dxCity may not inject **password** configuration parameters into the environment of VCS-hosted scripts unless they are also exposed as environment variables.

**Recommended (one-time, build configuration):** Parameters → Add → **Environment variable**:

| Name | Value |
|------|-------|
| `env.JIRA_API_TOKEN` | `%JIRA_API_TOKEN%` |
| `env.CURSOR_API_KEY` | `%CURSOR_API_KEY%` |
| `env.EPIC_KEY` | `%EPIC_KEY%` |
| `env.QA_TASK_KEY` | `%QA_TASK_KEY%` |
| `env.CRTQA_SSH_HOST` | `%CRTQA_SSH_HOST%` |
| `env.CORNER_CI_STEP` | *(empty — set at runtime by step scripts via `setParameter`)* |

Keep the underlying **password** parameters (`JIRA_API_TOKEN`, `CURSOR_API_KEY`, …) as today.

Scripts also call [`read_teamcity_params.py`](../tools/teamcity/read_teamcity_params.py) to read `TEAMCITY_BUILD_PROPERTIES_FILE` when env is still empty — belt and suspenders. **`TEAMCITY_BUILD_URL`** is resolved from `teamcity.build.url` in that file when not in env (D13).

### Overview status (EPIC + failed step)

Pipeline steps 1–10 call [`corner-tc-overview.sh`](../tools/teamcity/corner-tc-overview.sh) `corner_tc_step_begin` (records step name in `CORNER_CI_STEP`). Steps 11/12 set TeamCity **Status** text:

| Outcome | Example Status column |
|---------|------------------------|
| Green | `CRT-671 - Success` |
| Red | `CRT-671 - failed at COVERAGE verify` |

Optional (UI only): **General Settings → Build number format** `%EPIC_KEY% #%build.counter%` — epic also visible in Build # column.

### Script-level step contracts (defense in depth)

Pipeline wrappers enforce upstream dependencies via `.teamcity-ci/state/*.ok` markers:

- Shared checks: [`corner-tc-preflight.sh`](../tools/teamcity/corner-tc-preflight.sh)
- Marker state: [`corner-tc-state.sh`](../tools/teamcity/corner-tc-state.sh)
- If TeamCity UI settings drift, downstream steps fail fast with `ERROR: contract violation: ...`.

## Step 11 / 12 — Jira comments (mutually exclusive)

dxCity **Parameter-based Execution Condition** (equals / contains) **cannot** express `not(success())`. Use **Execute step** + script guard instead.

| Step | Execute step setting | Custom script (Command Line) | Script behaviour |
|------|----------------------|------------------------------|------------------|
| **11** JIRA success | **Only if all previous steps were successful** | `bash automation/tools/teamcity/jira-success.sh` | Posts success; writes `.teamcity-ci/jira-success.posted` |
| **12** JIRA fail | **Even if some of the previous steps failed** | `bash automation/tools/teamcity/jira-failure.sh` | Skips comment if success marker exists ([`jira-notify-guard.sh`](../tools/teamcity/jira-notify-guard.sh)) |

On a green build, step 12 may still **appear** in the log but should log `SKIP failure Jira comment` — not `comment status: 201` for failure.

Details: [jira-integration.md](jira-integration.md) · ADR [decisions.md](decisions.md) D12 · build URL self-resolve D13.

## Stash access

Operators need read access to `AI/agentic-feature-helper`. Repo visibility is an infra ticket if missing — not fixable in harness docs alone.

Push workflow and SSH blockers: [operations.md](operations.md).
