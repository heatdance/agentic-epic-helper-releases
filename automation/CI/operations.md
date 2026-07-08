# Operations — Corner Epic QA CI

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

## Stash push workflow

After local harness changes on `team`:

```bash
git push stash refs/heads/team:refs/heads/team
```

Requires SSH key authorized on Stash. GitHub `team` remote is a separate mirror — dxCity VCS uses **Stash**.
