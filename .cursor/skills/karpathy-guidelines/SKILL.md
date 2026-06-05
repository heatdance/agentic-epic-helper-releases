---
name: karpathy-guidelines
description: >-
  Karpathy-inspired coding discipline: clarify assumptions, simplify,
  surgical diffs, verifiable done. Use when writing, reviewing, or refactoring
  Python under automation/ — not for epic pipelines, harness docs, or coaches.
license: MIT
---

# Karpathy guidelines (Corner QA workspace)

Behavioral guidelines to reduce common LLM coding mistakes, derived from [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876). Upstream: [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills). Contract: [docs/karpathy-guidelines-contract.json](../../docs/karpathy-guidelines-contract.json).

**Tradeoff:** These guidelines bias toward caution over speed. For trivial one-line fixes, use judgment.

## Corner scope

**Use when:**

- Writing or reviewing **Python** under [automation/tools/](../../automation/tools/) or [automation/docs/](../../automation/docs/) (verifiers, probes, helpers, small test modules).
- Refactoring an existing tool with a clear user request and verifiable done criteria.

**Do not use when:**

- Running or editing **epic pipelines** (`EPIC-PREP:` … `CLOSE:`), playbooks, or epic JSON under `epics/`.
- Editing harness **rules**, hooks, coaches, or tier docs — follow [intent-corner.mdc](../../rules/intent-corner.mdc) and [preservation-corner.mdc](../../rules/preservation-corner.mdc).
- **Conversation** coaches (`/better-prompt`, `/better-skill`) — advice-only turns.

This skill does **not** replace intent gates, harness-principles section 14 action-close, or preservation.

## Relation to Corner harness tools

| Tool | Role |
|------|------|
| **karpathy-guidelines** (this skill) | Code discipline for `automation/` Python |
| `/better-prompt` | Coach operator task wording (no code) |
| `/better-skill` | Coach playbook/command/skill docs (no code) |
| `*_verify.py` | Authoritative for epic artefact shape — run after code changes that affect verifiers |
| [preservation-corner.mdc](../../rules/preservation-corner.mdc) | Shipped core frozen; verifier logic changes need explicit entrust |

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — do not pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style in the target file, even if you'd do it differently.
- If you notice unrelated dead code, mention it — do not delete it unless asked.

When your changes create orphans:

- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:

- "Add validation" → "Add a test or run `python automation/tools/<tool>.py --self-test` (or documented CLI) exit 0"
- "Fix the bug" → "Reproduce with a minimal command, then fix; re-run verifier if behaviour is normative"
- "Refactor X" → "Run existing tests/self-test before and after"

For multi-step tasks, state a brief plan:

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Weak criteria ("make it work") require constant clarification. Prefer naming **exit codes**, **CLI flags**, or **fixture paths** under `automation/tools/fixtures/`.

## Always-on in a product repo (embed)

This skill is **opt-in** in this QA harness repo. For always-on behavior in an application repo, copy upstream [karpathy-guidelines.mdc](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/.cursor/rules/karpathy-guidelines.mdc) per [CURSOR.md](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CURSOR.md).
