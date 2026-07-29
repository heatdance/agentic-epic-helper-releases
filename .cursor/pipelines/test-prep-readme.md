# Test preparation (guide)

## Purpose

Produce regression test **drafts**: bundled executable outlines that operationalize the coverage checklist for humans or test-management importΓÇönot one micro-test per bullet by default.

## When to use

When coverage obligations are stable and precon (recommended) defines session shape. Trigger with `TEST-PREP:` locally.

## Inputs

- Coverage JSON (required)
- Precon JSON (recommended)
- Discover JSON (optional gates)
- Template: `epics/templates/tests-ref.json`

## Process steps

1. Plan bundles and case outlines; respect excluded checks and gap references from analysis.
2. Expand outlines into action/result pairs under your `executable_outline` or teaching profile.
3. Merge bundle drafts; run your verifier in plan, draft, merge, and emit modes.
4. Keep generation mode free of auto-created test-issue keys unless your operator enables indexing.

## Outputs

- `epics/<KEY>/<KEY>-tests.json`
- `epics/<KEY>/<KEY>-tests.md` for human execution and manual import

## Build your own

Define TBD rules (session literals, oracles) in a private contract file; implement `test_prep_verify.py`. Import to your test tool remains a human or integration step outside this export.
