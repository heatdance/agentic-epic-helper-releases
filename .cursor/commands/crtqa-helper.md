---
description: Epic pipeline orchestrator — one stage per turn, three human gates, resume via /crtqa-helper resume
---

# /crtqa-helper

**BLUF:** Bind one epic per chat session and advance the **recommended pipeline chain** **one stage per agent turn** until the next human gate or finish. Contract: [`docs/crtqa-helper-contract.json`](../../docs/crtqa-helper-contract.json). Skill: [`.cursor/skills/crtqa-helper/SKILL.md`](../skills/crtqa-helper/SKILL.md).

## Triggers

| Phrase | Action |
|--------|--------|
| **`/crtqa-helper CRT-1234`** | Cold start or re-bind epic; create/update `epics/<KEY>/helper/session.json`; run **env** stage |
| **`/crtqa-helper resume`** | Clear gate or advance **one** automated stage; optional trailing text → `operator-feedback.md` |

No subcommands (`status`, `proceed`, …). State lives in `session.json`.

## Cold start (`/crtqa-helper <KEY>`)

1. Read contract `crtqaHelper` + `stages[]` + `execution_limits` (use **`jq`**).
2. Ensure `epics/<KEY>/` exists; create `epics/<KEY>/helper/` if needed.
3. Write or reset `session.json`: `active: true`, `epic_key`, `current_stage: env`, `awaiting_gate: null`, `completed_stages: []`, UTC timestamps.
4. Run **`python automation/tools/crtqa_env_probe.py`** (add `--coverage epics/<KEY>/<KEY>-coverage.json` only when that file exists).
5. **Env pass** → execute **`EPIC-PREP: <KEY>`** playbook **fully in this turn** → `epic_prep_verify.py` → append `stage-log.jsonl` → set `completed_stages` includes `env`, `epic_prep`; **STOP** (next resume = `coverage_v1`).
6. **Env fail** → set `awaiting_gate: env`; print probe checklist; **do not** call `/crtqa-console start`; **STOP**.

## Resume (`/crtqa-helper resume`)

1. Load `epics/<KEY>/helper/session.json` (`jq`); if missing or `active: false`, instruct cold start.
2. If user message has text after `resume`, append to `operator-feedback.md` with UTC header.
3. If `awaiting_gate` is set, handle gate only (see skill); on clear, set `awaiting_gate: null` and advance **one** stage.
4. Otherwise run **exactly one** stage from `current_stage` / `next_stage` per contract — **never** concatenate playbooks in one turn.
5. After stage verifier **OK**: append `stage-log.jsonl`, update `completed_stages`, set next gate or instruct `/crtqa-helper resume`.
6. **Hard stop** after each automated stage — emit gate message or “run `/crtqa-helper resume`”.

## Human gates (three only)

| Gate | When | Operator action |
|------|------|-----------------|
| **env** | Probe fail | Fix tunnel/console; `/crtqa-env`; `/crtqa-helper resume` |
| **coverage_review** | After `coverage_v1` | Edit `-coverage.md` and/or comment on resume; then `/crtqa-helper resume` |
| **discover_creds** | TEST-DISCOVER Phase 0 stop | Creds on resume line only (`dxtrade5_creds=`, `webbroker_creds=`) or waive per playbook; **never** persist creds in session |

**Coverage review:** record `coverage_md_sha_at_gate` (sha256 of `-coverage.md`) at gate entry; on resume, warn if file changed without feedback file update.

## Stage → pipeline map

| Stage | Trigger |
|-------|---------|
| `epic_prep` | `EPIC-PREP: <KEY>` |
| `coverage_v1` | `COVERAGE: <KEY>` |
| `analyse` | `ANALYSE: <KEY>` |
| `discover` | `TEST-DISCOVER: <KEY>` (+ cred tokens from resume line only) |
| `coverage_reinforce` | `COVERAGE-REINFORCE: <KEY>` |
| `precon` | `TEST-PRECON: <KEY>` |
| `test_prep` | `TEST-PREP: <KEY>` |
| `close` | `CLOSE: <KEY>` |

Before **`coverage_v1`** and **`coverage_reinforce`**: delegate **read-only** `explore` subagent on dxtrade5 + webbroker harness maps; parent writes checks.

After **`discover`** verifier OK: run `python automation/tools/crtqa_helper_affordances.py --discover epics/<KEY>/<KEY>-discover.json --out epics/<KEY>/helper/affordances-slice.json`.

## Anti-one-shot (mandatory)

- **One pipeline per turn** — verifiers are the progress signal, not prose summaries.
- **`jq`** before loading large epic JSON.
- Delete `epics/<KEY>/temp/` per each pipeline playbook before finishing that stage.
- **No secrets** in `helper/` files.

## Output template

1. **Stage** — id + epic key.
2. **Gate** — if waiting, checklist + exact resume phrase.
3. **Verifier** — command + exit (when stage ran).
4. **Artefacts** — paths touched.
5. **Next** — single action: `/crtqa-helper resume` or gate recovery.

## Shipped behavior

Bump `crtqaHelper.version` in contract + golden fixture when rubric changes. See [`docs/grounding-integration.json`](../../docs/grounding-integration.json) `soft_core[]`.
