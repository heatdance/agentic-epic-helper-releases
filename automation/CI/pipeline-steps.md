# Pipeline steps — Corner Epic QA

Twelve TeamCity build steps map to scripts under [`automation/tools/teamcity/`](../tools/teamcity/).

| # | Step name (suggested) | Script | Verifier / notes |
|---|------------------------|--------|------------------|
| 1 | Verify harness checkout | [`verify-checkout.sh`](../tools/teamcity/verify-checkout.sh) | Harness tree + **`jq`** + **`uvx`** + writes gitignored `.cursor/mcp.json` + Jira smoke |
| 2 | EPIC-PREP agent | [`epic-prep-agent.sh`](../tools/teamcity/epic-prep-agent.sh) | [`run_pipeline_agent.py`](../tools/teamcity/run_pipeline_agent.py); MCP + project rules; requires `-ref.json` |
| 3 | EPIC-PREP verify | [`epic-prep-verify.sh`](../tools/teamcity/epic-prep-verify.sh) | `epic_prep_verify.py` — **`|| exit 1`** |
| 4 | COVERAGE agent | [`coverage-agent.sh`](../tools/teamcity/coverage-agent.sh) | Runner; `strict_topology=yes strict_principal=yes`; requires ref + coverage JSON/MD |
| 5 | COVERAGE verify | [`coverage-verify.sh`](../tools/teamcity/coverage-verify.sh) | `coverage_verify.py --mode draft_truth` — **`|| exit 1`** |
| 6 | Console gate | [`console-gate-wrapper.sh`](../tools/teamcity/console-gate-wrapper.sh) | Sources [`crtqa-openssh-env.sh`](../tools/teamcity/crtqa-openssh-env.sh); `crtqa_console_probe.py` |
| 7 | GROUND agent | [`ground-agent.sh`](../tools/teamcity/ground-agent.sh) | CRTQA OpenSSH env + runner; CI addendum (Phase 0 done; no desktop multiplex) |
| 8 | GROUND verify | [`ground-verify.sh`](../tools/teamcity/ground-verify.sh) | `ground_verify.py --mode emit` — **`|| exit 1`** |
| 9 | ANALYSE agent | [`analyse-agent.sh`](../tools/teamcity/analyse-agent.sh) | Runner; `strict_topology=yes strict_principal=yes`; requires analysis JSON/MD |
| 10 | ANALYSE verify | [`analyse-verify.sh`](../tools/teamcity/analyse-verify.sh) | `analysis_verify.py --mode draft_truth` — **`|| exit 1`** |
| 11 | Jira success comment | [`jira-success.sh`](../tools/teamcity/jira-success.sh) | [`jira_success.py`](../tools/teamcity/jira_success.py) |
| 12 | Jira failure comment | [`jira-failure.sh`](../tools/teamcity/jira-failure.sh) | Execute: **Even if failed**; [`jira-notify-guard.sh`](../tools/teamcity/jira-notify-guard.sh) skips if step 11 posted — see [jira-integration.md](jira-integration.md) |

## Step 1 — agent bootstrap

[`verify-checkout.sh`](../tools/teamcity/verify-checkout.sh) (same TeamCity step name as v1):

1. Existing harness checks (`AGENTS.md`, verifiers, `epics/`, `.cursor/rules`, `.cursor/pipelines`).
2. `command -v jq` (must exist on agent image).
3. [`bootstrap-agent-env.sh`](../tools/teamcity/bootstrap-agent-env.sh) — **self-healing** on dxAgent:
   - installs `uv`/`uvx` to `$HOME/.local/bin` via astral installer if missing;
   - `pip install --user cursor-sdk`;
   - warms MCP wheel cache (`mcp-atlassian-with-bitbucket`);
   - writes `.teamcity-ci/bootstrap.env` for later steps (each step is a fresh shell).
4. [`write-mcp-config.py`](../tools/teamcity/write-mcp-config.py) — gitignored `.cursor/mcp.json` from **`JIRA_API_TOKEN`**.
5. [`mcp-smoke.sh`](../tools/teamcity/mcp-smoke.sh) — Jira REST smoke on `EPIC_KEY`.

## Agent runner (steps 2, 4, 7, 9)

All `*-agent.sh` scripts call [`run_pipeline_agent.py`](../tools/teamcity/run_pipeline_agent.py):

| Feature | Behavior |
|---------|----------|
| MCP | Inline `StdioMcpServerConfig` for `user-mcp-atlassian` (same env as step 1) |
| Project rules | `setting_sources=["project"]` — loads `.cursor/rules/` (pipeline-router) |
| Timeout | `AGENT_MAX_WAIT_MINUTES` (default 45) |
| Post-check | `--require` paths with `%EPIC_KEY%` expansion |
| Exit codes | **1** SDK error · **2** status ≠ `finished` or timeout · **3** missing required files |

`Agent.prompt` without MCP/project settings produced `status: finished` with **no** `epics/<KEY>/` artefacts — runner closes that gap. TeamCity step logs also emit `tool_call`, `REQUIRE OK` (size/mtime), `token_usage`, `run_stats`, and WARN on zero MCP calls / fast finish / stale files.

## Environment per step

| Steps | Required env / params |
|-------|------------------------|
| 1 | `JIRA_API_TOKEN`; `EPIC_KEY` for smoke (optional on manual checkout-only) |
| 2–5, 9–10 | `EPIC_KEY`, `CURSOR_API_KEY`, `JIRA_API_TOKEN`, `AGENT_MAX_WAIT_MINUTES` (optional) |
| 6–8 | `CRTQA_SSH_USER`, `CRTQA_SSH_PRIVATE_KEY_B64`, `CRTQA_SUDO_PASSWORD`, `CRTQA_CONSOLE_TRANSPORT=openssh` |
| 11–12 | `EPIC_KEY`, `QA_TASK_KEY`, `JIRA_API_TOKEN`, `TEAMCITY_BUILD_URL` |

TeamCity injects `%EPIC_KEY%`, `%QA_TASK_KEY%`, etc. Export `TEAMCITY_BUILD_URL` from `%teamcity.build.url%` in the Jira steps.

## Verify exit codes

Verify wrappers must fail the build when Python verifier exits non-zero:

```bash
python3 automation/tools/epic_prep_verify.py --epic "$EPIC" || exit 1
```

Printing «OK» after a failing verifier caused false-green builds in early rollout.

## Epic workspace

Agents write under `epics/%EPIC_KEY%/` at repo root. Artifact rule publishes that folder as **`epic-work`**.

Typical green-run files (count may vary):

- `{EPIC}-ref.json`
- `{EPIC}-coverage.json` + `{EPIC}-coverage.md`
- `{EPIC}-analysis.json` + `{EPIC}-analysis.md`

## Playbook references

Normative step semantics remain in:

- [`.cursor/pipelines/epic-prep.md`](../../.cursor/pipelines/epic-prep.md)
- [`.cursor/pipelines/coverage.md`](../../.cursor/pipelines/coverage.md)
- [`.cursor/pipelines/ground.md`](../../.cursor/pipelines/ground.md)
- [`.cursor/pipelines/analysis.md`](../../.cursor/pipelines/analysis.md)

CI does not replace those playbooks — it automates a bounded subset.
