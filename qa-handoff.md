# QA handoff — Corner Trader workspace

Last updated: 2026-07-27 (D17 consolidation).

## Current focus

**Push to Stash `team`:** fail-hard Atlassian auth (separate Confluence/Bitbucket PATs) + checklist semantic gates SD1–SD6 + `--ci-strict` + jira_success snippet gate (D17).

## Resume

- Branch `_stash-team-merge` → push `stash _stash-team-merge:team`
- After push: add TeamCity `CONFLUENCE_API_TOKEN` / `BITBUCKET_API_TOKEN` + env wiring; re-run CRT-635

## Next

1. Operator: TC password params + `env.*` for Confluence/Bitbucket
2. Re-run Pipeline for CRT-635; expect field-level coverage.md
3. Optional calibrate gold from successful CI artefacts

## Pointers

- D17: [automation/CI/decisions.md](automation/CI/decisions.md)
- Research: [automation/temp/ci-quality-research-crt635.md](automation/temp/ci-quality-research-crt635.md) (local scratch)
- Fixtures: `crt635-skeleton-bad-*` / `crt635-target-good-*`
