# Coverage reinforce (guide)

## Purpose

Second coverage pass after discovery: merge verification affordances, obligation-ledger hints, and operator feedback into an existing Smart Checklist without re-running greenfield coverage from ref-only inputs.

## When to use

When discover JSON exists and the first coverage pass is row-complete but affordance-thin. Trigger with `COVERAGE-REINFORCE:` in a private harness, or as an automatic stage in an orchestrator pattern.

## Inputs

- Pass-1 `-coverage.json` / `.md` (merge base)
- `-discover.json` slices: verification affordances, obligation ledger, fixture needs
- Optional operator feedback captured at a human review gate (markdown scratch, not secrets)

## Process steps

1. Load merge base and discover slices with JSON projection — do not paste full discover JSON unfiltered.
2. Add or deepen executable checklist lines tied to `obligation_ids[]`; fix thin widget-only rows when discover cites DB or history affordances.
3. Re-run obligation row-complete checks; bump `coverage_pass` or equivalent metadata field.
4. Regenerate coverage markdown; delete ephemeral scratch.

## Outputs

- Updated `-coverage.json` and `-coverage.md` (pass 2)

## Build your own

Wire a dedicated reinforce trigger after discover in your router. Keep operator feedback and affordance slices in gitignored scratch until archive. This export only shows the artefact shape and phase ordering.
