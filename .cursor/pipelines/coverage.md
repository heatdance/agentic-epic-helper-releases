# Pipeline: coverage

**Trigger**: user message starts with `COVERAGE:` and includes a Jira **Epic key** (e.g. `COVERAGE: CRT-593`). Optional tokens on the same line:

- **`repo=…`** — Bitbucket default for this run: Cloud `workspace/slug` or Stash `PROJECT_KEY/repo_slug` (e.g. `COVERAGE: CRT-593 repo=BRO/xt`; Adaptive-focused runs may use `repo=CAN/corner`).
- **`focus=...`** — free-text **verification focus override** when Jira is ambiguous or to stress a subset (e.g. `COVERAGE: CRT-639 focus=FX_SPOT_WeightedAvg_metrics`). Sets `epic_verification_focus.source` to `user_trigger_focus` and merges into `epic_verification_focus.statement` (see phase 3a). If `focus=` **conflicts** with Jira summary/description, record in `validation_log` and `anti_pattern_findings` rather than silently overriding Jira.
- **`strict_principal=yes`** — opt-in; finalize runs **`coverage_verify.py --strict-principal`** when ref has principal fields per [`docs/coverage-principal-contract.json`](../../docs/coverage-principal-contract.json). May combine with implicit **`--strict-topology`** when ref has topology.
- **`fix_breadth=yes`** — draft+truth pass 2 only: requires **`-analysis.json`** with open gaps **`recommended_action: rerun_coverage`**; increments **`draft_truth_round`** (max **2** per [`docs/draft-truth-contract.json`](../../docs/draft-truth-contract.json)). Must close prior ANALYSE gaps in **`scenario_coverage_map`** / checks.

**Version note (obligation subprocesses + topology + principal + draft_truth)**: schema **`schema_version: 2`** with **`obligations_coverage`**, **`scenario_coverage_map`**, **`coverage_pass`**, **`draft_truth_round`**. Contracts: [`docs/coverage-obligation-contract.json`](../../docs/coverage-obligation-contract.json), [`docs/coverage-topology-contract.json`](../../docs/coverage-topology-contract.json), [`docs/coverage-principal-contract.json`](../../docs/coverage-principal-contract.json), [`docs/coverage-draft-truth-contract.json`](../../docs/coverage-draft-truth-contract.json). Verifier: [`automation/docs/coverage-verify.md`](../../automation/docs/coverage-verify.md) (`--mode draft_truth` requires **`--ref`**).

**Scope**: **one Epic** per run. **Router rule**: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc).

**Forbidden inputs (production)**: CRTQA Jira issues, operator gold under **`.cursor/calibrate/`**, **`-tests.json`**, **`-discover.json`**, **`-precon.json`** — coverage reads **`-ref.json`** + Jira/tools only.

## Epic workspace (`{EpicDir}`)

Resolve **`{EpicDir}`** = `epics/<KEY>/` per [`epic-prep.md`](epic-prep.md).

**Prerequisite**: `{EpicDir}dependencies/<KEY>-ref.json` **must** already exist (from [`EPIC-PREP:`](epic-prep.md)). If missing: **stop** and instruct the user to run `EPIC-PREP: <KEY>` first. Do not fabricate requirement snippets.

**Outputs**:

- `{EpicDir}dependencies/<KEY>-coverage.json` — structured artifact (from [`epics/templates/coverage-ref.json`](../../epics/templates/coverage-ref.json)).
- `{EpicDir}<KEY>-coverage.md` — Jira Smart Checklist paste (`smart_checklist_markdown` body + optional header).

**Ephemeral**: `{EpicDir}temp/` — **must be deleted** before the run is considered complete (success or abort). Durable files must **not** contain **`/temp/`** or **`temp/`** as a path segment in any persisted string.

---

## Preconditions

- **user-mcp-atlassian**: Jira, Confluence, Bitbucket tools — read each tool’s schema before calls.
- **Yogi** (optional live REST): [`automation/docs/yogi-url-resolve.md`](../../automation/docs/yogi-url-resolve.md) — `yogi_resolve.py`, `yogi_snippet.py`; cookie or `--storage-file` into `temp/` when needed.
- **Figma MCP** (optional): when `figma.com` links exist and archetype is UI-heavy, [`automation/docs/figma-mcp.md`](../../automation/docs/figma-mcp.md).
- **Bitbucket**: **Recommended** when `sources.bitbucket_repo` can be resolved (see phase **1**). Parse `repo=WORKSPACE/SLUG` from the user message when present. If **no** repo is known after phase **1**, **skip** phase **7** searches with `validation_log` + `anti_pattern_findings` — do **not** invent a workspace/slug. Team default: [`docs/project.json`](../../docs/project.json) **`bitbucket.default_repo`**; Stash tool ladder and repo roles: [`docs/corner-platform-map.json`](../../docs/corner-platform-map.json) **`stash_notes`** / **`code_streams`** (optional; no secrets in repo). On Stash, `bitbucket_search_code` may **404** while **`bitbucket_browse_directory`** still works — phase **7** requires a **capped browse fallback** when search fails after correct **`project_key`** / **`repo_slug`** mapping (same rules as [`epic-prep.md`](epic-prep.md) step **5b**).

**Context anchors**: [`docs/project.json`](../../docs/project.json) (CT **342168339**, XT **402589545**), [`docs/qa-project.json`](../../docs/qa-project.json) (QAPORTAL Corner **497097273** subtree; **Corner Trader + Adaptive** client shells per `product_outline`), [`docs/corner-platform-map.json`](../../docs/corner-platform-map.json) (environment hosts, Jira index, Stash defaults).

**Epic ref**: Read **`client_shell_impact`** from `{EpicDir}dependencies/<KEY>-ref.json` (EPIC-PREP step 2b) when building **surfaces** and **cross-surface** checks; if missing, treat as gap — log in `validation_log` and use `qa_default_both` reasoning only with explicit note. When ref includes **`epic_archetype`** and **`verification_topology`** (EPIC-PREP steps **2c**, **3f**–**3h**), **MUST** consume per [`docs/coverage-topology-contract.json`](../../docs/coverage-topology-contract.json) — copy archetype, set **`emit_layout`**, seed scenario surfaces, bind oracle/delivery on checks — **do not re-infer** archetype or ignore delivery/oracle handoff. When ref includes **`verification_focus_proposed`** / **`principal_coverage_threads`** (EPIC-PREP step **3i**), **MUST** consume per [`docs/coverage-principal-contract.json`](../../docs/coverage-principal-contract.json) — copy focus verbatim, materialize thread H2 spine, keyed deferrals.

**Format norms**: [Smart Checklist markdown](#smart-checklist-markdown-normative) (this file).

---

## Smart Checklist markdown (normative)

Jira **Smart Checklist** body: scenario-based lines aligned with this pipeline’s outputs.

| Token | Use |
|--------|-----|
| `##` / `###` | Sections and subsections. Prefer **one E2E thread per major `##` section** (prerequisites → checks → variants). |
| `- ` | **One scenario per line** — **one primary observable outcome** per line. |
| `> ` | **Details**: execution variants, grep examples, formulas, Figma/Slack links, secondary evidence — not a separate scenario when the outcome is the same family. **Operator hints only** — prefixes from [`docs/coverage-operator-hints.json`](../../docs/coverage-operator-hints.json) (`Oracle`, `Harness`, `Verified`, `Prerequisite`, `Contrast`, `Note`). |
| `!` | **Ambiguity only** — include a **short human reason** naming the requirement key and what is unavailable (e.g. `! reason: DXINV-025 field specs unavailable — Confluence auth failed`). Do **not** paste bare machine enums (`mcp_export_failed`, `no_cookie`, …). Do **not** use vague “TBD” on executable lines. |

**Operator vs linker lines**: Machine audit strings (`> Discover:`, fixture ids, affordance ids, obligation ids) belong in **`checks[].linker_trace_lines[]`** on **`-coverage.json` only** — **never** in **`smart_checklist_markdown`** or **`-coverage.md`**. Expand human setup/harness hints from [`docs/coverage-operator-hints.json`](../../docs/coverage-operator-hints.json) when COVERAGE-REINFORCE merges discover fixtures.

**Platform reuse annex**: When ref has **`platform_reuse_candidates`**, set **`platform_reuse_annex`** on JSON for CLOSE/tests topology — **do not** paste into **`-coverage.md`** (JSON-only; `emit_to_markdown: false` per topology contract).

**Traceability**: put the **primary** `[REQ-KEY]` at the **start** of the scenario line (e.g. `[CRT-856] Console - …`). Use `>` for secondary links and extra keys. Repeat `[KEY]` when the dominant requirement changes (or once per section if the team prefers DRY + section note).

**Scope**: cover only epic scope; minimal cross-cutting with a one-line rationale when shared layers are touched.

**Epic verification focus (directional epics)**: Linked requirements often describe **both** branches of a configuration (e.g. FIFO vs WeightedAvg). The checklist must follow **`epic_verification_focus`** in `<KEY>-coverage.json` — **Jira narrative** (summary/description) wins over broad branching spec text unless `focus=` explicitly narrows. **`epic_verification_focus.statement`** is **JSON-only** for machine audit — **do not** paste `## Primary focus` into **`-coverage.md`**. Collapse setup into **`## Prerequisites`** (2–4 bullets). Do **not** emit symmetric peer sections for both branches when the epic describes a **one-way** change or a **single instrument class** unless both branches are `verification_role: primary` in the matrix.

**`widget_ui` / `shell_first` placement**: Card/trade **availability** (“card is available”) belongs under **`## Prerequisites`**, not as the sole check under a surface `###` subsection — use **`kind: invariant`**, never **`parity`**. Changing the `kind` does not move the check: an availability line stays under **`## Prerequisites`** unless **its own** obligation carries `config_vs_position` (`availability_misplaced`), and a heading emitted with nothing under it fails (`empty_markdown_section`). Field observables are one `-` each under the matching `###` (**one check per variation obligation** from EPIC-PREP). Currency / sign / 2dp claims live **with the field check** as a `>` oracle line copied from inventory `spec_text` — do **not** open **`## Rounding and display policy`** on `shell_first` (that H2 is `formula_first` only). Setup H2 is **`## Data setup`** (neutral). End with **`## Not attempted`** when out-of-scope or unmatched catalogue cells exist. A subsection whose only primary line matches stub wording (`card is available`, …) is invalid — emit a keyed `!` deferral instead of a skeleton stub.

**Out-of-epic fork prose**: For matrix rows with **`verification_role: out_of_epic`**, do **not** paste **non-target branch formulas** in checklist **`>`** lines or extra `-` lines. Confine fork description to **`explicitly_out_of_scope`** (consolidated bullet) unless Jira/AC **explicitly** requires in-checklist contrast; then at most one `### Contrast` subsection per prior rules.

**Metrics epics**: verify **definition and inputs** (truth source) before “same number in two UIs.” Do not assume UI **labels** match spec terms (e.g. midpoint vs mark).

**Calculation scenario contract** (`metrics_calculation` / metrics-heavy `mixed`): For each **`verification_role: primary`** metric row, require **at least one** top-level `-` that states **executable preconditions** (e.g. concrete order sequence, quantities, prices) and **expected outcome or relation** (e.g. average unchanged after partial close, rounding behavior), **or** a structured **`! reason: ...`** (e.g. `snippet_text missing for CRT-…`, `nested CRT-… not in requirements[]`). **Nested requirement keys** cited in snippets (e.g. rounding rules) must become a **check line or `!`**, not be silently dropped.

**Archetypes**: `widget_ui` (surfaces, Figma in `>`); `metrics_calculation` (formulas, position/account/portfolio level); `mixed` (both).

---

## Folder lifecycle

1. Ensure `{EpicDir}` exists.
2. Create `{EpicDir}temp/` if raw exports are needed.
3. **Allowed in `temp/` only**: e.g. `jira-epic.json`, `yogi-*.json`, `bitbucket-*.json`, **`coverage-section-<slug>.json`** (per-section subprocess drafts), scratch. **No cookies or tokens** in committed files.
4. **Section subprocess fan-out (phase 9)**: orchestrator merges `temp/coverage-section-*.json` into durable **`checks[]`** — parent **MUST NOT** one-shot all sections in one chat turn.
5. Merge durable facts into `{EpicDir}dependencies/<KEY>-coverage.json` and write `{EpicDir}<KEY>-coverage.md`.
6. **Delete** `{EpicDir}temp/` recursively before finishing.
7. **Self-check**: `<KEY>-coverage.json` and `.md` must **not** contain **`/temp/`** or **`temp/`** path segments (same bar as [`test-prep.md`](test-prep.md) durable JSON hygiene).

### Fresh-session stability

Prefer **deterministic structure** and **stable requirement-facing wording** copied from Jira or **`requirements[].snippet_text`** where it applies — avoid paraphrasing the same scenario with different surface text when the epic’s evidence already supplies phrasing. Post-hoc scoring vs operator gold: [`.cursor/pipelines/calibrate.md`](calibrate.md).

---

## Phases (complete all unless N/A — document skip in `validation_log`)

### 1. Load epic ref + Jira refresh

- **MUST** project `{EpicDir}dependencies/<KEY>-ref.json` with `jq` per [automation/docs/jq.md](../../automation/docs/jq.md) before loading the full file into context; then read fields needed for coverage (`requirements[]`, `synthesis`, **`client_shell_impact`**, `traversal.xt_refs`, `design.figma`, **`implementation.hits`**, **`epic_archetype`**, **`verification_topology`** from EPIC-PREP). Recommended jq slice for topology (store in working memory or `temp/ref-topology-slice.json` — **do not** persist secrets):

```bash
jq '{ epic_archetype, verification_topology, verification_focus_proposed, principal_coverage_threads: .verification_topology.principal_coverage_threads, obligations_proposed: [.obligations_proposed[] | {id, kind, disposition, deferral_reason, downstream_hints}] }' epics/<KEY>/dependencies/<KEY>-ref.json
```

- If **`client_shell_impact`** is null/missing, append **`validation_log`** + **`anti_pattern_findings`** (`fix_hint`: re-run EPIC-PREP for step 2b) and proceed with conservative surface defaults noted in phase 4/9.
- If **`epic_archetype`** / **`verification_topology`** missing → **legacy path** (infer archetype in phase **3**; thematic emit in phases **8**–**9**). If present → set **`topology_provenance.ref_path`**, **`fields_consumed[]`**, **`copied_at`** when copying in phases **3** / **4** / **9**.
- MCP `jira_get_issue` for `<KEY>`; optional save raw JSON to `temp/jira-epic.json`.
- **`sources.bitbucket_repo`** (resolve in order; **`repo=`** on the trigger **wins** and **short-circuits** the rest for **this run only**):
  1. **`repo=`** on the **COVERAGE** trigger when present.
  2. Else epic-ref **`sources.bitbucket_repo`** when non-null **unless** **Adaptive-only** applies: **`client_shell_impact.adaptive.status`** **`affected`** **and** **`client_shell_impact.corner_trader.status`** **`not_applicable`** **and** the ref’s repo is **`BRO/xt`** (stale default)—then use **`CAN/corner`** from [`docs/corner-platform-map.json`](../../docs/corner-platform-map.json) **`code_streams`** **`can_corner`** **`stash_repo`**.
  3. Else if **Adaptive-only** (same shell test) and ref repo is null → **`CAN/corner`** from that map entry.
  4. Else [`docs/project.json`](../../docs/project.json) **`bitbucket.default_repo`** if non-null.
  5. Else null.
- Set `sources.jira_fetched_at`, `sources.epic_ref_loaded_at` (ISO-8601), `epic_key`, `epic_ref_path`, and the resolved `sources.bitbucket_repo` above. Set optional `sources.note` if repo came from ref vs map vs project default (audit only).
- Parse optional **`focus=`** from the user message (free text after `focus=` until next space-delimited token or end of line). Preserve Jira **summary**, **description**, and `synthesis.problem_gist` (if present) as inputs for phase **3a**.
- Append `validation_log`: step `1`, action summary (include Bitbucket repo **source**: `trigger` | `epic_ref` | `adaptive_map` | `project_default` | `none`).

### 1½. Load epic obligations (required)

- From epic-ref **`obligations_proposed[]`**, initialize **`obligations_coverage`** map: for each row with **`disposition: primary_candidate`**, draft `status` `covered` | `deferred_in_check` | `excluded_with_reason` (finalized in phases **4b**, **8.5**, **9**, **11**).
- For each row with **`disposition: deferral_candidate`** or **`kind: explicit_deferral`**, initialize **`obligations_coverage`** with **`status: deferred_in_check`** (pending keyed check in phase **9**).
- **`deferral_candidate`** obligations may map to structured **`!`** checks only with **`obligation_ids[]`** on the check — not silent Dimensions deferral.
- If ref **`schema_version` < 4** or obligations missing: **STOP** — instruct **EPIC-PREP** re-run with obligation subprocesses.
- Append `validation_log`: step `1.5`, count primary vs deferral obligations.

### 2. Jira link–key hygiene

- Parse Epic `description` (and comments if needed) for `/requirements/` links and Yogi URLs.
- For each link: compare **visible label** (e.g. `DXINV-CB-34`) to **URL path** (e.g. …/DXINV-CB-29). On mismatch, record in `validation_log` and in `anti_pattern_findings` with `fix_hint` (do not silently trust label).
- Parse **tables**, **numbered scenarios**, **pre-requisites** (e.g. two account groups, different quotes, limit orders, AF validation).
- Append `validation_log`: step `2`.

### 3. Archetype classification

- **When `ref.epic_archetype.value` is present** (topology path): copy to **`coverage.archetype`**; set **`emit_layout`** from [`docs/coverage-topology-contract.json`](../../docs/coverage-topology-contract.json) **`map_from_archetype`** (`metrics_calculation` → **`formula_first`**; **`widget_ui`** / **`mixed`** → **`shell_first`**). Set **`topology_provenance.archetype_source`**: `copied_from_ref`. **Skip** inference subprocess.
- **Else (legacy path)**: set `archetype` to one of:
  - **`widget_ui`** — primary deliverable is widgets, screens, cards; heavy Figma; calculation is secondary.
  - **`metrics_calculation`** — primary deliverable is metrics, formulas, pre-trade validation, cross-surface numeric consistency.
  - **`mixed`** — both materially present.
  - Set **`emit_layout`** from the same map once archetype is inferred; set **`topology_provenance.archetype_source`**: `inferred`.
- Evidence must cite Jira text or `requirements[].snippet_text`; if inferred, note in `validation_log`.
- Append `validation_log`: step `3`, action summary (include `archetype`, `emit_layout`, `copied_from_ref` | `inferred`).

### 3a. Epic verification focus (required before matrix completion)

- **Principal path (preferred when ref has `verification_focus_proposed.statement`)**: copy **verbatim** to **`epic_verification_focus.statement`**; set **`source`**: **`epic_ref_proposed`**; copy **`keywords[]`** when present; set **`principal_provenance.focus_source`**: **`epic_ref_proposed`**.
- **Else**: populate **`epic_verification_focus`** from Jira summary/description/synthesis (`statement`, `source`, optional `keywords[]`) per existing rules below.
- **`statement`**: 1–3 sentences describing what this epic **primarily** verifies.
- **`source`**: `jira_summary` | `jira_description` | `epic_ref_synthesis` | **`epic_ref_proposed`** | `user_trigger_focus`. If the user passed **`focus=`**, set `source` to `user_trigger_focus` and merge that text into `statement` (or append with clear delimiter). If `focus=` **contradicts** ref **`verification_focus_proposed`** or Jira summary/description, log in `validation_log` and add `anti_pattern_findings` with `fix_hint`; do not hide the conflict.
- If requirement text is **broader** than Jira (e.g. full FIFO vs WeightedAvg matrix while Jira only names FX Spot migration), **Jira wins** for primary scope unless `focus=` overrides.
- **Obligation gate**: Do **not** drop **`primary_candidate`** obligations from scope without logging **`validation_log`** conflict (e.g. `focus=` vs invariant obligation) and updating **`obligations_coverage`** to `excluded_with_reason` with rationale.
- **`epic_verification_focus` must be set before building `coverage_matrix[]`** so each row can be tagged with `verification_role`.
- Append `validation_log`: step `3a`, action summary.

### 4. Coverage matrix

- Build `coverage_matrix[]` from ref **`verification_topology.scenario_capability_rows[]`** when present (draft+truth per [`docs/coverage-draft-truth-contract.json`](../../docs/coverage-draft-truth-contract.json)): one matrix row per **`scr-*`** requiring coverage; else legacy obligation-driven rows.
- Optional **matrix subprocess** per major section slug when matrix is large — output `temp/coverage-matrix-<slug>.json` merged by orchestrator.
- **Stable matrix `id` (normative)**: `id` must identify the **same semantic row** across reruns. **Assign ids after deterministic ordering**: sort rows by `capability` (string), then `aggregation_level`, then joined sorted `requirement_keys` (e.g. `KEY1|KEY2`), then label **`m-001`**, **`m-002`**, … in order. Do **not** add ad-hoc suffixes such as **`m-006b`** for the same conceptual capability across runs; if you **split** one row into two, note the retired id in `notes_from_epic` and log the change in `validation_log` (step `4`).
- **`supporting` vs `out_of_epic` decision ladder**:
  1. Clearly in Jira / **`epic_verification_focus`** scope → **`primary`** or **`supporting`**.
  2. Linked requirement text is **explicitly not epic-owned** → **`out_of_epic`** **and** the rationale must also appear under **`explicitly_out_of_scope`** (phase 11) — not a stray matrix row alone.
  3. **Ambiguous** → default **`out_of_epic`** + rationale (phase 11) rather than **`supporting`** to reduce `verification_role` flips between runs.
- **Stable classification**: Re-assigning the **same** capability (`capability` + keyed evidence) between **`primary`** / **`supporting`** / **`out_of_epic`** across reruns **without** new Jira/snippet/BB evidence is an **anti-pattern**. Prefer one decision per evidence snapshot; if interpretation must change, append **`validation_log`** step `4` with **why** (do not silently flip roles).
- **`verification_role` rules**:
  - **`primary`** — must drive **top-level `-`** checks (or a structured `!` with reason if blocked).
  - **`supporting`** — formula/variant belongs under **`>`** on a primary check, or in **at most one** optional `### Contrast / regression (non-epic path)` subsection with **minimal** `-` lines **only** if Jira/AC explicitly requires non-regression on other branches/types.
  - **`out_of_epic`** — must **not** appear as standalone top-level `-` for that branch alone; record under **`explicitly_out_of_scope`** with rationale (consolidate duplicate rationales when possible).
- **Row-complete gate**: every row in the Epic’s **impacted metrics / capabilities table** and every **explicit scenario bullet** must map to at least one matrix row or `explicitly_out_of_scope` with rationale (no silent omission). **Row-complete does not mean** every semantic variant of every linked requirement gets its **own top-level `-` line** — non-primary branches are **`supporting`** or **`out_of_epic`**, not peer scenarios, unless both are **`primary`** per `epic_verification_focus`.
- **Single-class / narrow epic**: When **`epic_verification_focus`** names **one instrument class** or one-way migration, **do not** add a **second top-level `-`** whose only purpose is enumerating a **full configuration type matrix** from a linked requirement (e.g. entire FIFO vs WA instrument-type table); fold into **one** primary config check or a single **`>`** under it, with **`supporting`** / **`out_of_epic`** matrix rows as needed.
- **Surfaces**:
  - **When `verification_topology.jira_scenario_surfaces[]` is non-empty** (`shell_first` or mixed with scenario block): **primary seed** for matrix `surfaces[]` and phase **8** section order — preserve array order (= runner view). Map each row’s `shell` / `widget` into matrix notes; attach **`obligation_ids[]`** from the surface row when present. Merge/dedupe with **`client_shell_impact`**; **topology order wins** for **`shell_first`** emit.
  - **When topology surfaces empty** (`formula_first`, e.g. CRT-639): seed `surfaces[]` from **`client_shell_impact`** (dxTrade5, WebBroker, **Adaptive**, console/API as applicable) plus epic text; keep matrix-first obligation mapping (639 regression).
  - Include **Adaptive** when status is **`affected`** or **`qa_default_both`** — do not omit unless **`not_applicable`** with Jira evidence.
  - Apply **`verification_topology.shell_roles`**: when **`webbroker_dealer`** / **`webbroker_client`** differ, add matrix **`notes_from_epic`** hints (dealer Backup Prices vs client Client Area) — no credentials in durable JSON.
- Append `validation_log`: step `4`.

### 4b. Invariants section subprocess (when ref has `kind: invariant`)

- **Dedicated subprocess** (do not fold into generic Dimensions): for each **`primary_candidate`** **`invariant`** obligation, draft **primary** `checks[]` under section **`## Invariants under configuration change`** ([`docs/coverage-obligation-contract.json`](../../docs/coverage-obligation-contract.json)).
- Set matrix row(s) with **`verification_class`** hint `invariant_under_change` per [`docs/epic-obligation-kinds.json`](../../docs/epic-obligation-kinds.json).
- Example pattern: account **group** change must **not** alter existing position **average price** / open P/L inputs — executable ladder or keyed deferral with **`obligation_ids[]`**, **not** `! epic silent on multi-group`.
- Write `temp/coverage-section-invariants.json`; merge in phase **9**.
- Update **`obligations_coverage`** for each invariant `obl-###`.
- Append `validation_log`: step `4b`.

### 5. Snippet enrichment

- For each `requirement_keys` entry and keys from epic-ref `requirements[]`: ensure token-light `snippet_text` (Yogi live or MCP export to `temp/`). Respect existing **`snippet_status`** / **`snippet_failure_reason`** from EPIC-PREP ([`epic-prep.md`](epic-prep.md) steps **3**, **3b**, **8**); if enriching fixes a gap, note in `validation_log`. If a key remains without usable snippet after enrichment, use **one** structured **`! reason: snippet_text missing for <KEY>`** (or equivalent) per [calculation scenario contract](#smart-checklist-markdown-normative) — **do not** add **extra** duplicate diagnostic **`-`** lines beyond that contract and normal ambiguity rules (avoids bullet-count noise when prep is incomplete).
- Collect **nested** requirement links from snippets into `nested_requirement_refs[]` (`key`, `page_id`, `short_url`, `source`); **nested keys** (e.g. rounding) must flow into **checks or `!`** per calculation contract.
- Never fabricate snippet text.
- Append `validation_log`: step `5`.

### 6. XT Confluence (targeted)

- Seed from matrix keywords, `traversal.xt_refs` in epic-ref, and explicit XT URLs in Jira.
- **Narrow** search in XT space; add `xt_confluence_hits[]` with `page_id`, `url`, `title`, `why_relevant`, `summary` (short — **no** full page body in durable JSON).
- This pipeline may perform **more** XT lookups than epic-prep’s cap; each hit must justify `why_relevant`.
- If phase N/A (pure CT-local UI with no XT signal), skip with `validation_log` reason.
- Append `validation_log`: step `6`.

### 7. Bitbucket implementation search

- **Merge prep hits**: If epic-ref **`implementation.hits[]`** is non-empty, **import** each row into the coverage artifact’s working set. **Dedupe** by `(path, normalized fragment)` (trim whitespace; treat empty fragment as path-only key) against any existing row. Preserve **`source_phase`**: `epic_prep` on imported rows when present.
- **Renumber**: Assign coverage **`implementation_hits[].id`** as **`impl-001`**, **`impl-002`**, … in stable order: **first** all deduped prep hits (preserving a deterministic sort — e.g. by `path` then `search_query`), **then** hits discovered in the coverage-only pass below.
- **Coverage-only pass**: Map `sources.bitbucket_repo` to MCP arguments the same way as [`epic-prep.md`](epic-prep.md) step **5b** (**`project_key`** + **`repo_slug`** for Stash `PROJECT_KEY/repo_slug`; **`workspace`** + **`repo_slug`** for Cloud). Run **`bitbucket_search_code`** for strings from **enriched** snippets and **`coverage_matrix`**: metric names, flags, feature toggles, collision-prone symbols. **Cap** new search calls similarly to prep (order of magnitude **~8**). If search returns **HTTP 404** / `/rest/api/1.0/search` after correct mapping, use the **same browse fallback** as epic-prep step **5b** (at most **3** `bitbucket_browse_directory`, optional **one** `bitbucket_get_file_content`) and add tool-backed rows. Add new hits with **`source_phase`**: `coverage` (or omit if the template treats absence as coverage-era). Append only rows not already deduped.
- Each hit: `id`, `search_query`, `path`, `fragment`, `note` (one-line relevance). Flag contradictions (e.g. missing feature flag, duplicate logic paths) for checklist `>` or structured `!` with reason.
- If `bitbucket_repo` missing: **still retain** merged prep hits from epic-ref if any were imported; **skip** new `bitbucket_search_code` calls and append `validation_log` + `anti_pattern_findings` explaining blocked **additional** search pass (unless prep hits already ground implementation — then note reduced BB scope).
- If `bitbucket_repo` missing **and** epic-ref has **no** `implementation.hits`: **skip** as today — `validation_log` + `anti_pattern_findings`.
- Append `validation_log`: step `7` (prep hit count, new search count, dedupe summary).

### 8. E2E spine from epic scenarios

**Layout by `emit_layout`** ([`docs/coverage-topology-contract.json`](../../docs/coverage-topology-contract.json)):

**`formula_first`** ( **`metrics_calculation`** — CRT-639 regression; phases **8**–**9** unchanged in substance):

- Derive **section structure** for `smart_checklist_markdown`: one **##** section per E2E thread (CRTQA-10034 style): prerequisites / data setup → capability group → variants (groups, quotes, hours).
- **Primary focus block (required, verbatim)**: The **first substantive `##`** after any title/header must satisfy [Smart Checklist markdown — Epic verification focus](#smart-checklist-markdown-normative) (verbatim **`epic_verification_focus.statement`**), and must anchor the **primary thread** (data/instrument/config under test → metrics or UI outcomes). Place additional narrative **after** that block or under following **`##`** sections — do not paraphrase the focus line. Avoid symmetric **FIFO section / WeightedAvg section** (or equivalent forks) **unless** both forks are **`verification_role: primary`** in the matrix.
- **Algorithm stressors** that **define** a metric (e.g. **position crosses zero**, **partial close without changing weighted average**, **opening-trade-only contribution**) belong in the **same `##` section** as the parent capability (e.g. average fill / open P/L tied to CRT-1740 / CRT-1738), not isolated under a generic **Dimensions** section unless they are **genuinely cross-cutting** with phase-10 evidence.
- **Section requirements**: When ref has **`primary_candidate`** **`invariant`** → include **`## Invariants under configuration change`**. When ref has **`rounding`** → include **`## Rounding and display policy`** (headings per coverage-obligation-contract).
- Subsections **`###`** for logical UI groupings only when they clarify a formula/ladder thread — not shell-per-widget layout.

**`shell_first`** ( **`widget_ui`** / UI-heavy **`mixed`** — CRT-594 runner view):

- **One `##` per `jira_scenario_surfaces[]` row** in ref order. Heading pattern: **`## {shell_label} — {widget}`** using contract **`shell_labels`** (e.g. `## dxTrade5 — Derivatives`, `## dxCore — show prices` when console surface present in matrix).
- **Primary focus**: still required — use **`## Primary focus`** as first substantive **`##`** with verbatim **`epic_verification_focus.statement`** on the following **`-`** line (same normative rule); **then** surface sections in topology order.
- Trailing **`## Cross-surface invariants`** for midpoint/mark/backup rules that span surfaces (from obligations + **`pricing_oracle_rules`** with `cross_group` / mark surfaces).
- **Do not** emit **`## Platform reuse candidates`** in markdown — set **`platform_reuse_annex`** on JSON only when ref has **`platform_reuse_candidates`**.
- **Anti-pattern `thematic_only_widget_epic`**: do **not** use only thematic sections (setup → mapping → invariants) when **`emit_layout: shell_first`** — runner order must match Jira Scenarios.

- Append `validation_log`: step `8`, include `emit_layout`.

### 8.5. Principal thread materialization (when ref has `principal_coverage_threads[]`)

**Requires:** step **8** spine; ref **`verification_topology.principal_coverage_threads[]`** non-empty; contract [`docs/coverage-principal-contract.json`](../../docs/coverage-principal-contract.json).

1. For each thread in **ref array order**, emit **`## {title}`** (use thread **`title`** or **`thread_section_map`** default for **`coverage_thread`**).
2. Draft **≥1 primary `-`** per **`obligation_ids[]`** in that thread (executable preconditions for **`environment_setup`**; set optional **`checks[].coverage_thread`** for audit).
3. **`shell_first` order normative:** **`## Primary focus`** (verbatim statement) → **principal thread `##`** sections → **surface `##`** from **`jira_scenario_surfaces`** → trailing sections (Cross-surface invariants only).
4. Set **`principal_provenance.threads_consumed[]`**: `{ thread_id, section_heading, obligation_ids[] }`; **`principal_provenance.copied_at`** (ISO-8601).
5. Subprocess: `temp/coverage-section-thread-<thread_id>.json` when **>4** threads; parent merges before phase **9**.
6. Append `validation_log`: step `8.5`.

**`metrics_calculation` short-circuit:** setup thread optional; still copy focus when **`verification_focus_proposed`** present.

### 8.6. Scenario groups (draft for TEST-PREP)

**Contract:** [`docs/scenario-groups-contract.json`](../../docs/scenario-groups-contract.json).

**Requires:** step **8** / **8.5** complete; **`checks[]`** primary rows emitted.

1. Derive initial **`scenario_groups[]`** on **`-coverage.json`**:
   - From ref **`principal_coverage_threads[]`**: one group per thread when thread maps to distinct test narrative; merge surface checks within same thread when combinatorics fit **`variant_sequence`**.
   - From Smart Checklist **`##`** sections: checks sharing a section may share a group when they exercise the same capability variant set.
   - Default **`combinatorics`**: **`variant_sequence`** when ≥2 checks in group are parallel variants (e.g. order types); **`single_flow`** otherwise.
   - Set **`source`**: **`principal_thread`** | **`section`**; **`source_ref`**: thread id or section heading.
2. **Human gate (`coverage_review`):** operator **may merge/split** groups (e.g. three order-type checks → one group **`Issuing orders`**); set **`source`**: **`operator_merge`** on edited rows.
3. **Finalize at freeze:** when operator sets **`sources.coverage_frozen_at`**, **`scenario_groups[]`** **MUST** partition all **`verification_role: primary`** checks (each **`check_id`** in exactly one group).
4. Append **`validation_log`**: step **`8.6`**.

**Downstream:** TEST-PREP emits one **`test_bundles[]`** row per group — see [`.cursor/pipelines/test-prep.md`](test-prep.md).

### 9. Draft checks (archetype branches) — per-section subprocesses

**Orchestrator**: one subprocess per major **`##`** section (+ **invariants** / **rounding** passes from **4b**). Input: section slug, matrix rows, obligations slice, snippets. Output: `temp/coverage-section-<slug>.json` with `checks[]` fragment. Merge into artifact; set **`obligation_ids[]`** / **`obligation_kinds[]`** on each check.

**Forbidden**: moving **`invariant`** obligations to generic **Dimensions** `!` deferrals ([`dimension_deferral_without_obligation_review`](../../docs/coverage-obligation-contract.json)).

**Keyed deferrals (required for ref deferral obligations)**

- For each **`deferral_candidate`** / **`explicit_deferral`** row: emit **one** check with **`scenario_line`**: `- ! reason: <deferral_reason from ref>` and **`obligation_ids: [obl-###]`**; set **`ambiguity`**: `{ "flag": "!", "reason": "<deferral_reason>" }`; update **`obligations_coverage`** → **`deferred_in_check`** + **`check_id`**.
- **Forbidden:** generic Dimensions `!` without **`obligation_ids`** when ref lists deferral obligations ([`docs/coverage-principal-contract.json`](../../docs/coverage-principal-contract.json)).

**All archetypes**

- One **observable outcome** per `-` line.
- Lead with **`[REQ-KEY]`** when a primary requirement applies (e.g. `[CRT-856]`, `[DXINV-CB-25]`).
- Use `>` for: grep examples, Figma/Slack links, formula expansion, parameter variants, **Bitbucket paths / fragments** from **`implementation_hits`** (including **`source_phase: epic_prep`**) when they ground the check (not separate top-level checks when same outcome family).
- **`!`** only as structured ambiguity: `! reason: <short machine-readable explanation>` — **no** casual TBD on executable scenario lines. Unexecutable unknowns go to `checks[].ambiguity` or a dedicated “Blocked / needs BA” subsection.
- **Optional / conditional scenarios** (retest lines, roadmap or platform disclaimers, “nice-to-have” checks): either **include in every run** with evidence or a structured **`! reason:`**, **or** **omit** and record the omission in **`explicitly_out_of_scope`** and/or `coverage_matrix[].notes_from_epic` — **no silent** inclusion in one run only.
- **Requirement terminology**: When Jira or **`requirements[].snippet_text`** uses specific setup or domain terms the epic **depends on** (e.g. **account group**, two-group preconditions), include **≥1** evidence-backed **`-`** line (or scoped **`>`** detail under the dominant primary check) that **preserves that vocabulary** — do **not** invent synonyms for concepts the source text already names.

**`metrics_calculation` / `mixed` (metrics-heavy)**

- **Primary-first rule**: **Top-level `-` lines** must **predominantly** address **`verification_role: primary`** matrix rows. Set each check’s optional **`verification_role`** to match the dominant matrix row for auditability.
- **Calculation scenario contract**: For each **primary** metric row, emit **≥1** `-` with **executable ladder** (orders, prices, qty) + **expected relation** **or** **`!`** per [Smart Checklist markdown](#smart-checklist-markdown-normative). Set optional **`calculation_contract`** on the check: `ladder_present` | `deferred_ambiguous` (see template).
- **Order**: (1) Truth source / formula / **calculation scenarios** for **primary** rows. (2) **Then** **per-surface** consistency: **one primary `-` per in-scope surface** (dxTrade5, WebBroker, **Adaptive**, API as applicable) for each **in-scope metric** (avg fill, open P/L, % P/L gross, realized P/L, etc. as epic implies) **or** `! reason: metric not exposed on this surface` — avoid one bundled line with only “e.g.” **Seed surfaces from `client_shell_impact`**. (3) **Visibility**: where relevant, state **UI vs API-only vs DB** observable **or** `!` if undocumented. (4) **Then** API / Account Statement / Explain margin / perspective metrics **if** epic or snippets imply.
- **Non-primary branches**: **`supporting`** content → **`>`** under a primary check **only** if still inside epic focus; **`out_of_epic`** → **`explicitly_out_of_scope`** only — **no** fork formulas in **`>`** under primary checks (see normative **Out-of-epic fork prose**). **At most one** optional `### Contrast / regression (non-epic path)` with **minimal** `-` lines **only** if Jira/AC **explicitly** requires proving no regression on other types/config branches.
- **Do not** assume UI labels match spec vocabulary (e.g. “midpoint” may not appear as a column name); tie checks to **semantic** definition from requirements + `implementation_hits`.
- State **aggregation level** for margin-style metrics (position vs account vs portfolio).

**`widget_ui` / `mixed` (UI-heavy)**

- **Atomic obligation mapping (required):** each ref **`primary_candidate`** obligation → **exactly one** `checks[]` row with **`obligation_ids: [obl-###]`**. Copy **`emit_subsection`** → **`checks[].subsection`**; **`scenario_line`** → `- [REQ] {assertion_fragment}` from obligation (or short statement when fragment absent). **Forbidden** tag-level stubs when snippet is OK: `card is available`, `is present and visible`, `must expose … per linked requirements` without a named observable ([`docs/coverage-obligation-contract.json`](../../docs/coverage-obligation-contract.json) `tag_level_stub_patterns`).
- When **`emit_layout: shell_first`**: align **`-`** checks to the **surface `##`** section for each **`jira_scenario_surfaces`** row; set optional **`topology_surface_id`** (`jss-###`) on checks for verifier binding.
- **Oracle binding**: When ref has **`pricing_oracle_rules[]`**, set **`checks[].oracle_rule_id`** to matching rule **`id`**; put surface-specific oracle in **`>`** hints (e.g. **first tier** for Positions/Derivatives, **TextConfiguration tier closest ≥ qty** for Watchlist/OE) — avoid generic “tier-appropriate” on every line.
- **Delivery honesty**: Map ref **`delivery_notes[]`** to affected checks — set **`delivery_status`**: `known_fail` → **`failed`** (markdown **`[FAILED]`** on scenario line); `excluded` → **`excluded`** (markdown **`x`** or “excluded” wording); `waived` / `pending_verification` → **`deferred`**. **Distinct** from requirement **`!`** ambiguity deferral.
- Align sections with Figma frames (links in `>`) when design links exist; scope strictly to epic; use `explicitly_out_of_scope` for adjacent features. Apply the same **`epic_verification_focus`** / **`verification_role`** discipline when the epic is directional (e.g. one widget family or one instrument class).

- Append `validation_log`: step `9`.

### 10. Dimensions pass

Add explicit `-` checks **only when supported by evidence** — Jira epic text, **`requirements[].snippet_text`**, **`implementation_hits`**, matching **`obligations_proposed[]`** row, **or** a **`variation`** object whose **`rule_id`** is in [`docs/variation-catalogue.json`](../../docs/variation-catalogue.json) (`variation_catalogue_rule`) — that this epic **changes** or **must validate** that dimension. **Do not** add generic dimension lines “for coverage” without that signal (record **`anti_pattern_findings`** `dimension_without_evidence` if the model would otherwise pad).

**Contract** ([`docs/coverage-obligation-contract.json`](../../docs/coverage-obligation-contract.json)): **Forbid** blanket lines such as **`! reason: epic silent on multi-account`** / **multi-group quote permutations** when ref contains **`primary_candidate`** **`invariant`** with **`config_vs_position`** `position_state` or **`account_group_assignment`** — those belong under **Invariants** (phase **4b**), not Dimensions.

Candidate dimensions (each requires the evidence gate above):

- Trading vs **non-trading hours** (only if epic/snippets/BB imply session or mark-path changes).
- **Two accounts, two groups**, different quotes — only if Jira/snippets **or obligation** describe multi-account/group behavior **and** not already covered as an **invariant** check; else omit or keyed deferral with **`obligation_id`**.
- **Position crosses zero** / partial-close stress — if **not** already placed under the parent metric **`##`** in phase 8, add here **only** when cross-cutting; prefer parent-section placement for metric-definitional rules.
- **FX conversion** — instrument vs account vs portfolio currency when multi-currency applies and epic implies.
- **Order mark vs position mark**; **pre-trade validation** vs **open position** metrics separately when epic implies.
- **Explain margin** / **perspective metrics** when referenced in requirements.
- **Catalogue-mandated variations** already emitted as obligations in EPIC-PREP — map 1:1; do **not** drop them as “padding”.

- Append `validation_log`: step `10`.

### 10b. Oracle detail lines + Not attempted (variation)

- For each primary check whose obligation has **`variation`**: require **≥1** `>` detail line that copies a distinctive substring of the inventory **`spec_text`** for that parameter (sign / color / currency / precision / “only if”). Verifier: `variation_oracle_detail_required`.
- **Name the parameter** in the detail line (`> Realized PL — Signed. Colored: …`), so a bullet read on its own says which field it governs. Verifier: `variation_oracle_detail_unlabelled`.
- **State the outcome per variation.** Two variations of the same parameter must not carry identical detail text: negative → minus sign and red; positive → green, no minus. Copying the whole spec cell onto both is a shortfall, not an oracle. Verifier: `duplicate_variation_oracle_detail`.
- Set **`needs_setup: true`** when catalogue rule or variation kind needs seeded data (`negative`, `absence`, multi-fill).
- Emit **`## Not attempted`** when `explicitly_out_of_scope` or any requirement `unmatched_spec_patterns` is non-empty — short bullets so the engineer sees where to extend. Do **not** hide gaps.

### 11. Scope prune

- Fill `explicitly_out_of_scope[]` with `{ item, rationale }`.
- **Canonical out-of-scope wording for gates**: Where team **gold** or downstream checks expect a **literal** marker in consolidated scope prose (e.g. the phrase **`out of epic`** in an **`item`** or **`rationale`**), use that **exact** wording **at least once** in the consolidated **`explicitly_out_of_scope`** text for the relevant theme — avoid **only** synonymous phrasing so substring gates and humans stay aligned. (Still obey [Out-of-epic fork prose](#smart-checklist-markdown-normative) in the checklist body.)
- **If/then requirement branches not named in `epic_verification_focus`**: add at least one **`explicitly_out_of_scope`** entry listing those branches (e.g. “FIFO path for non-target instrument types — out of epic scope per Jira”), **unless** every such branch is already captured as **`out_of_epic`** matrix rows with the same rationale consolidated in one bullet.
- **Optional / conditional checklist items** (phase 9): if not emitted as **`-`** lines, capture here **why** they are out of scope or deferred so reruns do not drift.
- Minimal cross-cutting checks only with one-line justification (shared component touched).

- Append `validation_log`: step `11`.

### 12. Grounding audit

- For each check `id`, set `grounding_audit.by_check_id[]` with `evidence_keys`, optional `evidence_impl_ids`, `status` `grounded` | `ungrounded`.
- **`evidence_impl_ids`**: include **`impl-…`** ids for **`implementation_hits`** that support the check, whether **`source_phase`** was **`epic_prep`** (handoff from EPIC-PREP) or added in phase **7** — same grounding rules for both.
- **Epic focus alignment**: If a **top-level `-`** check’s observable addresses only **`supporting`/`out_of_epic`** subject matter (per matrix) without a **`primary`** mapping or without Jira/AC explicitly requiring that contrast, set **`ungrounded`** and note misalignment in `validation_log` step `12` (do not add a third enum value — use `ungrounded` + log).
- List all `ungrounded_check_ids[]`. **Enumeration only** — do not treat a second LLM pass as proof.

- Append `validation_log`: step `12`.

### 13. Anti-pattern scan

- Populate `anti_pattern_findings[]` for: UI-only rows without calculation path (metrics epic); assumed visible “midpoint” label; generic group-switch line without metric-specific meaning; bundled unrelated observables on one line; duplicate `>` blobs (dedupe with section-level note once).
- **`dual_branch_symmetry_without_epic_warrant`**: symmetric top-level `-` coverage for **both** sides of a config fork (e.g. FIFO and WeightedAvg peer sections) when Jira describes a **single instrument class**, **one-way migration**, or **one-sided AC**. **`fix_hint`**: tighten `epic_verification_focus`, demote rows to `supporting`/`out_of_epic`, move non-target branch to `explicitly_out_of_scope`.
- **`fork_formula_in_body_for_out_of_epic`**: non-target branch formulas in **`-` or `>`** when `verification_role: out_of_epic` — move to **`explicitly_out_of_scope`** only.
- **`dimension_without_evidence`**: trading hours, multi-account, or similar dimension lines with **no** Jira/snippet/BB/obligation support for **this** epic.
- **`dimension_deferral_without_obligation_review`**: generic `!` under Dimensions for invariant/group-change work.
- **`obligation_without_check_or_exclusion`**: `primary_candidate` in ref not in **`obligations_coverage`** as covered or excluded.
- **`invariant_obligation_in_dimensions_only`**: invariant obligation only deferred under Dimensions.
- **`missing_calculation_ladder`**: primary metric row without **ladder `!` pair** per calculation scenario contract.
- **`adaptive_missing_when_in_scope`**: **`client_shell_impact.adaptive`** is **`affected`** or **`qa_default_both`** but no Adaptive-targeted **`-`** in cross-surface section (unless every metric has `!` N/A on Adaptive).
- **`shell_section_orphan`**: **`shell_first`** and ref **`jira_scenario_surfaces`** row has **no** check in matching **`##`** section (or missing **`topology_surface_id`** binding).
- **`oracle_unbound`**: ref **`pricing_oracle_rules`** rule with **`disposition: primary_candidate`** has **no** check with matching **`oracle_rule_id`**.
- **`delivery_silent`**: ref **`delivery_notes`** with **`known_fail`** or **`excluded`** has **no** check with **`delivery_status`** **`failed`** / **`excluded`** and markdown marker.
- **`thematic_only_widget_epic`**: **`widget_ui`** epic with scenario surfaces emitted only as thematic sections (no per-surface **`##`**) **without** principal thread preface when ref has **`principal_coverage_threads`**.
- **`deferral_without_obligation_id`**: deferral obligation in ref with **`!`** check missing **`obligation_ids[]`**.
- **`setup_thread_missing_checks`**: ref **`environment_setup`** thread obligation with no check in setup section.
- **`focus_drift_from_ref_proposed`**: ref **`verification_focus_proposed.statement`** present but **`epic_verification_focus.statement`** differs (no **`focus=`** override logged).

- Append `validation_log`: step `13`.

### 13b. Obligations verifier (required before emit)

```text
python automation/tools/coverage_verify.py --mode obligations \
  --coverage {EpicDir}dependencies/<KEY>-coverage.json \
  --ref {EpicDir}dependencies/<KEY>-ref.json
```

Block phase **14** until exit **0**. Fix **`obligations_coverage`**, invariant section, or **`excluded_checks_with_reason`** on failure.

### 14. Emit

- Set **`schema_version`: 2** on coverage JSON.
- Set **`emit_layout`**, **`topology_provenance`**, optional **`platform_reuse_annex`** when topology path was used.
- Run **`python automation/tools/coverage_md_sync.py --coverage {EpicDir}dependencies/<KEY>-coverage.json --write --md {EpicDir}<KEY>-coverage.md`** to build collapsed paste markdown from **`checks[]`** (`##` / `###` grouping, **`## Prerequisites`**, no `## Primary focus`).
- Set **`smart_checklist_markdown`** on JSON from the same builder (canonical: [`automation/tools/coverage_md_sync.py`](../../automation/tools/coverage_md_sync.py)). **Self-check**: no `## Primary focus` in paste; **`shell_first`**: surface **`##`** order matches ref **`jira_scenario_surfaces`**; **`coverage_matrix[].id`** ordering matches phase **4**; every **`out_of_epic`** matrix row has **`explicitly_out_of_scope`** rationale; no **`> Discover:`** / platform reuse heading in markdown body.
- Write `{EpicDir}<KEY>-coverage.md` at epic root; write `{EpicDir}dependencies/<KEY>-coverage.json`.
- Run **`python automation/tools/coverage_verify.py --mode emit --coverage {EpicDir}dependencies/<KEY>-coverage.json --md {EpicDir}<KEY>-coverage.md`** — block finish until exit **0**.
- When ref has **`epic_archetype`** + **`verification_topology`**, also run **`python automation/tools/coverage_verify.py --mode emit --strict-topology --coverage {EpicDir}dependencies/<KEY>-coverage.json --ref {EpicDir}dependencies/<KEY>-ref.json --md {EpicDir}<KEY>-coverage.md`** — block finish until exit **0**.
- When trigger includes **`strict_principal=yes`** or ref has **`verification_focus_proposed`** + **`principal_coverage_threads`**, also run **`--strict-principal`** on the same command line.
- **Delete** `{EpicDir}temp/`.

**Downstream handoff (no action in this pipeline):** **ANALYSE** consumes unresolved **`delivery_notes`** / **`oracle_rule=unresolved`** gaps; **COVERAGE-REINFORCE** may split surface checks after **TEST-DISCOVER**.

---

## Pitfalls

- **Missing epic-ref** — Never skip EPIC-PREP; coverage depends on `requirements[]` and validated synthesis.
- **Bitbucket without repo** — Resolve via phase **1** (`repo=` → epic-ref → `project.json` default); if still unknown, merge epic-ref **`implementation.hits`** only; avoid inventing workspace/slug.
- **Label vs URL mismatch** — Breaks traceability; fix in hygiene step.
- **Symmetric requirement branching vs directional epic** — Linked Yogi rows may describe **both** FIFO and WeightedAvg (or similar forks). **Do not** mirror that into **peer top-level `-` lines** when Jira only changes **one** side — use `epic_verification_focus`, `verification_role`, and `explicitly_out_of_scope`.
- **Out-of-epic fork text in checklist body** — Fork formulas belong in **`explicitly_out_of_scope`**, not under **`>`** on primary checks, unless Jira mandates contrast.
- **Missing `client_shell_impact`** — COVERAGE should flag **EPIC-PREP** gap; Corner + Adaptive must be considered for surfaced metrics/UI.
- **Temp leakage** — Mandatory delete + substring self-check.
- **LLM “validation”** — Grounding audit lists evidence; it does not replace human review for high-risk metrics.
- **Matrix `id` drift** — Use phase **4** deterministic ordering; avoid ad-hoc suffix rows that change between runs without a logged split.
- **Focus line paraphrase** — Phase **8** / **14** require verbatim **`epic_verification_focus.statement`** in the first substantive **`##`** block.
- **Calibrate gold vs playbook** — Post-hoc prod vs operator gold: [`.cursor/pipelines/calibrate.md`](calibrate.md); see [Fresh-session stability](#fresh-session-stability).

---

## Related

- Template: [`epics/templates/coverage-ref.json`](../../epics/templates/coverage-ref.json) (**schema v2**)
- Obligation contract: [`docs/coverage-obligation-contract.json`](../../docs/coverage-obligation-contract.json)
- Topology contract: [`docs/coverage-topology-contract.json`](../../docs/coverage-topology-contract.json)
- Upstream topology: [`docs/epic-prep-topology-contract.json`](../../docs/epic-prep-topology-contract.json)
- Verifier: [`automation/docs/coverage-verify.md`](../../automation/docs/coverage-verify.md)
- Smart Checklist norms: [above](#smart-checklist-markdown-normative)
- Epic handoff: [`epics/templates/epic-ref.json`](../../epics/templates/epic-ref.json), [`epics/README.md`](../../epics/README.md)
- Epic pipeline: [`epic-prep.md`](epic-prep.md)
- Yogi: [`automation/docs/yogi-url-resolve.md`](../../automation/docs/yogi-url-resolve.md)
