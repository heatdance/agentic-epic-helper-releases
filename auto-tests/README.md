# auto-tests — delivery smoke automation

Executable **pytest** + **Playwright** smoke tests for Corner Trader deliveries. This tree is **not** [automation/](../automation/) (harness verifiers, epic pipeline tools, CTQA probes).

## Layout

| Path | Role |
|------|------|
| [docs/](docs/) | Private pedagogy, env runbooks, teaching notes (not published to team) |
| [specs/](specs/) | Smoke manifest, env profiles, orchestration schema (see specs README) |
| [tests/](tests/) | Test implementation (team-publishable when ready) |
| [tmp/](tmp/) | Ephemeral reports, traces, local scratch (gitignored) |

## Session

- **`/teach`** — teach-first agent mode; loads contract and context.
- **`/teach stop`** — end teach mode.
- Session state: [`.teacher-session.example.json`](.teacher-session.example.json) (live file gitignored).

## Contract

Normative charter: [docs/auto-tests-contract.json](../docs/auto-tests-contract.json).

## Separation from epic harness

| Area | Location |
|------|----------|
| Manual E2E drafts, Smart Checklist, pipelines | `epics/<KEY>/`, `TEST-PREP:` |
| Smoke automation code + runbooks | `auto-tests/` |

Specs: [specs/schema.json](specs/schema.json) (norms) and [specs/smoke-manifest.json](specs/smoke-manifest.json) (32 tests from CRTQA-10247).
