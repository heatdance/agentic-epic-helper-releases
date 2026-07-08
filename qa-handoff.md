# QA handoff — Corner Trader workspace

Last updated: 2026-03-08.

## Current focus

**Corner Epic QA CI (dxCity)** — documentation sync after MCP patch rollout session. Branch `team` @ `792f519` (GitHub `team` synced; Stash push blocked SSH).

## Corner Epic QA CI — state

| Area | Status |
|------|--------|
| Docs | `automation/CI/` synced — rollout-learnings, scripts-reference, D10–D12 |
| Code | MCP runner, bootstrap, param loader, agent logging, jira-notify-guard |
| Dispatch | Operator set `DISPATCH_LOOKBACK_MINUTES=120` |
| Pipeline CRT-670 | Green build reported; ~9 min — verify artefact quality manually |
| Stash VCS | **Blocked** — `Permission denied (publickey)` on `git push stash` |

## TeamCity operator TODO

- [ ] `env.JIRA_API_TOKEN`, `env.CURSOR_API_KEY`, `env.EPIC_KEY` on Pipeline
- [ ] Build timeout 180 min; `AGENT_MAX_WAIT_MINUTES=45`
- [ ] **Stop build on failure** on Pipeline
- [ ] Step 11: Execute **Only if all previous steps successful**
- [ ] Step 12: Execute **Even if some previous steps failed** (guard prevents duplicate Jira)
- [ ] Confirm Stash `team` revision matches GitHub after SSH fix

## Next steps

1. Push `team` to Stash so dxCity picks up doc + script commits.
2. Re-run Pipeline or Dispatch for CRT-670 / new CRTQA comment with full logging.
3. Optional: single `jira-notify.sh` TeamCity step; Dispatch `maxResults` bump.

## Pointers

- CI entry: [automation/CI/README.md](automation/CI/README.md)
- Session matrix: [automation/CI/rollout-learnings.md](automation/CI/rollout-learnings.md)
- Operator onboarding: [automation/CI/operations.md](automation/CI/operations.md)

## Blockers

- Stash SSH for `AI/agentic-feature-helper` push
- dxCity UI has no `not(success())` — rely on Execute step + `jira-notify-guard.sh` (D12)
