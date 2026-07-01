---
description: Run one epic pipeline stage per turn with console and coverage human gates; use resume to continue.
---

# /epic-helper

Bind one epic per chat and advance **draft_truth_v3** **one automated stage per turn**. Contract: [`docs/epic-helper-contract.json`](../../docs/epic-helper-contract.json). Master chain: [`docs/draft-truth-contract.json`](../../docs/draft-truth-contract.json).

## Triggers

| Phrase | Action |
|--------|--------|
| **`/epic-helper CRT-1234`** | Cold start; create `epics/<KEY>/helper/session.json`; run **console gate** then **EPIC-PREP** when console passes |
| **`/epic-helper resume`** | Clear a gate or run **one** stage; optional text → `operator-feedback.md` |

## Cold start

1. Read contract `stages[]` + `gates[]` with **`jq`**.
2. Create `epics/<KEY>/helper/` if needed; reset `session.json`.
3. Run **`python automation/tools/crtqa_console_probe.py`**.
4. **Console pass** → **`EPIC-PREP: <KEY>`** this turn → `epic_prep_verify.py` → **STOP** (next resume = `coverage_v1`).
5. **Console fail** → `awaiting_gate: env`; print checklist; **do not** start console; **STOP**.

Gate id in `session.json` remains **`env`** (console multiplex check only).

## Resume

1. Load `session.json`; if inactive, instruct cold start.
2. Append resume comment to `operator-feedback.md` when provided.
3. If `awaiting_gate` set → handle gate only; else run **exactly one** stage per contract.
4. After verifier **OK** → update `stage-log.jsonl`, **STOP**.

## Human gates (two only)

| Gate | When | Operator action |
|------|------|-----------------|
| **env** (console) | Console probe fail | **`/crtqa-console start`**; re-run probe or **`/epic-helper resume`** |
| **coverage_review** | After machine loop | Merge `-coverage.md`; edit **`scenario_groups[]`**; then **`/epic-helper resume`** |

**No PRECON in v3.** TEST-PREP does not need console.

## Stage map

| Stage | Trigger |
|-------|---------|
| `epic_prep` | `EPIC-PREP: <KEY>` |
| `coverage_v1` | `COVERAGE: <KEY>` |
| `ground` | `GROUND: <KEY>` |
| `analyse` | `ANALYSE: <KEY>` |
| `coverage_fix_breadth` | `COVERAGE: <KEY> fix_breadth=yes` (optional) |
| `discover` | `TEST-DISCOVER: <KEY>` (linker — no browser) |
| `test_prep` | `TEST-PREP: <KEY>` (scenario_intent) |
| `close` | `CLOSE: <KEY>` |

Before **`coverage_v1`:** read-only explore subagent on dxtrade5 + webbroker harness maps.

After **`discover` OK:** optional `epic_helper_affordances.py` when affordances non-empty.

One pipeline per turn; delete `epics/<KEY>/temp/` per playbook.
