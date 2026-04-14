# Prompt scaffold: combined QA task (Jira + Confluence + codebase)

Copy or adapt this into chat. **Jira and Confluence**: always **user-mcp-atlassian** (read tool schemas first). **Code**: narrow search and bounded reads only.

## Inputs (fill in)

- **Jira issue key(s)**: <!-- -->
- **Confluence page(s) or search terms** (if any): <!-- -->
- **Code area or repo hint** (if any): <!-- -->
- **Deliverable**: <!-- test draft norms/schema: epics/templates/tests-ref.json (format_norms) + TEST-PREP; DR per docs/dr-ref; Epic Smart Checklist via COVERAGE: + .cursor/pipelines/coverage.md; Epic analysis via ANALYSE: + .cursor/pipelines/analysis.md; Epic regression test drafts via TEST-PREP: + .cursor/pipelines/test-prep.md (after coverage); optional E2E materialization via TEST-EXEC: + .cursor/pipelines/test-exec.md (after -tests.json; env-dependent); harness drift via SYNC: + .cursor/pipelines/sync.md on develop/main only -->

## Ordered workflow for the agent

1. Apply [docs/harness-map.json](../../docs/harness-map.json): read **T0** (`qa-handoff.md`, `AGENTS.md`), then only the **T1** packages that match this task’s language (e.g. [docs/project.json](../../docs/project.json) for product/fork, [docs/qa-project.json](../../docs/qa-project.json) for Corner QA scope—**not** all JSON files every time). Use those files for Confluence/Jira **scope** before MCP.
2. Read and update context from [qa-handoff.md](../../qa-handoff.md) (read first; plan to update last).
3. **Jira**: MCP fetch issues → extract AC and scope; note gaps.
4. **Epic ref** (when work is Epic-scoped or you need stored Yogi snippets): create or refresh `epics/<EPIC-KEY>/<EPIC-KEY>-ref.json` from [epics/templates/epic-ref.json](../../epics/templates/epic-ref.json); for a full preflight run use **`EPIC-PREP:`** + key and follow [`.cursor/pipelines/epic-prep.md`](../pipelines/epic-prep.md) (delete `epics/<KEY>/temp/` when done). Fill **`client_shell_impact`** (Corner Trader vs **Adaptive** per [docs/qa-project.json](../../docs/qa-project.json)) and `requirements[]` with [yogi_resolve.py](../../automation/tools/yogi-tool/yogi_resolve.py) / [yogi_snippet.py](../../automation/tools/yogi-tool/yogi_snippet.py); set **`snippet_status`** / **`snippet_failure_reason`** when a snippet cannot be extracted. See [epics/README.md](../../epics/README.md).
5. **Epic coverage** (Smart Checklist draft + grounding audit): after `-ref.json` exists, use **`COVERAGE:`** + Epic key (optional **`repo=WORKSPACE/REPO`**, optional **`focus=...`**) and follow [`.cursor/pipelines/coverage.md`](../pipelines/coverage.md) → `epics/<KEY>/<KEY>-coverage.json` and `<KEY>-coverage.md` (`epic_verification_focus`, matrix `verification_role`, **calculation ladders** / `calculation_contract`, **out_of_epic** fork rules, per-surface lines including Adaptive when in scope). Delete `epics/<KEY>/temp/` when done.
6. **Epic requirement analysis** (optional): use **`ANALYSE:`** + Epic key (optional **`include_closed=yes`**) and follow [`.cursor/pipelines/analysis.md`](../pipelines/analysis.md) → `epics/<KEY>/<KEY>-analysis.json` and `<KEY>-analysis.md`; loads **`-ref.json`** / **`-coverage.json`** from disk when present; may append **Known issue** **`>`** lines to coverage. Delete `epics/<KEY>/temp/` when done.
6b. **Epic regression test drafts** (optional): after **`-coverage.json`** exists, use **`TEST-PREP:`** + Epic key (optional **`map_only=yes`**) and follow [`.cursor/pipelines/test-prep.md`](../pipelines/test-prep.md) → `epics/<KEY>/<KEY>-tests.json` and `<KEY>-tests.md`. Delete `epics/<KEY>/temp/` when done.
6c. **Epic optional E2E materialization** (optional): after **`-tests.json`** exists and the environment is ready (app URL, Playwright MCP, optional postgres-ctqa + tunnel), use **`TEST-EXEC:`** + Epic key and follow [`.cursor/pipelines/test-exec.md`](../pipelines/test-exec.md) → `epics/<KEY>/tests/*.spec.ts` and `<KEY>-test-exec.json`. Delete `epics/<KEY>/temp/` when done.
6d. **Harness consistency** (optional): when this change adds or renames a pipeline, template, tool, or harness doc path, run **`SYNC:`** on **`develop`** or **`main`** per [`.cursor/pipelines/sync.md`](../pipelines/sync.md) (optional **`scope=`**). **Not** for **`release`** — use **`PUBLIC-SCRUB:`** there for public export.
7. **Confluence** (if applicable): MCP search/fetch under the right space/subtree (CT, XT, or QAPORTAL Corner page **497097273** and descendants per `project.json` / `qa-project.json`) → reconcile with Jira; flag conflicts.
8. **Codebase** (if applicable): targeted exploration only; summary table of file → role; no huge dumps.
9. Produce the **requested artifact** using [epics/templates/tests-ref.json](../../epics/templates/tests-ref.json) (**format_norms** + schema) or [docs/dr-ref](../../docs/dr-ref) as the structural reference, or **coverage** outputs from step 5 when the deliverable is Epic Smart Checklist coverage ([`.cursor/pipelines/coverage.md`](../pipelines/coverage.md)), or **analysis** outputs from step 6 when the deliverable is requirement analysis, or **tests** outputs from step 6b when the deliverable is regression test drafting ([`.cursor/pipelines/test-prep.md`](../pipelines/test-prep.md)), or **test-exec** outputs from step 6c when the deliverable is optional Playwright materialization ([`.cursor/pipelines/test-exec.md`](../pipelines/test-exec.md)).
10. End with **verifiable** next steps (what to run, what to re-check in Jira, etc.).
11. Update [qa-handoff.md](../../qa-handoff.md) with session summary, ticket keys in focus, blockers, and next steps.

## Forbidden

- Search/discovery of Atlassian content without MCP.
- Pasting entire modules or unbounded grep output into the conversation.
