# TeamCity scripts reference — Corner Epic QA

Executable wrappers under [`automation/tools/teamcity/`](../tools/teamcity/). Pipeline maps 12 TeamCity steps to these scripts — see [pipeline-steps.md](pipeline-steps.md).

## Bootstrap and shared (all agent steps)

| Script | Called from | Role |
|--------|-------------|------|
| [`verify-checkout.sh`](../tools/teamcity/verify-checkout.sh) | Step 1 | Harness tree + bootstrap + mcp.json + Jira smoke |
| [`corner-tc-overview.sh`](../tools/teamcity/corner-tc-overview.sh) | Steps 1–12 | `setParameter` + `buildStatus` — EPIC and human step in overview Status |
| [`bootstrap-agent-env.sh`](../tools/teamcity/bootstrap-agent-env.sh) | Step 1, agent steps | Install `uv`/`uvx`, `cursor-sdk`, MCP wheel cache; writes `.teamcity-ci/bootstrap.env` |
| [`load-teamcity-params.sh`](../tools/teamcity/load-teamcity-params.sh) | All steps needing secrets | Loads password params from `TEAMCITY_BUILD_PROPERTIES_FILE` when env empty |
| [`read_teamcity_params.py`](../tools/teamcity/read_teamcity_params.py) | Via load-teamcity-params | Emits safe shell exports for PAT/text params |
| [`write-mcp-config.py`](../tools/teamcity/write-mcp-config.py) | Step 1 | Writes gitignored `.cursor/mcp.json` (single `JIRA_API_TOKEN`) |
| [`mcp-smoke.sh`](../tools/teamcity/mcp-smoke.sh) | Step 1 | Jira REST `GET issue/{EPIC_KEY}` before agents |
| [`agent-env.sh`](../tools/teamcity/agent-env.sh) | Steps 2, 4, 7, 9 | `EPIC_KEY`, bootstrap marker, `AGENT_MAX_WAIT_MINUTES` |

## Agent runner (steps 2, 4, 7, 9)

| Script | Step | `--require` outputs |
|--------|------|---------------------|
| [`epic-prep-agent.sh`](../tools/teamcity/epic-prep-agent.sh) | 2 | `{EPIC}-ref.json` |
| [`coverage-agent.sh`](../tools/teamcity/coverage-agent.sh) | 4 | ref + coverage JSON/MD |
| [`ground-agent.sh`](../tools/teamcity/ground-agent.sh) | 7 | coverage JSON (mutated in place) |
| [`analyse-agent.sh`](../tools/teamcity/analyse-agent.sh) | 9 | analysis JSON/MD |
| [`run_pipeline_agent.py`](../tools/teamcity/run_pipeline_agent.py) | Via *-agent.sh | MCP inline + project rules; exit **1** SDK / **2** not finished / **3** missing files |

## Verifiers (steps 3, 5, 8, 10)

| Script | Python verifier |
|--------|-----------------|
| [`epic-prep-verify.sh`](../tools/teamcity/epic-prep-verify.sh) | `epic_prep_verify.py --strict-topology --strict-principal` |
| [`coverage-verify.sh`](../tools/teamcity/coverage-verify.sh) | `coverage_verify.py --mode draft_truth` |
| [`ground-verify.sh`](../tools/teamcity/ground-verify.sh) | `ground_verify.py --mode emit` |
| [`analyse-verify.sh`](../tools/teamcity/analyse-verify.sh) | `analysis_verify.py --mode draft_truth` |

## Console (steps 6–7)

| Script | Role |
|--------|------|
| [`crtqa-openssh-env.sh`](../tools/teamcity/crtqa-openssh-env.sh) | Decode B64 SSH key; export OpenSSH CRTQA env |
| [`console-gate-wrapper.sh`](../tools/teamcity/console-gate-wrapper.sh) | Step 6 — `crtqa_console_probe.py` |

## Jira (steps 11–12)

| Script | Python | Role |
|--------|--------|------|
| [`jira-env.sh`](../tools/teamcity/jira-env.sh) | [`read_teamcity_params.py`](../tools/teamcity/read_teamcity_params.py) | Load params, resolve `TEAMCITY_BUILD_URL`, preflight |
| [`jira-success.sh`](../tools/teamcity/jira-success.sh) | `jira_success.py` | Success comment on CRTQA |
| [`jira-failure.sh`](../tools/teamcity/jira-failure.sh) | `jira_failure.py` | Failure comment on CRTQA |
| [`jira-notify-guard.sh`](../tools/teamcity/jira-notify-guard.sh) | — | Marker `.teamcity-ci/jira-success.posted` — step 12 skips if step 11 posted |

## Ephemeral paths (build workspace, not committed)

| Path | Purpose |
|------|---------|
| `.teamcity-ci/bootstrap.env` | PATH, `UVX_BIN` for later steps |
| `.teamcity-ci/jira-success.posted` | Jira mutual-exclusion marker |
| `.cursor/mcp.json` | Generated MCP config (gitignored) |
| `epics/{EPIC}/` | Pipeline deliverables → `epic-work` artifact |

## Runner log fields (steps 2, 4, 7, 9)

See [troubleshooting.md](troubleshooting.md#reading-agent-step-logs).
