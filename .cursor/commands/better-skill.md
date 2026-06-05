---
description: Coach pipeline/command/skill drafts before shipping (Conversation-only; no repo writes)
---

# Better skill

Review a draft playbook, slash command, or skill before you merge harness changes. **Advice only** — no file writes and no execution of the draft workflow.

Skill: [`.cursor/skills/better-skill/SKILL.md`](../skills/better-skill/SKILL.md). Patterns: [`docs/skill-authoring-patterns.json`](../../docs/skill-authoring-patterns.json). Contract: [`docs/operator-assist-contract.json`](../../docs/operator-assist-contract.json) (`betterSkill.version`).

## When to use

- Adding or changing `.cursor/pipelines/*.md`, `.cursor/commands/*.md`, or `.cursor/skills/**/SKILL.md`.
- Unsure whether subprocesses, Phase 0 gates, or verifier `--mode` flags are spelled out.

Not for everyday Jira tickets — use `/better-prompt` instead.

## Agent instructions

1. **Conversation** only — no repo edits ([`docs/harness-principles.md`](../../docs/harness-principles.md) §14).
2. Read the attached draft (and linked contract/verifier paths if cited).
3. Score four rubrics from `skill-authoring-patterns.json`; mark **N/A** when the draft is not a pipeline.
4. If all applicable rubrics pass → **Good to go** (still no file writes in this turn).
5. End with: **Coaching only — harness was not changed.**

### Rubrics (Corner)

| Rubric | Pass signal |
|--------|-------------|
| **subagents** | Read-only explore/MCP before writes; parent runs verifiers |
| **validation_done** | Done = exit code, path, or `--mode` — not “complete” |
| **verification_schema** | Points to `*-contract.json` and matching `*_verify.py` |
| **iterative_subsets** | Bounded phases; `epics/<KEY>/temp/` deleted; no unbounded Jira |

### Output template

1. **Interpreted intent** — what the draft is trying to govern.
2. **Rubric table** — pass / gap / N/A per row (max 2 sentences per gap).
3. **Top fixes** — up to 3 concrete edits (paths, flag names).
4. **Verdict** — **Good to go** or **Revise then re-run /better-skill**.

## Shipped behavior

Version bump + golden fixture when coach behavior changes. See [`preservation-corner.mdc`](../rules/preservation-corner.mdc).
