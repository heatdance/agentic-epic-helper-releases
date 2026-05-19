# QA session handoff — Corner Trader

Read at the start of substantive QA work; **update before ending** (date, focus, next steps). Detail lives in **`epics/<KEY>/`** and **[AGENTS.md](AGENTS.md)** — do not duplicate long pipeline logs here.

## Last updated

- **Date**: 2026-05-19 — **Harness doc reconciliation** complete: [HOW-TO.md](HOW-TO.md), [epics/README.md](epics/README.md), [README.md](README.md), [sync.md](.cursor/pipelines/sync.md) registry, scratch WS-A/WS-C/session notes; templates post-`context/` notes; **TEST-EXEC** refs removed from durable docs (intentional “replaces TEST-EXEC” in this file only).
- **Date**: 2026-05-19 — **`CLOSE:`** pipeline implemented: [`docs/close-contract.json`](docs/close-contract.json), [`.cursor/pipelines/close.md`](.cursor/pipelines/close.md), verifiers [`close_verify.py`](automation/tools/close_verify.py) / [`close_archive.py`](automation/tools/close_archive.py).
- **Date**: 2026-05-19 — **ANALYSE v2** + **EPIC-PREP/COVERAGE obligation patch** (see prior entries).

## Current focus

- **CRT-639:** Run **`TEST-PRECON:`** / **`TEST-PREP:`** (production) to restore **`-discover.json`**, **`-precon.json`**, **`-tests.json`** at epic root, then optional **`CLOSE: CRT-639`**.
- **Harness:** Mandatory-chain doc reconciliation (discover always required in all playbooks) — **deferred** separate pass.

Doctrine: **[docs/harness-principles.md](docs/harness-principles.md)** (CLOSE archive note in §9).

## Blockers

- **`CLOSE: CRT-639`** — preflight **fails** today: missing **`-discover.json`**, **`-precon.json`**, **`-tests.json`** under `epics/CRT-639/` (only ref/coverage/analysis present).
- **user-mcp-atlassian** for live pipeline re-runs.

## Next steps

1. **`TEST-PRECON: CRT-639`** → **`TEST-PREP: CRT-639`**.
2. **`CLOSE: CRT-639`** (optional `heal=no` to audit-only).
3. Do **not** rerun upstream pipelines on a **closed** epic without moving JSON out of `context/` — [HOW-TO.md](HOW-TO.md).

## Notes

- **Deferred (next pass):** mandatory-chain doc wording (optional → required for discover/precon); benchmark CLOSE KPIs; automated un-archive.
- **Retired:** **TEST-EXEC** / Playwright chain step — use **`CLOSE:`** for integrity + archive; chrome-devtools remains for discover/precon/prep ad-hoc only.
