---
description: Coach a draft QA task prompt before pipelines run (Conversation-only; no repo writes)
---

# Better prompt

Coach a draft task prompt before you send it for real work. **Advice only** — the agent does not execute your task, edit files, or spawn subagents for it.

Skill: [`.cursor/skills/better-prompt/SKILL.md`](../skills/better-prompt/SKILL.md). Contract: [`docs/operator-assist-contract.json`](../../docs/operator-assist-contract.json) (`betterPrompt.version`).

## When to use

- Unsure what to include (Epic key, scope, env, done criteria).
- Multi-step or vague asks (“improve coverage”, “fix harness”).
- You want a paste-ready addendum for a **later** message with `EPIC-PREP:` / `COVERAGE:` / etc.

Skip when the draft is already a full pipeline trigger with Epic key and you are ready to run.

## Agent instructions

1. Classify this turn as **Conversation** ([`docs/harness-principles.md`](../../docs/harness-principles.md) §14): no edits under `epics/`, harness docs, or `qa-handoff.md`.
2. Read the operator draft from the message (and any `@` attachments). Do **not** run pipelines, verifiers, or Task/subagents for that task.
3. Score against the **Corner rubric** (scope, done, environment, constraints, verification). Surface only the **top 2** gaps in “Worth adding”.
4. Apply the output template unless **minimal mode** applies.
5. End with: **Coaching only — your task was not started.**

### Corner rubric

| Gap | Check |
|-----|--------|
| **Scope** | Epic key (CRT-*), pipeline trigger vs ad-hoc, surfaces (dxTrade5 / WebBroker / console / DB) |
| **Done** | `*_verify.py` exit 0, artefact path (`epics/<KEY>/<KEY>-coverage.json`), or named MCP fetch — not “works” |
| **Environment** | CTQA/CTDEV; `dxtrade5_creds` / `webbroker_creds` when FE required ([`fe-ui-probe-contract.json`](../../docs/fe-ui-probe-contract.json)) |
| **Constraints** | `known_issues=yes`, `crtqa_index=yes`, `map_only=yes`; no secrets in repo |
| **Verification** | Verifier mode if TEST-PREP (`plan` / `draft` / `merge` / `tests`) |

### Minimal mode

Use when: single path + clear verb; or full pipeline trigger already present.

**Minimal output:** Interpreted intent (one sentence) · one suggested done bullet · **Ready to send** · coaching disclaimer.

### Full template (~150–250 words)

1. **Interpreted intent** — one sentence.
2. **Suggested done** — 2–4 verifiable bullets (commands, paths, exit codes).
3. **Worth adding** — up to **2** numbered optional questions (highest impact first).
4. **Paste-ready addendum** — short block for the *next* message (do not submit it).
5. **Next step** — send as-is, merge addendum, or re-run `/better-prompt`.

## Shipped behavior

Versioned in `operator-assist-contract.json`. Behavior changes require version bump + maintainer golden update ([`automation/tools/fixtures/operator-assist/`](../../automation/tools/fixtures/operator-assist/)). See [`preservation-corner.mdc`](../rules/preservation-corner.mdc).
