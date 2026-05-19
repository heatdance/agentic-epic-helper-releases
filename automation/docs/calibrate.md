# Calibrate (`/crtqa-calibrate`)

Post-hoc **production vs operator gold** analysis. **Not** a pipeline trigger.

## When

After pipelines (+ optional **`CLOSE:`**) and after **operator-curated** gold exists under **`.cursor/calibrate/<KEY>-gold/`** — **not** a copy of `context/` without edits.

## Gold requirements

| File | Required |
|------|----------|
| `README.md` with `gold_as_of: YYYY-MM-DD` | yes |
| `<KEY>-coverage.json` | yes |
| `<KEY>-tests.json` | yes |

## CLI modes

From repo root (`python automation/tools/calibrate_verify.py`):

| Mode | Exit 0 means | Exit 1 |
|------|----------------|--------|
| `gold_gate` | Required files + README `gold_as_of` | Missing gold |
| `gold_distinct` | Gold JSON **differs** from prod (byte or normalized) | **`GOLD_NOT_DISTINCT`** — hard stop |
| `prod_gate` | Epic has root `.md` or `context/*.json` | Missing prod |
| `compare` | Always 0 if parse OK; see **`outcome`** in JSON | IO/parse errors only |

**Compare outcomes** (stdout JSON + `outcome=` line):

| Outcome | Meaning |
|---------|---------|
| `NO_ACTIONABLE_DELTA` | **Success — no harness work**; do not emit suggestions |
| `DELTA_REVIEW` | Mechanical diffs exist; run playbook |
| `GOLD_NOT_DISTINCT` | From `gold_distinct` (before compare) |

```bash
python automation/tools/calibrate_verify.py --mode compare --epic CRT-639
# writes .cursor/calibrate/reports/CRT-639-compare.json by default
```

```bash
python automation/tools/calibrate_verify.py --self-test
```

## Agent flow (order)

1. `gold_gate` → `gold_distinct` → `prod_gate` → `compare`
2. If `NO_ACTIONABLE_DELTA` → **stop** (no harness lessons)
3. If `DELTA_REVIEW` → [`.cursor/pipelines/calibrate.md`](../../.cursor/pipelines/calibrate.md) through 6.6

## CRT-639 note

Seed gold under `.cursor/calibrate/CRT-639-gold/` may still be **prod-identical** until replaced; `gold_distinct` will **fail** until you curate real oracle JSON.

## Contract

[docs/calibrate-contract.json](../../docs/calibrate-contract.json) — schema v2: signals, `lesson_policy`, outcomes.
