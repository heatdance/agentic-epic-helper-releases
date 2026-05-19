# CRT-639 gold (operator-curated)

**Required before `/crtqa-calibrate`:** `CRT-639-coverage.json`, `CRT-639-tests.json` (same schemas as production pipeline output).

**Optional:** `CRT-639-precon.json`, `CRT-639-analysis.json`.

Populate from human-reviewed Jira/Confluence/CRTQA exports or copy normalized JSON from `epics/CRT-639/context/` after editing. **Do not** commit secrets.

`CRT-639-gold-meta.json` — legacy thin oracle (substring/threshold hints); not a substitute for required JSON files.

**Sources (examples):** CRTQA-10132 (TCD), CRTQA-10176–10184 (tests), epic Smart Checklist in Jira.
