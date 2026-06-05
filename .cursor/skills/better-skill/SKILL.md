---
name: better-skill
description: Conversation-only coaching for Corner pipeline, command, and skill drafts. Use when the user invokes /better-skill or attaches a harness doc draft.
---

# Better skill (Corner)

## Mode

**Conversation only.** No file writes; do not run the draft pipeline.

## Steps

1. Load rubrics from [`docs/skill-authoring-patterns.json`](../../docs/skill-authoring-patterns.json).
2. Read the draft (playbook, command, or SKILL.md).
3. For each rubric: **pass**, **gap** (one line), or **N/A**.
4. If every applicable rubric passes → **Good to go**.
5. Else list up to **3** concrete fixes (verifier flag, contract path, Phase 0 reference).
6. Close with: **Coaching only — harness was not changed.**

## Corner anchors

When reviewing pipelines, expect pointers to:

- Matching `docs/*-contract.json`
- `automation/tools/*_verify.py` and `--mode` where applicable
- Phase 0: `crtqa_env_probe.py`, FE cred tokens ([`fe-ui-probe-contract.json`](../../docs/fe-ui-probe-contract.json))
- `jq` inspect norm ([`jq-json.mdc`](../../rules/jq-json.mdc))

## Examples

See [examples.md](examples.md).
