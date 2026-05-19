# Epic close (guide)

## Purpose

Documentation-only integrity pass after prep: verify artefact set, regenerate human summaries, and archive JSON under `context/` while keeping root markdown for operators.

## When to use

When the epic artefact chain is complete in your process and you want a formal handoff record. Trigger with `CLOSE:` in your private harness.

## Inputs

- Ref, coverage, discover, precon, and tests JSON at epic root (paths per your layout)
- Template: `epics/templates/close-ref.json`

## Process steps

1. Run an integrity ladder (schema presence, cross-references, forbidden secret patterns).
2. Regenerate the four human markdown views from JSON where your playbook defines that mapping.
3. Move durable JSON into `epics/<KEY>/context/`; retain markdown at epic root if that is your convention.
4. Record verdict and findings in close JSONΓÇöno live environment or browser execution required.

## Outputs

- `epics/<KEY>/context/<KEY>-close.json`
- Updated `*-coverage.md`, `*-analysis.md`, `*-precon.md`, `*-tests.md` at root when applicable

## Build your own

Implement `close_verify.py` and optional archive helper; keep close free of MCP unless you explicitly extend it in private docs.
