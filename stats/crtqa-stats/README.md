# CRTQA stats (clean slate)

Command entrypoint: [`/crtqa-stats`](../../.cursor/commands/crtqa-stats.md).

## Modes

- `initial_assessment`: full baseline build for one Jira user.
- `incremental_update`: add only new done TCD tasks for that user.

## Cohort

- Epics: `project = CRT AND issuetype = Epic AND "test lead" = <user>`
- Tasks: `project = CRTQA AND issuetype = "Test Execution" AND summary ~ "Test Case Development" AND "Epic Link" = <CRT-KEY> AND statusCategory = Done`

## Reporting

- The report is always generated, including small samples (for example `1 assisted`, `1 manual`).
- Small samples are marked as weak evidence; they are not suppressed.
- Keep interpretation associative (not causal).

## Files

- `latest.md` - current readable report.
- `state/last-sync.json` - current cumulative state.
- `state/longitudinal.json` - per-run history.
- `temp/categories.json` - category taxonomy used for classification.
- `raw/*.jsonl` - run audit logs (gitignored).
