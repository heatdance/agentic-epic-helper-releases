# auto-tests/specs

Machine-readable smoke automation specs (team-publishable minimal set).

| File | Role |
|------|------|
| [schema.json](schema.json) | Norms, env profile shape (pending confirmation), teach track phases, phase-2 stubs, execution context |
| [smoke-manifest.json](smoke-manifest.json) | 32-row grid from Jira execution [CRTQA-10247](https://jira.in.devexperts.com/browse/CRTQA-10247) |

**Sync:** `jql` in manifest — `issue in testExecutionTests(CRTQA-10247)`. Re-sync after execution membership changes.

**CLEAN:** `schema.json` and `smoke-manifest.json` are **kept** on `team/team`; other files under `specs/` are not published. Private pedagogy stays in [../docs/](../docs/).

Do not duplicate epic JSON under `epics/`; link manual tests via `crtqa_key` and fill `automation_scope` in `/teach` phase 0.
