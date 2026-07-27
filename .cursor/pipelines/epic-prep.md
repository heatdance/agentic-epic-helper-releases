# Pipeline: epic-prep

**Trigger**: user message starts with `EPIC-PREP:` and includes a Jira **Epic key** (e.g. `EPIC-PREP: CRT-1234`). Optional tokens on the same line:

- **`repo=…`** — Bitbucket/Stash repository for the optional prep code search: Bitbucket Cloud `workspace/slug`, or internal Stash **`PROJECT_KEY/repo_slug`** (e.g. `EPIC-PREP: CRT-1234 repo=BRO/xt`). Defaults: [docs/project.json](../../docs/project.json) **`bitbucket.default_repo`** (see also [docs/corner-platform-map.json](../../docs/corner-platform-map.json) **`code_streams`** for `BRO/xt` vs `CAN/corner` vs packaging repos).
- **`focus=...`** — free-text merge into synthesis and **obligations reconcile** (step **6b**), same spirit as COVERAGE `focus=` (e.g. `focus=FX_SPOT_WeightedAvg_metrics`).
- **`strict_topology=yes`** — opt-in; finalize runs **`epic_prep_verify.py --strict-topology`** (required on new emits after topology rollout).
- **`strict_principal=yes`** — opt-in; finalize runs **`epic_prep_verify.py --strict-principal`**; requires principal reconcile (step **3i**) per [`docs/epic-prep-principal-contract.json`](../../docs/epic-prep-principal-contract.json). May combine with **`strict_topology=yes`**.

**Version note (obligation subprocesses + topology + principal)**: schema **`schema_version: 4`** with **`obligations_proposed[]`**, **`downstream_hints`**, **`verification_focus_proposed`**, **`principal_coverage_threads`**, **`epic_archetype`**, **`verification_topology`** (additive). Finalize gate **`epic_prep_verify.py`** (`--strict-topology` / `--strict-principal` on new emits). Kinds: [`docs/epic-obligation-kinds.json`](../../docs/epic-obligation-kinds.json). Topology contract: [`docs/epic-prep-topology-contract.json`](../../docs/epic-prep-topology-contract.json). Principal contract: [`docs/epic-prep-principal-contract.json`](../../docs/epic-prep-principal-contract.json). Verifier: [`automation/docs/epic-prep-verify.md`](../../automation/docs/epic-prep-verify.md).

**Step execution order (normative)**: **1** → **3** → **3b** → **3c** → **3d** → **3e** → **2b** → **2c** → **3f** → **3g** → **3h** → **3i** → **4** → **5** → **5b** → **6** → **7** → **6b** → **8**. Steps **2b–2c**, **3f–3h**, and **3i** are documented out of numeric order but **must** run in this sequence. Renumbering map: legacy step **4** (Design) unchanged; topology/principal inserts do not renumber **5–8**.

**Forbidden inputs (production)**: Do **not** read or copy from sibling **`-coverage.json`**, **`-discover.json`**, **`-precon.json`**, **`-tests.json`**, CRTQA Jira issues, or operator gold under **`.cursor/calibrate/`** (calibrate is post-hoc only).

**Scope**: **one Epic** per run. **Router rule**: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc).

## Epic workspace (`{EpicDir}`)

Before any filesystem work, parse `<KEY>` from the **same user message line** as **`EPIC-PREP:`**.

- **`{EpicDir}`** = `{repo_root}/epics/<KEY>/`

Normative paths use **`{EpicDir}`** as directory prefix ending in `/<KEY>/`.

**Output**: `{EpicDir}dependencies/<KEY>-ref.json` (copy from [`epics/templates/epic-ref.json`](../../epics/templates/epic-ref.json)). **Human paste** (later): `{EpicDir}<KEY>-coverage.md` at epic root only per [`docs/epic-artifact-layout.json`](../../docs/epic-artifact-layout.json). **Ephemeral**: `{EpicDir}temp/` — **must be deleted** before the run is considered complete (success or abort).

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

1. Ensure `{EpicDir}` exists.
2. Create `{EpicDir}temp/`.
3. **Allowed in `temp/` only** (examples): `jira-issue.json` (raw MCP issue), `yogi-<REQKEY>.json` (storage exports), **`epic-obligation-<REQKEY>.json`** (per-requirement obligation slices), **`epic-topology-scenario-<slug>.json`** (per-section scenario surface slices), **`epic-topology-oracle-<slug>.json`** (pricing oracle slices), **`epic-obligation-reconcile.json`** (merge scratch), `xt-candidates.json` (search results metadata), `bitbucket-*.json` (raw search exports), scratch notes. **Do not** commit secrets; no cookies in files.
4. Work: merge durable facts into `{EpicDir}dependencies/<KEY>-ref.json`.
5. **Exit**: delete `{EpicDir}temp/` recursively (`Remove-Item -Recurse` on Windows, `rm -rf` on Unix).
6. **Self-check**: `<KEY>-ref.json` must **not** contain the substring `/temp/` (no stale paths).

**Abort / failure**: If `temp/` was created, still delete it unless legal retention requires otherwise (none expected here).

---

## Steps

### 1. Jira — fetch Epic

- MCP fetch the issue by key; save raw JSON to `temp/jira-issue.json` (optional but recommended for audit).
- If **`{EpicDir}dependencies/<KEY>-ref.json` already exists**, **MUST** project with `jq` per [automation/docs/jq.md](../../automation/docs/jq.md) before loading the full file — then read **`sources.bitbucket_repo`** (and optionally prior **`implementation.hits`**) for merge hints **before** overwriting.
- Copy template → `{EpicDir}dependencies/<KEY>-ref.json`.
- Fill `epic` (`key`, `url`, `summary`, `status`, `labels`, `issue_type`) and `sources.jira_fetched_at` (ISO-8601).
- Parse optional **`repo=`** from the user message (same token shape as [`coverage.md`](coverage.md)). **Repo resolution** for `sources.bitbucket_repo` (first match wins): trigger **`repo=`** → **prior** ref’s `sources.bitbucket_repo` (from the pre-overwrite read above) → [`docs/project.json`](../../docs/project.json) **`bitbucket.default_repo`** if non-null. If still unresolved, leave null for step **5b** (optional search skipped).

### 2b. Client shell impact (mandatory) — Corner Trader vs Adaptive

**Runs after step 3e (synthesis)** — see below.

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

### 2c. Epic archetype (mandatory) — after 2b

**Requires:** step **2b** `client_shell_impact`; step **1** `temp/jira-issue.json` description/summary; step **3e** `synthesis` (when available — re-read after 3e if 2c runs immediately after 2b).

- Populate **`epic_archetype`** on the ref (template `_epic_archetype` shape). Same enum as COVERAGE phase **3**: `widget_ui` | `metrics_calculation` | `mixed`.
- **Decision tree** (first match wins; tie-break on step 4):
  1. Jira/synthesis primary deliverable = **formulas, ladders, settlement metrics, P/L calculation** → **`metrics_calculation`**
  2. Primary = **widgets, quote display, configuration UI, Figma-driven screens** → **`widget_ui`**
  3. **Material both** (e.g. tiered quotes **and** formula/metric proofs) → **`mixed`**
  4. **Tie-break:** count **`primary_candidate`** obligation kinds — `formula|ladder|rounding|settlement` vs `config_posture|parity` with **`routing_or_markup`** plus Jira **Scenarios** naming UI surfaces; heavier count wins; equal → **`mixed`**
- Set **`source`**: `jira_summary` | `jira_description` | `jira_scenarios` | `obligation_kinds` | `user_trigger_focus` | `inferred_from_jira`
- Set **`evidence`**: one short citation (no long Jira paste — verbatim quotes belong in `verification_topology` or `client_shell_impact.evidence`)
- Append **`validation_log`**: `{ "step": "2c", "at": "<ISO8601>", "action": "epic_archetype=<value> source=<source>" }`
- **COVERAGE** (plan 2) **must** copy `epic_archetype.value` to `coverage.archetype` when present — do not re-infer.

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

### 3c. Obligation extraction — per-requirement subprocess (mandatory)

**Parent orchestrator MUST NOT** one-shot all requirements in a single chat turn. For **each** `requirements[]` row with usable `snippet_text` (or Epic description excerpt naming that key):

1. **Input pack** (subprocess only): that row + Epic summary/description sentences mentioning **`key`** only.
2. **Output**: write `temp/epic-obligation-<REQKEY>.json` with shape `{ "requirement_key": "<KEY>", "obligations_proposed": [ … ] }`.
3. Each obligation: `id` (`obl-###` unique epic-wide), `kind` from [`docs/epic-obligation-kinds.json`](../../docs/epic-obligation-kinds.json), `statement`, **`assertion_fragment`** (short observable for checklist bullet — no repeated widget/card context), **`emit_subsection`** (optional `### …` heading for COVERAGE grouping), `requirement_keys[]`, `evidence_anchor` (string or `{ field, excerpt, source }`), optional `config_vs_position`, `disposition` (`primary_candidate` | `deferral_candidate`), `deferral_reason` when deferral, **`downstream_hints`** per [`docs/epic-prep-principal-contract.json`](../../docs/epic-prep-principal-contract.json):
   - **`config_vs_position: account_group_assignment`** + **`primary_candidate`** → **`needs_dual_account_contrast: true`**; **`coverage_thread`**: `environment_setup` or `invariants` per statement.
   - **`kind: environment_setup`** → **`needs_environment_provision: true`**, **`coverage_thread: environment_setup`**.
   - **`kind: explicit_deferral`** or **`disposition: deferral_candidate`** → **`coverage_thread: deferral_only`**; require **`deferral_reason`**.
   - **`config_vs_position: routing_or_markup`** / **`parity`** with UI surfaces → **`coverage_thread`**: `surface_quotes` or `mapping_routing`; set **`personas`** from shell impact.
   - Bind **`linked_delivery_note_ids`** when step **3h** will emit matching **`delivery_notes`** (may back-fill in **3i**).
4. Use **disambiguation_notes** — e.g. instrument-type config change ≠ account group assignment ≠ position-state invariant.
5. **0 obligations** is valid when snippet is purely procedural with no testable obligation; log in subprocess output `notes`.
6. **`widget_ui` / UI-heavy `mixed` atomic rule:** when `snippet_text` names **≥2** UI parameters / table rows (Side, Quantity, Description, fees, card sections, etc.), emit **one `primary_candidate` obligation per observable** — not one obligation per entire requirement key. Card-level availability (`renders`, `not omitted`) may be separate `invariant` / `parity` obligations but **do not** replace field obligations. Set **`requirements[].observable_yield`** to the count of distinct parameters recognized; verifier requires **≥ `observable_yield`** field obligations (availability / `environment_setup` do **not** count).
7. When `snippet_status` is **failed**: emit **one** `deferral_candidate` with **human** `deferral_reason` (name the key and what is unavailable — **never** bare enum `mcp_export_failed` / `no_cookie` alone) — **no** field obligations for that key.

Merge slices into ref **`obligations_proposed[]`** (dedupe by statement similarity; keep distinct kinds separate).

### 3d. Nested-link obligation subprocess (optional)

When `snippet_text` cites nested `/requirements/` URLs or sibling keys **not** in `jira_linked_keys`, run a **second** subprocess per nested key (same contract as **3c**); append to `temp/epic-obligation-<NESTEDKEY>.json` and merge. Cap **5** nested keys unless user widens scope.

### 3e. Synthesis (3.1) — after obligations

- Populate `synthesis` informed by **`obligations_proposed[]`** (problem framing must not contradict primary invariants):
  - `problem_gist` + `problem_gist_source` (`from_jira_field` | `inferred_from_jira`).
  - `impact_areas[]`, `keywords[]` — prefer objects `{ "text": "...", "source": "from_jira_field" | "inferred_from_jira" }`.
- Merge optional trigger **`focus=`** into keywords / problem_gist with `validation_log` note when it narrows scope.
- Do not invent platform facts not present in Jira, snippets, or obligation evidence.

### 3f. Jira scenario surfaces + shell roles (mandatory) — after 3e and 2c

**Requires:** step **2c** `epic_archetype`; step **3e** `synthesis`; step **1** Jira description (Scenarios block); merged **`obligations_proposed[]`**.

- Initialize **`verification_topology`** on the ref if null (see template `_verification_topology`).
- Parse Jira **numbered scenarios**, nested `##` bullets, and post-condition lines (e.g. Watchlist, Position Book, Instrument page, Derivatives, Client Area, User Management, Backup Prices widget).
- Emit **`verification_topology.jira_scenario_surfaces[]`** per [`docs/epic-prep-topology-contract.json`](../../docs/epic-prep-topology-contract.json) `jira_scenario_surface_item`:
  - **`id`**: `jss-001`, …
  - **`surface`**: stable id e.g. `dxtrade5_watchlist`, `webbroker_client_area`
  - **`shell`**: `console` | `dxtrade5` | `adaptive` | `webbroker_dealer` | `webbroker_client`
  - **`widget`**, **`metric`**, **`source_quote`** (verbatim scenario bullet), **`obligation_ids[]`**
- Emit **`verification_topology.shell_roles`**: `console`, `dxtrade5`, `adaptive`, `webbroker_dealer`, `webbroker_client` — each `{ status: in_scope | not_applicable, evidence }`. Split WebBroker **dealer** (User Management, Account groups) vs **client** (Client Area) when Jira mentions both.
- **Subprocess rule:** when **>5** scenario surfaces, one subprocess per scenario **section**; write `temp/epic-topology-scenario-<slug>.json`; parent merges into ref.
- **`metrics_calculation` short-circuit:** when Jira has **no** widget scenario block, set `jira_scenario_surfaces: []` and append **`validation_log`** `{ "step": "3f_skipped_no_ui_scenarios", … }` — **do not** invent Watchlist/Derivatives rows.
- Append **`validation_log`**: step `3f`.

### 3f½. Scenario capability inventory (mandatory for widget_ui / mixed) — after 3f

**Requires:** step **3f** `jira_scenario_surfaces[]`; step **3h** `platform_reuse_candidates[]` (may be empty).

Per [`docs/epic-prep-scenario-contract.json`](../../docs/epic-prep-scenario-contract.json):

1. Emit **`verification_topology.scenario_capability_rows[]`**: one **`scr-*`** per **`jira_scenario_surfaces[]`** row (`capability_kind: jira_scenario`, `promotion: primary_candidate`, `jira_surface_id` link).
2. For each **`platform_reuse_candidates[]`** with **`binding: suggestion_only`**, emit matching **`scr-*`** with **`platform_reuse_id`**, **`capability_kind: platform_invariant`**, **`promotion: platform_invariant`** (e.g. non-trading-day backup for FX_SPOT).
3. Optional **`cross_surface`** rows for midpoint/mark/console invariants not tied to a single Jira widget bullet.
4. **Subprocess:** when **>5** rows, `temp/epic-scenario-<slug>.json`; parent merges.
5. **Verifier:** `epic_prep_verify.py --mode scenario` before finalize when archetype is **`widget_ui`** or **`mixed`**.

- Append **`validation_log`**: step `3f_half`, row counts (jira vs platform_invariant vs cross_surface).

### 3g. Pricing oracle rules (mandatory when quote/tier keywords) — after 3f½

**Requires:** step **3f** `jira_scenario_surfaces`; **`requirements[].snippet_text`**; **`obligations_proposed[]`** with `routing_or_markup` or `parity` kinds where applicable.

- For each quote/tier/mark-related obligation or snippet keyword (bid, ask, tier, TextConfiguration, midpoint, mark, Quote stream):
  - Emit **`verification_topology.pricing_oracle_rules[]`** per contract `pricing_oracle_rule_item`
  - **`oracle_rule`** from contract enum: `first_tier_quote`, `text_configuration_closest_gte_qty`, `midpoint_invariant`, `mark_from_midpoint`, `console_show_prices_first_tier`, `console_agent_event_quote`, `console_agent_event_text_configuration`, `backup_midpoint_at_eod`, or **`unresolved`**
  - Bind **`surface`** to a `jira_scenario_surfaces[].surface` or `console_*` id
  - **`volume_control`**: `order_default_qty` | `order_qty` | `position_qty` | `first_tier` | `not_applicable`
- **Surface-specific defaults** (when snippet names tier behavior but not per-widget):
  - Watchlist / OTC OE / Adaptive OE → prefer **`text_configuration_closest_gte_qty`** with **`order_default_qty`**
  - Positions / Derivatives / Order book (position qty context) → prefer **`first_tier_quote`** unless snippet explicitly says tier-by-position-qty
  - Console `show prices` → **`console_show_prices_first_tier`**
  - Midpoint/mark invariants → **`midpoint_invariant`** / **`mark_from_midpoint`**
- **Conflict rule:** snippet silent on a scenario surface → row with **`oracle_rule: unresolved`**, **`disposition: deferral_candidate`** (feeds ANALYSE plan 3 — **do not invent** oracle)
- **Subprocess:** one `temp/epic-topology-oracle-<slug>.json` when **>4** rules; parent merges.
- **`metrics_calculation` short-circuit:** when no quote/tier/mark keywords in Jira/snippets, set `pricing_oracle_rules: []` and log **`validation_log`** step `3g_skipped_no_quote_keywords`.
- Append **`validation_log`**: step `3g`.

### 3h. Delivery notes + platform reuse candidates — after 3g

**Requires:** step **3g** oracle rules (for delivery/oracle conflicts); Jira description/comments; optional **`focus=`** when it explicitly states delivery status.

- **`verification_topology.delivery_notes[]`**: `{ id, target, status, source, evidence }`
  - **`status`**: `known_fail` | `excluded` | `waived` | `pending_verification`
  - **Sources:** Jira comments, epic post-conditions, **`focus=`** only when explicit — **never infer `known_fail` from absence**
- **`verification_topology.platform_reuse_candidates[]`**: `{ id, topic, suggested_crtqa_pattern, confidence, evidence, binding: suggestion_only }`
  - Trigger on keywords from contract `platform_reuse_keyword_triggers` (EOD, backup price, daily_data_recorder, mark price column, …)
  - **`suggested_crtqa_pattern`**: human-readable family label only — **no CRTQA issue keys** in durable JSON (harness §3)
  - Every row **`binding`**: **`suggestion_only`** — not structural test input
- Both arrays may be **`[]`** for **`metrics_calculation`** epics with no delivery/reuse signals.
- Append **`validation_log`**: step `3h`.

### 3i. Principal reconcile — after 3h, before 4

**Requires:** merged **`obligations_proposed[]`** with **`downstream_hints`** (step **3c**); **`verification_topology`** from **3f–3h**; step **2c** **`epic_archetype`**.

Per [`docs/epic-prep-principal-contract.json`](../../docs/epic-prep-principal-contract.json):

1. Build **`verification_focus_proposed`**: `{ statement, source, keywords[] }` from Jira summary + synthesis (1–3 sentences; **no paraphrase** of epic one-liner — COVERAGE copies verbatim in step 2 Round 2).
2. Assemble **`verification_topology.principal_coverage_threads[]`**: `{ thread_id, title, coverage_thread, obligation_ids[], required_when }` from obligations + **`archetype_rules`** (e.g. **`widget_ui`** + setup keywords → **`environment_setup`** thread; **`invariant`** primaries → **`invariants`** thread; backup/EOD keywords → **`backup_eod`** thread).
3. Back-link **`delivery_notes[].linked_obligation_ids`** / **`linked_surface_ids`** from obligations and **`jira_scenario_surfaces`**.
4. When **>6** threads, write `temp/epic-principal-reconcile.json` then merge to ref.
5. Append **`validation_log`**: step `3i`.

**`metrics_calculation` short-circuit:** **`environment_setup`** thread optional; still emit **`verification_focus_proposed`** when obligations exist.

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
- **Hits**: Append to `implementation.hits[]` with `id` (`prep-impl-001`, …), `search_query`, `path`, `fragment`, `note` (one-line **why_relevant**), optional **`related_obligation_ids[]`** when hit supports an obligation, **`source_phase`**: `epic_prep`.
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

### 6b. Obligations reconcile (mandatory)

- Merge all `temp/epic-obligation-*.json` slices; assign stable **`obl-###`** ids if subprocesses used local placeholders.
- Set **`obligations_reconcile`**: `{ "epic_summary_aligned": true|false, "conflicts": [ { "obligation_id", "summary", "resolution" } ] }`.
- Resolve **config_vs_position** conflicts using [`docs/epic-obligation-kinds.json`](../../docs/epic-obligation-kinds.json) **disambiguation_notes** (e.g. do not classify group-change avg-price invariant as “skip config scenarios”).
- Every **`primary_candidate`** must be cited in reconcile narrative or listed in **`conflicts`** with resolution.
- Optional **`focus=`** from trigger merges here; log in `validation_log`.
- Run **`python automation/tools/epic_prep_verify.py --mode reconcile --ref {EpicDir}dependencies/<KEY>-ref.json`**. On failure: fix and retry (**max 2** iterations); then proceed to finalize.

### 8. Finalize

- **Snippet finalize gate**: Do **not** delete `temp/` or treat the run as complete while any `requirements[]` row whose **`key`** is in **`jira_linked_keys`** (step 3) has **`snippet_status`** `missing` or `failed`, **unless** `validation_log` contains an explicit **`deferral_accepted`** entry for this epic (short reason, e.g. macro unsupported, page unresolved, or human-approved skip). Keys never collected into `requirements[]` are out of scope for this gate.
- Set `sources.confluence_method` (`snippet` / `mcp` / `mixed`) as appropriate.
- Ensure **`sources.bitbucket_repo`** reflects the resolved workspace/slug (step **1** / **5b**) for downstream **COVERAGE** when the user omits `repo=` on the coverage trigger.
- Set **`schema_version`: 4** on the ref.
- Ensure **`epic_archetype`** and **`verification_topology`** are populated per steps **2c**, **3f–3h** (null **`verification_topology`** object is invalid on **new** emits — use empty arrays inside the object).
- Ensure **`verification_focus_proposed`** and **`principal_coverage_threads`** per step **3i** when trigger includes **`strict_principal=yes`** or operator expects principal handoff.
- Run **`python automation/tools/epic_prep_verify.py --mode ref --ref {EpicDir}dependencies/<KEY>-ref.json --strict-topology`** on **new** EPIC-PREP emits (after topology rollout). Legacy refs without topology pass **`ref`** without **`--strict-topology`** until re-prepped.
- When trigger includes **`strict_principal=yes`**, also run **`--strict-principal`** on the same command line.
- Run **`python automation/tools/epic_prep_verify.py --mode ref --ref {EpicDir}dependencies/<KEY>-ref.json`** — **block** delete of `temp/` and run completion until exit **0**.
- Validate JSON.
- **Delete** `{EpicDir}temp/`.
- Confirm `<KEY>-ref.json` contains no `/temp/` substring.

---

## Pitfalls

- **Bitbucket noise / rate limits** — Keep queries specific; cap at **8**; each hit needs a **`note`** explaining relevance; broad strings return junk.
- **Bitbucket Server search 404 / MCP shape** — Always split `PROJECT_KEY/repo_slug` into **`project_key`** + **`repo_slug`** for Stash. If `bitbucket_search_code` still returns **404** on `/rest/api/1.0/search`, use step **5b** browse fallback (capped); do not treat browse-only grounding as “Bitbucket offline.”
- **XT noise** — Small caps, keyword-seeded search, per-page `why_relevant`, pass 3.6 pruning.
- **LLM “validation”** — Steps 3.4 / 3.6 are structured audits (delete uncited / weak links), not proof of truth.
- **Obligation one-shot** — Skipping **3c** per-requirement subprocesses collapses invariants into COVERAGE `!` rows; parent must fan out.
- **Downstream leakage** — Never read **`-coverage`** / CRTQA during EPIC-PREP.
- **Yogi auth** — Skip live snippet or use MCP + `--storage-file` into `temp/` then merge; always set **`snippet_status`** / **`snippet_failure_reason`** when `snippet_text` is absent — do not leave unexplained nulls. Use step **3b** + finalize gate (step **8**) so first-pass flakiness does not ship silent gaps.
- **Adaptive omission** — Do not default to dxTrade5-only; use **`client_shell_impact`** and **`qa_default_both`** when appropriate.
- **Topology one-shot** — Skipping **3f–3g** subprocesses causes COVERAGE/PREP to over-generalise tier rules; parent must fan out like **3c**.
- **CRTQA in prep** — **`platform_reuse_candidates`** are **`suggestion_only`**; never fetch or cite CRTQA keys in `-ref.json`.
- **Delivery fabrication** — Do not emit **`known_fail`** / **`excluded`** without verbatim Jira or operator **`focus=`** evidence.
- **Principal one-shot** — Skipping **3i** leaves COVERAGE without thread spine or focus seed; parent must reconcile after **3h**.
- **Temp leakage** — Mandatory delete + grep self-check.

---

## Related

- Template: [`epics/templates/epic-ref.json`](../../epics/templates/epic-ref.json) (**schema v4**, `obligations_proposed[]`, `downstream_hints`, `verification_focus_proposed`, `verification_topology`)
- Topology contract: [`docs/epic-prep-topology-contract.json`](../../docs/epic-prep-topology-contract.json)
- Principal contract: [`docs/epic-prep-principal-contract.json`](../../docs/epic-prep-principal-contract.json)
- Obligation kinds: [`docs/epic-obligation-kinds.json`](../../docs/epic-obligation-kinds.json)
- Verifier: [`automation/docs/epic-prep-verify.md`](../../automation/docs/epic-prep-verify.md)
- Layout: [`epics/README.md`](../../epics/README.md)
- QA scope (Corner + Adaptive): [`docs/qa-project.json`](../../docs/qa-project.json)
- Yogi: [`automation/docs/yogi-url-resolve.md`](../../automation/docs/yogi-url-resolve.md)
- Coverage handoff: **COVERAGE** merges `implementation.hits` from this ref into `implementation_hits` — see [`coverage.md`](coverage.md) phase **7**.
