# Pipeline steps — Corner Epic QA

Twelve TeamCity build steps map to scripts under [`automation/tools/teamcity/`](../tools/teamcity/).

| # | Step name (suggested) | Script | Verifier / notes |
|---|------------------------|--------|------------------|
| 1 | Verify harness checkout | [`verify-checkout.sh`](../tools/teamcity/verify-checkout.sh) | Asserts `AGENTS.md`, `automation/tools`, `epics/` |
| 2 | EPIC-PREP agent | [`epic-prep-agent.sh`](../tools/teamcity/epic-prep-agent.sh) | Cursor SDK; prompt `EPIC-PREP: {EPIC} strict_topology=yes strict_principal=yes` |
| 3 | EPIC-PREP verify | [`epic-prep-verify.sh`](../tools/teamcity/epic-prep-verify.sh) | `epic_prep_verify.py` — **`|| exit 1`** |
| 4 | COVERAGE agent | [`coverage-agent.sh`](../tools/teamcity/coverage-agent.sh) | Cursor SDK; `COVERAGE: {EPIC}` |
| 5 | COVERAGE verify | [`coverage-verify.sh`](../tools/teamcity/coverage-verify.sh) | `coverage_verify.py --mode draft_truth` — **`|| exit 1`** |
| 6 | Console gate | [`console-gate-wrapper.sh`](../tools/teamcity/console-gate-wrapper.sh) | Sources [`crtqa-openssh-env.sh`](../tools/teamcity/crtqa-openssh-env.sh); `crtqa_console_probe.py` |
| 7 | GROUND agent | [`ground-agent.sh`](../tools/teamcity/ground-agent.sh) | **Must source CRTQA env** (same as step 6) before agent |
| 8 | GROUND verify | [`ground-verify.sh`](../tools/teamcity/ground-verify.sh) | `ground_verify.py --mode emit` — **`|| exit 1`** |
| 9 | ANALYSE agent | [`analyse-agent.sh`](../tools/teamcity/analyse-agent.sh) | Cursor SDK; `ANALYSE: {EPIC}` |
| 10 | ANALYSE verify | [`analyse-verify.sh`](../tools/teamcity/analyse-verify.sh) | `analysis_verify.py --mode draft_truth` — **`|| exit 1`** |
| 11 | Jira success comment | [`jira-success.sh`](../tools/teamcity/jira-success.sh) | [`jira_success.py`](../tools/teamcity/jira_success.py) |
| 12 | Jira failure comment | [`jira-failure.sh`](../tools/teamcity/jira-failure.sh) | **Execution condition:** `not(success())` only |

## Environment per step

| Steps | Required env / params |
|-------|------------------------|
| 2–5, 9–10 | `EPIC_KEY`, `CURSOR_API_KEY` |
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
