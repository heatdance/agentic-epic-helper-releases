# Requirement analysis (guide)

## Purpose

Identify gaps, contradictions, and exploration debt between coverage and what the team already knowsΓÇöbefore expensive discover/prep work.

## When to use

When coverage JSON exists. Trigger with a convention such as `ANALYSE:` in your private harness.

## Inputs

- `epics/<KEY>/<KEY>-coverage.json`
- Optional: known-issue policy flags your contract defines
- Template: `epics/templates/analysis-ref.json`

## Process steps

1. Compare coverage checks to requirement snippets and implementation hints you trust.
2. Record gaps with severity and disposition; suppress exploration only with explicit rationale.
3. Avoid mutating known-issue registries unless your operator opts in.
4. Verify gap objects against your analysis contract before emitting.

## Outputs

- `epics/<KEY>/<KEY>-analysis.json` (gaps-first structure)
- `epics/<KEY>/<KEY>-analysis.md` for human review when used

## Build your own

Add `analysis_verify.py` and link downstream discover/prep gates to `exploration_suppressed[]` or equivalent fields in your schema fork.
