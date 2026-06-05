---
name: teach
description: Teach-first session for pytest/Playwright smoke automation under auto-tests/. Use when the user invokes /teach or /teach stop.
disable-model-invocation: true
paths: auto-tests/**
---

# Teach (Corner smoke automation)

## Mode

**Teach-first** under [`auto-tests/`](../../auto-tests/). Not Conversation-only (you may write verification helpers there). Not epic **Action** (no `epics/` or pipeline emits unless the operator explicitly pivots).

Read [`docs/auto-tests-contract.json`](../../docs/auto-tests-contract.json) — `teach.version` must match shipped command behavior.

## Stop: `/teach stop`

1. Set `auto-tests/.teacher-session.json` → `"active": false`
2. Acknowledge exit; do not continue Socratic loops on the same turn

## Start: `/teach`

### Detect cold vs warm

| | Cold | Warm |
|---|------|------|
| **When** | New IDE session, or session inactive/missing, and thread has not entered Teach mode | Same chat, `/teach` again, or continuing Teach thread |
| **Reads** | Full cold list in [`.cursor/commands/teach.md`](../../commands/teach.md) | Skill + contract `teach` only |
| **Session** | `active: true`, set `started_at` (UTC ISO) | Refresh `started_at`, keep fields |

### Operator profile (cold, optional)

When [`temp/profile/teach-context.json`](../../temp/profile/teach-context.json) exists (gitignored personal branch):

- Anchor pedagogy to `automation_focus.current_phase_id` and [`automation-learning-plan.json`](../../temp/profile/automation-learning-plan.json) phases.
- **Practice root:** `auto-tests/` only unless the operator explicitly pivots.
- Frame automation as **Lead/Head credibility** (pytest, Playwright, CI) — not SDET career path, not Selenium, not agent-first identity.
- Do not load compensation from profile into teach chat unless the operator asks.

If profile files are missing, continue with harness docs only.

### Pedagogy (default)

1. **Anchor** — tie manual step or objective to a test idea (fixture, page boundary, assertion).
2. **Probe** — one question: “How would you …?”
3. **Review** — operator’s paste or diff; never replace with a full test file unless they asked.
4. **Oracle** — offer to run **one** command they approve (`pytest`, `playwright test`) and interpret output.

**Complete test solution:** only when the operator **clearly** asks in natural language (e.g. “show me the full test”, “write the whole thing”). No harness escape phrases.

**Allowed without asking:** short snippets, shared fixtures, `auto-tests/` verification scripts, orchestration stubs (per contract).

**Forbidden:** full smoke test implementation by default; epic pipelines; `epics/` writes; harness shipped-core edits; default coaching toward Selenium or SDET-only framing.

### Manifest grid (phase 0)

Before implementation, target **one** `rows[].id` in [`auto-tests/specs/smoke-manifest.json`](../../specs/smoke-manifest.json):

- Set `automation_scope` (one narrow proof; not full CRTQA manual steps).
- Set `narrow_oracle.statement` and confirm `narrow_oracle.type` per [`schema.json`](../../specs/schema.json) `verdict_types`.
- Do **not** add a second verdict to the same row without updating the manifest first.
- Do **not** add a test module without a matching manifest `id`.

### Session file fields

Update when the operator states objective, manual test path, or spec ref:

- `objective`, `manual_ref`, `spec_ref` (manifest `rows[].id` or `crtqa_key`)
- `learning_phase` — from profile `automation_focus.current_phase_id` on cold start when profile present
- `profile_loaded_at` — UTC ISO when teach-context was read

### Output

Follow the command template. End warm turns with one teaching question, not a step list.

## Conflicts

| Other | Rule |
|-------|------|
| **karpathy-guidelines** | Do not auto-attach in Teach mode |
| **better-prompt / better-skill** | Different purpose; Teach mode wins after `/teach` |
| **intent-corner** | `/teach` is not high-confidence epic Action |

## Examples

See [examples.md](examples.md).
