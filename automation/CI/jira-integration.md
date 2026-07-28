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

## Comment shape (both steps)

Success and failure render through the same builder, [`jira_comment.py`](../tools/teamcity/jira_comment.py) `render_comment`, so a CRTQA ticket reads as one series instead of three layouts. Block order is fixed and every block is always present:

```
Corner Epic QA - {EPIC_KEY} - {ready|failed}

Build: {TEAMCITY_BUILD_URL}
Stage: {green through … | failed at … | failed after …}
Artifacts: epic-work
- {EPIC}-ref.json: yes|no
- {EPIC}-coverage.json: yes|no
- {EPIC}-coverage.md: yes|no
- {EPIC}-analysis.json: yes|no
- {EPIC}-analysis.md: yes|no
Coverage: mandated=27 emitted=27 checks=24 density=0.89 unmatched=3
Next: {one action}
Note: {conditional hint, may repeat}
```

| Block | Source |
|-------|--------|
| Header | `EPIC_KEY` + outcome; grep `Corner Epic QA - <KEY> -` to scan ticket history |
| `Stage` | `CORNER_CI_STEP` when the failing step set it, otherwise the highest-numbered `.teamcity-ci/state/NN-*.ok` marker |
| `Artifacts` | Presence per deliverable, checked in `dependencies/`, `context/`, then the epic root. Always listed — never dropped when files are missing; `Artifacts: none in this build` when the epic folder is absent |
| `Coverage` | `collect_variation_metrics` + `variation_density` recomputed from the ref and coverage JSON. Omitted when it cannot be computed — a notification step must not fail over a metric |
| `Next` | Single action: extend the checklist (ready) or open the log and rerun (failed) |

## Success comment (step 11)

Posted when the build completed steps 1–10 successfully.

**TeamCity Execute step:** `Only if all previous steps were successful` (default).

**Custom script:** `bash automation/tools/teamcity/jira-success.sh`

`TEAMCITY_BUILD_URL` is resolved automatically from env, `teamcity.build.url` in TeamCity properties ([`jira-env.sh`](../tools/teamcity/jira-env.sh), D13). Optional belt: `export TEAMCITY_BUILD_URL="%teamcity.build.url%"` in the step script.

Preflight line in the build log (no secrets):

```
Jira preflight: epic=CRT-657 qa=CRTQA-10236 build_url=set token=set
```

Status is `ready`, `Stage` reads `green through {last marker}`, and `Next` points the engineer at `epic-work` to extend `{EPIC}-coverage.md` on the ticket — the repo copy stays machine-generated. The gate still refuses to post when any requirement `snippet_status` is not `ok` (D17).

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

Status is `failed` and the layout is identical to the success comment — there is no longer a separate “generic” versus “partial” template. The artifact list shows what the run produced before it stopped, `Coverage:` appears when coverage JSON exists, and the oracle-token hint is appended as a `Note:` line rather than changing the shape.

See [teamcity-setup.md](teamcity-setup.md#step-11--12--jira-comments-mutually-exclusive).

## No API attachment (v1)

File attach via Jira REST returned **HTTP 403** with operator PAT (manual UI attach still works). v1 delivers files via **TeamCity artifacts only** — see [decisions.md](decisions.md) D3.

QA downloads `{EPIC}-coverage.md` and JSON from **`epic-work`** on the build page.

## COMMENT_ID

Dispatch passes `COMMENT_ID` for traceability. v1 Jira scripts do not reference it in comment body; optional future use for threading or dedup audit.

## Manual Pipeline test

Set `QA_TASK_KEY` and `EPIC_KEY` manually; `COMMENT_ID` may be empty. Jira steps still run when token is set; build URL is auto-resolved from TeamCity properties when not exported.
