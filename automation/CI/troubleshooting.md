# Troubleshooting — Corner Epic QA CI

## Dispatch

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| No compatible agents | Agent pool / requirement mismatch | Assign Linux `dxAgent*`; remove OS-specific requirements |
| Build fails before script (404 artifact) | Dispatch depends on Pipeline or first run without state | Depend on **self** only; first run without dependency |
| `queued=1` but no Pipeline | Wrong `PIPELINE_BUILD_TYPE_ID` | Copy current id from Pipeline settings |
| `TeamCity queue FAILED: HTTP 401/403` | Bad `TC_REST_TOKEN` | Regenerate dxCity token with trigger scope |
| `SKIP … no CRT-* in summary` | CRTQA title lacks epic key | Fix summary to include `CRT-###` |
| Duplicate Pipelines | Multiple new comments or dedup disabled | Expected; use parallel=1; restore artifact dependency |

## Pipeline — checkout / agents

| Symptom | Fix |
|---------|-----|
| `Harness checkout OK` missing | VCS root / branch not `team`; Stash credentials on TeamCity |
| `jq not on PATH` | Install jq on dxAgent image (bootstrap cannot install without root) |
| `curl or wget required` | Install curl on dxAgent image |
| `uv install finished but uvx/uv still not on PATH` | Check `$HOME` writable; inspect step 1 bootstrap log |
| `JIRA_API_TOKEN empty` | Add password param on Pipeline **and** `env.JIRA_API_TOKEN=%JIRA_API_TOKEN%`; or ensure step references `%JIRA_API_TOKEN%` |
| Jira smoke HTTP 401/403 | Bearer PAT scope; same token as comment steps |
| Agent not Linux | Console gate requires OpenSSH on agent |
| Agent `finished` but verify «file not found» | Pre-patch bare SDK — upgrade `team` scripts; runner exit **3** if `--require` missing |
| `required output file(s) missing` (exit 3) | Agent did not write artefact — read agent log; increase `AGENT_MAX_WAIT_MINUTES` |
| `ERROR: contract violation: upstream step marker missing` | Upstream step failed or TeamCity executed steps out-of-order; inspect first failing step and `.teamcity-ci/state/*.ok` |

## Pipeline — verifiers false green

| Symptom | Fix |
|---------|-----|
| Log shows verifier errors but build Success | Add `\|\| exit 1` after `*_verify.py` in wrapper scripts |

## Console gate / GROUND

| Symptom | Fix |
|---------|-----|
| `CRTQA_SSH_PRIVATE_KEY_B64 empty` | Set B64 password param |
| `ERROR: contract violation: env CRTQA_SSH_HOST is required` | Add Pipeline param `CRTQA_SSH_HOST` and expose `env.CRTQA_SSH_HOST=%CRTQA_SSH_HOST%` |
| Invalid PEM / SSH fail | Re-encode key; single line B64 |
| Gate OK, GROUND fails `runtime_probes` | Ensure step 7 sources `crtqa-openssh-env.sh` |
| Spurious TeamCity `name` parameter | Remove `%TOKEN%` from script comments |
| `Corrupted MAC on input` | Set `CRTQA_SSH_EXTRA_OPTS` per [crtqa-console-ci.md](../docs/crtqa-console-ci.md) |

See [crtqa-console-ci.md](../docs/crtqa-console-ci.md) for full console table.

## Jira

| Symptom | Fix |
|---------|-----|
| `HTTP 401` on comment | Use Bearer PAT, not Basic |
| `HTTP 403` on attach | Expected — v1 comment-only |
| Success + failure comments on green build | Set step 11/12 **Execute step** per [teamcity-setup.md](teamcity-setup.md); push `jira-notify-guard` (`792f519`); step 12 logs `SKIP failure Jira comment` |
| Steps run after early failure | Enable **Stop build on failure** on Pipeline |
| Step 11/12 instant `exit 1`, no script output | Step must invoke `bash automation/tools/teamcity/jira-success.sh` / `jira-failure.sh` — not an empty custom script |
| `Jira preflight: … build_url=MISSING` | Push harness with D13 (`jira-env.sh`); optional `export TEAMCITY_BUILD_URL="%teamcity.build.url%"` in step script |
| `TEAMCITY_BUILD_URL required` | Same as above; [`read_teamcity_params.py`](../tools/teamcity/read_teamcity_params.py) reads `teamcity.build.url` from properties |
| `QA_TASK_KEY empty` | Add `env.QA_TASK_KEY=%QA_TASK_KEY%` on Pipeline; Dispatch must pass `QA_TASK_KEY` |
| Step 11/12: only `Jira preflight: … set`, then exit 1; no `comment status` | `jira-notify-guard.sh` used `return 1` when marker absent → `set -e` aborted before Python (D15) | Push fix on `team`; expect `Jira success comment on …` / `comment status: 201` |

## Pipeline — COVERAGE verify

| Symptom | Fix |
|---------|-----|
| `forbidden oracle token` in step 5 | Expected quality gate — agent put enum (e.g. `first_tier_quote`) in Smart Checklist markdown; download epic-work, fix `-coverage.md`, rerun COVERAGE agent or Pipeline (D14 addendum in step 4 prompt) |
| Agent OK, verify fail, epic-work present | Step 12 posts **partial** Jira comment listing which artefacts exist (D14) |

## Artifacts

| Symptom | Fix |
|---------|-----|
| Empty Artifacts tab | Refresh page; check log for `Publishing N files` |
| Partial epic-work on fail | Expected if fail late — use log + partial JSON; step 12 partial comment lists present files (D14) |

## Cursor agent

| Symptom | Fix |
|---------|-----|
| `CURSOR_API_KEY is empty` | Set password param on Pipeline |
| Agent status not `finished` | Read agent log; retry; check API quota |
| `agent wait exceeded N minutes` | Raise `AGENT_MAX_WAIT_MINUTES` (default 45) and build timeout (180 min) |
| MCP calls absent in agent log | Ensure step 1 green; runner uses inline MCP — look for `mcp_tool_started=0` WARN |
| `REQUIRE OK … STALE` | Reused agent checkout — file from prior build; run clean checkout or delete `epics/<KEY>/` |
| `finished in Ns (< …s typical minimum)` | Suspiciously fast agent — check `mcp_tool_started`, artefact size, step 3 verify |
| Strict verifier fail after artefacts exist | Expected — agent ran playbook; quality gate failed (topology/principal/draft_truth) |

## Stash

| Symptom | Fix |
|---------|-----|
| `Permission denied (publickey)` on push | Configure SSH key for Stash; GitHub `team` mirror does not feed dxCity VCS — see [rollout-learnings.md](rollout-learnings.md) |

## Reading agent step logs

Agent steps (2, 4, 7, 9) emit structured lines from [`run_pipeline_agent.py`](../tools/teamcity/run_pipeline_agent.py):

| Log line | Healthy signal | Red flag |
|----------|----------------|----------|
| `runner: mcp_cmd=… uvx` | MCP launcher resolved | empty / wrong path |
| `tool_call: jira_get_issue (running)` | MCP used | — |
| `run_stats: … mcp_tool_started=0` | — | No Atlassian MCP calls |
| `wall_seconds: …` | EPIC-PREP often **300+** | `< 300` + WARN typical minimum |
| `REQUIRE OK: … (N bytes, mtime=…)` | File created this step | **STALE** = reused checkout |
| `status: finished` + exit 0 | Agent + `--require` passed | Step 3 verify is still the quality gate |
| exit **3** | — | Missing required file |
| exit **2** | — | Not finished or timeout |

**Step 3+ verify** remains authoritative for schema/strict gates — agent exit 0 ≠ gold quality. See [operations.md](operations.md#green-build-vs-gold-quality).
