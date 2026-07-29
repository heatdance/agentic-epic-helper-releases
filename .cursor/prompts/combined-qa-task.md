# Prompt scaffold: combined QA task (Jira + Confluence + codebase)

Copy or adapt this into chat. **Jira and Confluence**: always **user-mcp-atlassian** (read tool schemas first). **Code**: narrow search and bounded reads only.

## Inputs (fill in)

- **Jira issue key(s)**: <!-- -->
- **Confluence page(s) or search terms** (if any): <!-- -->
- **Code area or repo hint** (if any): <!-- -->
- **Deliverable**: <!-- test draft norms/schema: epics/templates/tests-ref.json (format_norms) + TEST-PREP; DR per docs/dr-ref; Epic Smart Checklist via COVERAGE: + .cursor/pipelines/coverage.md; Epic analysis via ANALYSE: + .cursor/pipelines/analysis.md; Epic regression test drafts via TEST-PREP: + .cursor/pipelines/test-prep.md (after coverage); optional epic close via CLOSE: + .cursor/pipelines/close.md (after full artifact set; documentation-only); publish via /clean + .cursor/pipelines/clean.md on personal branch only -->

## Ordered workflow for the agent

**`{EpicDir}`** = **`epics/<KEY>/`** for all pipeline triggers.

1. Apply [docs/harness-map.json](../../docs/harness-map.json): read **T0** (`qa-handoff.md`, `AGENTS.md`), then only the **T1** packages that match this task’s language (e.g. [docs/project.json](../../docs/project.json) for product/fork, [docs/qa-project.json](../../docs/qa-project.json) for Corner QA scope, [docs/corner-platform-map.json](../../docs/corner-platform-map.json) when the task names an **environment**, **Stash repo**, **branch/fork**, or **which Jira project**—**not** all JSON files every time). Use those files for Confluence/Jira **scope** before MCP.
2. Read and update context from [qa-handoff.md](../../qa-handoff.md) (read first; plan to update last).
3. **Jira**: MCP fetch issues → extract AC and scope; note gaps.
4. **Epic ref** (when work is Epic-scoped or you need stored Yogi snippets): create or refresh **`{EpicDir}<EPIC-KEY>-ref.json`** from [epics/templates/epic-ref.json](../../epics/templates/epic-ref.json); for a full preflight run use **`EPIC-PREP:`** + key and follow [`.cursor/pipelines/epic-prep.md`](../pipelines/epic-prep.md) (delete **`{EpicDir}temp/`** when done). Fill **`client_shell_impact`** (Corner Trader vs **Adaptive** per [docs/qa-project.json](../../docs/qa-project.json)) and `requirements[]` with [yogi_resolve.py](../../automation/tools/yogi-tool/yogi_resolve.py) / [yogi_snippet.py](../../automation/tools/yogi-tool/yogi_snippet.py); set **`snippet_status`** / **`snippet_failure_reason`** when a snippet cannot be extracted. See [epics/README.md](../../epics/README.md).
5. **Epic coverage** (Smart Checklist draft + grounding audit): after **`-ref.json`** exists, use **`COVERAGE:`** + Epic key (optional **`repo=WORKSPACE/REPO`**, optional **`focus=...`**) and follow [`.cursor/pipelines/coverage.md`](../pipelines/coverage.md) → **`{EpicDir}<KEY>-coverage.json`** and **`<KEY>-coverage.md`**. Delete **`{EpicDir}temp/`** when done.
6. **Epic requirement analysis** (optional): use **`ANALYSE:`** + Epic key (optional **`known_issues=yes`** default off, **`resolve=no`**, **`include_closed=yes`** with known_issues) and follow [`.cursor/pipelines/analysis.md`](../pipelines/analysis.md) → **`{EpicDir}<KEY>-analysis.json`** and **`<KEY>-analysis.md`**. Delete **`{EpicDir}temp/`** when done.
6a. **Epic optional precondition authoring** (optional): after **`-coverage.json`** exists (and ideally **`-discover.json`**), use **`TEST-PRECON:`** + Epic key and follow [`.cursor/pipelines/test-precon.md`](../pipelines/test-precon.md) → **`{EpicDir}<KEY>-precon.json`** and **`<KEY>-precon.md`**. Delete **`{EpicDir}temp/`** when done.
6b. **Epic regression test drafts** (optional): after **`-coverage.json`** exists (and optionally **`-precon.json`**), use **`TEST-PREP:`** + Epic key (optional **`map_only=yes`**, FE cred tokens like discover/precon) and follow [`.cursor/pipelines/test-prep.md`](../pipelines/test-prep.md) → **`{EpicDir}<KEY>-tests.json`** and **`<KEY>-tests.md`**. Delete **`{EpicDir}temp/`** when done.
6c. **Epic optional close** (optional): after **`-tests.json`**, **`-discover.json`**, **`-coverage.json`**, **`-ref.json`** exist at **`{EpicDir}`** root (`-precon.json` optional legacy), use **`CLOSE:`** + Epic key and follow [`.cursor/pipelines/close.md`](../pipelines/close.md) → **`{EpicDir}context/<KEY>-close.json`** + three root **`.md`**. Delete **`{EpicDir}temp/`** when done.
6d. **Harness publish** (optional): when ready to align pointers and push team/public exports, run **`/clean`** on **`personal`** per [`.cursor/commands/clean.md`](../commands/clean.md) (optional **`scope=align`** first).
7. **Confluence** (if applicable): MCP search/fetch under the right space/subtree (CT, XT, or QAPORTAL Corner page **497097273** and descendants per `project.json` / `qa-project.json`) → reconcile with Jira; flag conflicts.
8. **Codebase** (if applicable): targeted exploration only; summary table of file → role; no huge dumps.
9. Produce the **requested artifact** using [epics/templates/tests-ref.json](../../epics/templates/tests-ref.json) (**format_norms** + schema) or [docs/dr-ref](../../docs/dr-ref) as the structural reference, or **coverage** outputs from step 5 when the deliverable is Epic Smart Checklist coverage ([`.cursor/pipelines/coverage.md`](../pipelines/coverage.md)), or **analysis** outputs from step 6 when the deliverable is requirement analysis, or **tests** outputs from step 6b when the deliverable is regression test drafting ([`.cursor/pipelines/test-prep.md`](../pipelines/test-prep.md)), or **close** outputs from step 6c when the deliverable is epic integrity + archive ([`.cursor/pipelines/close.md`](../pipelines/close.md)).
10. End with **verifiable** next steps (what to run, what to re-check in Jira, etc.).
11. Update [qa-handoff.md](../../qa-handoff.md) with session summary, ticket keys in focus, blockers, and next steps.

## Forbidden

- Search/discovery of Atlassian content without MCP.
- Pasting entire modules or unbounded grep output into the conversation.
- Loading full in-repo epic or harness **`*.json`** into chat for inspection without **`jq`** projection first per [automation/docs/jq.md](../../automation/docs/jq.md) (see [jq-json.mdc](../rules/jq-json.mdc)).
