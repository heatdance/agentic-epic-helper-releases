---
description: Compare epic outputs to operator gold under .cursor/calibrate/ and report mechanical harness deltas.
---

# /epic-calibrate

Compare **`epics/<KEY>/`** (and **`context/`** when archived) to operator gold in **`.cursor/calibrate/<KEY>-gold/`**. Ends with harness suggestions only when mechanical compare finds an actionable delta; otherwise **hard stop**.

## Workflow

1. **Ask** for epic key (from `epics/*/`, `.cursor/calibrate/*-gold/`, or [qa-handoff.md](../../qa-handoff.md)).
2. **Gold preflight:** `python automation/tools/calibrate_verify.py --mode gold_gate --epic <KEY>`
3. **Gold distinct:** `python automation/tools/calibrate_verify.py --mode gold_distinct --epic <KEY>` — stop if not distinct.
4. **Production preflight:** `python automation/tools/calibrate_verify.py --mode prod_gate --epic <KEY>`
5. **Compare:** `python automation/tools/calibrate_verify.py --mode compare --epic <KEY>` — parse `outcome=`.
6. If **`DELTA_REVIEW`** only: follow [`.cursor/pipelines/calibrate.md`](../pipelines/calibrate.md).

| `outcome` | Action |
|-----------|--------|
| **`NO_ACTIONABLE_DELTA`** | Stop — no harness changes recommended |
| **`DELTA_REVIEW`** | Run playbook (max 3 lessons with `diff_evidence`) |

Related: [docs/calibrate-contract.json](../../docs/calibrate-contract.json), [.cursor/calibrate/README.md](../calibrate/README.md).
