# CRT-639 gold (operator-curated)

gold_as_of: 2026-05-19

## Status (seed — replace before real calibrate)

**`CRT-639-coverage.json`** and **`CRT-639-tests.json`** in this folder are currently **copies of** `epics/CRT-639/context/` from pipeline output — **not** operator oracle.

**`/crtqa-calibrate`** will **hard stop** at **`gold_distinct`** (`GOLD_NOT_DISTINCT`) until you replace these files with human-reviewed gold (e.g. CRTQA-10176–10184, Jira Smart Checklist exports).

## Required files

- `CRT-639-coverage.json`
- `CRT-639-tests.json`

Optional: `CRT-639-precon.json`, `CRT-639-analysis.json`, `CRT-639-gold-meta.json` (threshold hints only).

## Sources (targets when curating)

- CRTQA tests: 10176 (precon class), 10177, 10182, 10183, 10184
- Epic Smart Checklist / coverage in Jira
- See `CRT-639-gold-meta.json` for scope statement (not a substitute for required JSON)
