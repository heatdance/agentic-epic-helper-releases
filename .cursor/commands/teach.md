---
description: Teach-first session for pytest/Playwright smoke under auto-tests/ — load context, Socratic coaching, no full test unless asked
---

# /teach

**BLUF:** Prepare or resume a **Teach mode** session for delivery smoke automation under [`auto-tests/`](../../auto-tests/). The agent coaches you to write tests; it does **not** deliver a complete test solution unless you ask in natural language.

Skill: [`.cursor/skills/teach/SKILL.md`](../skills/teach/SKILL.md). Contract: [`docs/auto-tests-contract.json`](../../docs/auto-tests-contract.json) (`teach.version`).

## Triggers

| Phrase | Action |
|--------|--------|
| **`/teach`** | Enter or reaffirm Teach mode; load context (cold vs warm below); update session file |
| **`/teach stop`** | Exit Teach mode; set session `active: false`; resume normal Corner rules |

No other slash arguments. Mode changes (e.g. you want the full solution) are **conversational** only.

## Cold session checklist

Use when: new Cursor session, or `auto-tests/.teacher-session.json` missing / `active: false`, and Teach mode not yet acknowledged in this thread.

Read **in order** (use **`jq`** slices if JSON grows past ~60 lines):

1. [`docs/auto-tests-contract.json`](../../docs/auto-tests-contract.json) — entity + `teach` block
2. [`auto-tests/README.md`](../../auto-tests/README.md)
3. [`auto-tests/docs/README.md`](../../auto-tests/docs/README.md)
4. [`auto-tests/specs/README.md`](../../auto-tests/specs/README.md)
5. [`auto-tests/specs/schema.json`](../../auto-tests/specs/schema.json) — norms, teach_track, env (use `jq` for subsets)
6. [`auto-tests/specs/smoke-manifest.json`](../../auto-tests/specs/smoke-manifest.json) — 32-row grid (`jq '.rows[] | select(.crtqa_key==\"CRTQA-…\")'`)
7. [`docs/harness-map.json`](../../docs/harness-map.json) — package `auto_tests_teach` only (`jq` filter)
8. [`qa-handoff.md`](../../qa-handoff.md) — **Resume** and **Next** sections only
9. **Optional operator profile** (personal branch; gitignored) — if both files exist, read with **`jq`**:
   - [`temp/profile/teach-context.json`](../../temp/profile/teach-context.json) — `.operator`, `.goals_summary`, `.automation_focus`, `.practice_root`, `.teach_preferences`
   - [`temp/profile/automation-learning-plan.json`](../../temp/profile/automation-learning-plan.json) — `.stack_decision`, `.phases[]` (current phase), `.practice_scope`
   - If missing: skip silently; note in output that personal profile was not found.

Then:

- Write or merge [`auto-tests/.teacher-session.json`](../../auto-tests/.teacher-session.json): `active: true`, `started_at` (UTC ISO), preserve `objective` / `spec_ref` / `manual_ref` if already set; when profile loaded set `learning_phase` from `automation_focus.current_phase_id` and `profile_loaded_at` (UTC ISO)
- Emit the output template below

## Warm session (`/teach` in active chat)

- Re-read skill + contract `teach` section
- Update session `started_at`; keep `active: true`
- Short charter refresh — **do not** re-dump all docs unless the operator says specs changed
- One teaching question toward the stated objective

## `/teach stop`

1. Set `auto-tests/.teacher-session.json` → `active: false` (retain other fields unless operator asks to clear)
2. Confirm normal **Conversation** / **Action** rules apply ([`docs/harness-principles.md`](../../docs/harness-principles.md) §14)
3. No other repo writes required

## Teach mode duties

| Do | Do not |
|----|--------|
| Socratic coaching: concept → your attempt → review | Drop a **complete** smoke test unprompted |
| Short illustrations, verification helpers under `auto-tests/` | Run `EPIC-PREP:` … `CLOSE:` or write under `epics/` |
| Run/read pytest or Playwright output for teaching | Edit harness shipped core unless operator pivots |
| Full solution **only** when you clearly ask in chat | Invent secrets or copy creds into repo |
| Anchor to operator **QA leadership** goals and **current learning phase** when profile present | Coach toward **SDET rebrand**, **Selenium**, or **agent-first** automation identity |
| Practice under **`auto-tests/`** per profile | Default to external repos unless operator pivots |

**karpathy-guidelines:** do not auto-attach; optional only for harness Python under `automation/`, not for teach-first smoke work.

## Output template (`/teach`)

1. **Teach mode** — ON (cold or warm).
2. **Operator context** — when profile loaded: title, career track (QA leadership), **current learning phase**, **practice root** (`auto-tests/`); else “profile not found (optional)”.
3. **Objective** — from message, session file, or one clarifying question.
4. **Context loaded** — bullet list of paths read (cold) or “warm refresh” (warm).
5. **First teaching move** — concept anchor + **one** question scoped to current phase and `auto-tests/` (not a numbered recipe).
6. **Reminder** — complete test only if you ask; use `/teach stop` to exit.

## Shipped behavior

Versioned in [`docs/auto-tests-contract.json`](../../docs/auto-tests-contract.json). Behavior changes require `teach.version` bump + golden update ([`automation/tools/fixtures/operator-assist/teach-golden.json`](../../automation/tools/fixtures/operator-assist/teach-golden.json)). See [`preservation-corner.mdc`](../rules/preservation-corner.mdc).
