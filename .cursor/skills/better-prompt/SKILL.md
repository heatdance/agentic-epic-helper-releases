---
name: better-prompt
description: Conversation-only coaching for Corner QA task prompts before pipeline runs. Use when the user invokes /better-prompt or attaches this skill with a draft prompt.
---

# Better prompt (Corner)

## Mode

**Conversation only.** Do not call write/edit tools, run `*_verify.py`, start pipelines, or use Task/subagents for the user's task.

## Steps

1. Read [`docs/operator-assist-contract.json`](../../docs/operator-assist-contract.json) — `betterPrompt.version` must stay aligned with command behavior.
2. Parse the operator draft (message + `@` files).
3. Score five gaps: scope, done, environment, constraints, verification (Corner table in [`.cursor/commands/better-prompt.md`](../../commands/better-prompt.md)).
4. Pick the **two** highest-impact missing gaps only.
5. Emit the command's full or minimal template.
6. Close with: **Coaching only — your task was not started.**

## Done bullets (good vs bad)

| Good | Bad |
|------|-----|
| `python automation/tools/coverage_verify.py --coverage epics/CRT-639/CRT-639-coverage.json` exit 0 | Coverage looks good |
| `COVERAGE: CRT-639` after `-ref.json` exists | Improve coverage |
| `TEST-DISCOVER: CRT-639 proceed` after Phase 0 pass | Run discover when ready |

## Paste-ready addendum

Only include paths the operator named or attached. Do not invent Epic keys.

## Examples

See [examples.md](examples.md).
