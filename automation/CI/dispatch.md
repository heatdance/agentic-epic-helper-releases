# Dispatch — Jira poll and Pipeline queue

Reference script: [`dispatch/poll-and-queue.sh`](dispatch/poll-and-queue.sh).

## Behaviour

Each Dispatch run:

1. Merges prior `processed_comment_ids.txt` from artifact dependency (`dispatch-state.in/`).
2. Searches Jira **CRTQA** issues updated in the lookback window.
3. For each issue, loads comments containing the trigger phrase.
4. Skips comments already in `processed` set (`CRTQA-xxxx#commentId`).
5. Parses **`CRT-\d+`** from issue **summary** — skips tasks without epic token.
6. POSTs to TeamCity **`/app/rest/buildQueue`** with `EPIC_KEY`, `QA_TASK_KEY`, `COMMENT_ID`.
7. Appends new ids to `processed_comment_ids.txt` and publishes `dispatch-state` artifact.

## JQL

```
project = CRTQA AND updated >= -{LOOKBACK}m ORDER BY updated DESC
```

`LOOKBACK` comes from parameter `DISPATCH_LOOKBACK_MINUTES` (e.g. `60` for hourly cron with margin).

## Parameters

| Parameter | Type | Example |
|-----------|------|---------|
| `JIRA_API_TOKEN` | password | Bearer PAT |
| `PIPELINE_BUILD_TYPE_ID` | text | `CornerTrader_QATooling_CornerEpicQaPipeline` |
| `DISPATCH_LOOKBACK_MINUTES` | text | `60` |
| `TRIGGER_PHRASE` | text | `Agent: Coverage` |
| `TC_REST_TOKEN` | password | dxCity personal access token (trigger build) |
| `TC_SERVER_URL` | text | `https://dxcity.in.devexperts.com` (optional default) |

**Critical:** `PIPELINE_BUILD_TYPE_ID` must match Pipeline config after project moves (old id `CornerTrader_CornerEpicQaPipeline` will queue nothing useful).

## TeamCity REST queue

Uses XML body to `/app/rest/buildQueue` with Bearer `TC_REST_TOKEN`. **`##teamcity[runBuild ...]`** service messages were unreliable in v1 — REST is canonical.

## Dedup format

One line per processed comment:

```
CRTQA-10241#4466772
```

Reset dedup (emergency re-run): clear artifact state or edit `processed_comment_ids.txt` on a maintainer run — **will re-queue** all matching comments in lookback window.

## Manual Run vs cron

| Action | Effect |
|--------|--------|
| **Run Dispatch** | Same script as schedule — processes all **new** comments in lookback |
| **Run Pipeline** | Single epic with manual params — **bypasses** Dispatch dedup |

## Multi-comment burst

Two new comments on two CRTQA tasks → Dispatch queues **two** Pipeline builds. With **1 parallel build**, second waits in queue.

## Python constraints in TeamCity

Do **not** use `%` in inline Python (e.g. `strftime`) — TeamCity treats `%X` as parameter references. Timestamp parsing uses `datetime.fromisoformat` on first 19 chars of Jira `created`.

## Log lines to expect

```
QUEUE pipeline CornerTrader_QATooling_CornerEpicQaPipeline for CRTQA-10241#4466772 epic=CRT-671
TeamCity queued: HTTP 200
Dispatch done, queued=1
```

If `queued=0`: no new matching comments, or all already processed, or epic not in summary.
