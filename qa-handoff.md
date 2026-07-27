# QA handoff — Corner Trader workspace

Last updated: 2026-07-27.

## Current focus

**Corner Epic QA CI (dxCity)** — cherry-pick harness v7 (atomic coverage draft + `dependencies/` layout) onto Stash `team` for CI pickup.

**Coverage draft quality (2026-07-27):** Atomic field-level obligations in EPIC-PREP (`assertion_fragment`, `emit_subsection`); COVERAGE 1:1 obligation→check; collapsed Smart Checklist emit (no `## Primary focus` in paste); pre-CLOSE JSON under `epics/<KEY>/dependencies/`, human paste `epics/<KEY>/<KEY>-coverage.md` only. epic-helper **v7** — [docs/epic-artifact-layout.json](docs/epic-artifact-layout.json).

## Corner Epic QA CI — state

| Area | Status |
|------|--------|
| Docs | `automation/CI/` synced — rollout-learnings, scripts-reference, D10–D12 |
| Code | MCP runner, bootstrap, param loader, agent logging, jira-notify-guard |
| Dispatch | Operator set `DISPATCH_LOOKBACK_MINUTES=120` |
| Pipeline CRT-670 | Green build reported; ~9 min — verify artefact quality manually |
| Stash VCS | Push in progress — `personal:team` non-fast-forward; cherry-pick onto `stash/team` |

## TeamCity operator TODO

- [ ] `env.JIRA_API_TOKEN`, `env.CURSOR_API_KEY`, `env.EPIC_KEY` on Pipeline
- [ ] Build timeout 180 min; `AGENT_MAX_WAIT_MINUTES=45`
- [ ] **Stop build on failure** on Pipeline
- [ ] Step 11: Execute **Only if all previous steps successful**
- [ ] Step 12: Execute **Even if some previous steps failed** (guard prevents duplicate Jira)
- [ ] Confirm Stash `team` revision matches harness v7 after push

## Next steps

1. Finish cherry-pick; push `_stash-team-merge:team` to Stash.
2. Re-run Pipeline or Dispatch for CRT-670 / new CRTQA comment with full logging.
3. Optional: single `jira-notify.sh` TeamCity step; Dispatch `maxResults` bump.

## Pointers

- CI entry: [automation/CI/README.md](automation/CI/README.md)
- Session matrix: [automation/CI/rollout-learnings.md](automation/CI/rollout-learnings.md)
- Operator onboarding: [automation/CI/operations.md](automation/CI/operations.md)
- Epic layout: [docs/epic-artifact-layout.json](docs/epic-artifact-layout.json)

## Blockers

- Stash `team` diverged from `personal` — merge via cherry-pick, not force-push
- dxCity UI has no `not(success())` — rely on Execute step + `jira-notify-guard.sh` (D12)
