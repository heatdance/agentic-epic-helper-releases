# Per-epic context (`<EPIC-KEY>-ref.json`)

For **one Epic at a time**, the durable handoff file is **`epics/<EPIC-KEY>/<EPIC-KEY>-ref.json`** (e.g. `epics/CRT-XXXX/CRT-XXXX-ref.json`). Copy the schema from [templates/epic-ref.json](templates/epic-ref.json).

**Pipeline `EPIC-PREP:`** — playbook: [`.cursor/pipelines/epic-prep.md`](../.cursor/pipelines/epic-prep.md). Optional trigger token **`repo=…`** for a **capped** Bitbucket code search (step **5b**), after Yogi snippets and precision pass **3.4** — use **`PROJECT_KEY/repo_slug`** on internal Stash (e.g. **`BRO/xt`**, **`CAN/corner`**) or Bitbucket Cloud **`workspace/slug`**; see [docs/project.json](../docs/project.json) **`bitbucket`**. Persist **`sources.bitbucket_repo`**, **`sources.bitbucket_searched_at`**, **`implementation.hits`** (`source_phase: epic_prep`), and **`implementation.skipped_reason`** when skipped. Repo resolution: trigger **`repo=`** → prior ref (read before template overwrite) → [docs/project.json](../docs/project.json) **`bitbucket.default_repo`**. It uses **`epics/<KEY>/temp/`** for raw exports during the run and **deletes `temp/`** when finished; the ref must not contain `/temp/` paths.

Fill **business context**, **synthesis**, **`client_shell_impact`** (Corner Trader surfaces vs **Adaptive** — mandatory per [`.cursor/pipelines/epic-prep.md`](../.cursor/pipelines/epic-prep.md) step 2b: short stable **`note`**, verbatim **`evidence`**; fixed template sentence for **`qa_default_both`** when applicable; see [docs/qa-project.json](../docs/qa-project.json) `product_outline`), **design**, **`requirements[]`** (Yogi keys + **token-light** `snippet_text`; **`snippet_status`** / **`snippet_failure_reason`** when extract fails; EPIC-PREP steps **3b** retry + step **8** finalize gate for **jira-linked** keys unless **`deferral_accepted`** in `validation_log`), **implementation**, and **traversal** per template `_comment`. **Schema** `schema_version` **3** adds **implementation** + Bitbucket **sources** fields. Workflow detail: [automation/docs/yogi-url-resolve.md](../automation/docs/yogi-url-resolve.md).

# Per-epic coverage (`<EPIC-KEY>-coverage.json` / `.md`)

After **`epics/<KEY>/<KEY>-ref.json`** exists, pipeline **`COVERAGE:`** + key (optional **`repo=WORKSPACE/REPO_SLUG`** — overrides epic-ref **`sources.bitbucket_repo`** and [docs/project.json](../docs/project.json) **`bitbucket.default_repo`**) produces:

- **`epics/<KEY>/<KEY>-coverage.json`** — structured matrix, checks, grounding audit, `validation_log` (from [templates/coverage-ref.json](templates/coverage-ref.json)). Includes **`epic_verification_focus`**, per-row **`verification_role`**, optional **`checks[].calculation_contract`** (metrics ladders), surfaces seeded from **`client_shell_impact`** (including Adaptive). Phase **7** **merges** epic-ref **`implementation.hits`** into **`implementation_hits`** (dedupe, **`impl-001`…** ids), then runs additional Bitbucket search when **`sources.bitbucket_repo`** is resolved.
- **`epics/<KEY>/<KEY>-coverage.md`** — Jira Smart Checklist paste body.

Playbook: [`.cursor/pipelines/coverage.md`](../.cursor/pipelines/coverage.md) — deterministic **`coverage_matrix[].id`**, **`supporting` vs `out_of_epic`** ladder, verbatim **primary focus** block in Smart Checklist (first substantive **`##`**), optional scenario discipline. Uses **`epics/<KEY>/temp/`** the same way as epic-prep; **delete `temp/`** when finished; durable files must not reference `/temp/`.

**Router**: [.cursor/rules/pipeline-router.mdc](../.cursor/rules/pipeline-router.mdc).

# Per-epic analysis (`<EPIC-KEY>-analysis.json` / `.md`)

After **`epics/<KEY>/<KEY>-ref.json`** exists (and ideally **`epics/<KEY>/<KEY>-coverage.json`** from `COVERAGE:`), pipeline **`ANALYSE:`** + key (optional **`include_closed=yes`**) produces:

- **`epics/<KEY>/<KEY>-analysis.json`** — structured summary, gaps, questions, known issues, Jira search audit, optional **`coverage_mutations`** (from [templates/analysis-ref.json](templates/analysis-ref.json)).
- **`epics/<KEY>/<KEY>-analysis.md`** — human-readable four-section view (Summary, Gaps, Questions, Known issues).

When **`-coverage.json`** is present, the playbook **reconciles** known issues against **`epic_verification_focus`** / matrix / checks / **`explicitly_out_of_scope`**, then may append **Known issue** **`>`** detail lines to **`checks[].detail_lines`** (OPEN by default; dedupe by issue key). Same **`epics/<KEY>/temp/`** rule: delete when finished.

Playbook: [`.cursor/pipelines/analysis.md`](../.cursor/pipelines/analysis.md).

# Per-epic test prep (`<EPIC-KEY>-tests.json` / `.md`)

After **`epics/<KEY>/<KEY>-coverage.json`** exists, pipeline **`TEST-PREP:`** + key (optional **`map_only=yes`**) produces:

- **`epics/<KEY>/<KEY>-tests.json`** — `test_bundles[]` (minimal Jira-ready titles + `covers_check_ids` from coverage `checks[].id`), `jira_test_search`, `existing_tests_considered[]`, `excluded_checks_with_reason[]`, **`reverse_validation`** (coverage gaps, orphan bundles), `validation_log` (from [templates/tests-ref.json](templates/tests-ref.json)).
- **`epics/<KEY>/<KEY>-tests.md`** — mapping table + draft **Preconditions / Actions / Results / Peculiarities** per [docs/tc-ref](../docs/tc-ref) (or map-only stub).

**Compliance first**: internal workflow uses the Smart Checklist as the matrix; Jira **regression** classification is client-facing. Bundles are E2E combinatoric instructions for humans—not one test per bullet when one session suffices. **Full draft prose** (when not `map_only`) is authored **one bundle per subprocess** (e.g. Cursor Task), after shells are planned in phase 8a—see playbook. **Jira reuse**: steps only from **`jira_get_issue`** fields; otherwise `[GAP]` / `[TBD]`. **v1** does not use Playwright, QA DB, or SSH/console execution for verification.

Playbook: [`.cursor/pipelines/test-prep.md`](../.cursor/pipelines/test-prep.md). **Router**: [.cursor/rules/pipeline-router.mdc](../.cursor/rules/pipeline-router.mdc).

# Per-epic test exec (`<EPIC-KEY>-test-exec.json`, `tests/*.spec.ts`)

After **`epics/<KEY>/<KEY>-tests.json`** exists (from **`TEST-PREP:`**), pipeline **`TEST-EXEC:`** + key (optional **`base_url=…`**, **`skip_postgres=yes`**, **`include_blocked=yes`**, **`max_bundles=N`**) may produce:

- **`epics/<KEY>/<KEY>-test-exec.json`** — run/manifest per [templates/test-exec-ref.json](templates/test-exec-ref.json) (per-bundle status, traceability to `covers_check_ids`, no `/temp/` paths).
- **`epics/<KEY>/tests/*.spec.ts`** — Playwright specs (one per materialized `bundle_id`, e.g. `tb-001.spec.ts`).

**Optional and non-gating**: depends on app URL, **user-mcp-playwright**, and optionally **postgres-ctqa** (SSH tunnel + global MCP). Does **not** use dxCore console, SSH to hosts, or webbroker-only setup; such bundles are **`blocked`** unless the user passes **`include_blocked=yes`**. Raw scratch lives only in **`epics/<KEY>/temp/`** (`test-exec-*`); **delete `temp/`** when finished—same lifecycle as other epic pipelines.

`-tests.json` **schema_version 2** adds optional **`test_bundles[].automation`** (`feasibility`, `blocked_reason`) for alignment with exec; older files remain valid.

Playbook: [`.cursor/pipelines/test-exec.md`](../.cursor/pipelines/test-exec.md). **Router**: [.cursor/rules/pipeline-router.mdc](../.cursor/rules/pipeline-router.mdc).

# Repo-wide harness (no Epic key)

These chat triggers are defined in [.cursor/rules/pipeline-router.mdc](../.cursor/rules/pipeline-router.mdc); they reconcile or export the **repository** rather than a single `epics/<KEY>/` tree.

- **`PUBLIC-SCRUB:`** — sanitize for public export; run only on branch **`release`** — [`.cursor/pipelines/public-scrub.md`](../.cursor/pipelines/public-scrub.md).
- **`SYNC:`** — keep router, harness-map, AGENTS, README, HOW-TO, and related pointers aligned; run only on **`develop`** or **`main`** — [`.cursor/pipelines/sync.md`](../.cursor/pipelines/sync.md).
