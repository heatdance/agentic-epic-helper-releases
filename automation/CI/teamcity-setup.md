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

## Dispatch settings

| Setting | Recommended value |
|---------|-------------------|
| Schedule trigger | `0 0 7-17 * * ?` (hourly 07:00–17:00 UTC) |
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

**Pipeline:** `EPIC_KEY`, `QA_TASK_KEY`, `COMMENT_ID`, `CURSOR_API_KEY`, `JIRA_API_TOKEN`, CRTQA OpenSSH params, plus TeamCity built-in `teamcity.build.url` (exposed as `TEAMCITY_BUILD_URL` in Jira steps).

### Expose secrets to all steps (required for MCP patch)

dxCity may not inject **password** configuration parameters into the environment of VCS-hosted scripts unless they are also exposed as environment variables.

**Recommended (one-time, build configuration):** Parameters → Add → **Environment variable**:

| Name | Value |
|------|-------|
| `env.JIRA_API_TOKEN` | `%JIRA_API_TOKEN%` |
| `env.CURSOR_API_KEY` | `%CURSOR_API_KEY%` |
| `env.EPIC_KEY` | `%EPIC_KEY%` |

Keep the underlying **password** parameters (`JIRA_API_TOKEN`, `CURSOR_API_KEY`, …) as today.

Scripts also call [`read_teamcity_params.py`](../tools/teamcity/read_teamcity_params.py) to read `TEAMCITY_BUILD_PROPERTIES_FILE` when env is still empty — belt and suspenders.

## Step 11 / 12 — Jira comments (mutually exclusive)

| Step | When it must run | TeamCity execution condition |
|------|------------------|------------------------------|
| **11** JIRA success | Green build only | *(default)* previous steps succeeded — or explicit `success()` |
| **12** JIRA fail | **Failed build only** | **`not(success())`** — **required** |

### Fix duplicate success + failure comments

If both steps run on a green build, step 12 has **no** execution condition in TeamCity.

**dxCity UI:** Pipeline → Build Steps → **Step 12** (JIRA fail) → **Execution conditions** → Add:

```
not(success())
```

Save. On the next green build, step 12 should show **Skipped** in the log.

Scripts also use [jira-notify-guard.sh](../tools/teamcity/jira-notify-guard.sh): if step 11 posted success, step 12 exits without commenting (belt when TC condition is missing).

## Step 12 execution condition (reference)

Failure Jira step must run **only on failed builds**:

```
not(success())
```

Without this, a green build also posts «pipeline failed».

## Stash access

Operators need read access to `AI/agentic-feature-helper`. Repo visibility is an infra ticket if missing — not fixable in harness docs alone.
