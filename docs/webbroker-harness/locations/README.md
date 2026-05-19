# Stage 3 — location layers

**Canonical CTQA file:** [`ctqa.json`](ctqa.json) — per-feature verification and drift (see [`PHASE0.md`](PHASE0.md), [`WAVES.md`](WAVES.md)). When `phase0.stage3_locations_waves_complete` is set, all playbook waves **W1–W4** for that file are merged and parity-complete until you re-run verification.

Add **per-environment** JSON here after live verification (Chrome DevTools MCP or manual session), for example:

- `ctqa.json` — `https://ctqa.prosp.devexperts.com/webbroker/` (dealer WebBroker app path on CTQA; re-run waves after login to replace drift with live `verify` data)

Each feature entry should reference **`concept-map.json` feature `id`** values and include `verified_at` (ISO date), `steps[]`, and `verify` cues (stable text, region names). Selectors are optional hints marked `may_change`.

**Parity (compass vs locations):** run `python automation/tools/webbroker-harness/check_locations_parity.py` from repo root.

Do not store credentials in this folder.
