# AGENTS.md (public guide)

Short map for coding agents working from this **guide-only** export.

## Defaults

- Treat every playbook path as **`*-readme.md`** under `.cursor/pipelines/` — full executable playbooks are not shipped here.
- Do **not** assume MCP servers, databases, or admin shells exist; the operator configures those in a private harness.
- Prefer **template JSON** under `epics/templates/` for structure; do not invent requirement text or issue keys in generation mode.

## Context routing

Start with [HOW-TO.md](HOW-TO.md) and the pipeline readme for the phase you are studying. Open only template JSON and docs needed for that phase — avoid loading the entire tree.

## Phase triggers (configure locally)

Wire your own router rules for names such as `EPIC-PREP:`, `COVERAGE:`, `ANALYSE:`, `TEST-DISCOVER:`, `TEST-PRECON:`, `TEST-PREP:`, and `CLOSE:` after copying templates. The public [pipeline-router.mdc](.cursor/rules/pipeline-router.mdc) lists phases for reading order only.

## Outputs

Each phase produces JSON (and often markdown) under `epics/<YOUR-EPIC-KEY>/` in a real workspace. This export shows **schemas**, not filled epics.

## Security

- No secrets in repo files.
- No employer-specific URLs or product names in public artefacts.
- Do not commit MCP connection examples with environment-specific server names in public forks.
