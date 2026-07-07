# Jira integration — Corner Epic QA CI

## Target issue

Comments post to **`QA_TASK_KEY`** (CRTQA task), **not** the CRT epic issue.

## Authentication

[`jira_success.py`](../tools/teamcity/jira_success.py) and [`jira_failure.py`](../tools/teamcity/jira_failure.py) use:

```
Authorization: Bearer {JIRA_API_TOKEN}
POST /rest/api/2/issue/{QA_TASK_KEY}/comment
```

## Success comment (step 11)

Posted only on **successful** build. Requires `TEAMCITY_BUILD_URL` (from `%teamcity.build.url%`).

Template (from `jira_success.py`):

```
Corner Epic QA: coverage for {EPIC_KEY} is ready.

Build: {TEAMCITY_BUILD_URL}

TeamCity artifacts: download epic-work from the build (contains `{EPIC}-coverage.md` and JSON).
```

No «started» or progress comments in v1 — only final success or failure.

## Failure comment (step 12)

Posted when build **not successful** (`not(success())` execution condition).

Template (from `jira_failure.py`):

```
Corner Epic QA: pipeline failed for {EPIC_KEY}.

Build: {TEAMCITY_BUILD_URL}

Open the build log for the failing step. If the run got far enough, partial outputs may be in TeamCity artifacts epic-work.
```

## No API attachment (v1)

File attach via Jira REST returned **HTTP 403** with operator PAT (manual UI attach still works). v1 delivers files via **TeamCity artifacts only** — see [decisions.md](decisions.md).

QA downloads `{EPIC}-coverage.md` and JSON from **`epic-work`** on the build page.

## COMMENT_ID

Dispatch passes `COMMENT_ID` for traceability. v1 Jira scripts do not reference it in comment body; optional future use for threading or dedup audit.

## Manual Pipeline test

Set `QA_TASK_KEY` and `EPIC_KEY` manually; `COMMENT_ID` may be empty. Jira steps still run if token and build URL are set.
