# Jira integration — Corner Epic QA CI

## Target issue

Comments post to **`QA_TASK_KEY`** (CRTQA task), **not** the CRT epic issue.

## Authentication

[`jira_success.py`](../tools/teamcity/jira_success.py) and [`jira_failure.py`](../tools/teamcity/jira_failure.py) use:

```
Authorization: Bearer {JIRA_API_TOKEN}
POST /rest/api/2/issue/{QA_TASK_KEY}/comment
```

Single PAT (`JIRA_API_TOKEN`) for comments and MCP — see [secrets-and-params.md](secrets-and-params.md).

## Success comment (step 11)

Posted when the build completed steps 1–10 successfully.

**TeamCity Execute step:** `Only if all previous steps were successful` (default).

**Custom script:** `bash automation/tools/teamcity/jira-success.sh`

`TEAMCITY_BUILD_URL` is resolved automatically from env, `teamcity.build.url` in TeamCity properties ([`jira-env.sh`](../tools/teamcity/jira-env.sh), D13). Optional belt: `export TEAMCITY_BUILD_URL="%teamcity.build.url%"` in the step script.

Preflight line in the build log (no secrets):

```
Jira preflight: epic=CRT-657 qa=CRTQA-10236 build_url=set token=set
```

Template (from `jira_success.py`):

```
Corner Epic QA: coverage for {EPIC_KEY} is ready.

Build: {TEAMCITY_BUILD_URL}

TeamCity artifacts: download epic-work from the build (contains `{EPIC}-coverage.md` and JSON).
```

After HTTP 201, [`jira-notify-guard.sh`](../tools/teamcity/jira-notify-guard.sh) writes `.teamcity-ci/jira-success.posted`.

## Failure comment (step 12)

Posted when the build **failed** before a success comment was posted.

**TeamCity Execute step:** `Even if some of the previous steps failed`.

**Custom script:** `bash automation/tools/teamcity/jira-failure.sh`

### dxCity UI limitation

The **Parameter-based Execution Condition** dialog (equals / contains / …) **cannot** express `not(success())`. Do **not** use that dialog for step 12.

| Mechanism | Purpose |
|-----------|---------|
| Execute step settings (11 vs 12) | Step 11 skipped when prior steps failed; step 12 can still run |
| [`jira-notify-guard.sh`](../tools/teamcity/jira-notify-guard.sh) | If step 11 posted success, step 12 **skips** failure comment (logs `SKIP failure Jira comment`; continue path returns **0** under `set -e` — D15) |

On a green build you may still see step 12 **start** in the log — but it should not post a failure comment after guard + `792f519`.

Template (from `jira_failure.py`) — **generic** (no epic-work on agent):

```
Corner Epic QA: pipeline failed for {EPIC_KEY}.

Build: {TEAMCITY_BUILD_URL}

Open the build log for the failing step. If the run got far enough, partial outputs may be in TeamCity artifacts epic-work.
```

**Partial** (when `epics/{EPIC}/` contains ref and/or coverage JSON — D14):

```
Corner Epic QA: pipeline failed for {EPIC_KEY} (partial outputs available).

Build: {TEAMCITY_BUILD_URL}

Partial artifacts in this build (download epic-work from TeamCity):
- {EPIC}-ref.json: yes/no
- {EPIC}-coverage.json: yes/no
…

If step 5 COVERAGE verify failed, check for forbidden oracle enum tokens in smart_checklist_markdown …
Rerun: Manual Pipeline with the same EPIC_KEY and QA_TASK_KEY …
```

See [teamcity-setup.md](teamcity-setup.md#step-11--12--jira-comments-mutually-exclusive).

## No API attachment (v1)

File attach via Jira REST returned **HTTP 403** with operator PAT (manual UI attach still works). v1 delivers files via **TeamCity artifacts only** — see [decisions.md](decisions.md) D3.

QA downloads `{EPIC}-coverage.md` and JSON from **`epic-work`** on the build page.

## COMMENT_ID

Dispatch passes `COMMENT_ID` for traceability. v1 Jira scripts do not reference it in comment body; optional future use for threading or dedup audit.

## Manual Pipeline test

Set `QA_TASK_KEY` and `EPIC_KEY` manually; `COMMENT_ID` may be empty. Jira steps still run when token is set; build URL is auto-resolved from TeamCity properties when not exported.
