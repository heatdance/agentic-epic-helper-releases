# Coverage (guide)

## Purpose

Translate the epic ref into a verification checklist: what must be true, how obligations map to checks, and what ΓÇ£doneΓÇ¥ means for coverage before analysis and test design.

## When to use

When `epics/<KEY>/<KEY>-ref.json` exists with proposed obligations. Trigger in your harness with a convention such as `COVERAGE:`.

## Inputs

- Epic ref JSON (obligations proposed)
- Template: `epics/templates/coverage-ref.json`
- Optional focus text from the operator (scope narrowing)

## Process steps

1. Load ref and reconcile obligation ids with your coverage contract.
2. Draft checklist sections and matrix rows that trace back to requirementsΓÇönot generic QA boilerplate.
3. Populate `obligations_coverage` so every in-scope obligation is owned or explicitly deferred.
4. Verify JSON against your template before sharing with the team.

## Outputs

- `epics/<KEY>/<KEY>-coverage.json` (machine checklist)
- `epics/<KEY>/<KEY>-coverage.md` (human-facing smart-checklist shape) when your process uses paired markdown

## Build your own

Maintain [docs/clean-public-style.md](../../docs/clean-public-style.md) norms in your private repo; add `coverage_verify.py` and router wiring. Coverage is the compliance-oriented layerΓÇökeep client-facing test taxonomy separate if your organization distinguishes them.
