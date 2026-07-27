# Pipeline: test-precon (LEGACY — not in draft_truth_v3 chain)

> **LEGACY:** **TEST-PRECON** is **not** in the production chain after draft_truth_v3. **Do not run from `/epic-helper`.** Use for calibrate/benchmark fixtures only. Production path: **TEST-PREP scenario_intent** after **TEST-DISCOVER linker**. See [docs/draft-truth-contract.json](../../docs/draft-truth-contract.json).

**Trigger**: user message starts with **`TEST-PRECON:`** and includes a Jira **Epic key** (e.g. `TEST-PRECON: CRT-639`). Optional tokens on the **same line**:

- **`proceed`** — after a **Phase 0 hard stop** only. Re-run Phase **0** from scratch; on pass, start a **fresh** run (new **`sources.precon_run_started_at`**, new **`temp/precon-ledger.json`**). **MUST NOT** merge into a prior failed attempt.
- **`skip_cold_gate=yes`** — waive Phase **0** machine gates. **`sources.cold_gate_skip_token_used: true`**; **`validation_log`** **MUST** record **`cold_gate_skipped`**.
- **`dxtrade5_creds=<user>/<password>`** and **`webbroker_creds=<user>/<password>`** — transient only (**MUST NOT** enter durable JSON).
- **`fe_exploration_waived=yes`** — only after Phase **0b** hard stop + operator ack; caps UI at **`shell_only`**; **`sources.fe_exploration_waived: true`**.
- **`strict_principal=yes`** — opt-in Round 2 principal handoff (session placeholders + **`pc-setup`** provisioning cluster). Phase **5** runs **`precon_verify.py --strict-principal`** when ref/discover principal loaded per [`docs/precon-principal-contract.json`](../../docs/precon-principal-contract.json).

**Scope**: **one Epic** per run. **Router**: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc).

**Doctrine**: [docs/harness-principles.md](../../docs/harness-principles.md) §9 — **PRECON** owns live exploration (Phase 0 + Phase 4). Load **`checks[].runtime_probes`** from frozen **`-coverage.json`** (GROUND); optional linker **`-discover.json`** for ledger hints only. See [`docs/precon-draft-truth-contract.json`](../../docs/precon-draft-truth-contract.json).

**Jira shape reference (not fetched as SoT):** [CRTQA-10176](https://jira.in.devexperts.com/browse/CRTQA-10176) — action + commands + branches; no harness vocabulary.

**Operator prep (legacy):** **`/crtqa-console start`** — see [automation/archive/legacy-ctqa-env/README.md](../../archive/legacy-ctqa-env/README.md) for deprecated Postgres/tunnel env probe.

---

## Epic workspace (`{EpicDir}`)

Resolve **`{EpicDir}`** like [`epic-prep.md`](epic-prep.md).

### Prerequisites (after Phase 0)

| Artefact | Required |
|----------|----------|
| `{EpicDir}dependencies/<KEY>-coverage.json` | **Yes** — if missing: **STOP**; instruct **`COVERAGE: <KEY>`** |
| `{EpicDir}dependencies/<KEY>-discover.json` | **Optional** — linker slices when present |
| `{EpicDir}dependencies/<KEY>-ref.json` | **Recommended** |
| `{EpicDir}dependencies/<KEY>-analysis.json` | Optional |

**Frozen coverage:** **`sources.coverage_frozen_at`** should be set (draft+truth path).

### Outputs

- **`{EpicDir}dependencies/<KEY>-precon.json`** — [`epics/templates/precon-ref.json`](../../epics/templates/precon-ref.json) **schema_version 5**.
- **`{EpicDir}dependencies/<KEY>-precon.md`** — Jira wiki paste body only (no preamble/footer; generated in phase 5).

**Out of scope:** creating/updating Jira issues via API; **mutating** console/DB during PRECON; trade **ladders** in precon steps; CRTQA Pre-Condition search as **authoring** SoT.

---

## Exploration map (normative)

| Layer | Answers | Human paste |
|-------|---------|-------------|
| **TEST-DISCOVER (linker)** | Classified affordances (no browser) | None |
| **TEST-PRECON** | How to set up the environment once? | **`-precon.md`** |
| **TEST-PREP** | How to run each test bundle? | `-tests.md` (separate playbook) |

PRECON performs **live read-only exploration** in Phase **4D/4C** per [`docs/exploration-depth-ladder.json`](../../docs/exploration-depth-ladder.json). **MUST NOT** replay discover probes (Phase 4R removed). Linker **`fixture_needs[].notes`** → **`exploration_grounding`** only — not **`body`**.

---

## Normative rules (MUST / MUST NOT)

### Greenfield authoring

- **MUST NOT** treat existing CRTQA **Pre-Condition** issues as structural input.
- **MAY** optional **`jira_search`** audit — log in **`sources.optional_jira_audit`** with **`steps_provenance: not_used_for_authoring`**.

### Jira voice (human fields)

- **`steps[].body`**, **`code_examples[]`**, **`branch_notes[]`**, **`-precon.md`**: imperative **action-result** only.
- **MUST NOT** include: pipeline names, discover/probe/multiplex/parity/fixture/obligation language, bundle ids (`tb-*`), probe account names, long numeric session ids.
- **Account creation:** describe **process** with placeholders; **MUST NOT** reuse operator login or probe session accounts.
- **IDs:** use **`show account_group_hierarchy`** workflow and **`<group_key>`** placeholders — not pasted **`account_group_id=`** digits from a prior session.

### Exploration (read-only) — priority in phase 4

| Surface | Allowed | Forbidden |
|---------|---------|-----------|
| **Console** | `Invoke-CrtqaDxConsole.ps1` read-only: `show console_guide`, `help`, `show account_group_hierarchy`, `show profiles domains=ExternalExecution`; [`docs/dxcore-console-harness.json`](../../docs/dxcore-console-harness.json) | `create`, `update`, routing assignment, `pub_to_realtime`, any mutating setup |
| **Chrome** | Navigate CTQA WebBroker (and dxTrade5 if in cluster **`surfaces`**); snapshot for labels; harness read-only | Secrets in repo; automated full setup |
| **Postgres** | MCP readonly `query`/`schema`/`list_tables` if needed | Writes |

Partial grounding is OK: **`[TBD]`** + “run **`help <command>`** on CTQA”.

### Orchestration — no one-shot

- **MUST NOT** run Phase 0 + skeleton + all cluster steps + emit in one completion.
- **MUST** use **`{EpicDir}temp/precon-ledger.json`**; merge after phases 2–4; emit in phase 5.
- Subprocesses: **2** skeleton → **3** clusters → **4R/4D/4C** exploration per fixture/surface/console → **4A** author per cluster → **4V** verifier loop → **5** emit.

### Path hygiene

- Scratch only **`{EpicDir}temp/`**. **Delete** before run complete.
- **MUST NOT** persist **`/temp/`** or secrets in durable files.

---

## Phase 0 — Cold gates (hard stop)

**MUST** complete Phase 0 before **`temp/precon-ledger.json`** or **`-precon.json`**, unless **`skip_cold_gate=yes`**.

1. Parse trigger tokens; if **`proceed`**: re-run this phase only, then restart from phase 1 with fresh ledger.
2. If **`-coverage.json`** missing → **STOP** (instruct **`COVERAGE:`**).
3. **Legacy env probe (archived):** see [automation/archive/legacy-ctqa-env/](../../automation/archive/legacy-ctqa-env/) for former `crtqa_env_probe.py` + Postgres gates. For console only: **`crtqa_console_probe.py`**.
4. **Console depth** — **`Get-CrtqaConsoleStatus.ps1`** or **`crtqa_console_probe.py`** exit **0**.
5. **Chrome readiness** — when **`tooling_intent.chrome_devtools`** is **`required`** and phase 3/4 will use dxTrade5/webbroker/adaptive: confirm **`chrome-devtools`** MCP is configured ([`automation/docs/chrome-devtools-mcp.md`](../../automation/docs/chrome-devtools-mcp.md)). Configured ≠ logged in.
6. If **`skip_cold_gate=yes`**: set **`sources.cold_gate_skip_token_used: true`**; log **`cold_gate_skipped`**; continue with degraded exploration honesty.

#### Phase 0b — FE credential gate (same contract as discover)

[`docs/fe-ui-probe-contract.json`](../../docs/fe-ui-probe-contract.json).

1. **`required_fe_surfaces`** from coverage **`surfaces`**, phase 3 cluster **`surfaces`**, **`test_skeleton[].surfaces`**, and ref **`client_shell_impact.adaptive`** (adaptive: no cred token).
2. For **dxtrade5** / **webbroker** in **`required_fe_surfaces`**: missing cred token and no **`fe_exploration_waived=yes`** → **STOP** + **`operator_recovery`** (**`fe_dxtrade5_creds_missing`** / **`fe_webbroker_creds_missing`**). No **`-precon.json`**.
3. **`fe_exploration_waived=yes`** → **`sources.fe_exploration_waived: true`**; skip authenticated smoke for waived surfaces.

#### Phase 0c — Post-login smoke (when creds supplied)

**chrome-devtools** + trigger creds only. Pass criteria: contract **`post_login_smoke`**. On fail → **STOP** (**`fe_ui_authentication_failed`**). Set **`fe_ui_sessions`** on scratch ledger for phase 1.

7. On pass: set **`sources.cold_gate_resolved_at`** (ISO-8601); append **`validation_log`**: **`phase0`**.

**MUST NOT** emit **`-precon.json`** when required Phase 0 gates failed without **`skip_cold_gate=yes`** or FE waiver where applicable.

---

## Algorithm (phases 1–6)

### Phase 1 — Load inputs

1. Set **`{EpicDir}`** = `epics/<KEY>/`, **`epic_key`**.
2. **MUST** project each present artifact with `jq` per [automation/docs/jq.md](../../automation/docs/jq.md) before loading full files into context:
   - **`-coverage.json`**: e.g. `jq '.checks[] | {id, summary, verification_role}'`, `jq '.surfaces'`, `jq '{archetype, emit_layout, coverage_pass}'`, `jq '.checks[] | select(.verification_role=="primary") | {id, oracle_rule_id, topology_surface_id, delivery_status}'`; when **`coverage_pass: 2`**, prefer reinforce **`detail_lines`** over pass-1 only
   - **`-discover.json`** (when present): e.g. `jq '{discovery_status, test_prep_gates}'`, `jq '.fixture_needs[]'`, `jq '.verification_affordances[] | {id, linked_check_ids, oracle_binding, topology_surface_id}'`, `jq '.obligation_ledger[] | select(.disposition=="tooling_blocked")'`, `jq '.sources.topology_loaded'`, `jq '.sources.principal_loaded'`, `jq '[.fixture_needs[]? | select(.derivation == "ref_principal_provision")]'`
   - **`-ref.json`**: e.g. `jq '.client_shell_impact'`, `jq '.verification_topology.shell_roles'`, `jq '.verification_topology.pricing_oracle_rules'`, `jq '.verification_topology.jira_scenario_surfaces'`, principal slice:

```bash
jq '{
  provision_obligations: [.obligations_proposed[]? | select(.downstream_hints.needs_environment_provision == true or .kind == "environment_setup") | {id, downstream_hints}],
  personas: [.obligations_proposed[]?.downstream_hints.personas[]?] | unique,
  dual_contrast: [.obligations_proposed[]? | select(.downstream_hints.needs_dual_account_contrast == true) | .id]
}' epics/<KEY>/dependencies/<KEY>-ref.json
```

   - **`-analysis.json`** (v2): `jq '.gaps[]'`, `jq '.resolved_gaps[]'`, `jq '.exploration_suppressed[]'` — seed **`case_outline[]`** from **`resolved_gaps`** + high-confidence **`gaps[]`** with `pointers.check_id`; skip checks in **`exploration_suppressed`** with **`blocks_fixture_probe: true`**; extend deferral for **`delivery_known_fail`** / **`delivery_excluded`** / **`deferral_obligation_keyed`**
   Then **Read** only fields required for phase 2+ authoring (or use further `jq` for subprocess slices). **`-discover.json`** remains **SHOULD** when absent.
3. **Topology load** per [`docs/precon-topology-contract.json`](../../docs/precon-topology-contract.json): set **`sources.topology_loaded: true`** when ref/coverage/discover topology fields consumed; record **`sources.ref_topology_fields[]`**; build **skip-deepen set** from discover **`obligation_ledger`** delivery **`tooling_blocked`**, analysis **`exploration_suppressed`** delivery reasons and **`deferral_obligation_keyed`**, and coverage **`checks[].delivery_status`** **`failed`** / **`excluded`** and deferral **`out_of_epic`** keyed checks — checks in skip-deepen **MUST NOT** receive Phase **4R/4D** probes or new **`case_outline[]`** rows (document in **`excluded_checks_with_reason[]`**).
4. **Principal load** per [`docs/precon-principal-contract.json`](../../docs/precon-principal-contract.json): when ref has **`needs_environment_provision`** / **`environment_setup`** obligations, discover has **`ref_principal_provision`** fixtures, or ref **`downstream_hints.personas`** present — set **`sources.principal_loaded: true`**, record **`sources.ref_principal_fields[]`**, optional **`principal_provenance`**; append **`validation_log`**: **`phase1-principal`**.
5. Set **`sources.*`**, **`sources.precon_run_started_at`** (once per fresh run).
6. Copy **`environment.client_shell_impact`** from ref when loaded (agent notes only — **must not** copy chk/pipeline text into Jira fields).
7. Persist **`fe_credentials`**, **`fe_ui_sessions`**, **`sources.fe_exploration_waived`** from Phase **0b/0c** (and discover when loaded — discover values are informational; PRECON re-probes in phase 4).
8. Initialize **`{EpicDir}temp/precon-ledger.json`**; **`validation_log`**: **`phase1`**, **`phase1-topology`** when topology slices loaded.

### Phase 2 — Test skeleton (subprocess recommended)

Plan **`test_skeleton[]`** before precon steps.

Apply bundling from [test-prep.md § Bundling](test-prep.md#bundling-normative):

1. Merge checks when same surface, shared session, shared env setup.
2. **`ladder_in_test: true`** for ladder/engine execution bundles — **not** pure configuration (chk-001-style).
3. Exclude per test-prep: **`explicitly_out_of_scope`**, **`checks[].ambiguity`**, analysis gaps.
4. Assign **`bundle_id`**, **`proposed_title`**, **`covers_check_ids`**, **`covers_sections`**.
5. Default **`precon_cluster_id`**: **`pc-001`**.
6. **`excluded_checks_with_reason[]`** for skipped checks — include **skip-deepen** delivery-blocked and analysis-deferred primaries (reason **`delivery_blocked`** or **`deferred_ambiguous`**).

**Archetype routing** (from coverage **`archetype`** / **`emit_layout`** + ref **`epic_archetype`** per [`docs/precon-topology-contract.json`](../../docs/precon-topology-contract.json)):

| Archetype / layout | Bundling note |
|--------------------|---------------|
| **`metrics_calculation`** / **`formula_first`** | **`ladder_in_test: true`** for ladder/metric execution bundles; config-only bundles **`false`** |
| **`widget_ui`** / **`shell_first`** | **`ladder_in_test: false`** — observation-only; batch by **`topology_surface_id`** when **`emit_layout: shell_first`** |

**`validation_log`**: **`phase2_skeleton`**.

### Phase 2b — Case outlines (one subprocess per bundle)

**After Phase 2**, before Phase 3. Feeds **TEST-PREP v3** [`docs/test-prep-draft-profiles.json`](../../docs/test-prep-draft-profiles.json).

**Input per subprocess:** coverage slice for **`covers_check_ids`**, skeleton row, optional **`-discover.json`** obligation hints. **Phase 2b** **`case_outline[]`**: seed steps from **coverage `checks[]`** + matching **ref `obligations_proposed[]`** (`obligation_ids` / check text).

**Output:** merge into skeleton row **`case_outline[]`**:

| Field | Required |
|-------|----------|
| **`case_id`** | `c01`, `c02`, … per bundle |
| **`check_id`** | Must be in **`covers_check_ids`** |
| **`title`** | Human-readable scenario (CRTQA-shaped) |
| **`intent`** | What to verify |
| **`pattern_ref`** | Key into epic **`command_patterns`** — **MUST** when discover **`oracle_binding`** or coverage **`oracle_rule_id`** present; map **`oracle_rule`** enum via contract **`oracle_rule_to_pattern_ref`** |

**Archetype `command_patterns` emit (once on epic root):**

| Archetype | Emit |
|-----------|------|
| **`metrics_calculation`** (639) | **`ladder_step`**; optional **`console_config_show`** from ref **`shell_roles.console`** when in scope |
| **`widget_ui`** / **`shell_first`** (594) | Widget observation blocks from discover **`oracle_binding`** + ref **`pricing_oracle_rules`** — e.g. **`watchlist_tier_by_qty`**, **`position_first_tier_quote`**, **`console_show_prices_first_tier`**; **MUST NOT** emit trade **`ladder_step`** as sole pattern |
| Delivery blocked (skip-deepen) | **No** new outline rows; add **`excluded_checks_with_reason`** with **`delivery_blocked`** |

Derive **`min_case_count`** hints from coverage **`calculation_contract`** + [`docs/test-verification-classes.json`](../../docs/test-verification-classes.json) (agent adds rows until count met).

**Ephemeral:** **`{EpicDir}temp/precon-outline-<bundle_id>.json`** → merge into ledger **`test_skeleton[]`**.

**Also emit on epic root (once):**

- **`session_placeholders`** — angle-bracket tokens for PREP (no real session ids in repo). When ref **`needs_dual_account_contrast`**: emit **`group_key_enrg`**, **`group_key_oppt`**. When ref **`downstream_hints.personas[]`** present and cluster surfaces require routing: optional persona tokens (e.g. **`dealer_principal`**, **`retail_account`**). Base tokens: **`console_principal`**, **`instrument_symbol`**, **`account_code`** per [`docs/precon-principal-contract.json`](../../docs/precon-principal-contract.json).
- **`command_patterns`** — reuse blocks per archetype table above; align with [`docs/test-prep-tbd-contract.json`](../../docs/test-prep-tbd-contract.json).

**`validation_log`**: **`phase2b_outline_<bundle_id>`**, **`phase2b_topology_<bundle_id>`** when topology-bound **`pattern_ref`** rows emitted; append **`phase1-principal`** when placeholders extended from ref principal slice.

### Phase 3 — Precon clusters (orchestrator)

1. **Provisioning cluster (principal)** — when discover **`fixture_needs[]`** has **`derivation: ref_principal_provision`**: emit **`pc-setup`** **before** observation **`pc-001`**. Title e.g. **`{KEY}: Account groups and quote publication`**. **`satisfies_fixture_ids`**: provision fixture id (e.g. **`fix-env-001`**). **`satisfies_check_ids`**: fixture **`linked_check_ids`** (e.g. **`chk-s1`**, **`chk-s2`**). Steps: console-first account group hierarchy, FxConfiguration posture, publish streams — imperative Jira voice, **`session_placeholders`** only; **MAY** merge reinforce setup **`detail_lines`** from coverage pass-2 into exploration grounding (not verbatim in **`body`**). Optional skeleton row **`tb-setup`** with **`covers_check_ids`** for setup primaries. Append **`validation_log`**: **`phase3-provision`**.
2. Default **`pc-001`**: title **`{KEY}: Account & system configuration`** (observation / config cluster).
3. **`surfaces`**: from discover fixture kinds + coverage (console, webbroker; adaptive usually not in precon steps).
4. **`satisfies_fixture_ids`**: config kinds (e.g. **`weighted_avg_fx_spot_account`**); **exclude** **`console_ladder_session`** from driving new steps; provision fixtures belong on **`pc-setup`**, not **`pc-001`**.
5. **`served_bundle_ids`**: bundles depending on this cluster; observation bundles depend on **`pc-setup`** completion order in **`-precon.md`** when **`pc-setup`** present.
6. Initialize **`exploration_log: []`** on cluster.
7. Split **`pc-002`** only for disjoint fixture kind groups (rare).

**`validation_log`**: **`phase3_clusters`**, **`phase3-provision`** when **`pc-setup`** emitted.

### Phase 4 — Exploration depth ladder (subprocesses per cluster)

**Depth contract:** [`docs/exploration-depth-ladder.json`](../../docs/exploration-depth-ladder.json). **MUST NOT** one-shot explore + author in a single completion.

**If `-discover.json` missing:** **continue** — use coverage + ref + harness maps only.

**Budgets (emit on `-precon.json`):** `exploration_budgets` from ladder defaults — **`max_cluster_iterations: 3`**, **`max_fe_nav_cycles_per_surface: 6`**, **`max_console_commands: 12`**.

#### Phase 4D — FE deepen (one subprocess per surface in cluster)

Surfaces: **`dxtrade5`**, **`webbroker`**, **`adaptive`** when in cluster **`surfaces`** or skeleton.

When **`emit_layout: shell_first`**, **MUST** batch subprocesses by **`topology_surface_id`** (Watchlist / Position Book / Adaptive / WebBroker per ref **`jira_scenario_surfaces`**) — one **`precon-explore-<cluster_id>-<topology_surface_id>.json`** per batch.

**Skip Phase 4D** for checks in **skip-deepen** set; log **`phase4_skipped_delivery_blocked`** in **`validation_log`**. For deferral-keyed checks: skip Phase **4D**; log **`phase4_skipped_deferral_keyed`**; document in **`excluded_checks_with_reason[]`**.

**Output:** **`{EpicDir}temp/precon-explore-<cluster_id>-<surface>.json`** (or **`-<topology_surface_id>.json`** when shell_first)

**MUST** append **≥1** **`precon_drill`** row per **`required_views[]`** entry for linked fixture kinds (ladder JSON).

**WebBroker:** open **User Management**; snapshot **create-user** and **assign-account** form field labels — not only top-nav menu strings.

**dxTrade5:** open **Positions** widget; record metric column headers.

**Adaptive:** when ref **`client_shell_impact.adaptive`** is **`affected`** / **`likely_affected`**, CTQA Adaptive URL + portfolio metric labels (shared principal — no cred token).

**Chrome MCP:** navigate → snapshot → record **`view_id`**, **`url_path`**, **`widgets_seen[]`** per row. Distinct **`at`** timestamps per navigation (verifier anti-batch).

- **MUST NOT** set **`outcome: pass`** with action text “post-login smoke” unless **`depth_level: smoke`** (0c only).
- **MUST NOT** set **`outcome: pass`** on FE without **`login_state: authenticated`** unless **`fe_exploration_waived`**.

#### Phase 4C — Console deepen (one subprocess per cluster)

**Input:** discover notes with sanitized **`instrument_id`** / **`account_group_id`** when present; ref **`pricing_oracle_rules`** where **`surface`** matches **`console_show_prices`** or **`console_agent_event_*`**.

**Skip Phase 4C** console oracle probes for delivery-blocked checks in **skip-deepen** set.

**Output:** **`{EpicDir}temp/precon-explore-<cluster_id>-console.json`**

**Read-only extended:** targeted **`show`** on linked account/instrument/group when discover captured ids; **`show account_group_hierarchy`**, **`show profiles domains=ExternalExecution`**, **`help`** families.

**Forbidden:** `create`, `update`, `pub_to_realtime`, routing assignment during exploration.

#### Phase 4A — Author steps (one subprocess per cluster)

**Input:** merged **`exploration_log[]`** from 4D/4C.

Emit **`steps[]`** — **`provenance: exploration`** only when matching exploration rows exist with **`precon_drill`** or console evidence.

Discover **`fixture_needs[].notes`** → **`exploration_grounding`** only — **not** **`body`**.

WebBroker: three numbered steps when **`user_management_create_form`** view grounded. Console order unchanged (session → account → subtype → groups → routing → quote).

**`validation_log`**: **`phase4a_<cluster_id>`**.

#### Phase 4V — Verifier loop (orchestrator, max 3 iterations)

```powershell
python automation/tools/precon_verify.py `
  --mode draft_truth `
  --coverage {EpicDir}dependencies/<KEY>-coverage.json `
  --precon {EpicDir}temp/precon-ledger.json `
  --ref {EpicDir}dependencies/<KEY>-ref.json
```

Optional **`--discover`** when linker file present. Optional **`--strict-topology`** / **`--strict-principal`**.

On fail: re-run **4D/4C** for failing cluster/surface only; append **`validation_log`**: **`closure_iteration_N`**.

**No-progress** (zero new log rows / no depth upgrade): set **`precon_status: incomplete`**, populate **`exploration_gaps[]`**, **do not** set **`precon_verify_passed: true`**.

On pass: proceed to Phase **5**.

### Phase 5 — Emit

1. Merge ledger → **`{EpicDir}dependencies/<KEY>-precon.json`** (**schema_version 5**); set **`precon_status: complete | incomplete`**.
2. Generate **`{EpicDir}dependencies/<KEY>-precon.md`** from ledger **only**:
   - Cluster **`title`** as heading.
   - **`h3.`** per surface section (`Configuration through console` / `WebBroker`).
   - Numbered **`1.`** steps from **`body`**; WebBroker user/account/group as **three** steps when grounded; **`{code}`** from **`code_examples[]`**; sub-bullets from **`branch_notes[]`** (platform URL allowed).
   - **`validation_log`** entries **MAY** use structured objects (`step`, `note`, `at`) in JSON only.
   - **No** preamble (paste instructions, JSON paths) or footer (bundle ids, **`ladder_in_test`**).
3. Traceability: **`satisfies_fixture_ids`** include **`fix-003`** (or discover id for webbroker dealer metrics) when WebBroker authenticated smoke ran; align **`satisfies_check_ids`** with **`served_bundle_ids`** or document config-only subset in **`validation_log`**.
4. Verifier:

```powershell
python automation/tools/precon_verify.py `
  --coverage {EpicDir}dependencies/<KEY>-coverage.json `
  --precon {EpicDir}dependencies/<KEY>-precon.json `
  --discover {EpicDir}dependencies/<KEY>-discover.json `
  --ref {EpicDir}dependencies/<KEY>-ref.json `
  --strict-topology `
  --strict-principal `
  --md {EpicDir}dependencies/<KEY>-precon.md
```

When topology not loaded (legacy precon), omit **`--strict-topology`**; when principal not loaded (legacy metrics-only), omit **`--strict-principal`**. Archetype **`command_patterns`** rules still apply from coverage **`archetype`** / **`emit_layout`**. Opt-in trigger **`strict_principal=yes`** enables **`--strict-principal`** per [`docs/precon-principal-contract.json`](../../docs/precon-principal-contract.json).

5. Set **`precon_verify_passed`** from exit code.
6. **`validation_log`**: **`phase5_emit`**.

**Downstream handoff (TEST-PREP 7/8):** emit **`case_outline[]`**, **`command_patterns`**, and oracle rule bindings for **`crtqa_outline`** expansion — **no** CRTQA test implementation in PRECON.

### Phase 6 — Cleanup

**Delete** **`{EpicDir}temp/`** entirely.

---

## Tooling pointers

| Need | Doc |
|------|-----|
| Step archetypes + exploration hints | [`docs/precon-step-archetypes.json`](../../docs/precon-step-archetypes.json) |
| Discover fixtures | [`docs/discover-fixture-probes.json`](../../docs/discover-fixture-probes.json) |
| Console harness | [`docs/dxcore-console-harness.json`](../../docs/dxcore-console-harness.json) |
| CTQA URLs | [`docs/corner-platform-map.json`](../../docs/corner-platform-map.json) |
| Environment probe (archived) | [automation/archive/legacy-ctqa-env/](../../automation/archive/legacy-ctqa-env/) · active console: [`crtqa_console_probe.py`](../../automation/tools/crtqa_console_probe.py) |
| Verifier | [`automation/tools/precon_verify.py`](../../automation/tools/precon_verify.py) |
| WebBroker harness | [`docs/webbroker-harness/`](../../docs/webbroker-harness/) |
| FE UI probe contract | [`docs/fe-ui-probe-contract.json`](../../docs/fe-ui-probe-contract.json) |
| Exploration depth ladder | [`docs/exploration-depth-ladder.json`](../../docs/exploration-depth-ladder.json) |
| Precon topology contract | [`docs/precon-topology-contract.json`](../../docs/precon-topology-contract.json) |
| Precon principal contract | [`docs/precon-principal-contract.json`](../../docs/precon-principal-contract.json) |
| Precon verifier doc | [`automation/docs/precon-verify.md`](../../automation/docs/precon-verify.md) |

---

## Anti-patterns

| Pattern | Severity |
|---------|----------|
| Emit **`-precon.json`** when Phase 0 required gates failed (no **`skip_cold_gate`**) | **Violation** |
| Mutating console/DB during PRECON exploration | **Violation** |
| Probe account names or harness language in **`body`** / **`-precon.md`** | **Violation** |
| Numeric session ids in Jira-facing text | **Violation** |
| Preamble/footer in **`-precon.md`** | **Violation** |
| Skipping phase 4 exploration subprocess; template-only steps | **Violation** |
| One-shot all phases in one completion | **Violation** |
| Ladder trades in **`precon_clusters[].steps[]`** | **Violation** |
| Invented console commands without exploration or harness | **Violation** |
| **`exploration_log` `outcome: pass`** on login form only (no **`login_state: authenticated`**) | **Violation** |
| Post-login WebBroker/dxTrade5 **`body`** when **`fe_ui_sessions.*`** is **`shell_only`** / **`waived`** | **Violation** |
| Phase **0b** FE stop without waiver then emit | **Violation** |
| Login-only **`exploration_log`** pass without **`view_id`** / **`precon_drill`** | **Violation** |
| Identical **`at`** on all cluster exploration rows (batch fabricate) | **Violation** |
| Shallow **`widgets_seen`** (nav denylist only) when drill required | **Violation** |
