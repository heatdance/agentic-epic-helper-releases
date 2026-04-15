# Pipeline: epic-prep

**Trigger**: user message starts with `EPIC-PREP:` and includes a Jira **Epic key** (e.g. `EPIC-PREP: CRT-1234`). Optional token on the same line:

- **`repo=…`** — Bitbucket/Stash repository for the optional prep code search: Bitbucket Cloud `workspace/slug`, or internal Stash **`PROJECT_KEY/repo_slug`** (e.g. `EPIC-PREP: CRT-1234 repo=BRO/xt`). Defaults: [docs/project.json](../../docs/project.json) **`bitbucket.default_repo`** (see also [docs/corner-platform-map.json](../../docs/corner-platform-map.json) **`code_streams`** for `BRO/xt` vs `CAN/corner` vs packaging repos).

**Scope**: **one Epic** per run. **Router rule**: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc).

**Output**: `epics/<KEY>/<KEY>-ref.json` (copy from [`epics/templates/epic-ref.json`](../../epics/templates/epic-ref.json)). **Ephemeral**: `epics/<KEY>/temp/` — **must be deleted** before the run is considered complete (success or abort).

---

## Preconditions

- **user-mcp-atlassian** available; read tool schemas before calls.
- **Corner QA product split**: [`docs/qa-project.json`](../../docs/qa-project.json) — Corner Trader (dxTrade5 web stack, WebBroker, related hosts) and **Adaptive** (mobile-oriented client) are **both in scope** for QA. Epic-prep must record **impact on both client shells** unless Jira explicitly limits scope. Do not assume desktop/web only.
- **Yogi** (optional live REST): [`automation/docs/yogi-url-resolve.md`](../../automation/docs/yogi-url-resolve.md) — `CONFLUENCE_SESSION_COOKIE` or `--cookie` for `yogi_snippet`; without auth, use MCP storage export to `temp/` + `--storage-file`, or set `snippet_status` / `snippet_failure_reason` — **never fabricate** `snippet_text`.
- **Figma MCP** (optional): if `figma.com` URLs appear in Jira text, [`automation/docs/figma-mcp.md`](../../automation/docs/figma-mcp.md).
- **XT context**: [`docs/project.json`](../../docs/project.json) — XT home page id **402589545**, space **XT** (upstream fork / platform). Use **narrow** Confluence search; do not crawl the whole space.
- **Bitbucket** (optional): same **user-mcp-atlassian** server as Jira/Confluence — read `bitbucket_search_code`, `bitbucket_browse_directory`, and `bitbucket_get_file_content` schemas before calls. Prep search is **non-blocking**: missing repo → skip with `validation_log` + `implementation.skipped_reason`; **do not** extend the Yogi finalize gate to Bitbucket. For **Bitbucket Server / DC** (`stash.in.devexperts.com`), `bitbucket_search_code` may return **HTTP 404** on `/rest/api/1.0/search` even when browse APIs work — use step **5b** browse fallback when that happens.

---

## Folder lifecycle

1. Ensure `epics/<KEY>/` exists.
2. Create `epics/<KEY>/temp/`.
3. **Allowed in `temp/` only** (examples): `jira-issue.json` (raw MCP issue), `yogi-<REQKEY>.json` (storage exports), `xt-candidates.json` (search results metadata), `bitbucket-*.json` (raw search exports), scratch notes. **Do not** commit secrets; no cookies in files.
4. Work: merge durable facts into `epics/<KEY>/<KEY>-ref.json`.
5. **Exit**: delete `epics/<KEY>/temp/` recursively (`Remove-Item -Recurse` on Windows, `rm -rf` on Unix).
6. **Self-check**: `<KEY>-ref.json` must **not** contain the substring `/temp/` (no stale paths).

**Abort / failure**: If `temp/` was created, still delete it unless legal retention requires otherwise (none expected here).

---

## Steps

### 1. Jira — fetch Epic

- MCP fetch the issue by key; save raw JSON to `temp/jira-issue.json` (optional but recommended for audit).
- If **`epics/<KEY>/<KEY>-ref.json` already exists**, read **`sources.bitbucket_repo`** (and optionally prior **`implementation.hits`**) for merge hints **before** overwriting.
- Copy template → `epics/<KEY>/<KEY>-ref.json`.
- Fill `epic` (`key`, `url`, `summary`, `status`, `labels`, `issue_type`) and `sources.jira_fetched_at` (ISO-8601).
- Parse optional **`repo=`** from the user message (same token shape as [`coverage.md`](coverage.md)). **Repo resolution** for `sources.bitbucket_repo` (first match wins): trigger **`repo=`** → **prior** ref’s `sources.bitbucket_repo` (from the pre-overwrite read above) → [`docs/project.json`](../../docs/project.json) **`bitbucket.default_repo`** if non-null. If still unresolved, leave null for step **5b** (optional search skipped).

### 2. Synthesis (3.1) — from Jira text only

- Populate `synthesis` in the ref:
  - `problem_gist` + `problem_gist_source` (`from_jira_field` | `inferred_from_jira`).
  - `impact_areas[]`, `keywords[]` — prefer objects `{ "text": "...", "source": "from_jira_field" | "inferred_from_jira" }` for non-obvious rows; plain strings only when verbatim from Jira.
- Do not invent platform facts not present in Jira or later tool outputs.

### 2b. Client shell impact (mandatory) — Corner Trader vs Adaptive

- Populate **`client_shell_impact`** in the ref (see template `_client_shell_impact` shape).
- **Stable phrasing (reduces rerun variance)**:
  - **`note`**: one short sentence in a **fixed pattern**: state **`status`**, then **`source`** (e.g. “Corner Trader: **affected** (`jira_field`) — …”). Do **not** put long verbatim Jira quotes in **`note`**.
  - **`evidence`**: verbatim Jira excerpts, component/label names, or `none_found` — keep quotes here, not duplicated in **`note`**.
- **`corner_trader`**: `status` `affected` | `not_applicable` | `unknown`; **`note`**; **`evidence`** (Jira component, label, description quote, linked story — or state `none_found`).
- **`adaptive`**: same structure.
- **`source`**:
  - **`jira_field`** — explicit component/label/fix version or description mentions Adaptive vs dxTrade5/WebBroker.
  - **`jira_text_inference`** — reasonable inference from text; put the supporting quote in **`evidence`**, not a long paraphrase in **`note`**.
  - **`qa_default_both`** — use when Jira is **silent** on client split but the epic is **metrics, portfolio, orders, or shared backend** likely to surface in **both** shells: set both to **`affected`** and use **this exact sentence** for **`corner_trader.note`** and **`adaptive.note`** (both): `Default both clients per qa-project.json unless Jira excludes Adaptive; confirm at test time.` For **pure backend-only** epics with **no user-visible metric/UI** in either client, set **`not_applicable`** with Jira evidence in **`evidence`** and a short factual **`note`**.
- Append **`validation_log`** if either shell remains **`unknown`** after reasonable parse.
- **COVERAGE** consumes this object to seed **metric × surface** checks (including Adaptive).
- **Bitbucket repo (post–client-shell)**: If **`sources.bitbucket_repo`** was set **only** from [`docs/project.json`](../../docs/project.json) **`bitbucket.default_repo`** (no **`repo=`** trigger, no **prior** ref override) **and** **`client_shell_impact.adaptive.status`** is **`affected`** **and** **`client_shell_impact.corner_trader.status`** is **`not_applicable`**, set **`sources.bitbucket_repo`** to **`CAN/corner`** (see [`docs/corner-platform-map.json`](../../docs/corner-platform-map.json) **`code_streams`** id **`can_corner`**; same value as **`bitbucket.adaptive_repo`** in `project.json`). Append **`validation_log`**. Do **not** override an explicit **`repo=`** or a **prior** ref repo.

### 3. Requirements (3.2) — Yogi

- Collect requirement keys from the **Requirement Yogi** custom field if present; else regex for `/requirements/` URLs and `req-CRT-…` / similar in description and comments (best-effort). Treat this set as **`jira_linked_keys`** for finalize gating (step 8).
- For each key: [`automation/tools/yogi-tool/yogi_resolve.py`](../../automation/tools/yogi-tool/yogi_resolve.py) → `short_url`, `anchor`; obtain `page_id` via `--follow` + cookie or canonical URL from human/browser.
- For each `(page_id, key)`: [`yogi_snippet.py`](../../automation/tools/yogi-tool/yogi_snippet.py) → append to `requirements[]` with `snippet_text`, `extract_mode`.
- **Confluence method**: **MCP `confluence_get_page` (storage) + `yogi_snippet.py --storage-file`** is a **first-class success path**, equal to live REST + `yogi_snippet`. Set **`sources.confluence_method`** to `snippet` / `mcp` / `mixed` accordingly. Do **not** treat MCP-only extraction as a “failed” or inferior path in **`validation_log`** prose unless the row is still empty after retries.
- **Snippet status (required on every row)**:
  - If extract succeeds: **`snippet_status`**: `ok`; **`snippet_failure_reason`**: omit or `null`.
  - If `snippet_text` is null or empty: **`snippet_status`**: `missing` or `failed`; set **`snippet_failure_reason`** to one of: `yogi_extract_empty`, `no_cookie`, `macro_shape_unsupported`, `page_id_unresolved`, `mcp_export_failed`, `other` (with short detail in `validation_log` if needed).
- **Never fabricate** `snippet_text`.

### 3b. Snippet completion retry (before Design)

- After the initial pass in step 3, for each `requirements[]` row whose **`key`** is in **`jira_linked_keys`** and where `snippet_text` is still null or empty **and** `snippet_failure_reason` is in the **recoverable** set below, run **exactly one** additional attempt before proceeding to step 4:
  - **Recoverable reasons**: `mcp_export_failed`, `no_cookie` (when MCP storage export is available in this session), `yogi_extract_empty` (one MCP + `--storage-file` attempt if not already tried for that key).
  - **Retry action**: MCP `confluence_get_page` (storage) → save to `temp/` → `yogi_snippet.py --storage-file` per [`automation/docs/yogi-url-resolve.md`](../../automation/docs/yogi-url-resolve.md). Update the row’s `snippet_text`, `snippet_status`, and `snippet_failure_reason` after the attempt.
- Append **`validation_log`**: `{ "step": "3b_snippet_retry", "at": "<ISO8601>", "action": "<keys retried and outcome summary>" }`.
- Rows with **`macro_shape_unsupported`**, **`page_id_unresolved`**, or persistent **`other`** after retry need explicit handling: either document **`deferral_accepted`** in `validation_log` (step 8) or keep `failed` and **block finalize** per step 8.

### 4. Design (3.3)

- Parse Jira text for `figma.com` links → `design.figma[]` (`url`, optional `note`).
- Set `design.ui_artifacts_in_jira` to `none` | `figma` | `other` based **only** on parsed links.
- If no Figma links: `design.notes` = neutral evidence string, e.g. `no_figma_urls_in_jira_description`. Do **not** conclude “likely backend” from absence of design links.

### 5. Precision pass (3.4)

- List factual claims in `synthesis` and **`client_shell_impact`**; remove or downgrade any claim **without** support from `temp/jira-issue.json` fields or `requirements[].snippet_text` (or explicit Jira evidence strings in `client_shell_impact.evidence`).
- Append to `validation_log`: `{ "step": "3.4", "at": "<ISO8601>", "action": "<short description>" }`.

### 5b. Bitbucket implementation search (prep) — optional

- **When**: After validated synthesis and snippets (step **5**). Runs **before** XT Confluence so XT titles do not pollute query seeds on the first pass.
- **Repo**: Use `sources.bitbucket_repo` from step **1** resolution. If null: set `implementation.skipped_reason` (e.g. `no_bitbucket_repo`), clear or leave `implementation.hits` empty, append `validation_log` — **skip** this step’s searches; continue to step **6**.
- **Queries**: Seed from Epic **summary**, **validated** `synthesis.keywords`, and **token-light** phrases from `requirements[].snippet_text` (metric names, flags, feature toggles, collision-prone symbols). **Cap**: at most **8** `bitbucket_search_code` queries (same order of magnitude as XT ref cap). Pure UI epics with no implementation signal may use **minimal** queries or skip with `validation_log` reason in `implementation.skipped_reason` instead of burning the cap on noise.
- **MCP parameters (before any Bitbucket call)**: Map `sources.bitbucket_repo` to tool arguments. **Stash / Server** token **`PROJECT_KEY/repo_slug`** (e.g. `BRO/xt`): set **`project_key`** to the segment before the first `/` and **`repo_slug`** to the segment after (trim both). **Do not** pass the combined `BRO/xt` string as **`repo_slug`** alone — MCP requires **`project_key`** for Server/DC and will reject the call. **Bitbucket Cloud** token **`workspace/repository`**: use **`workspace`** + **`repo_slug`** per the tool schema (no `project_key`).
- **Execution — code search**: Run `bitbucket_search_code` once per capped query with the mapped parameters.
- **Execution — when code search is unavailable**: If the MCP reports **project key is required**, fix **`project_key`** / **`repo_slug`** mapping and retry **`bitbucket_search_code`** once per query. If, with correct parameters, calls fail with **HTTP 404** or a URL containing **`/rest/api/1.0/search`** (common on internal Stash when the code-search REST route is absent while browse APIs work): run a **browse fallback** — at most **3** `bitbucket_browse_directory` calls using the same `project_key` / `repo_slug` (e.g. `path` `""` for repo root, then up to two plausible top-level dirs inferred from Epic wording such as `dxcore`, `webbroker`, `common`). Optionally **one** `bitbucket_get_file_content` only if a listing yields an obvious single candidate path; keep stored **`fragment`** short — **no** full files in durable JSON. Add `implementation.hits[]` rows for meaningful listing or file evidence with **`note`** explaining browse-path relevance. Optionally save raw MCP JSON under `temp/bitbucket-*.json` until merged, then delete with `temp/`.
- **Hits**: Append to `implementation.hits[]` with `id` (`prep-impl-001`, …), `search_query`, `path`, `fragment`, `note` (one-line **why_relevant**, mirror XT `why_relevant` discipline), **`source_phase`**: `epic_prep`.
- **Timestamps**: Set `sources.bitbucket_searched_at` (ISO-8601) when at least one **successful** `bitbucket_search_code` **or** browse fallback call completes; if skipped entirely, leave null.
- Append **one** `validation_log` entry `{ "step": "5b_bitbucket_prep", "at": "<ISO8601>", "action": "<summary>" }` where **`action`** states query count, search hit count, `search_404_used_browse_fallback` when applicable, or skip reason (e.g. `no_bitbucket_repo`).

### 6. XT Confluence (3.5) — high risk, capped

- **Seed** queries from: Epic **summary**, **validated** `synthesis.keywords`, and **explicit** Confluence/Jira URLs in description/comments.
- Search/list in space **XT** only; prefer titles/snippets from search results over full page bodies.
- **Cap**: add at most **8** entries to `traversal.xt_refs[]` in this step (adjust only if user approves).
- Each entry: `page_id`, `url`, `title`, `why_relevant` (one line), `source_query_or_link`.
- **Forbidden**: pasting full `confluence_get_page` bodies into the ref. If full body was needed briefly, keep under `temp/` only until summarized, then delete with `temp/`.

### 7. XT relevance pass (3.6)

- For each `xt_refs[]` row: **keep**, **remove**, or **flag** with `status` + `reason` per template.
- Prefer **removal** over weak ties. Append `validation_log` entries for bulk actions.

### 8. Finalize

- **Snippet finalize gate**: Do **not** delete `temp/` or treat the run as complete while any `requirements[]` row whose **`key`** is in **`jira_linked_keys`** (step 3) has **`snippet_status`** `missing` or `failed`, **unless** `validation_log` contains an explicit **`deferral_accepted`** entry for this epic (short reason, e.g. macro unsupported, page unresolved, or human-approved skip). Keys never collected into `requirements[]` are out of scope for this gate.
- Set `sources.confluence_method` (`snippet` / `mcp` / `mixed`) as appropriate.
- Ensure **`sources.bitbucket_repo`** reflects the resolved workspace/slug (step **1** / **5b**) for downstream **COVERAGE** when the user omits `repo=` on the coverage trigger.
- Validate JSON.
- **Delete** `epics/<KEY>/temp/`.
- Confirm `<KEY>-ref.json` contains no `/temp/` substring.

---

## Pitfalls

- **Bitbucket noise / rate limits** — Keep queries specific; cap at **8**; each hit needs a **`note`** explaining relevance; broad strings return junk.
- **Bitbucket Server search 404 / MCP shape** — Always split `PROJECT_KEY/repo_slug` into **`project_key`** + **`repo_slug`** for Stash. If `bitbucket_search_code` still returns **404** on `/rest/api/1.0/search`, use step **5b** browse fallback (capped); do not treat browse-only grounding as “Bitbucket offline.”
- **XT noise** — Small caps, keyword-seeded search, per-page `why_relevant`, pass 3.6 pruning.
- **LLM “validation”** — Steps 3.4 / 3.6 are structured audits (delete uncited / weak links), not proof of truth.
- **Yogi auth** — Skip live snippet or use MCP + `--storage-file` into `temp/` then merge; always set **`snippet_status`** / **`snippet_failure_reason`** when `snippet_text` is absent — do not leave unexplained nulls. Use step **3b** + finalize gate (step **8**) so first-pass flakiness does not ship silent gaps.
- **Adaptive omission** — Do not default to dxTrade5-only; use **`client_shell_impact`** and **`qa_default_both`** when appropriate.
- **Temp leakage** — Mandatory delete + grep self-check.

---

## Related

- Template: [`epics/templates/epic-ref.json`](../../epics/templates/epic-ref.json)
- Layout: [`epics/README.md`](../../epics/README.md)
- QA scope (Corner + Adaptive): [`docs/qa-project.json`](../../docs/qa-project.json)
- Yogi: [`automation/docs/yogi-url-resolve.md`](../../automation/docs/yogi-url-resolve.md)
- Coverage handoff: **COVERAGE** merges `implementation.hits` from this ref into `implementation_hits` — see [`coverage.md`](coverage.md) phase **7**.
