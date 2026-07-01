# QA session handoff — Corner Trader

Read at the start of substantive QA work; **update before ending** (date, focus, next steps). Detail lives in **`epics/<KEY>/`** and **[AGENTS.md](AGENTS.md)** — do not duplicate long pipeline logs here.

Turn model: **[docs/harness-principles.md](docs/harness-principles.md)** §14 (Conversation vs Action). Epic orchestrator: **`/epic-helper`**, **`/epic-helper resume`** → [docs/epic-helper-contract.json](docs/epic-helper-contract.json) (**v6**, console-only gate). Slash commands: **`/epic-stats`**, **`/epic-calibrate`**, **`/clean-release`**, **`/release-notes`**, **`/crtqa-console`**.

**`/crtqa-env` deprecated (2026-06-19):** removed from active harness; legacy env probe + Postgres tunnel archived under [automation/archive/legacy-ctqa-env/](automation/archive/legacy-ctqa-env/). Active gate: [crtqa_console_probe.py](automation/tools/crtqa_console_probe.py).

**Coverage operator UX (2026-06-19):** Split machine trace from human Smart Checklist paste — **`platform_reuse_annex`** and **`checks[].linker_trace_lines`** JSON-only; **`detail_lines`** operator hints per [docs/coverage-operator-hints.json](docs/coverage-operator-hints.json). Regenerated [epics/CRT-594/CRT-594-coverage.md](epics/CRT-594/CRT-594-coverage.md). Helper: [coverage_md_sync.py](automation/tools/coverage_md_sync.py). Verifiers: `coverage_verify.py --mode emit`, `ground_verify.py`, `test_prep_verify.py --md` forbid platform reuse heading and `> Discover:` in markdown.

## Resume

**EPIC-PREP topology (plan 1/8, 2026-06-18):** Shipped **`epic_archetype`** + **`verification_topology`** on `-ref.json` (contract [docs/epic-prep-topology-contract.json](docs/epic-prep-topology-contract.json); playbook steps **2c**, **3f–3h**). Verifier: `epic_prep_verify.py --strict-topology`. Fixtures: `automation/tools/fixtures/epic-prep/`. Validation refs: `epics/CRT-639/CRT-639-ref.json` (15 obligations, `metrics_calculation`), `epics/CRT-594/CRT-594-ref.json` (4 obligations, `widget_ui`, 6 surfaces, 6 oracle rules). Legacy refs without topology still pass `ref` without `--strict-topology`.

**Round 2 EPIC-PREP principal (step 1/8, 2026-06-18):** Shipped **`downstream_hints`** on obligations, **`verification_focus_proposed`**, **`principal_coverage_threads[]`**, delivery **`linked_obligation_ids`** / **`linked_surface_ids`**; playbook steps **3c** extend + **3i** principal reconcile; opt-in **`strict_principal=yes`** / `epic_prep_verify.py --strict-principal` / `--mode principal`. Contract: [docs/epic-prep-principal-contract.json](docs/epic-prep-principal-contract.json). Kind **`environment_setup`** in [docs/epic-obligation-kinds.json](docs/epic-obligation-kinds.json). Fixtures: extended 594/639 + `ref-principal-bad-missing-setup.json`.

**Round 2 COVERAGE principal (step 2/8, 2026-06-18):** Shipped principal consumption on `-coverage.json`: copy **`verification_focus_proposed`** verbatim; phase **8.5** materialize **`principal_coverage_threads[]`** H2 spine (setup before surfaces); keyed deferrals with **`obligation_ids[]`**; `coverage_verify.py --strict-principal` / `--mode principal`. Contract: [docs/coverage-principal-contract.json](docs/coverage-principal-contract.json). Fixtures: `coverage-594-shell-principal-minimal`, `coverage-639-formula-principal-minimal`, `coverage-principal-bad-blanket-deferral`.

**Round 2 ANALYSE principal (step 3/8, 2026-06-18):** Shipped deferral ↔ gap honesty on `-analysis.json`: keyed **`deferred_check`** gaps with **`pointers.obligation_id`**, delivery gaps with **`linked_obligation_ids`**, **`exploration_suppressed`** reason **`deferral_obligation_keyed`**; `analysis_verify.py --strict-principal` / `--mode principal`. Contract: [docs/analysis-principal-contract.json](docs/analysis-principal-contract.json). Fixtures: `analysis-639-formula-principal-minimal`, `analysis-594-shell-principal-minimal`, `analysis-principal-bad-empty-gaps`.

**Round 2 TEST-DISCOVER principal (step 4/8, 2026-06-18):** Shipped ref **`needs_environment_provision`** → **`fixture_needs[]`** with **`linked_obligation_ids`**, ANALYSE **`deferral_obligation_keyed`** → honest ledger disposition; `discover_verify.py --strict-principal` / `--mode principal`; kind **`account_group_environment_setup`** in discover-fixture-probes. Contract: [docs/discover-principal-contract.json](docs/discover-principal-contract.json). Fixtures: `discover-594-shell-principal-minimal`, `discover-639-formula-principal-minimal`, `discover-principal-bad-missing-provision`.

**Round 2 COVERAGE-REINFORCE principal (step 5/8, 2026-06-18):** Shipped discover provision **`fixture_needs`** merge into pass-2 setup **`detail_lines`**, deferral-keyed skip-deepen, **`sources.reinforce_principal_loaded`**; `coverage_verify.py --mode reinforce --strict-principal`. Contract: [docs/coverage-reinforce-principal-contract.json](docs/coverage-reinforce-principal-contract.json). Fixtures: `coverage-594-shell-reinforce-principal-minimal`, `coverage-639-formula-reinforce-principal-minimal`, `coverage-reinforce-principal-bad-missing-fixture-merge`.

**Round 2 TEST-PRECON principal (step 6/8, 2026-06-18):** Shipped ref **`downstream_hints`** → **`session_placeholders`** (dual-account tokens), discover **`ref_principal_provision`** → **`pc-setup`** cluster, deferral-keyed skip-deepen; `precon_verify.py --strict-principal` / `--mode principal`. Contract: [docs/precon-principal-contract.json](docs/precon-principal-contract.json). Fixtures: `precon-594-shell-principal-minimal`, `precon-639-formula-principal-minimal`, `precon-principal-bad-missing-provision`.

**Round 2 CLOSE principal (step 8/8, 2026-06-18):** Shipped Phase **E¾** terminal cross-artifact principal lint: provision chain, placeholder/deferral parity, delegated tests-leg checks; `close_verify.py --mode principal --strict-principal`. Contract: [docs/close-principal-contract.json](docs/close-principal-contract.json). Fixtures: `principal-594-pass`, `principal-639-pass` under `automation/tools/fixtures/close/`. **Round 2 correction program (steps 1–8) complete.**

**Plan 2 (COVERAGE, 2026-06-18):** Shipped topology consumption on `-coverage.json`: **`emit_layout`** (`formula_first` | `shell_first`), **`topology_provenance`**, check **`delivery_status`** / **`oracle_rule_id`**; playbook phases **1**, **3**, **4**, **8**–**9**, **13**–**14**; `coverage_verify.py --strict-topology`. Fixtures: `automation/tools/fixtures/coverage/` (639 formula, 594 shell). Legacy coverage without topology unchanged.

**Plan 3 (ANALYSE, 2026-06-18):** Shipped topology gap kinds (`delivery_known_fail`, `delivery_excluded`, `surface_oracle_unresolved`, `delivery_coverage_drift`); playbook phases **1**, **2**–**3**, **5**, **10**; `exploration_suppressed` for failed/excluded delivery; `analysis_verify.py --strict-topology`. Fixtures: `automation/tools/fixtures/analysis/` (639 deferred, 594 delivery, oracle-unresolved slice).

**Plan 4 (TEST-DISCOVER, 2026-06-18):** Shipped topology consumption on `-discover.json`: delivery **`exploration_suppressed`** → ledger **`tooling_blocked`** (not **`scope_gap`**); **`verification_affordances[].oracle_binding`** from ref/coverage oracle topology; playbook Steps **A**, **B**, **E**, **F**, **G**; `discover_verify.py --strict-topology`. Fixtures: `automation/tools/fixtures/discover/` (639 formula no-op, 594 shell oracle + delivery blocked).

**Plan 5 (COVERAGE-REINFORCE, 2026-06-18):** Shipped topology merge on pass-2 coverage: discover **`oracle_binding`** / **`topology_surface_id`** → **`detail_lines`**; delivery **`tooling_blocked`** skip-deepen; playbook phases **1**–**4**; `epic_helper_affordances.py` topology fields; `coverage_verify.py --mode reinforce`. Fixtures: `coverage-639-formula-reinforce-minimal`, `coverage-594-shell-reinforce-minimal`.

**Plan 6 (TEST-PRECON, 2026-06-18):** Shipped topology consumption on `-precon.json`: Phase **1** ref/coverage/discover topology load + **`skip_deepen`**; archetype **`command_patterns`** (`ladder_step` for metrics, widget observation keys for shell_first); oracle **`pattern_ref`** on **`case_outline[]`**; Phase **4D** surface batches; `precon_verify.py --strict-topology`. Fixtures: `automation/tools/fixtures/precon/` (639 formula, 594 shell). Handoff → **Plan 7 (TEST-PREP)**.

**Plan 7 (TEST-PREP, 2026-06-18):** Shipped topology consumption on `-tests.json`: Phase **1** PRECON/coverage/ref topology load; **8b** **`pattern_ref`** expansion for ladder + widget observation keys; **`platform_reuse_annex`**; `test_prep_verify.py --strict-topology`. Fixtures: `tests-639-formula-minimal`, `tests-594-shell-minimal` under `automation/tools/fixtures/test_prep/`.

**Plan 8 (CLOSE, 2026-06-18):** Shipped terminal cross-artifact topology lint (Phase E½) and Round 2 principal lint (Phase E¾): `close_verify.py --mode topology --strict-topology` / `--mode principal --strict-principal`. Fixtures: `automation/tools/fixtures/close/`. **Round 1 Plans 1–8 + Round 2 steps 1–8 correction programs complete.**

**`CLEAN:` full run (2026-06-05):** **P** `origin/personal` → **`a8bb3a9`**; **T** `team/team` → **`4a05e09`** (force-push; AGENTS.team.md forbidden-substring fix); **U** `releases/public-1.6` → **`6b29ee1`**. Manual public strip: skills/hooks/auto-tests (apply_public gap). **Postflight FAIL:** GitHub default on `agentic-epic-helper-releases` still **`public-1.5`** — set default to **`public-1.6`**, delete **`public-1.5`**, then `clean_verify.py --mode public_remote --superseded public-1.5` + `--mode postflight`.

**Draft+truth v3 (scenario intent, 2026-06-18):** **TEST-PRECON removed** from production chain. **`scenario_groups[]`** on frozen coverage; **TEST-PREP** default **`scenario_intent`**. **`/epic-helper` v4** (two gates). CLOSE: **three** root `.md`. Master [docs/draft-truth-contract.json](docs/draft-truth-contract.json) `program_complete: true`.

**Pipeline + HOW-TO alignment review (2026-06-19):** Operator docs synced to v3 — [HOW-TO.md](HOW-TO.md) rewrite; [`.cursor/commands/epic-helper.md`](.cursor/commands/epic-helper.md) v4; slim [automation/docs/epic-helper.md](automation/docs/epic-helper.md); drift fixes in coverage-reinforce, clean, ground, qa-artifacts, harness-map, epics/README; contracts: scenario_groups in coverage-draft-truth, scenario_intent in test-prep-tbd; audit note: [automation/temp/pipeline-v3-audit.md](automation/temp/pipeline-v3-audit.md). Verifiers green (scenario_intent + corner-harness-verify full).

**Draft+truth v2 (discover linker slim, 2026-06-18):** TEST-DISCOVER linker-only; helper v3 two gates.

**Draft+truth pipeline refactor (Round 3, 2026-06-18):** Shipped **`docs/draft-truth-contract.json`** master index. Bounded machine loop **COVERAGE → GROUND → ANALYSE** (max 2 rounds, `fix_breadth=yes`), human **coverage_review** gate with **`coverage_frozen_at`**, downstream map-only packaging. New **`GROUND:`** pipeline + `ground_verify.py`. **COVERAGE-REINFORCE** legacy opt-in only. Calibrate stays out-of-band after CLOSE.

**CRT-663** (manual path): coverage v1 done; operator may continue **ANALYSE** / **TEST-DISCOVER (linker)** without helper.

**CRTQA stats v5** promoted: test-first corpus, per-user `latest-<user>.md`, contract [docs/epic-stats-contract.json](docs/epic-stats-contract.json), library under `automation/tools/epic_stats/`. Experiment `temp/stats-test/` removed. Regenerate per engineer via `/epic-stats mode=initial_assessment`.

**Smoke specs** landed: [auto-tests/specs/schema.json](auto-tests/specs/schema.json) + [smoke-manifest.json](auto-tests/specs/smoke-manifest.json) (32 rows, CRTQA-10247). **``** + operator profile (v2). Pytest/Playwright implementation **next** via teach phases.

## Next

1. **`/epic-helper resume` CRT-671** — **coverage_review** gate: edit `CRT-671-coverage.md` / `scenario_groups[]`, then resume.
2. **CRT-594** — operator **`coverage_review`** gate if machine loop resume pending.
3. **``** — confirm `ct_qa` env profile; phase 0 for first manifest row.

## Anchors

- Teach / smoke: [docs/auto-tests-contract.json](docs/auto-tests-contract.json) · [auto-tests/](auto-tests/)
- Charter: [docs/grounding-integration.json](docs/grounding-integration.json)
- Doctrine §14: [docs/harness-principles.md](docs/harness-principles.md)
- Epic (closed): `epics/CRT-639/context/`

## Last updated

- **Date**: 2026-06-30 — **`/epic-helper resume` CRT-671:** **ANALYSE** complete — 7 gaps (6 delivery_known_fail + 1 console_probe_blocked); `draft_truth_recommendation: human_coverage_review`; helper **`awaiting_gate: coverage_review`**.
- **Date**: 2026-06-30 — **`/epic-helper resume` CRT-671:** **GROUND** complete — `show order last [n] [open]` syntax verified on chk-e1; `ground_verify.py --mode emit` OK; helper at **`analyse`**.
- **Date**: 2026-06-30 — **`/epic-helper resume` CRT-671:** **COVERAGE v1** complete — `CRT-671-coverage.json` draft_truth pass 1 (14 checks, 6 known_fail); `coverage_verify.py --mode draft_truth --strict-topology --strict-principal` OK; helper at **`ground`**.
- **Date**: 2026-06-30 — **`/epic-helper CRT-671`** cold start: console gate pass; **EPIC-PREP** emitted `epics/CRT-671/CRT-671-ref.json` (widget_ui, 3 obligations, 5 surfaces, 6 delivery notes); `epic_prep_verify.py` reconcile+scenario+ref `--strict-topology --strict-principal` OK; helper at **`coverage_v1`**.
- **Date**: 2026-06-29 — **`/epic-helper resume` CRT-594:** **ANALYSE** complete — 0 gaps; `draft_truth_recommendation: human_coverage_review`; helper **`awaiting_gate: coverage_review`**.
- **Date**: 2026-06-29 — **`/epic-helper resume` CRT-594:** **GROUND** complete — runtime probes on chk-009/chk-011; `ground_verify.py --mode emit` OK; helper at **`analyse`**.
- **Date**: 2026-06-29 — **`/epic-helper resume` CRT-594:** **COVERAGE v1** complete — `CRT-594-coverage.json` draft_truth pass 1; `coverage_verify.py --mode draft_truth --strict-topology --strict-principal` OK; helper at **`ground`**.
- **Date**: 2026-06-29 — **`/epic-helper` CRT-594** cold start: console gate pass; **EPIC-PREP** emitted `epics/CRT-594/CRT-594-ref.json` (widget_ui, 5 obligations, 6 surfaces); verifiers reconcile+scenario+ref `--strict-topology --strict-principal` OK; helper at **`coverage_v1`**.
- **Date**: 2026-06-19 — **`/epic-helper` CRT-594:** **CLOSE** complete — `epic_verdict: pass`; JSON archived to `context/`; four root `.md`; helper → `context/helper/`; full chain env→close done.
- **Date**: 2026-06-19 — **`/epic-helper` CRT-594:** **TEST-DISCOVER** complete — Phase 0c dxtrade5+webbroker smoke pass; `CRT-594-discover.json` (11/11 closure, `discovery_status: incomplete`); `discover_verify.py --strict-topology --strict-principal` OK; `helper/affordances-slice.json` (8 rows); session at **`coverage_reinforce`**.
- **Date**: 2026-06-19 — **`/epic-helper CRT-594` cold start:** env probe pass; **EPIC-PREP** emitted `epics/CRT-594/CRT-594-ref.json` (widget_ui, 5 obligations, 6 surfaces); `epic_prep_verify.py` reconcile+ref `--strict-topology` OK; helper `session.json` at `coverage_v1` / gate `coverage_review`.
- **Date**: 2026-06-18 — **ANALYSE correction (3/8):** [docs/analysis-topology-contract.json](docs/analysis-topology-contract.json) + template; playbook topology gaps + delivery suppression; `analysis_verify.py --strict-topology`; fixtures under `automation/tools/fixtures/analysis/`.
- **Date**: 2026-06-18 — **COVERAGE correction (2/8):**** [docs/coverage-topology-contract.json](docs/coverage-topology-contract.json) + template fields; playbook topology consume + dual emit; `coverage_verify.py --strict-topology`; fixtures 639/594 under `automation/tools/fixtures/coverage/`.
- **Date**: 2026-06-18 — **EPIC-PREP correction (1/8):** topology contract + template + playbook steps 2c/3f–3h; `epic_prep_verify.py` topology mode + `--strict-topology`; fixtures 639/594; calibrate stub `.cursor/calibrate/CRT-594-gold/CRT-594-gold-meta.json`.
- **Date**: 2026-06-12 — **CLEAN stats guard + CRTQA restore:** `clean_stats_personal.py` backup/restore around Phase T (`stats_personal_preserve` in clean-contract); peer-reviewed `latest-mshpak.md` / `latest-amukanova.md` + state (CRT-594/639 attestation, arodzevich comparison, team rollup with per-user table) restored from Downloads + Jira harvest.
- **Date**: 2026-06-12 — **CRTQA stats restore:** Phase T team strip (`clean_apply_team.py` → `rmtree stats/epic-stats/**`) wiped gitignored `state/` + `latest-*.md` in shared checkout during 2026-06-05 CLEAN; regenerated all five `latest-<user>.md` + `latest-team.md` from Jira harvest (state under `stats/epic-stats/state/`).
- **Date**: 2026-06-10 — **`/release-notes 459`:** no issues in master or FX Spot JQL — both lanes skipped (no `releases/459/` files).
- **Date**: 2026-06-10 — **`/release-notes 457-458`:** `releases/457-458/457-458-rns.md` (v457: 2 master) + `457-458-rns-fx.md` (v457: 8 CR, 2 DR); v458 empty (both lanes skipped in output).
- **Date**: 2026-06-08 — **`/epic-helper CRT-663`** (operator bound CRT-663 not closed CRT-639): ANALYSE v2 emitted; helper `session.json` at `discover`; operator-feedback for COVERAGE-REINFORCE atomic E2E; env probe console FAIL.
- **Date**: 2026-06-05 — **`CLEAN: proceed` full run:** P **`a8bb3a9`**, T **`4a05e09`**, U **`public-1.6`** / **`6b29ee1`**; postflight blocked on GitHub default; `releases` remote added locally; AGENTS.team.md substring fix for team verify.
- **Date**: 2026-06-04 — **CLEAN + HOW-TO tier update:** stats/coaches personal-only; `/epic-helper` on team (full), public (concept in HOW-TO); HOW-TO restructured (shared intro, helper + prep table); tier matrix + `clean_verify` team checks updated.
- **Date**: 2026-06-04 — **`/epic-helper` orchestrator v1:** `docs/epic-helper-contract.json`, command/skill, `COVERAGE-REINFORCE:` pipeline + router, `epic_helper_affordances.py`, `close_archive` helper archive, harness-map/AGENTS/HOW-TO/README, golden fixture; `corner-harness-verify` full OK.
- **Date**: 2026-06-04 — **COVERAGE: CRT-663** (production): `CRT-663-coverage.json` v2 + `.md` — archetype `widget_ui`, 15 checks, 16 matrix rows, 13 obligations covered; `coverage_verify.py` obligations+emit OK; `temp/` deleted.
- **Date**: 2026-06-04 — **EPIC-PREP: CRT-663** (production): `CRT-663-ref.json` v4 — FX_SPOT visibility in Orders/Transactions/Positions (Web+WB+Adaptive parity); 14 `obligations_proposed[]`; workflow states from CT Order Statuses; child CRs XT-7210–7212; `epic_prep_verify.py` ref+reconcile OK; `temp/` deleted.
- **Date**: 2026-05-25 — **Smoke specs:** `schema.json` + `smoke-manifest.json` (CRTQA-10247, 32 rows); teach cold reads; CLEAN team-keep for minimal specs; manifest verify in `corner-harness-verify`.
- **Date**: 2026-05-25 — **Teach harness prep:** `auto-tests/` entity; `` + ` stop`; contract, CLEAN tiers, `corner-harness-verify` teach checks.
- **Date**: 2026-05-25 — **Karpathy Pass 4 (complete):** opt-in `/SKILL.md`; `docs/-contract.json`; charter `optional_skills` + `pass4_artifacts`; T1 ``; CLEAN tier rows; `corner-harness-verify` karpathy checks; pipelines unchanged.
- **Date**: 2026-05-25 — **Grounding remediation Pass 3 (complete):** qa-artifacts pointer; harness-principles section 16 paths; charter `remediation.status=complete`; final regression pass.
- **Date**: 2026-05-25 — **Grounding remediation Pass 2:** soft_core in charter; preservation; HOW-TO guard advisory; README coaches; clean-publish-tier-matrix.md grounding table.
- **Date**: 2026-05-25 — **Grounding remediation Pass 1:** `` + `harness_hygiene` T1; pipeline-router recap; golden checks in `corner-harness-verify`; [automation/docs/corner-harness-verify.md](automation/docs/corner-harness-verify.md).
- **Date**: 2026-05-25 — **Grounding remediation Pass 0:** charter `passes` 1+2 complete; sessionStart-only hooks; ASCII `inject-corner.json`; regression block incl. epic_prep + coverage smoke; `corner-harness-verify` mojibake + hooks_session_start_only gates.
- **Date**: 2026-05-25 — **Grounding-kit pass 1:** `/`, `/`, corner rules (`intent-`, `delegation-`, `preservation-`, `communication-`), `docs/grounding-integration.json`, harness-principles §14; pass 2 scaffold (`hooks.json`, `inject-corner.json`, `corner-harness-verify.ps1`).
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
- **Date**: 2026-05-19 — **Benchmark retired → `/epic-calibrate`**: removed `.cursor/benchmark/`, `docs/benchmark-contract.md`, benchmark Python tools; added `.cursor/calibrate/`, `docs/calibrate-contract.json`, `calibrate_verify.py`, playbooks/commands/docs; HOW-TO §3 rewritten.
- **Date**: 2026-05-19 — **`/epic-stats`** `initial_assessment` for `arodzevich`: cohort **2** TCD tasks (CRTQA-10034 corpus, CRTQA-10132 comparison); state `stats/epic-stats/state/last-sync.json` v3; report `stats/epic-stats/latest.md` (corpus benchmark pending — n under 4 per category).
- **Date**: 2026-05-19 — **Harness doc reconciliation** complete: [HOW-TO.md](HOW-TO.md), [epics/README.md](epics/README.md), [README.md](README.md), [sync.md](.cursor/pipelines/sync.md) registry, scratch WS-A/WS-C/session notes; templates post-`context/` notes; **TEST-EXEC** refs removed from durable docs (intentional “replaces TEST-EXEC” in this file only).
- **Date**: 2026-05-19 — **`CLOSE:`** pipeline implemented: [`docs/close-contract.json`](docs/close-contract.json), [`.cursor/pipelines/close.md`](.cursor/pipelines/close.md), verifiers [`close_verify.py`](automation/tools/close_verify.py) / [`close_archive.py`](automation/tools/close_archive.py).
- **Date**: 2026-05-19 — **ANALYSE v2** + **EPIC-PREP/COVERAGE obligation patch** (see prior entries).

## Current focus

- **CRT-663:** **`/epic-helper`** — **COVERAGE-REINFORCE** pass 2 (`coverage_pass: 2`, 24 checks, atomic Market/Limit/Stop E2E); next **TEST-PRECON**.
- **CRT-639:** **closed** — do not rerun upstream pipelines without restoring JSON from `context/` to epic root.
- **Release notes:** v3 playbook + contract; run `/release-notes` to populate `releases/<batch>/` (no corner-map).
- **Harness:** Mandatory-chain doc reconciliation (discover always required in all playbooks) — **deferred** separate pass.

Doctrine: **[docs/harness-principles.md](docs/harness-principles.md)** (CLOSE archive note in §9).

## Blockers

- **CLEAN postflight** — `releases` default branch still **`public-1.5`**; cannot delete until default is **`public-1.6`** (see Resume).
- **CRT-1738 numeric oracle** — Jira notes dependency on **XT-7911** (`obl-015` deferral in ref); reflected in excluded checks and analysis gaps.
- **user-mcp-atlassian** for live pipeline re-runs.

## Next steps

1. **CLEAN finish:** GitHub → `agentic-epic-helper-releases` → default branch **`public-1.6`** → delete **`public-1.5`** → `python automation/tools/clean_verify.py --mode public_remote --superseded public-1.5` + `--mode postflight`.
2. Human: create CRTQA test issues from **`CRT-639-tests.md`** (generation mode — no CRTQA keys in repo).
3. To re-run **EPIC-PREP** / **COVERAGE** / etc. on CRT-639: move JSON from `epics/CRT-639/context/` back to epic root first — [HOW-TO.md](HOW-TO.md).

## Notes

- **Deferred (next pass):** mandatory-chain doc wording (optional → required for discover/precon); automated un-archive.
- **Calibrate v1.1:** `calibrate_verify.py` adds `gold_distinct`, `compare`, `NO_ACTIONABLE_DELTA`; CRT-639 seed gold still **prod-identical** → `/epic-calibrate` stops at `GOLD_NOT_DISTINCT` until real oracle JSON.
- **Retired:** **TEST-EXEC** / Playwright chain step — use **`CLOSE:`** for integrity + archive; chrome-devtools remains for discover/precon/prep ad-hoc only.
