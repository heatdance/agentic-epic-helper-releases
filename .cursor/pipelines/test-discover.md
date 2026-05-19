# Pipeline: test-discover (obligation closure)

**Trigger**: user message starts with **`TEST-DISCOVER:`** and includes a Jira **Epic key** (e.g. `TEST-DISCOVER: CRT-639`). Optional tokens on the **same line**:

- **`benchmark_suite=<suite_id>`** / **`benchmark_attempt=<n>`** — shadow **`{EpicDir}`** per [`docs/benchmark-contract.md`](../../docs/benchmark-contract.md); sets **`sources.discovery_mode: benchmark`** and **`sources.crtqa_index_enabled: true`** (CRTQA Jira index allowed).
- **`crtqa_index=yes`** — force CRTQA Jira index (Step **C-index**) in **generation** mode without benchmark tokens.
- **`proceed`** — after a **Phase 0 hard stop** only. Re-run **Phase 0** from scratch; on pass, start a **fresh** run (new **`sources.discover_run_started_at`**, new **`validation_log`** chain, new **`temp/discover-ledger.json`**). **MUST NOT** append to a prior failed attempt or merge an existing **`-discover.json`** `validation_log`.
- **`skip_cold_gate=yes`** — explicit opt-out from Phase **0** probes. **`validation_log`** **MUST** record **`cold_gate_skipped`**; **`sources.cold_gate_skip_token_used: true`** in **`-discover.json`**.
- **`dxtrade5_creds=<user>/<password>`** and **`webbroker_creds=<user>/<password>`** — transient FE helpers only (**MUST NOT** enter durable JSON). **`supplied`** ≠ authenticated Chrome session.
- **`fe_exploration_waived=yes`** — only after Phase **0b** hard stop + operator ack. Caps dxTrade5/WebBroker Chrome at **`shell_only`**; sets **`sources.fe_exploration_waived: true`** and **`fe_credentials.*: waived`** for waived surfaces.

**CRTQA index default:** **`sources.crtqa_index_enabled: false`** unless **`crtqa_index=yes`** **or** both benchmark tokens are present. When false, **MUST NOT** run Step **C-index**; **`reference_index`**, **`precondition_signals`**, **`prerequisite_edges`** **MUST** be **`[]`** at emit.

**Scope**: **one Epic** per run. **Router**: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc).

**Doctrine**: [docs/harness-principles.md](../../docs/harness-principles.md) §8 — **TEST-DISCOVER** is a **closure engine** over **coverage obligations**, not a CRTQA catalogue.

**Flow**: **`EPIC-PREP:`** → **`COVERAGE:`** → (optional **`ANALYSE:`** / human polish) → **`TEST-DISCOVER:`** → **`TEST-PREP:`**.

---

## Epic workspace (`{EpicDir}`)

Resolve **`{EpicDir}`** like [`epic-prep.md`](epic-prep.md).

### Prerequisites (blocking)

| Artefact | Required |
|----------|----------|
| `{EpicDir}<KEY>-ref.json` | **Yes** |
| `{EpicDir}<KEY>-coverage.json` | **Yes** |
| `{EpicDir}<KEY>-analysis.json` | **Recommended** (schema v2) — load **`exploration_suppressed[]`**; set `sources.analysis_loaded` |

### Outputs

- **`{EpicDir}<KEY>-discover.json`** only ([`epics/templates/discover-ref.json`](../../epics/templates/discover-ref.json) **schema_version 3**).
- **No** `-discover.md` in v1.

**Out of scope**: authoring full precondition tickets; ordered setup recipes; global fixture aggregation; edits under [`docs/dxtrade5-harness/`](../../docs/dxtrade5-harness/README.md) / [`docs/webbroker-harness/`](../../docs/webbroker-harness/) (read-only).

---

## Discovery closure contract

**Universe** = **primary** `checks[]` and **primary** `coverage_matrix[]` in **`-coverage.json`** only. Do **not** add obligations from unconstrained Jira search.

**Structured `!` checks:** For a primary check whose **`scenario_line`** is **`!` only**, set **`scope_gap`** in **`obligation_ledger[]`** **only** when **`obligations_coverage[<obligation_id>].status`** is **`deferred_in_check`** (or the check lists **`obligation_ids[]`** tied to a deferral). **Do not** auto-**`scope_gap`** generic Dimensions deferrals (e.g. former **`chk-009`**-style “epic silent on multi-group”) when ref **`-ref.json`** already has a **`primary_candidate`** **invariant** covered by an executable check after **COVERAGE** obligation patch — treat those as **`affordance_mapped`** / **`fixture_need_mapped`** targets instead.

Three lanes (epic-agnostic):

| Lane | Question | Durable fields |
|------|----------|----------------|
| **Obligations** | What must we prove? | **`obligation_ledger[]`** (one row per primary `chk-*`) |
| **Affordances** | How can we observe each proof? | **`verification_affordances[]`**, tooling |
| **Fixture needs** | What must exist in the environment first? | **`fixture_needs[]`** (from coverage/ref + setup-depth probes) |

Optional when **`crtqa_index_enabled`**: **`reference_index[]`** (and mirrored **`precondition_signals[]`**), **`prerequisite_edges[]`**.

**Finished** when:

1. Every primary obligation has **`disposition`** ∈ `affordance_mapped` \| `fixture_need_mapped` \| `prerequisite_mapped` (index on only) \| `tooling_blocked` \| `scope_gap`.
2. When **`crtqa_index_enabled`**: reference queue drained or **`unresolved_precondition_refs[]`** + **`reference_cap_hit`** logged.
3. **`python automation/tools/discover_verify.py`** exits **0** for target **`discovery_status`** (see [Emit rules](#emit-rules-discovery_status)).

**`discovery_status: incomplete`** = honest gaps **after Phase 0 passed** (setup depth insufficient, verifier partial closure, etc.). **`aborted`** = Phase 0 hard stop without waive — **no** **`-discover.json`** written.

**Phase 0 hard stop:** When a **required** Postgres, crtqa console, or **FE credential** probe fails (and **`skip_cold_gate=yes`** / **`fe_exploration_waived=yes`** is not set per gate), **MUST NOT** write **`{EpicDir}<KEY>-discover.json`** or start the closure loop. Reply in chat with BLUF + **`operator_recovery`**-shaped blocks (see [Tooling and session_gates contract](#tooling-and-session_gates-contract)). Optional scratch only: **`{EpicDir}temp/discover-cold-gate.json`** — **delete** before the operator finishes (success or abort); **never** merge cold-gate scratch into final discover.

---

## Normative rules (MUST / MUST NOT)

### Orchestration — no one-shot

- **MUST NOT** materialize ledger, run closure, and **Final emit** in one completion as if done without **verifier** pass (Phase 0 **`proceed`** rules excepted).
- **MUST** use **one subprocess per heavy slice**: affordance batch (Step **B**), fixture needs (Step **C-fixture**), optional CRTQA index (Step **C-index**), delivery competency (Step **D**), affordance smoke per competency (Step **E**).
- Recommended: Cursor **Task** **`generalPurpose`** with narrow prompts.

### Self-heal closure loop

After Step **A** (ledger materialized):

1. Run Steps **B** → **E** (target **pending** rows; **C-index** / ref queue only when **`crtqa_index_enabled`**).
2. Merge into **`{EpicDir}temp/discover-ledger.json`** (+ optional **`discover-closure-iteration-NN.json`**).
3. Run **`discover_verify.py`** (see [Verifier gate](#verifier-gate-step-f)).
4. If **fail** and **iterations_used < 5** and **progress** (≥1 new disposition or depth upgrade): goto 1. If any **primary**-linked **`fixture_needs[]`** row remains **`classified_only`** and its **`kind`** is listed in [`docs/discover-fixture-probes.json`](../../docs/discover-fixture-probes.json), iteration **N+1** **MUST** run that kind’s probe batch (log **`validation_log`** step **`phaseE_fixture_<kind>`**)—**MUST NOT** repeat only **`console_guide`** for config kinds.
5. If **fail** and **no progress**: stop loop; emit **`incomplete`** with **`closure_gaps`** / **`setup_depth_gaps`**.
6. If **pass** for target status: **Final emit**.

**Caps** (defaults in **`exploration_budgets`**): **5** closure iterations, **25** Jira **`jira_get_issue`** fetches per run (C-index only), reference **depth 2**, **8** FE navigational cycles per surface cluster.

### Path hygiene / scrub

- Scratch only under **`{EpicDir}temp/`**. **Delete** `temp/` before run complete.
- **MUST NOT** persist **`/temp/`** or secrets in **`-discover.json`**.

### Evidence

- **`evidence_grade`** on operational claims per schema enums.
- **MUST NOT** invent PR URLs, SQL rows, or commands.

---

## Algorithm (Steps 0 → G)

### Step 0 — Cold-session gates (blocking, hard stop)

Run after **`-ref.json`** and **`-coverage.json`** load. **MUST** project coverage/ref (and later **`temp/discover-ledger.json`**) with `jq` per [automation/docs/jq.md](../../automation/docs/jq.md) before loading full files into context for the closure loop. Set **`sources.discovery_mode`** (`generation` \| `benchmark`) and **`sources.crtqa_index_enabled`** per trigger tokens.

1. **`skip_cold_gate=yes`**: skip probes; log **`cold_gate_skipped`**; set tooling/session_gates per [contract](#tooling-and-session_gates-contract); continue to Step **A**.
2. Else apply **[Tooling intent rubric](#tooling-intent-rubric-universal)** → **`tooling.*.intent`** (same labels as [`crtqa_env_common.py`](../../automation/tools/crtqa_env_common.py) **`tooling_intent_from_coverage`**).
3. Run **machine gates** (always both; coverage only sets **`required_for_epic`** on each gate):

```powershell
python automation/tools/crtqa_env_probe.py --coverage {EpicDir}<KEY>-coverage.json
```

Optional scratch: copy probe JSON to **`{EpicDir}temp/discover-cold-gate.json`** — **delete** before run complete; **never** reference **`temp/`** in durable JSON.

4. If any gate has **`status: fail`** and **`required_for_epic: true`** → **STOP** — no **`-discover.json`**, no closure loop. Chat: BLUF + copy each failed gate’s **`recovery`** block as **`operator_recovery`** (slash-first **`actions[]`** from probe output — e.g. **`/crtqa-console start`**, **`/crtqa-env`**, tunnel README).
5. **Postgres depth** — when rubric marks **`postgres_ctqa`** **`required`** and tunnel gate passed: MCP **`list_tables`** (or minimal readonly **`query`**) on **`postgres-ctqa`**. MCP failure → **`operator_recovery`** **`gate_id: postgres_ctqa_tunnel`** → **STOP** (port up but MCP down is still a hard stop).
6. **Console depth** — when rubric marks **`crtqa_dx_console`** **`required`**: **`Get-CrtqaConsoleStatus.ps1`** must exit **0** (session file + master PID + **`crtqa_multiplex_ok`** echo). Agent runs this script; **do not** ask the operator to “confirm in UI” at Phase 0.

#### Step 0b — FE credential gate (blocking)

Contract: [`docs/fe-ui-probe-contract.json`](../../docs/fe-ui-probe-contract.json).

1. Derive **`required_fe_surfaces`**: **`dxtrade5`**, **`webbroker`** when **`chrome_devtools`** intent is **`required`** and primary coverage/discover surfaces need that shell; **`adaptive`** when **`-ref.json`** **`client_shell_impact.adaptive.status`** is **`affected`** or **`likely_affected`** (no cred token).
2. For each of **`dxtrade5`** / **`webbroker`** in **`required_fe_surfaces`**:
   - If **no** matching cred token on trigger **and** **`fe_exploration_waived=yes`** is **not** set → **STOP** (no **`-discover.json`**). Chat: BLUF + **`operator_recovery`** with **`gate_id`**: **`fe_dxtrade5_creds_missing`** or **`fe_webbroker_creds_missing`**. Explain re-run with **`dxtrade5_creds=`** / **`webbroker_creds=`** or, after ack, **`fe_exploration_waived=yes`** (UI exploration capped at **`shell_only`**).
   - If **`fe_exploration_waived=yes`** on trigger → set **`sources.fe_exploration_waived: true`**; planned **`fe_ui_sessions.*`**: **`waived`** for waived surfaces; skip Step **0c** smoke for those surfaces.
3. **Adaptive** (when required): no cred gate; Step **0c** or Step **E** smoke only.

**MUST NOT** treat **`fe_credentials.supplied`** (token on line) as login success.

#### Step 0c — Post-login smoke (when creds supplied)

Use **`chrome-devtools`** MCP; creds **only** from trigger line. Minimum pass/fail: contract **`post_login_smoke`**.

| Surface | On pass | On fail |
|---------|---------|---------|
| **dxtrade5** | **`fe_ui_sessions.dxtrade5: authenticated`**; **`session_gates.fe_login_human_gate`**: **`authenticated`** | **STOP** — **`gate_id: fe_ui_authentication_failed`** |
| **webbroker** | **`fe_ui_sessions.webbroker: authenticated`** | same |
| **adaptive** | **`fe_ui_sessions.adaptive: authenticated`** or **`shell_only`** with documented absence | log; may continue with **`scope_gap`** if shell unreachable |

Record sanitized **`widgets_seen[]`** in scratch for Step **E** **`exploration_log`** / affordance artifacts. Surfaces not in **`required_fe_surfaces`**: **`fe_ui_sessions.*: not_required`**.

| Tool | When | Probe | On required failure |
|------|------|-------|---------------------|
| **`postgres_ctqa`** | intent `required` | **`crtqa_env_probe`** tunnel gate + MCP **`list_tables`** | **`gate_id: postgres_ctqa_tunnel`** → **STOP** |
| **`crtqa_dx_console`** | intent `required` | **`crtqa_env_probe`** + **`Get-CrtqaConsoleStatus.ps1`** | **`gate_id: crtqa_dx_console_session`** → **STOP** |

**Operator prep (recommended, not a pipeline):** tunnel tab → **`/crtqa-console start`** → **`/crtqa-env`** — see [automation/docs/crtqa-env.md](../../automation/docs/crtqa-env.md) and [`.cursor/commands/crtqa-env.md`](../commands/crtqa-env.md).

**`proceed`:** Re-run Step **0** from scratch (same env probe + MCP + status script). If all required probes pass, set **`sources.cold_gate_resolved_at`**, log **`validation_log`** entry **`phase0_proceed`**, then Step **A** with **fresh** **`sources.discover_run_started_at`** and **empty** **`validation_log`** before **`phase0`** / **`phaseA`** entries for this run.

**MUST NOT** emit **`discovery_status: incomplete`** (or any discover file) when Phase 0 required probes failed without **`skip_cold_gate=yes`**.

---

### Step A — Materialize obligation ledger (deterministic)

**Orchestrator only** — no Jira.

For each **`checks[]`** row with **`verification_role: primary`**:

| Field | Source |
|-------|--------|
| **`check_id`** | `checks[].id` |
| **`matrix_ids`** | `coverage_matrix[]` ids where `verification_role: primary` and surfaces/requirement_keys overlap |
| **`surfaces`** | union of check + matrix surfaces + ref **`client_shell_impact`** |
| **`requirement_keys`** | `checks[].requirement_keys` |
| **`calculation_contract`** | `checks[].calculation_contract` |
| **`evidence_need[]`** | derive: `ui` if dxtrade5/webbroker/adaptive; `console` if ladder/console language; `sql`/`api` if engine/DB/parity; `pr` if backend delivery needed; `doc_only` if only Confluence refs |
| **`disposition`** | **`pending`** |
| **`affordance_ids`**, **`fixture_need_ids`**, **`prerequisite_keys`** | `[]` |

Write **`{EpicDir}temp/discover-ledger.json`**. Set **`sources.discover_run_started_at`** (ISO-8601, once per run). Initialize **`validation_log: []`** on the ledger; append **`phaseA`** as first entry.

**Analysis v2 (when `-analysis.json` present):** `jq` project **`exploration_suppressed[]`**. For each listed **`check_id`**, set ledger disposition per keyed deferral rules — **do not** auto-**`scope_gap`** on `!`-only primary lines when suppression cites **`deferred_in_check`** or **`obligations_coverage`**. Set **`sources.analysis_loaded: true`**. If missing: **`sources.analysis_fallback_logged: true`**.

Copy **`environment.client_shell_impact`** from **`-ref.json`** (`corner_trader` / `adaptive` **`status`** and **`note`** only). Set **`fe_credentials.adaptive: not_required`**. Persist **`fe_credentials`** and **`fe_ui_sessions`** from Phase **0b/0c** (not from trigger tokens alone): **`supplied`** \| **`missing`** \| **`waived`** per surface; **`fe_ui_sessions`**: **`not_required`** \| **`waived`** \| **`shell_only`** \| **`authenticated`**. Set **`sources.fe_exploration_waived`** when waiver token used.

---

### Step B — Affordance mapping (subprocess per batch)

For each **pending** ledger row (batch by competency or surface):

- Assign **`affordance_ids`** (create **`verification_affordances[]`** stubs: `aff-NNN` with **`setup_role`**: `observation` or `fixture` as appropriate).
- Set candidate **`disposition`**: `affordance_mapped` when observation route identified; else stay **`pending`** for Step **C-fixture**.

Cross-link **`linked_check_ids`**. No invented widgets or SQL.

---

### Step C-fixture — Fixture needs (always)

**Orchestrator or subprocess** — **no CRTQA** unless covered by delivery keys (CRT/XT only in Step **D**).

1. From primary checks, matrix rows, checklist semantics, and **`-ref.json`** **`client_shell_impact`**, derive **`fixture_needs[]`** entries: **`id`** (`fix-NNN`), **`kind`** (e.g. `weighted_avg_fx_spot_account`, `console_ladder_session`, `webbroker_dealer_metrics`, `dxtrade5_retail_positions`—see [`docs/discover-fixture-probes.json`](../../docs/discover-fixture-probes.json)), **`surfaces`**, **`linked_check_ids`**, **`derivation`**, initial **`setup_depth: classified_only`**. Include **`adaptive`** in **`surfaces`** when the linked primary chk lists **`adaptive`** and config is shell-wide (metrics-only Adaptive smoke remains Step E Adaptive row).
2. Link ledger **`fixture_need_ids`** on affected rows.
3. Map harness pointers ([`docs/dxcore-console-harness.json`](../../docs/dxcore-console-harness.json), dxtrade5/webbroker harness, fixture probe registry) in **`notes`** only—no Jira keys.

**MUST NOT** populate **`reference_index`** or **`prerequisite_edges`** in this substep.

---

### Step C-index — CRTQA reference index (conditional)

Run **only** when **`sources.crtqa_index_enabled: true`**. **Separate** from **`delivery_issues_by_competency`**.

1. **Issuetype calibration** — one **`jira_search`** sample; record in **`issuetype_calibration`**.
2. **Epic-linked pull**: Tests, Pre-Condition, QA Task, Test Execution.
3. **`jira_get_issue`** each hit → **`reference_index[]`** (mirror to **`precondition_signals[]`** at emit).
4. **Reference queue**: extract `CRTQA-nnn`, `CRTBL-nnn`, etc. from fetched bodies (**cap 25**, **depth 2**). Unfetched → **`unresolved_precondition_refs[]`**.
5. **`prerequisite_edges[]`** from “Preconditions:” lines when present in Jira—**not** invented prose.
6. Update ledger: **`prerequisite_mapped`** + **`prerequisite_keys`** when Jira covers setup (index mode only).

**MUST NOT** run Step **C-index** when **`crtqa_index_enabled`** is false.

---

### Step D — Delivery + PR map (subprocess per competency)

**Delivery** — CR / DR / Improvement on Epic link (CRT/XT keys); all statuses. **Not** CRTQA Tests unless operator enabled C-index for separate bucket.

**PR URL extraction ladder** (per issue, in order):

1. **`jira_get_issue`** `*all` — dev-summary / PR URLs verbatim.
2. Description + comments — whitelist URL substrings only.
3. **`bitbucket_list_pull_requests`** capped match when repo known.

**`pr_code_map[]`** — one subprocess per competency; cap ~30 paths.

---

### Step E — Affordance smoke and setup depth (subprocess per competency)

Bounded probes to raise **`setup_depth`** on fixture affordances and prove observation reachability (not full test execution). Normative probe recipes: [`docs/discover-fixture-probes.json`](../../docs/discover-fixture-probes.json).

#### Fixture kinds (`fixture_needs[].kind`)

Run **one subprocess per kind** still at **`classified_only`** / **`shell_only`** after prior iteration. Update linked **`verification_affordances[]`** and **`fixture_needs[].setup_depth`**.

| `kind` | Probe | Depth when met |
|--------|-------|----------------|
| **`console_ladder_session`** | `Invoke-CrtqaDxConsole.ps1 -Probe`: `show console_guide` + `exit` | **`probe_executed`** |
| **`weighted_avg_fx_spot_account`** | After `console_guide`, grep/narrow live guide for **account_group**, **instrument**, **corner_subtype** / PL settings; **read-only** `show` commands only; capture sanitized **`instrument_id`**, **`account_group_id`**, WeightedAvg lane text in **`notes`** / aff artifacts | **`command_family`** if family identified but ids missing; **`probe_executed`** when ids + lane evidence present |
| **`webbroker_dealer_client_metrics`** | Chrome: dealer login; client metrics / Position Book | **`shell_only`** at login landing only; **`probe_executed`** only when **`fe_ui_sessions.webbroker`** is **`authenticated`** and grid/columns seen |
| **`dxtrade5_retail_positions`** | Chrome: login; Positions metric columns | **`shell_only`** max when **`fe_ui_sessions.dxtrade5`** is **`shell_only`** or **`waived`**; **`probe_executed`** only when **`authenticated`** and columns seen |

**Link parity account:** When Step E already opened an account (e.g. **antonfx**) on dxTrade5/WebBroker, **MUST** copy that account/symbol into **`weighted_avg_fx_spot_account`** **`notes`** and use it to target console instrument shows—do not leave **`fix-*`** config fixtures orphaned from FE probes.

**Postgres (optional):** For chks with **`sql`** in **`evidence_need`**, readonly query per registry + tunnel README discover subsection—does not replace console path for **`probe_executed`** on config kinds.

#### Surfaces (observation + Adaptive)

| Surface | Probe target | Depth when met |
|---------|--------------|----------------|
| **postgres** | `list_tables` / readonly shape query (Step **0** or here) | **`probe_executed`** for SQL affordances |
| **dxtrade5** / **webbroker** | Per kind table or FE cred tokens on trigger | per kind |
| **adaptive** | See below | **`probe_executed`** when bar met |

#### Adaptive (Chrome — no cred token)

| Condition | Requirement |
|-----------|-------------|
| **`-ref.json`** **`client_shell_impact.adaptive.status`** is **`affected`** or **`likely_affected`** | **MUST** Chrome smoke on CTQA **`application_urls.adaptive`** ([`docs/corner-platform-map.json`](../../docs/corner-platform-map.json) **`adaptive_login_policy`**: shared principal from Confluence—**no** `adaptive_creds=` token) |
| Adaptive **not** affected (`unaffected` / absent) | May **`scope_gap`** with explicit reason |
| Chrome unavailable | **`tooling_blocked`** or **`scope_gap`** with tooling note—not “creds missing” |

**Probe bar:** navigate → shell loads → confirm portfolio/position metric labels for linked checks (e.g. chk-007: Average Fill / Open P/L / % PL gross, or structured absence). **`fe_credentials.adaptive`** stays **`not_required`**. **`session_gates.fe_login_human_gate`**: **`not_required_adaptive_hardcoded`** when only Adaptive uses shared principal.

**Dispositions:** Adaptive-primary chks → **`affordance_mapped`** when smoke succeeds; **`scope_gap`** only when shell unreachable or Chrome down—not when creds were omitted by design.

Update **`verification_affordances[].setup_depth`**, **`fixture_needs[].setup_depth`**, and **`status`**.

**Ledger dispositions after E:**

- **`fixture_need_mapped`** when linked fixture needs meet rubric (**`command_family`** or **`probe_executed`** per [`discover-fixture-probes.json`](../../docs/discover-fixture-probes.json) **`complete_requires`**).
- **`scope_gap`** + **`setup_depth_gaps[]`** entry (`setup_depth_insufficient`) when required probe blocked.
- **`affordance_mapped`** when observation-only checks satisfied without deep fixture.

**MUST NOT** require full Pre-Condition ticket prose or ordered multi-step recipes.

**Step E depth rules (v3):**

- **MUST NOT** set **`fixture_needs[].setup_depth: probe_executed`** for **`webbroker_dealer_client_metrics`** / **`dxtrade5_retail_positions`** when matching **`fe_ui_sessions.*`** is **`shell_only`** or **`waived`** — max **`shell_only`**; use **`scope_gap`** + **`setup_depth_insufficient`** when generation bar needs depth.
- **`discovery_status: complete`** (generation): dxtrade5/webbroker fixture kinds at **`probe_executed`** require **`fe_ui_sessions.*: authenticated`** for those surfaces (or honest **`scope_gap`** on linked chks).
- Affordance **`exploration_log`** / artifacts: **`login_state`**: **`shell_only`** \| **`authenticated`**; **`widgets_seen[]`** sanitized labels only.

---

### Verifier gate (Step F)

```powershell
python automation/tools/discover_verify.py `
  --coverage {EpicDir}<KEY>-coverage.json `
  --ledger {EpicDir}temp/discover-ledger.json
```

Doc: [`automation/docs/discover-verify.md`](../../automation/docs/discover-verify.md).

- **Exit 0** → eligible for **`discovery_status: complete`** only if [emit rules](#emit-rules-discovery_status) also satisfied.
- **Non-zero** → another iteration or emit **`incomplete`**.

**MUST NOT** set **`complete`** without verifier pass.

---

### Emit rules (`discovery_status`)

| Mode | `complete` allowed when |
|------|-------------------------|
| **Generation** (`crtqa_index_enabled: false`) | Verifier pass **and** (same depth bar as v2) **and** when primary surfaces need dxtrade5/webbroker: **`fe_ui_sessions.*`** is **`authenticated`** or **`waived`** before any linked fixture kind is **`probe_executed`** at emit **and** when **`environment.client_shell_impact.adaptive.status`** is **`affected`** / **`likely_affected`**: Adaptive Chrome smoke **`probe_executed`** (no adaptive closure gaps) |
| **Benchmark / crtqa_index** | Verifier pass; setup depth **recommended** (warnings OK); index populated when C-index ran |

If generation depth bar not met: emit **`incomplete`**, **`obligation_closure.verifier_passed: true`** only when verifier allows incomplete target (use **`--allow-incomplete`** on post-check), or **`verifier_passed: false`** with gaps logged.

---

### Step G — Final emit

1. Project **`temp/discover-ledger.json`** into **`-discover.json`** per [`discover-ref.json`](../../epics/templates/discover-ref.json) v3 — **MUST NOT** copy **`validation_log`** or other fields from a prior **`-discover.json`** on disk.
2. Fill **`obligation_closure`** including **`setup_depth_gaps`**.
3. **`sources.discover_schema_version: 3`**, **`sources.discover_run_started_at`** from ledger. If **`crtqa_index_enabled`**: copy **`reference_index`** → **`precondition_signals`**; else both **`[]`**, **`prerequisite_edges: []`**.
4. Apply [Tooling and session_gates contract](#tooling-and-session_gates-contract) on final tooling/session_gates (Phase 0 passed before emit).
5. Post-emit: `discover_verify.py --discover ...`.
6. Write **`{EpicDir}<KEY>-discover.json`**. **Delete** **`{EpicDir}temp/`** entirely.

#### `validation_log` hygiene

- Append-only during the current run; each **`at`** ≥ **`sources.discover_run_started_at`**.
- Log **`phase0`** once after Phase 0 pass (or **`phase0_proceed`** then **`phase0`** on **`proceed`** runs). **Do not** log **`phase0`** again on closure iteration 2+.
- Closure iterations: append **`closure_iteration_N`** only.
- If duplicate **`phase0`** without **`phase0_proceed`** between them would appear, add **`anti_pattern_findings[]`**: `merged_validation_log_from_prior_run`.

---

## Tooling and session_gates contract

Epic-agnostic: persisted only **after Phase 0 pass** (or **`skip_cold_gate=yes`** with honest skipped flags).

| Probe outcome | `tooling.postgres_ctqa` | `session_gates.postgres_ctqa_tunnel` |
|---------------|-------------------------|--------------------------------------|
| MCP OK, intent required | `availability: available` | `probe_pass` |
| MCP fail, intent required | `availability: unavailable` | `probe_required_operator` — **do not emit** discover |
| intent skipped | `availability: skipped` | `skipped` or `not_required` |

| Probe outcome | `tooling.crtqa_dx_console` | `session_gates.crtqa_console_handshake` |
|---------------|----------------------------|------------------------------------------|
| multiplex present, intent required | `availability: available`, **`session_started: true`** | `success` |
| multiplex absent, intent required | `availability: unavailable`, **`session_started: false`** | `failed` or `pending_operator_session` — **do not emit** discover |
| intent skipped | `availability: skipped` | `skipped` |

**Forbidden:** `availability: available` with **`session_started: false`** when intent is **`required`**.

**`operator_recovery[]`** (when used at Phase 0 stop, chat only unless scratch file): each item **MUST** include **`gate_id`**, **`blocks_test_prep: true`**, **`symptom`**, **`required_when_note`**, non-empty **`actions[]`**, non-empty **`documentation_refs[]`**. **MUST NOT** use ad-hoc **`tool`** / **`action`**-only objects.

Final **`-discover.json`** **MUST** have **`operator_recovery: []`** when Phase 0 passed (recovery was chat-only for the stop path).

---

## Tooling intent rubric (universal)

| Intent | Meaning |
|--------|--------|
| **`required`** | Step **0** probe; failure → stop without waive |
| **`recommended`** | Probe; failure → log, no stop |
| **`optional`** / **`skipped`** | As today |

**`postgres_ctqa`**: **required** if primary checks/matrix mention engine, risk, export, SQL, DB, settlement, parity vs backend, or **`api`** surface primary, or **`metrics_calculation`** + engine-like keywords.

**`crtqa_dx_console`**: **required** if primary checks mention console, dxcore, publisher, position_metrics, execution trade, weighted average, or **`calculation_contract: ladder_present`**.

**`chrome_devtools`**: **required** if primary surfaces include dxtrade5, webbroker, or adaptive.

**`figma`**: **skipped** unless **`-ref`** has Figma URLs → **optional**.

---

## Bounded exploration caps

| Control | Cap |
|---------|-----|
| Closure iterations | **5** |
| Jira issue fetches / run (C-index only) | **25** |
| Reference traversal depth | **2** |
| FE cycles per surface cluster | **8** |
| Loop detection | 3 repeat snapshot hashes → **blocked** / `loop_detected` |

---

## Tooling pointers

| Need | Doc / tool |
|------|-------------|
| Atlassian MCP | [`.cursor/rules/mcp-atlassian-search.mdc`](../rules/mcp-atlassian-search.mdc) |
| Postgres CTQA | MCP **`postgres-ctqa`**; [`automation/tools/tunnel/README.md`](../../automation/tools/tunnel/README.md) |
| Chrome DevTools | [`automation/docs/chrome-devtools-mcp.md`](../../automation/docs/chrome-devtools-mcp.md) |
| crtqa console | [`automation/tools/crtqa-console/README.md`](../../automation/tools/crtqa-console/README.md) |
| **Verifier** | [`automation/tools/discover_verify.py`](../../automation/tools/discover_verify.py) |
| Fixture probe registry | [`docs/discover-fixture-probes.json`](../../docs/discover-fixture-probes.json) |
| FE UI probe contract | [`docs/fe-ui-probe-contract.json`](../../docs/fe-ui-probe-contract.json) |
| FE URLs | [`docs/corner-platform-map.json`](../../docs/corner-platform-map.json) |

---

## `test_prep_gates`

Set **`blocked: true`** when:

- Any primary obligation **`tooling_blocked`** without acceptable waiver.
- **`obligation_closure.verifier_passed`** is false at emit when operator expected runnable discover.
- Legacy: **`missing_pr_for_required_delivery`**, **`tool_unavailable_fe`**, mandatory affordance **blocked** without **`scope_gap`**.

**`reasons[]`**: include **`obligation_closure_incomplete`**, **`setup_depth_insufficient`** when applicable.

---

## Disposition reference

| Disposition | Generation (`crtqa_index_enabled: false`) | CRTQA index on |
|-------------|---------------------------------------------|----------------|
| **`affordance_mapped`** | Observation route identified | Same |
| **`fixture_need_mapped`** | Fixture needs classified + depth rubric met | Same |
| **`prerequisite_mapped`** | **Disallowed** | Jira keys cover setup |
| **`tooling_blocked`** | Required tool down + **`operator_recovery`** | Same |
| **`scope_gap`** | Adaptive/deferred/setup depth waived | Same |

---

## Environment

- Resolve CT QA URLs from **`corner-platform-map.json`** (Adaptive: **`adaptive_login_policy`** / **`adaptive_login_note`**—shared principal, no discover cred token).
- **`fe_credentials`** / **`fe_ui_sessions`** persisted from Phase **0b/0c** outcomes; cred tokens on trigger are input only.
- Never persist usernames/passwords in JSON.

---

## Anti-patterns

| Pattern | Severity |
|---------|----------|
| Chrome **`pass`** / **`probe_executed`** on login landing only (dealer/retail login form) | **Violation** |
| **`fe_credentials.supplied`** without **`fe_ui_sessions.authenticated`** then **`probe_executed`** on FE fixture kinds | **Violation** |
| **`session_gates.fe_login_human_gate: completed`** without authenticated smoke (use **`authenticated`** \| **`shell_only_waived`**) | **Violation** |
| Emit discover when Phase **0b** FE gate failed without waiver | **Violation** |
