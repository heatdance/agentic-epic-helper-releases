# Framework decisions (operator + )

Captured 2026-05-26. Normative rules remain in [../specs/schema.json](../specs/schema.json).

## Session target

- **First smoke row:** [CRTQA-1692](https://jira.in.devexperts.com/browse/CRTQA-1692) — manifest id `crtqa-1692-dxtf-authorization-log-in`
- **Order:** structure and env before test implementation

## Decisions

| Topic | Choice |
|-------|--------|
| Test isolation | **Prefer isolation** — fresh browser context (or equivalent) per test; avoid shared logged-in session across tests |
| Locator strategy | **TBD** — decide when implementing dxTrade5 helpers (role/text-first default for Playwright) |
| Credentials | **Role-based overlay** — logical roles in gitignored `auto-tests/dependencies/credentials.local.json`; example in `credentials.local.example.json` |
| Evidence on failure | **Screenshot + Playwright trace** on failure; align manifest `evidence_required` when row is finalized in phase 0 |
| Learning order | **Env reachability first (A)**, then minimal pytest skeleton (B), then phase 0 spec, then first test |

## Teach-track gate (do not skip)

| Phase | Name | Exit before next |
|-------|------|------------------|
| 0 | spec | `automation_scope` + `narrow_oracle.statement` set on target manifest row |
| 1 | fixtures | pytest loads `ct_qa` env profile; wiring test only — no product oracle |
| 2 | oracle | One smoke module, one assert path, tied to manifest `id` |
| 3 | evidence | Required `evidence_paths` on pass; trace on failure per table above |

Agent must **not** implement `test_crtqa_1692.py` until phases **0 and 1** exit criteria are met unless operator clearly requests a full solution in chat.

**Operator builds phase 1 fixtures** per [lessons/lesson-03-phase-1-fixtures.md](lessons/lesson-03-phase-1-fixtures.md); agent reviews only unless full solution requested.
