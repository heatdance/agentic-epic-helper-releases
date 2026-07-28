# Rollout learnings — Corner Epic QA CI (2026-03)

Session record: incidents during v1 dxCity rollout, patches on branch `team`, and documentation status. Normative operator steps: [operations.md](operations.md). ADRs: [decisions.md](decisions.md).

## Patch chronology (`team` branch)

| Commit | Summary |
|--------|---------|
| `2cd7379` | Initial `automation/CI/` documentation |
| `1dc8798` | MCP bootstrap + `run_pipeline_agent.py` + thin agent scripts |
| `749977d` | Self-install `uv`, `cursor-sdk`, MCP wheel cache on dxAgent |
| `3a730ae` | `read_teamcity_params.py` — password params into env |
| `3c2e643` | Verbose agent step logging (`tool_call`, `REQUIRE OK`, `run_stats`) |
| `792f519` | `jira-notify-guard.sh` — skip failure comment when success posted |
| *(D13)* | `jira-env.sh` + `teamcity.build.url` alias — Jira steps 11/12 self-resolve build URL |
| *(D14)* | COVERAGE CI addendum + partial failure Jira comment — verifier unchanged |
| *(D15)* | `jira-notify-guard.sh` return 0 on continue — `set -e` safe |

## Incident matrix

| # | Incident | Root cause | Patch | Doc status |
|---|----------|------------|-------|------------|
| 1 | Dispatch misses `Agent: Coverage` | `DISPATCH_LOOKBACK_MINUTES` too small vs hourly cron + queue delay | Operator: **120** | [dispatch.md](dispatch.md), [operations.md](operations.md) |
| 2 | EPIC-PREP `finished` without `*-ref.json` | Bare `Agent.prompt` — no MCP, no project rules | `1dc8798` — D9 | [decisions.md](decisions.md) D9, [pipeline-steps.md](pipeline-steps.md) |
| 3 | Step 1: `uvx not on PATH` | Expected pre-installed uv on dxAgent image | `749977d` — D10 | [secrets-and-params.md](secrets-and-params.md), [scripts-reference.md](scripts-reference.md) |
| 4 | Step 1: `JIRA_API_TOKEN empty` | Password param not in shell env for VCS scripts | `3a730ae` — D11 | [teamcity-setup.md](teamcity-setup.md) `env.JIRA_API_TOKEN` |
| 5 | Step 2 success unclear in log | Minimal runner output | `3c2e643` | [troubleshooting.md](troubleshooting.md#reading-agent-step-logs) |
| 6 | Success + failure Jira both posted | Step 12 always runs; dxCity UI has no `not(success())` expression field | `792f519` — D12 | [jira-integration.md](jira-integration.md), [teamcity-setup.md](teamcity-setup.md) |
| 7 | Steps 2–12 run after step 1 fails | TeamCity: no stop-on-failure | Operator TC setting | [teamcity-setup.md](teamcity-setup.md) |
| 8 | `git push stash` Permission denied | SSH key not on Stash | Infra / operator | [operations.md](operations.md) |
| 9 | Stale `epics/` on incremental checkout | Agent reuses work dir; old artefacts pass `--require` | `3c2e643` STALE warn | [troubleshooting.md](troubleshooting.md) |
| 10 | Fast green build (~9 min) suspicious | Agent stub + verifiers may still pass minimal shape | — | [operations.md](operations.md) «green ≠ gold» |
| 11 | Steps 11/12 fail after green QA (CRTQA-10236/10244) | `TEAMCITY_BUILD_URL` not in env; step script may be empty | D13 — `jira-env.sh`, properties alias | [teamcity-setup.md](teamcity-setup.md), [troubleshooting.md](troubleshooting.md) |
| 12 | COVERAGE verify fail after agent OK (CRTQA-10194/CRT-659) | Forbidden oracle enum in `smart_checklist_markdown` | D14 — prompt addendum + partial Jira fail comment | [troubleshooting.md](troubleshooting.md), [decisions.md](decisions.md) D14 |
| 13 | Steps 11/12 exit 1 after `Jira preflight: … set` (CRTQA-10028 / CRT-634) | Guard `return 1` under `set -e` before POST | D15 — guard continue returns 0 | [jira-integration.md](jira-integration.md), [troubleshooting.md](troubleshooting.md) |
| 14 | CRT-635 build 43 green stub checklist (`card is available` + `mcp_export_failed`) | Jira PAT reused for Confluence/Stash → 401; self-`deferral_accepted`; notify ignored quality | D17 — split PATs + smoke + `--ci-strict` + jira_success gate + SD semantic gates | [decisions.md](decisions.md) D17, [secrets-and-params.md](secrets-and-params.md) |
| 15 | Post-D17 checklist still thin paraphrase / empty `>` / CB `page_id_unresolved` | Harness defined coverage as restating requirements (1:1 paraphrase); CB keys lack cookie/browser page_id in CI | D18 — variation catalogue + inventory; confluence_search for page_id; variation_density metrics | [decisions.md](decisions.md) D18, [docs/variation-catalogue.json](../../docs/variation-catalogue.json) |
| 16 | Post-D18 build 46 still 9 field checks; empty `## Prerequisites`; one spec line copied as oracle onto 4 checks | Breadth threshold read the **declared** `parameter_inventory`, so a partial transcription lowered it; availability relabelled `parity` → `invariant` escaped the placement rule; oracle rule counted `>` lines, not distinct ones | D19 — inventory re-derived from `snippet_text`, `requirement_passes[]` fan-out evidence, `snippet_truncated`, per-check availability exemption, distinct labelled oracles | [decisions.md](decisions.md) D19 |
| 17 | Coverage semantic gates had no effect in CI since D17 | Step 5 ran **only** `coverage_verify --mode draft_truth`; stub wording, availability placement, variation oracles and `variation_density` live in `--mode obligations`. Build-43 stub fixture: `draft_truth` OK, `obligations` 20 failures | D19 — step 5 runs both modes and passes `--md` | [decisions.md](decisions.md) D19, [coverage-verify.sh](../tools/teamcity/coverage-verify.sh) |
| 18 | Step 11 always failed on green builds since D17 (CRT-661) | `jira_success.py` used `parents[2]`, which is `automation/` for a file in `automation/tools/teamcity/`, so the gate looked for `automation/epics/<KEY>/…`. Step 12 correctly skipped via the green-stop, so a green pipeline produced **no** Jira comment | `parents[3]` / `REPO_ROOT` env + `test_jira_success.py` | [troubleshooting.md](troubleshooting.md) |

## dxCity vs GitHub

- **Pipeline VCS:** Stash `AI/agentic-feature-helper` branch **`team`** (D8) — not GitHub `team` mirror.
- Pushes to `git push team team` update GitHub only until Stash SSH works.

## Open / deferred

| Item | Notes |
|------|-------|
| Stash SSH for maintainers | Blocker for dxCity picking up new commits |
| Single `jira-notify.sh` step | Optional — merge steps 11+12 when TC UI stays limited |
| `maxResults` in Dispatch JQL | Optional; not blocking v1 |
| Jira REST attach | D3 — PAT scope |
