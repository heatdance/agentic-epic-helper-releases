# QA session handoff — Corner Trader

Read at the start of substantive QA work; **update before ending** (date, focus, next steps). Detail lives in **`epics/<KEY>/`** and **[AGENTS.md](AGENTS.md)** — do not duplicate long pipeline logs here.

Turn model: **[docs/harness-principles.md](docs/harness-principles.md)** §14 (Conversation vs Teach vs Action). Coaches: **`/better-prompt`**, **`/better-skill`**. Smoke teach: **`/teach`**, **`/teach stop`** → [auto-tests/](auto-tests/). Epic orchestrator: **`/crtqa-helper`**, **`/crtqa-helper resume`** → [docs/crtqa-helper-contract.json](docs/crtqa-helper-contract.json).

## Resume

**`/crtqa-helper` shipped** (v1): contract, command, skill, **`COVERAGE-REINFORCE:`** playbook, `close_archive` helper → `context/helper/`, `corner-harness-verify` minimal+full OK. Pilot on a **fresh** epic (not CRT-663).

**CRT-663** (manual path): coverage v1 done; operator may continue **ANALYSE** / **TEST-DISCOVER** without helper.

**CRTQA stats v5** promoted: test-first corpus, per-user `latest-<user>.md`, contract [docs/crtqa-stats-contract.json](docs/crtqa-stats-contract.json), library under `automation/tools/crtqa_stats/`. Experiment `temp/stats-test/` removed. Regenerate per engineer via `/crtqa-stats mode=initial_assessment`.

**Smoke specs** landed: [auto-tests/specs/schema.json](auto-tests/specs/schema.json) + [smoke-manifest.json](auto-tests/specs/smoke-manifest.json) (32 rows, CRTQA-10247). **`/teach`** + operator profile (v2). Pytest/Playwright implementation **next** via teach phases.

## Next

1. **`/crtqa-helper CRT-…`** on a fresh epic when ready to validate orchestrator end-to-end.
2. **`/teach`** — confirm `ct_qa` env profile; phase 0 for first manifest row (`automation_scope` + narrow oracle).
3. Phase 1–2: fixtures + first smoke test under `auto-tests/tests/smoke/`.
4. Commit specs + harness wiring on `personal`.
5. When implementing harness Python only, attach **karpathy-guidelines** (not default for smoke teach).

## Anchors

- Teach / smoke: [docs/auto-tests-contract.json](docs/auto-tests-contract.json) · [auto-tests/](auto-tests/)
- Charter: [docs/grounding-integration.json](docs/grounding-integration.json)
- Karpathy (opt-in): [docs/karpathy-guidelines-contract.json](docs/karpathy-guidelines-contract.json)
- Doctrine §14: [docs/harness-principles.md](docs/harness-principles.md)
- Epic (closed): `epics/CRT-639/context/`

## Last updated

- **Date**: 2026-06-04 — **CLEAN + HOW-TO tier update:** stats/coaches/teach personal-only; `/crtqa-helper` on team (full), public (concept in HOW-TO); HOW-TO restructured (shared intro, helper + prep table); tier matrix + `clean_verify` team checks updated.
- **Date**: 2026-06-04 — **`/crtqa-helper` orchestrator v1:** `docs/crtqa-helper-contract.json`, command/skill, `COVERAGE-REINFORCE:` pipeline + router, `crtqa_helper_affordances.py`, `close_archive` helper archive, harness-map/AGENTS/HOW-TO/README, golden fixture; `corner-harness-verify` full OK.
- **Date**: 2026-06-04 — **COVERAGE: CRT-663** (production): `CRT-663-coverage.json` v2 + `.md` — archetype `widget_ui`, 15 checks, 16 matrix rows, 13 obligations covered; `coverage_verify.py` obligations+emit OK; `temp/` deleted.
- **Date**: 2026-06-04 — **EPIC-PREP: CRT-663** (production): `CRT-663-ref.json` v4 — FX_SPOT visibility in Orders/Transactions/Positions (Web+WB+Adaptive parity); 14 `obligations_proposed[]`; workflow states from CT Order Statuses; child CRs XT-7210–7212; `epic_prep_verify.py` ref+reconcile OK; `temp/` deleted.
- **Date**: 2026-05-25 — **Smoke specs:** `schema.json` + `smoke-manifest.json` (CRTQA-10247, 32 rows); teach cold reads; CLEAN team-keep for minimal specs; manifest verify in `corner-harness-verify`.
- **Date**: 2026-05-25 — **Teach harness prep:** `auto-tests/` entity; `/teach` + `/teach stop`; contract, CLEAN tiers, `corner-harness-verify` teach checks.
- **Date**: 2026-05-25 — **Karpathy Pass 4 (complete):** opt-in `.cursor/skills/karpathy-guidelines/SKILL.md`; `docs/karpathy-guidelines-contract.json`; charter `optional_skills` + `pass4_artifacts`; T1 `karpathy_coding`; CLEAN tier rows; `corner-harness-verify` karpathy checks; pipelines unchanged.
- **Date**: 2026-05-25 — **Grounding remediation Pass 3 (complete):** qa-artifacts pointer; harness-principles section 16 paths; charter `remediation.status=complete`; final regression pass.
- **Date**: 2026-05-25 — **Grounding remediation Pass 2:** soft_core in charter; preservation; HOW-TO guard advisory; README coaches; clean-publish-tier-matrix.md grounding table.
- **Date**: 2026-05-25 — **Grounding remediation Pass 1:** `operator_assist` + `harness_hygiene` T1; pipeline-router recap; golden checks in `corner-harness-verify`; [automation/docs/corner-harness-verify.md](automation/docs/corner-harness-verify.md).
- **Date**: 2026-05-25 — **Grounding remediation Pass 0:** charter `passes` 1+2 complete; sessionStart-only hooks; ASCII `inject-corner.json`; regression block incl. epic_prep + coverage smoke; `corner-harness-verify` mojibake + hooks_session_start_only gates.
- **Date**: 2026-05-25 — **Grounding-kit pass 1:** `/better-prompt`, `/better-skill`, corner rules (`intent-`, `delegation-`, `preservation-`, `communication-`), `docs/grounding-integration.json`, harness-principles §14; pass 2 scaffold (`hooks.json`, `inject-corner.json`, `corner-harness-verify.ps1`).
- **Date**: 2026-05-20 — **`/release-notes` JQL:** FX Epic **not in** CRT-650, CRT-644 (+ base excludes resolved, won't fix); Master Epic **in** CRT-650, CRT-644; adaptive still `status not in (aborted)`.
- **Date**: 2026-05-21 — **`CLEAN:` full run:** **P** `origin/personal` → **`e901a47`** (+ harness fixes **`ad034fb`**); **T** `team/team` → **`1c02e27`** (force-push); **U** `releases/public-1.5` → **`c8025f2`** (new branch). Tier rules applied (no release-notes on team; org maps kept on team; stats toolkit on team; public guide-only). **Postflight FAIL:** delete **`public-1.4`** blocked — GitHub default branch still **`public-1.4`**; set default to **`public-1.5`**, then `clean_verify.py --mode public_remote --superseded public-1.4` + `--mode postflight`.
- **Date**: 2026-05-21 — **CLEAN tier alignment** (operator-confirmed): **personal** = full private backup; **team** = private squad + **shared org-map truth** + runnable harness (no release-notes, no maintainer stats `latest.md`); **public** = guide-only (no stats/release-notes). Contract `tier_goals` locked.
- **Date**: 2026-05-20 — **`/release-notes` v3:** removed `corner-map.json`, `releases/exploration/`, `release_map_probe.py`; four fixed PMOPROC/Epic JQLs per fixVersion; adaptive without `project=`; contract schema v3; slim `release_notes.py`. Old batch outputs deleted — regenerate with `/release-notes` on `personal`.
- **Date**: 2026-05-20 — **CLEAN MCP fix:** Phase U no longer deletes gitignored `.cursor/mcp.json`; public verify allows ignored file on disk; team tier adds `.cursor/mcp.json.team.example` (scrubbed stack). Restored local `.cursor/mcp.json` from example — operator must set postgres `USER`/`PASSWORD` and confirm global MCP (Atlassian/Figma) in Cursor Settings.
- **Date**: 2026-05-19 — **`CLEAN: proceed`** (full publish from `personal`): **S/P** align OK (no personal commit); **T** `team/team` → **`83ccda1`** (`clean: team harness export`; **force-push** required — remote had diverged from `origin/personal`); **U** **`public-1.4`** → **`848ff3b`** on `releases` (`public-export: 1.4.0`); local back on **`personal`** only. **Postflight FAIL:** `releases` still has **`public-1.3`** + **`public-1.4`** — remote delete of `public-1.3` rejected (*current branch* on GitHub). **Operator:** set default branch to **`public-1.4`**, delete **`public-1.3`**, then `clean_verify.py --mode public_remote --superseded public-1.3` + `--mode postflight`.
- **Date**: 2026-05-19 — **CLEAN public hardening** on `personal`: `clean_apply_public` seeds, template overlays, `public` verify gates.
- **Date**: 2026-05-19 — **CLEAN v3 (three-branch model):** contract/playbook/verify — sequential checkout, direct `team/team` push, `postflight`/`legacy_remote`/`prune_team_remote`; [clean-remediation.md](automation/docs/clean-remediation.md). Remediation run: worktrees removed, `clean/*` pruned on team, `release-*` gone on releases; local only `personal`. **`team/team` still pre-strip** until next full `CLEAN:` Phase T.
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

- **CRT-663:** COVERAGE done — **TEST-DISCOVER:** / **ANALYSE:** next (EURUSD.spot, console orders, parity across dxTrade5 + WB + Adaptive).
- **CRT-639:** **closed** — do not rerun upstream pipelines without restoring JSON from `context/` to epic root.
- **Release notes:** v3 playbook + contract; run `/release-notes` to populate `releases/<batch>/` (no corner-map).
- **Harness:** Mandatory-chain doc reconciliation (discover always required in all playbooks) — **deferred** separate pass.

Doctrine: **[docs/harness-principles.md](docs/harness-principles.md)** (CLOSE archive note in §9).

## Blockers

- **CLEAN postflight** — `releases` default branch still **`public-1.4`**; cannot delete until default is **`public-1.5`** (see Last updated).
- **CRT-1738 numeric oracle** — Jira notes dependency on **XT-7911** (`obl-015` deferral in ref); reflected in excluded checks and analysis gaps.
- **user-mcp-atlassian** for live pipeline re-runs.

## Next steps

1. **CLEAN finish:** GitHub → `agentic-epic-helper-releases` → default branch **`public-1.5`** → delete **`public-1.4`** → `python automation/tools/clean_verify.py --mode public_remote --superseded public-1.4` + `--mode postflight`.
2. Human: create CRTQA test issues from **`CRT-639-tests.md`** (generation mode — no CRTQA keys in repo).
3. To re-run **EPIC-PREP** / **COVERAGE** / etc. on CRT-639: move JSON from `epics/CRT-639/context/` back to epic root first — [HOW-TO.md](HOW-TO.md).

## Notes

- **Deferred (next pass):** mandatory-chain doc wording (optional → required for discover/precon); automated un-archive.
- **Calibrate v1.1:** `calibrate_verify.py` adds `gold_distinct`, `compare`, `NO_ACTIONABLE_DELTA`; CRT-639 seed gold still **prod-identical** → `/crtqa-calibrate` stops at `GOLD_NOT_DISTINCT` until real oracle JSON.
- **Retired:** **TEST-EXEC** / Playwright chain step — use **`CLOSE:`** for integrity + archive; chrome-devtools remains for discover/precon/prep ad-hoc only.
