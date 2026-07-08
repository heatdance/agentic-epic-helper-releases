# Operations — Corner Epic QA CI

## Operator onboarding (first-time / after MCP patch)

1. **Push harness** to Stash `team` (`git push stash refs/heads/team:refs/heads/team`) — dxCity VCS reads Stash, not GitHub mirror. If SSH blocked, see [rollout-learnings.md](rollout-learnings.md).
2. **Pipeline parameters** — [secrets-and-params.md](secrets-and-params.md): `env.JIRA_API_TOKEN`, `env.CURSOR_API_KEY`, `env.EPIC_KEY`, `env.QA_TASK_KEY`; timeout **180 min**; `AGENT_MAX_WAIT_MINUTES=45`.
3. **Pipeline settings** — [teamcity-setup.md](teamcity-setup.md): stop build on failure; step 11/12 Execute step matrix.
4. **Dispatch** — `DISPATCH_LOOKBACK_MINUTES=120`.
5. **Smoke run** — Manual Pipeline `EPIC_KEY=CRT-###`; step 1: bootstrap + Jira smoke; step 2: `mcp_tool_started>0`, `REQUIRE OK`; step 3: verify OK.
6. **End-to-end** — New `Agent: Coverage` on CRTQA → Run Dispatch → confirm `queued=1`.

Session incident history: [rollout-learnings.md](rollout-learnings.md).

## Green build vs gold quality

TeamCity **Success** means all steps exited 0 (including verifiers) and step 11 posted Jira success. It does **not** guarantee operator-gold EPIC-PREP/COVERAGE/ANALYSE.

| Signal | Action |
|--------|--------|
| Build green in &lt;15 min | Download `epic-work`; check file sizes and `mcp_tool_started` in step 2 log |
| `mcp_tool_started=0` | Treat as failed playbook execution — rerun after fixing MCP/env |
| Verify OK but thin coverage | Human review in IDE; optional `/epic-helper` or manual `COVERAGE:` |
| `REQUIRE OK … STALE` | Trigger clean checkout or delete `epics/<KEY>/` on agent before rerun |

## Normal flow

1. QA posts **`Agent: Coverage`** on CRTQA task (summary must contain `CRT-###`).
2. Dispatch runs (cron or manual) — queues Pipeline if comment is new.
3. Pipeline runs ~15–180 min depending on epic size and `AGENT_MAX_WAIT_MINUTES`.
4. On success: Jira comment + `epic-work` artifacts.
5. QA downloads coverage markdown/JSON from TeamCity; continues manual review in harness or Jira.

## Manual Run Dispatch

Same as cron: one poll pass. Processes **all** new matching comments in lookback window.

Use when:

- Testing after config change
- Catching up after schedule was disabled

## Manual Run Pipeline

Set parameters explicitly:

| Parameter | Example |
|-----------|---------|
| `EPIC_KEY` | `CRT-671` |
| `QA_TASK_KEY` | `CRTQA-10241` |
| `COMMENT_ID` | *(optional)* |

Does **not** update Dispatch dedup — safe for debugging one epic without affecting production dedup state.

## Rerun after failure

1. Fix root cause (secrets, harness, agent prompt, env).
2. Push harness fix to Stash **`team`** if needed.
3. **Run Pipeline** manually with same keys **or** post a **new** `Agent: Coverage` comment (new comment id → Dispatch queues again).

Re-running Dispatch without new comment will **not** re-queue — id already in `processed_comment_ids.txt`.

## Reset dedup (maintainer only)

To force Dispatch to re-process a comment id:

1. Download `dispatch-state/processed_comment_ids.txt` from last Dispatch artifact.
2. Remove line `CRTQA-xxxx#commentId`.
3. Upload / seed state on next Dispatch run **or** temporarily disable artifact merge and edit on agent (advanced).

Misuse causes duplicate Pipeline runs.

## Parallelism

Keep Pipeline **max parallel builds = 1** unless infra and harness proven safe for concurrent `epics/*` writes on shared checkout (default: one build per agent checkout — safe).

## Cron recommendation

```
0 0 7-17 * * ?
```

Hourly during business hours UTC. Adjust lookback (`DISPATCH_LOOKBACK_MINUTES`) ≥ cron interval to avoid gaps.

## Disable during maintenance

1. Pause Dispatch schedule.
2. Cancel queued Pipeline builds in TeamCity if needed.
3. Re-enable after verification.

## MCP patch rollout (operator checklist)

After merging agent bootstrap + runner scripts to **`team`**:

| Where | Action |
|-------|--------|
| **Pipeline** build timeout | **180 min** |
| **Pipeline** text param | `AGENT_MAX_WAIT_MINUTES` = **`45`** (raise if EPIC-PREP times out) |
| **Pipeline** password | `JIRA_API_TOKEN` — same PAT for comments + MCP (no extra Confluence/Bitbucket passwords) |
| **Dispatch** text param | `DISPATCH_LOOKBACK_MINUTES` = **`120`** |
| **dxAgent pool** | `jq`, `curl`, Python 3.10+, writable `$HOME`, outbound Jira/Confluence/Stash/Cursor/**astral.sh** |
| **Verify** | Manual Pipeline `EPIC_KEY=CRT-670` — step 1 smoke + step 2 creates `CRT-670-ref.json` before verify |

Steps 2–12 names unchanged; VCS picks up new scripts from Stash `team`.

## Jira notify patch (D13 — operator checklist)

After merging `jira-env.sh` + `teamcity.build.url` alias to **`team`**:

| Where | Action |
|-------|--------|
| **Pipeline** env | Add `env.QA_TASK_KEY=%QA_TASK_KEY%` if not already set |
| **Step 11** Custom script | `bash automation/tools/teamcity/jira-success.sh` (not empty inline) |
| **Step 12** Custom script | `bash automation/tools/teamcity/jira-failure.sh` |
| **Step 11** Execute step | Only if all previous steps were successful |
| **Step 12** Execute step | Even if some of the previous steps failed |
| **Smoke rerun** | Manual Pipeline: `EPIC_KEY=CRT-657`, `QA_TASK_KEY=CRTQA-10236` — expect step 11 `Jira preflight: … build_url=set`, `comment status: 201`, step 12 `SKIP failure Jira comment` |

See [decisions.md](decisions.md) D13 · [rollout-learnings.md](rollout-learnings.md) incident 11.

## Stash push workflow

After local harness changes on `team`:

```bash
git push stash refs/heads/team:refs/heads/team
```

Requires SSH key authorized on Stash. GitHub `team` remote is a separate mirror — dxCity VCS uses **Stash**.
