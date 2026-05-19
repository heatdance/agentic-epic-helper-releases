# QA session handoff — Corner Trader

Read at the start of substantive QA work; **update before ending** (date, focus, next steps). Detail lives in **`epics/<KEY>/`** and **[AGENTS.md](AGENTS.md)** — do not duplicate long pipeline logs here.

## Last updated

- **Date**: 2026-05-19 — **TEST-PREP v3.1** (harness): expansion_policy in [`docs/test-prep-tbd-contract.json`](docs/test-prep-tbd-contract.json); `selection_rules_machine` + verifier gates in [`test_prep_verify.py`](automation/tools/test_prep_verify.py) (one pair per `case_outline` row for ladder/rounding; duplicate actions; excluded primary ↔ `coverage_gaps[]`; `--plan` required on draft/merge/tests emit). Fixtures: [`automation/tools/fixtures/test_prep/`](automation/tools/fixtures/test_prep/). **Archived CRT-639** `-tests.json` would fail new emit/cardinality until re-prep or gap backfill — no regen in this change.
- **Date**: 2026-05-19 — **`CLOSE: CRT-639`** (production): `context/CRT-639-close.json` — **`epic_verdict: pass`**; L0–L4 + epic-wide OK; JSON archived under `context/`; four root `.md` retained; **3** info findings (supporting chk-013–015 unbundled).
- **Date**: 2026-05-19 — **`TEST-PREP: CRT-639`** (production): `CRT-639-tests.json` v4 + `CRT-639-tests.md` — **3** bundles (`tb-001`..`tb-003`), `crtqa_outline`; Phase 0 pass; plan/explore/draft/merge/tests verify OK; excluded **chk-004**, **chk-012**, **chk-016**; creds not in JSON; `temp/` deleted.
- **Date**: 2026-05-19 — **`TEST-PRECON: CRT-639`** (production): `CRT-639-precon.json` v5 + `CRT-639-precon.md` — Phase 0 pass; **pc-001** (9 setup steps, console+WebBroker+dxTrade5 drill); **3** skeleton bundles (`tb-001`..`tb-003`); excluded **chk-004**, **chk-012**, **chk-016**; `precon_verify.py` OK; creds not in JSON; `temp/` deleted.
- **Date**: 2026-05-19 — **`TEST-DISCOVER: CRT-639`** (production): `CRT-639-discover.json` v3 **`discovery_status: complete`** — Phase 0 pass (env/console/FE smoke); **13** primary ledger rows (**3** `scope_gap`); `discover_verify.py` OK; creds not in JSON.
- **Date**: 2026-05-19 — **`ANALYSE: CRT-639`** (production): `CRT-639-analysis.json` v2 + gaps-first `.md` — **5** gaps, **3** `exploration_suppressed`; `analysis_verify.py` gaps/downstream/emit **OK**; `known_issues=no`.
- **Date**: 2026-05-19 — **`COVERAGE: CRT-639`** (production): `CRT-639-coverage.json` v2 + `CRT-639-coverage.md` — **16** checks, **8** matrix rows, **14** `obligations_coverage`; `coverage_verify.py` obligations+emit **OK**.
- **Date**: 2026-05-19 — **`EPIC-PREP: CRT-639`** (production): recreated `epics/CRT-639/CRT-639-ref.json` schema v4 — **15** `obligations_proposed[]`, **5** Yogi requirements (snippets ok via MCP), `client_shell_impact` qa_default_both, `BRO/xt` browse hits, **5** `xt_refs`; `epic_prep_verify.py` ref+reconcile **OK**; `temp/` deleted.
- **Date**: 2026-05-19 — **Benchmark retired → `/crtqa-calibrate`**: removed `.cursor/benchmark/`, `docs/benchmark-contract.md`, benchmark Python tools; added `.cursor/calibrate/`, `docs/calibrate-contract.json`, `calibrate_verify.py`, playbooks/commands/docs; HOW-TO §3 rewritten.
- **Date**: 2026-05-19 — **`/crtqa-stats`** `initial_assessment` for `arodzevich`: cohort **2** TCD tasks (CRTQA-10034 corpus, CRTQA-10132 comparison); state `stats/crtqa-stats/state/last-sync.json` v3; report `stats/crtqa-stats/latest.md` (corpus benchmark pending — n under 4 per category).
- **Date**: 2026-05-19 — **Harness doc reconciliation** complete: [HOW-TO.md](HOW-TO.md), [epics/README.md](epics/README.md), [README.md](README.md), [sync.md](.cursor/pipelines/sync.md) registry, scratch WS-A/WS-C/session notes; templates post-`context/` notes; **TEST-EXEC** refs removed from durable docs (intentional “replaces TEST-EXEC” in this file only).
- **Date**: 2026-05-19 — **`CLOSE:`** pipeline implemented: [`docs/close-contract.json`](docs/close-contract.json), [`.cursor/pipelines/close.md`](.cursor/pipelines/close.md), verifiers [`close_verify.py`](automation/tools/close_verify.py) / [`close_archive.py`](automation/tools/close_archive.py).
- **Date**: 2026-05-19 — **ANALYSE v2** + **EPIC-PREP/COVERAGE obligation patch** (see prior entries).

## Current focus

- **CRT-639:** **closed** — do not rerun upstream pipelines without restoring JSON from `context/` to epic root.
- **Harness:** Mandatory-chain doc reconciliation (discover always required in all playbooks) — **deferred** separate pass.

Doctrine: **[docs/harness-principles.md](docs/harness-principles.md)** (CLOSE archive note in §9).

## Blockers

- **CRT-1738 numeric oracle** — Jira notes dependency on **XT-7911** (`obl-015` deferral in ref); reflected in excluded checks and analysis gaps.
- **user-mcp-atlassian** for live pipeline re-runs.

## Next steps

1. Human: create CRTQA test issues from **`CRT-639-tests.md`** (generation mode — no CRTQA keys in repo).
2. To re-run **EPIC-PREP** / **COVERAGE** / etc. on CRT-639: move JSON from `epics/CRT-639/context/` back to epic root first — [HOW-TO.md](HOW-TO.md).

## Notes

- **Deferred (next pass):** mandatory-chain doc wording (optional → required for discover/precon); automated un-archive.
- **Calibrate v1.1:** `calibrate_verify.py` adds `gold_distinct`, `compare`, `NO_ACTIONABLE_DELTA`; CRT-639 seed gold still **prod-identical** → `/crtqa-calibrate` stops at `GOLD_NOT_DISTINCT` until real oracle JSON.
- **Retired:** **TEST-EXEC** / Playwright chain step — use **`CLOSE:`** for integrity + archive; chrome-devtools remains for discover/precon/prep ad-hoc only.
