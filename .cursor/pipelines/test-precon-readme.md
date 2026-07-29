# Test precondition authoring (guide)

## Purpose

Document how to set up sessions, accounts, and data fixtures before executing regression draftsΓÇöclustered by bundle, with placeholders instead of live secrets.

## When to use

When coverage exists and discover (if used) is understood. Trigger with `TEST-PRECON:` in your harness.

## Inputs

- Coverage JSON; optional discover JSON
- Templates: `epics/templates/precon-ref.json`
- Depth ladder or drill rules you maintain privately

## Process steps

1. Derive case outlines from coverage bundles and excluded checks.
2. Author setup steps per cluster: console, dealer UI, retail UI, or other surfaces your epic touches.
3. Use command-pattern placeholders for repeated operations; drill critical paths if your ladder requires it.
4. Verify precon JSON and paired markdown before prep consumes them.

## Outputs

- `epics/<KEY>/<KEY>-precon.json`
- `epics/<KEY>/<KEY>-precon.md` when your process uses human-readable precon

## Build your own

Keep credentials out of JSON; reference operator-run gates in private playbooks. Add `precon_verify.py` with discover linkage if you enforce cross-artifact consistency.
