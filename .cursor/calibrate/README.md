# Operator gold (calibrate)

Curated **reference** artefacts for **`/crtqa-calibrate`**: compare production `epics/<KEY>/` (+ `context/` when archived) to operator gold here.

## Layout

```
.cursor/calibrate/
  <KEY>-gold/
    README.md                 # REQUIRED: gold_as_of: YYYY-MM-DD + source links
    <KEY>-coverage.json       # required
    <KEY>-tests.json          # required
    <KEY>-precon.json         # optional
    <KEY>-analysis.json       # optional
    <KEY>-gold-meta.json      # optional thin oracle / thresholds (not a substitute)
  reports/
    <KEY>-compare.json        # mechanical compare output
    <KEY>-latest.md           # optional narrative
```

## Populate gold

1. Finish the epic workflow (pipelines through **`CLOSE:`** when you close).
2. Create **`<KEY>-gold/`** with **`README.md`** containing a line: **`gold_as_of: 2026-05-19`** (ISO date).
3. Add **required** JSON (same schemas as production templates):
   - **Do not** copy `context/*.json` into gold without review — **`gold_distinct`** will **reject** byte-identical copies.
4. Sources: final Jira Smart Checklist, CRTQA exports (scrub secrets), or MCP fetch from links during **`/crtqa-calibrate`** ingest.
5. Record source links in README.

**`*-gold-meta.json`** is optional threshold hints only; it does **not** replace required coverage/tests JSON.

## Run calibrate

**`/crtqa-calibrate`** in Cursor. See [automation/docs/calibrate.md](../../automation/docs/calibrate.md).

```bash
python automation/tools/calibrate_verify.py --mode gold_gate --epic <KEY>
python automation/tools/calibrate_verify.py --mode gold_distinct --epic <KEY>
python automation/tools/calibrate_verify.py --mode compare --epic <KEY>
```

Contract: [docs/calibrate-contract.json](../../docs/calibrate-contract.json).
