# Lesson 2 — Phase 0 spec (one manifest row)

**Goal:** Write machine-readable intent **before** any test code.

**Row:** `crtqa-1692-dxtf-authorization-log-in` in [../specs/smoke-manifest.json](../specs/smoke-manifest.json).

## Fields you filled

| Field | Purpose |
|-------|---------|
| `automation_scope` | What automation does vs skips (DB, logs, layout variants) |
| `narrow_oracle.statement` | One falsifiable UI check after login |
| `evidence_required` | `screenshot`, `playwright_trace` |

## Your oracle

Open **system actions (hamburger, top-right)** → username above **Log out** matches role `dxtf_bot` (compare to credentials overlay at runtime).

## Exercise (completed)

- [x] Draft `automation_scope` and `narrow_oracle.statement`
- [x] Pin env to `ct_qa` (not “environment of choice”)

## Rule

No `tests/smoke/test_crtqa_1692.py` until lesson 3 (fixtures) exit criteria pass.
