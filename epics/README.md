# Per-epic context (`<EPIC-KEY>-ref.json`)

For **one Epic at a time**, the durable handoff file is **`epics/<EPIC-KEY>/<EPIC-KEY>-ref.json`** (e.g. `epics/CRT-XXXX/CRT-XXXX-ref.json`) while the epic is **open**; after **`CLOSE:`**, JSON moves to **`epics/<KEY>/context/`** (four human **`.md`** stay at epic root). Copy the schema from [templates/epic-ref.json](templates/epic-ref.json).

**Pipeline `EPIC-PREP:`** — playbook: [`.cursor/pipelines/epic-prep.md`](../.cursor/pipelines/epic-prep.md). Optional trigger token **`repo=…`** for a **capped** Bitbucket code search (step **5b**), after Yogi snippets and precision pass **3.4** — use **`PROJECT_KEY/repo_slug`** on internal Stash (e.g. **`BRO/xt`**, **`CAN/corner`**) or Bitbucket Cloud **`workspace/slug`**; see [docs/project.json](../docs/project.json) **`bitbucket`**. Persist **`sources.bitbucket_repo`**, **`sources.bitbucket_searched_at`**, **`implementation.hits`** (`source_phase: epic_prep`), and **`implementation.skipped_reason`** when skipped. Repo resolution: trigger **`repo=`** → prior ref (read before template overwrite) → [docs/project.json](../docs/project.json) **`bitbucket.default_repo`**. It uses **`epics/<KEY>/temp/`** for raw exports during the run and **deletes `temp/`** when finished; the ref must not contain `/temp/` paths.

Fill **business context**, **synthesis**, **`client_shell_impact`** (Corner Trader surfaces vs **Adaptive** — mandatory per [`.cursor/pipelines/epic-prep.md`](../.cursor/pipelines/epic-prep.md) step 2b: short stable **`note`**, verbatim **`evidence`**; fixed template sentence for **`qa_default_both`** when applicable; see [docs/qa-project.json](../docs/qa-project.json) `product_outline`), **design**, **`requirements[]`** (Yogi keys + **token-light** `snippet_text`; **`snippet_status`** / **`snippet_failure_reason`** when extract fails; EPIC-PREP steps **3b** retry + step **8** finalize gate for **jira-linked** keys unless **`deferral_accepted`** in `validation_log`), **`obligations_proposed[]`**, **implementation**, and **traversal** per template `_comment`. **Schema** **v4** (`obligations_proposed[]`). Verifier: [epic-prep-verify.md](../automation/docs/epic-prep-verify.md). Workflow detail: [automation/docs/yogi-url-resolve.md](../automation/docs/yogi-url-resolve.md).

# Per-epic coverage (`<EPIC-KEY>-coverage.json` / `.md`)

After **`epics/<KEY>/<KEY>-ref.json`** exists, pipeline **`COVERAGE:`** + key (optional **`repo=WORKSPACE/REPO_SLUG`** — overrides epic-ref **`sources.bitbucket_repo`** and [docs/project.json](../docs/project.json) **`bitbucket.default_repo`**) produces:

- **`epics/<KEY>/<KEY>-coverage.json`** — structured matrix, checks, grounding audit, `validation_log` (from [templates/coverage-ref.json](templates/coverage-ref.json), **schema v2**). Includes **`epic_verification_focus`**, **`obligations_coverage`**, per-row **`verification_role`**, optional **`checks[].calculation_contract`** (metrics ladders), surfaces seeded from **`client_shell_impact`** (including Adaptive). Phase **7** **merges** epic-ref **`implementation.hits`** into **`implementation_hits`** (dedupe, **`impl-001`…** ids), then runs additional Bitbucket search when **`sources.bitbucket_repo`** is resolved. Verifier: [coverage-verify.md](../automation/docs/coverage-verify.md).
- **`epics/<KEY>/<KEY>-coverage.md`** — Jira Smart Checklist paste body.

Playbook: [`.cursor/pipelines/coverage.md`](../.cursor/pipelines/coverage.md) — deterministic **`coverage_matrix[].id`**, **`supporting` vs `out_of_epic`** ladder, verbatim **primary focus** block in Smart Checklist (first substantive **`##`**), optional scenario discipline. Uses **`epics/<KEY>/temp/`** the same way as epic-prep; **delete `temp/`** when finished; durable files must not reference `/temp/`.

**Router**: [.cursor/rules/pipeline-router.mdc](../.cursor/rules/pipeline-router.mdc).

# Per-epic analysis (`<EPIC-KEY>-analysis.json` / `.md`)

After **`epics/<KEY>/<KEY>-coverage.json`** exists (and ideally **`-ref.json`**), pipeline **`ANALYSE:`** + key (optional **`known_issues=yes`** default off, **`resolve=no`**, **`include_closed=yes`** with known_issues) produces:

- **`epics/<KEY>/<KEY>-analysis.json`** — **schema v2**: **`gaps[]`**, **`exploration_suppressed[]`**, optional **`coverage_writebacks`**; contract [analysis-gap-contract.json](../docs/analysis-gap-contract.json).
- **`epics/<KEY>/<KEY>-analysis.md`** — **gaps-first** human view; optional **Known issues** section only when **`known_issues=yes`**.

Known-issue **`>`** lines on coverage apply **only** when **`known_issues=yes`**. Same **`epics/<KEY>/temp/`** rule: delete when finished. Verifier: [analysis-verify.md](../automation/docs/analysis-verify.md).

Playbook: [`.cursor/pipelines/analysis.md`](../.cursor/pipelines/analysis.md).

# Per-epic discovery (`<EPIC-KEY>-discover.json`)

**Optional** after **`epics/<KEY>/<KEY>-ref.json`** and **`epics/<KEY>/<KEY>-coverage.json`** exist (and ideally **`-analysis.json`** from `ANALYSE:`). Pipeline **`TEST-DISCOVER:`** + key produces:

- **`epics/<KEY>/<KEY>-discover.json`** only — schema [templates/discover-ref.json](templates/discover-ref.json) **v3**: **obligation closure** (**`obligation_ledger`**, **`fixture_needs`**, setup depth), delivery/PR, tooling, **`verification_affordances`**, **`test_prep_gates`**. Optional **`reference_index`** when **`crtqa_index=yes`** on **`TEST-DISCOVER:`**. **No** `-discover.md` in v1.

Playbook: [`.cursor/pipelines/test-discover.md`](../.cursor/pipelines/test-discover.md) — Steps **0** → **G**, self-heal closure loop, **`discover_verify.py`** before emit; **`epics/<KEY>/temp/`** then **delete**; no secrets or **`/temp/`** in durable JSON.

**Flow:** EPIC-PREP → COVERAGE → ANALYSE → **optional TEST-DISCOVER** → **optional TEST-PRECON** → TEST-PREP → optional **CLOSE**.

# Per-epic precondition authoring (`<EPIC-KEY>-precon.json` / `.md`)

**Optional** after **`epics/<KEY>/<KEY>-coverage.json`** exists (and ideally **`-discover.json`** from `TEST-DISCOVER:`). Pipeline **`TEST-PRECON:`** + key produces:

- **`epics/<KEY>/<KEY>-precon.json`** — **schema v5**: `test_skeleton[]` with **`case_outline[]`**, **`session_placeholders`**, **`command_patterns`**; `exploration_log[]` with **`depth_level`** / **`view_id`**; [templates/precon-ref.json](templates/precon-ref.json); depth [docs/exploration-depth-ladder.json](../docs/exploration-depth-ladder.json).
- **`epics/<KEY>/<KEY>-precon.md`** — Jira Pre-Condition paste body only (action-result; no pipeline preamble).

Playbook: [`.cursor/pipelines/test-precon.md`](../.cursor/pipelines/test-precon.md) — **0c** smoke; **Phase 4R/4D/4C** **`precon_drill`**. Verifier: [`precon_verify.py`](../automation/tools/precon_verify.py) with **`--discover`** + **`--md`**. **`epics/<KEY>/temp/`** then **delete**.

# Per-epic test prep (`<EPIC-KEY>-tests.json` / `.md`)

After **`epics/<KEY>/<KEY>-coverage.json`** exists, pipeline **`TEST-PREP:`** + key (optional **`map_only=yes`**) produces:

- **`epics/<KEY>/<KEY>-tests.json`** — `test_bundles[]` (minimal Jira-ready titles + `covers_check_ids` from coverage `checks[].id`), `jira_test_search`, `existing_tests_considered[]`, `excluded_checks_with_reason[]`, **`reverse_validation`** (coverage gaps, orphan bundles), `validation_log` (from [templates/tests-ref.json](templates/tests-ref.json)).
- **`epics/<KEY>/<KEY>-tests.md`** — mapping table + draft **Preconditions / Actions / Results / Peculiarities** per [templates/tests-ref.json](templates/tests-ref.json) **format_norms** (or map-only stub).

**Compliance first**: internal workflow uses the Smart Checklist as the matrix; Jira **regression** classification is client-facing. Bundles are E2E combinatoric instructions for humans—not one test per bullet when one session suffices. **Full draft prose** (when not `map_only`) is authored **one bundle per subprocess** (e.g. Cursor Task), after shells are planned in phase 8a—see playbook. **Jira reuse**: steps only from **`jira_get_issue`** fields; otherwise `[GAP]` / `[TBD]`. **v1** does not use Chrome DevTools MCP (`chrome-devtools`), QA DB, or SSH/console execution for verification.

Playbook: [`.cursor/pipelines/test-prep.md`](../.cursor/pipelines/test-prep.md). **Router**: [.cursor/rules/pipeline-router.mdc](../.cursor/rules/pipeline-router.mdc).

# Per-epic close (`<EPIC-KEY>-close.json`, `context/`)

After **`epics/<KEY>/<KEY>-tests.json`** exists (from **`TEST-PREP:`**), and **`-ref.json`**, **`-coverage.json`**, **`-discover.json`**, **`-precon.json`** are present, pipeline **`CLOSE:`** + key (optional **`heal=no`**) produces:

- **`epics/<KEY>/context/<KEY>-close.json`** — integrity manifest per [templates/close-ref.json](templates/close-ref.json) (ladder findings, corrections, `epic_verdict`, archive metadata). **No** `-close.md`.
- **Post-close layout:** four human **`.md`** at **`epics/<KEY>/`** root only: **`-coverage.md`**, **`-analysis.md`**, **`-tests.md`**, **`-precon.md`** (regenerated from JSON before archive). All **`*.json`** (including **`-close.json`**) under **`epics/<KEY>/context/`**. Legacy **`tests/*.spec.ts`** move to **`context/tests/`** if present.

**Documentation-only**: backward ladder L0–L4; **no** MCP, creds, or live environment. **Archive always** (including on `fail`). Rerunning upstream pipelines on a closed epic requires moving JSON out of **`context/`** first — see [HOW-TO.md](../HOW-TO.md).

Playbook: [`.cursor/pipelines/close.md`](../.cursor/pipelines/close.md). Verifier: [automation/docs/close-verify.md](../automation/docs/close-verify.md). **Router**: [.cursor/rules/pipeline-router.mdc](../.cursor/rules/pipeline-router.mdc).

# Repo-wide harness (no Epic key)

These chat triggers are defined in [.cursor/rules/pipeline-router.mdc](../.cursor/rules/pipeline-router.mdc); they reconcile or export the **repository** rather than a single `epics/<KEY>/` tree.

- **`CLEAN:`** — align harness and publish **`personal`** → team repo → **`public-M.N`** releases; **`personal` branch only** — [`.cursor/pipelines/clean.md`](../.cursor/pipelines/clean.md).

# Calibrate (post-hoc, no Epic trigger)

After Close (or when production artefacts are stable), curate operator **gold** under **`.cursor/calibrate/<KEY>-gold/`** (required **`-coverage.json`** + **`-tests.json`**) and run **`/crtqa-calibrate`** — [automation/docs/calibrate.md](../automation/docs/calibrate.md), [HOW-TO.md §3](../HOW-TO.md#3-calibrate-prod-vs-operator-gold).
