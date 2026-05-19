# Pipeline: test-precon (precondition materialization)

**Trigger**: user message starts with **`TEST-PRECON:`** and includes a Jira **Epic key** (e.g. `TEST-PRECON: CRT-639`). Optional tokens on the **same line**:

- **`proceed`** — after a **Phase 0 hard stop** only. Re-run Phase **0** from scratch; on pass, start a **fresh** run (new **`sources.precon_run_started_at`**, new **`temp/precon-ledger.json`**). **MUST NOT** merge into a prior failed attempt.
- **`skip_cold_gate=yes`** — waive Phase **0** machine gates. **`sources.cold_gate_skip_token_used: true`**; **`validation_log`** **MUST** record **`cold_gate_skipped`**.
- **`dxtrade5_creds=<user>/<password>`** and **`webbroker_creds=<user>/<password>`** — transient only (**MUST NOT** enter durable JSON).
- **`fe_exploration_waived=yes`** — only after Phase **0b** hard stop + operator ack; caps UI at **`shell_only`**; **`sources.fe_exploration_waived: true`**.

**Scope**: **one Epic** per run. **Router**: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc).

**Doctrine**: [docs/harness-principles.md](../../docs/harness-principles.md) §9 — **DISCOVER → PRECON → PREP** must produce **strictly deeper evidence** per [`docs/exploration-depth-ladder.json`](../../docs/exploration-depth-ladder.json). Phase **0c** = **`smoke` only**; Phase **4** = **`precon_drill`** (replay discover + navigated views). PRECON authors **ordered environment setup** and **`test_skeleton[]`** for downstream **TEST-PREP**.

**Jira shape reference (not fetched as SoT):** [CRTQA-10176](https://jira.in.devexperts.com/browse/CRTQA-10176) — action + commands + branches; no harness vocabulary.

**Operator prep (recommended):** tunnel tab → **`/crtqa-console start`** → **`/crtqa-env`** — see [automation/docs/crtqa-env.md](../../automation/docs/crtqa-env.md) and [`.cursor/commands/crtqa-env.md`](../commands/crtqa-env.md).

---

## Epic workspace (`{EpicDir}`)

Resolve **`{EpicDir}`** like [`epic-prep.md`](epic-prep.md).

### Prerequisites (after Phase 0)

| Artefact | Required |
|----------|----------|
| `{EpicDir}<KEY>-coverage.json` | **Yes** — if missing: **STOP**; instruct **`COVERAGE: <KEY>`** |
| `{EpicDir}<KEY>-discover.json` | **SHOULD** — warn + more **`[TBD]`** if missing |
| `{EpicDir}<KEY>-ref.json` | **Recommended** |
| `{EpicDir}<KEY>-analysis.json` | Optional |

If **`-discover.json`** exists and **`test_prep_gates.blocked: true`**: **WARN** in **`validation_log`** after Phase 0 passes — **continue** (env gates are independent).

### Outputs

- **`{EpicDir}<KEY>-precon.json`** — [`epics/templates/precon-ref.json`](../../epics/templates/precon-ref.json) **schema_version 4**.
- **`{EpicDir}<KEY>-precon.md`** — Jira wiki paste body only (no preamble/footer; generated in phase 5).

**Out of scope:** creating/updating Jira issues via API; **mutating** console/DB during PRECON; trade **ladders** in precon steps; CRTQA Pre-Condition search as **authoring** SoT.

---

## Exploration map (normative)

| Layer | Answers | Human paste |
|-------|---------|-------------|
| **TEST-DISCOVER** | What areas must be satisfiable? | None |
| **TEST-PRECON** | How to set up the environment once? | **`-precon.md`** |
| **TEST-PREP** | How to run each test bundle? | `-tests.md` (separate playbook) |

PRECON **re-explores deeper than discover** (read-only) — replay Step E probes then open setup views/forms per [`docs/exploration-depth-ladder.json`](../../docs/exploration-depth-ladder.json). **MUST NOT** copy discover **`fixture_needs[].notes`** verbatim into **`body`** or **`-precon.md`**. Sanitized findings go to **`exploration_grounding`** / **`exploration_log[]`** (JSON only) with **`depth_level`**, **`view_id`**, **`discover_fixture_id`**.

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
3. Run:

```powershell
python automation/tools/crtqa_env_probe.py --coverage {EpicDir}<KEY>-coverage.json
```

Optional scratch: **`{EpicDir}temp/precon-cold-gate.json`** (probe JSON) — **delete** before finish.

4. If any gate **`status: fail`** and **`required_for_epic: true`** → **STOP**. Chat: BLUF + copy each failed gate’s **`recovery`** as **`operator_recovery`** (slash-first **`actions[]`**). **No** **`-precon.json`**.
5. **Postgres depth** — when probe **`tooling_intent.postgres_ctqa`** is **`required`**: MCP **`list_tables`** on **`postgres-ctqa`**. Failure → **STOP** (tunnel up but MCP down).
6. **Console depth** — when **`crtqa_dx_console`** is **`required`**: **`Get-CrtqaConsoleStatus.ps1`** exit **0** (agent runs script).
7. **Chrome readiness** — when **`tooling_intent.chrome_devtools`** is **`required`** and phase 3/4 will use dxTrade5/webbroker/adaptive: confirm **`chrome-devtools`** MCP is configured ([`automation/docs/chrome-devtools-mcp.md`](automation/docs/chrome-devtools-mcp.md)). Configured ≠ logged in.
8. If **`skip_cold_gate=yes`**: set **`sources.cold_gate_skip_token_used: true`**; log **`cold_gate_skipped`**; continue with degraded exploration honesty.

#### Phase 0b — FE credential gate (same contract as discover)

[`docs/fe-ui-probe-contract.json`](../../docs/fe-ui-probe-contract.json).

1. **`required_fe_surfaces`** from coverage **`surfaces`**, phase 3 cluster **`surfaces`**, **`test_skeleton[].surfaces`**, and ref **`client_shell_impact.adaptive`** (adaptive: no cred token).
2. For **dxtrade5** / **webbroker** in **`required_fe_surfaces`**: missing cred token and no **`fe_exploration_waived=yes`** → **STOP** + **`operator_recovery`** (**`fe_dxtrade5_creds_missing`** / **`fe_webbroker_creds_missing`**). No **`-precon.json`**.
3. **`fe_exploration_waived=yes`** → **`sources.fe_exploration_waived: true`**; skip authenticated smoke for waived surfaces.

#### Phase 0c — Post-login smoke (when creds supplied)

**chrome-devtools** + trigger creds only. Pass criteria: contract **`post_login_smoke`**. On fail → **STOP** (**`fe_ui_authentication_failed`**). Set **`fe_ui_sessions`** on scratch ledger for phase 1.

9. On pass: set **`sources.cold_gate_resolved_at`** (ISO-8601); append **`validation_log`**: **`phase0`**.

**MUST NOT** emit **`-precon.json`** when required Phase 0 gates failed without **`skip_cold_gate=yes`** or FE waiver where applicable.

---

## Algorithm (phases 1–6)

### Phase 1 — Load inputs

1. Set **`{EpicDir}`** = `epics/<KEY>/`, **`epic_key`**.
2. **MUST** project each present artifact with `jq` per [automation/docs/jq.md](../../automation/docs/jq.md) before loading full files into context:
   - **`-coverage.json`**: e.g. `jq '.checks[] | {id, summary, verification_role}'`, `jq '.surfaces'`
   - **`-discover.json`** (when present): e.g. `jq '{discovery_status, test_prep_gates}'`, `jq '.fixture_needs[]'`
   - **`-ref.json`**: e.g. `jq '.client_shell_impact'`
   - **`-analysis.json`** (v2): `jq '.gaps[]'`, `jq '.resolved_gaps[]'`, `jq '.exploration_suppressed[]'` — seed **`case_outline[]`** from **`resolved_gaps`** + high-confidence **`gaps[]`** with `pointers.check_id`; skip checks in **`exploration_suppressed`** with **`blocks_fixture_probe: true`**
   Then **Read** only fields required for phase 2+ authoring (or use further `jq` for subprocess slices). **`-discover.json`** remains **SHOULD** when absent.
3. Set **`sources.*`**, **`sources.precon_run_started_at`** (once per fresh run).
4. Copy **`environment.client_shell_impact`** from ref when loaded (agent notes only — **must not** copy chk/pipeline text into Jira fields).
5. Persist **`fe_credentials`**, **`fe_ui_sessions`**, **`sources.fe_exploration_waived`** from Phase **0b/0c** (and discover when loaded — discover values are informational; PRECON re-probes in phase 4).
6. Initialize **`{EpicDir}temp/precon-ledger.json`**; **`validation_log`**: **`phase1`**.

### Phase 2 — Test skeleton (subprocess recommended)

Plan **`test_skeleton[]`** before precon steps.

Apply bundling from [test-prep.md § Bundling](test-prep.md#bundling-normative):

1. Merge checks when same surface, shared session, shared env setup.
2. **`ladder_in_test: true`** for ladder/engine execution bundles — **not** pure configuration (chk-001-style).
3. Exclude per test-prep: **`explicitly_out_of_scope`**, **`checks[].ambiguity`**, analysis gaps.
4. Assign **`bundle_id`**, **`proposed_title`**, **`covers_check_ids`**, **`covers_sections`**.
5. Default **`precon_cluster_id`**: **`pc-001`**.
6. **`excluded_checks_with_reason[]`** for skipped checks.

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
| **`pattern_ref`** | Optional key into epic **`command_patterns`** (e.g. `ladder_step`) |

**Ephemeral:** **`{EpicDir}temp/precon-outline-<bundle_id>.json`** → merge into ledger **`test_skeleton[]`**.

**Also emit on epic root (once):**

- **`session_placeholders`** — angle-bracket tokens for PREP (no real session ids in repo).
- **`command_patterns`** — reuse blocks; align with [`docs/test-prep-tbd-contract.json`](../../docs/test-prep-tbd-contract.json).

Derive **`min_case_count`** hints from coverage **`calculation_contract`** + [`docs/test-verification-classes.json`](../../docs/test-verification-classes.json) (agent adds rows until count met).

**`validation_log`**: **`phase2b_outline_<bundle_id>`**.

### Phase 3 — Precon clusters (orchestrator)

1. Default **`pc-001`**: title **`{KEY}: Account & system configuration`**.
2. **`surfaces`**: from discover fixture kinds + coverage (console, webbroker; adaptive usually not in precon steps).
3. **`satisfies_fixture_ids`**: config kinds (e.g. **`weighted_avg_fx_spot_account`**); **exclude** **`console_ladder_session`** from driving new steps.
4. **`served_bundle_ids`**: bundles depending on this cluster.
5. Initialize **`exploration_log: []`** on cluster.
6. Split **`pc-002`** only for disjoint fixture kind groups (rare).

**`validation_log`**: **`phase3_clusters`**.

### Phase 4 — Exploration depth ladder (subprocesses per cluster)

**Depth contract:** [`docs/exploration-depth-ladder.json`](../../docs/exploration-depth-ladder.json). **MUST NOT** one-shot explore + author in a single completion.

**If `-discover.json` missing:** **WARN** in **`validation_log`**; cap FE exploration at **`smoke`**; more **`[TBD]`** in steps.

**Budgets (emit on `-precon.json`):** `exploration_budgets` from ladder defaults — **`max_cluster_iterations: 3`**, **`max_fe_nav_cycles_per_surface: 6`**, **`max_console_commands: 12`**.

#### Phase 4R — Replay discover (one subprocess per `fixture_needs[].id` linked to cluster)

**Input:** discover row (`kind`, `notes`, `setup_depth`), [`docs/discover-fixture-probes.json`](../../docs/discover-fixture-probes.json) probe steps.

**Output:** **`{EpicDir}temp/precon-explore-<cluster_id>-<fix_id>.json`** → merge into cluster **`exploration_log[]`**:

- Rows with **`depth_level: discover_probe`**, **`replay_of: discover_probe`**, **`discover_fixture_id`**
- When going deeper in same subprocess, add **`depth_level: precon_drill`**, **`replay_of: precon_deepen`**, **`view_id`** per ladder **`required_views[]`**

**MUST** re-execute Chrome/console actions from discover probes when **`setup_depth: probe_executed`** — not only read discover JSON.

#### Phase 4D — FE deepen (one subprocess per surface in cluster)

Surfaces: **`dxtrade5`**, **`webbroker`**, **`adaptive`** when in cluster **`surfaces`** or skeleton.

**Output:** **`{EpicDir}temp/precon-explore-<cluster_id>-<surface>.json`**

**MUST** append **≥1** **`precon_drill`** row per **`required_views[]`** entry for linked fixture kinds (ladder JSON).

**WebBroker:** open **User Management**; snapshot **create-user** and **assign-account** form field labels — not only top-nav menu strings.

**dxTrade5:** open **Positions** widget; record metric column headers.

**Adaptive:** when ref **`client_shell_impact.adaptive`** is **`affected`** / **`likely_affected`**, CTQA Adaptive URL + portfolio metric labels (shared principal — no cred token).

**Chrome MCP:** navigate → snapshot → record **`view_id`**, **`url_path`**, **`widgets_seen[]`** per row. Distinct **`at`** timestamps per navigation (verifier anti-batch).

- **MUST NOT** set **`outcome: pass`** with action text “post-login smoke” unless **`depth_level: smoke`** (0c only).
- **MUST NOT** set **`outcome: pass`** on FE without **`login_state: authenticated`** unless **`fe_exploration_waived`**.

#### Phase 4C — Console deepen (one subprocess per cluster)

**Input:** discover notes with sanitized **`instrument_id`** / **`account_group_id`** when present.

**Output:** **`{EpicDir}temp/precon-explore-<cluster_id>-console.json`**

**Read-only extended:** targeted **`show`** on linked account/instrument/group when discover captured ids; **`show account_group_hierarchy`**, **`show profiles domains=ExternalExecution`**, **`help`** families.

**Forbidden:** `create`, `update`, `pub_to_realtime`, routing assignment during exploration.

#### Phase 4A — Author steps (one subprocess per cluster)

**Input:** merged **`exploration_log[]`** from 4R/4D/4C.

Emit **`steps[]`** — **`provenance: exploration`** only when matching exploration rows exist with **`precon_drill`** or console evidence.

Discover **`fixture_needs[].notes`** → **`exploration_grounding`** only — **not** **`body`**.

WebBroker: three numbered steps when **`user_management_create_form`** view grounded. Console order unchanged (session → account → subtype → groups → routing → quote).

**`validation_log`**: **`phase4a_<cluster_id>`**.

#### Phase 4V — Verifier loop (orchestrator, max 3 iterations)

```powershell
python automation/tools/precon_verify.py `
  --coverage {EpicDir}<KEY>-coverage.json `
  --precon {EpicDir}temp/precon-ledger.json `
  --discover {EpicDir}<KEY>-discover.json
```

On fail: re-run **4R/4D/4C** for failing cluster/surface/fixture only; append **`validation_log`**: **`closure_iteration_N`**.

**No-progress** (zero new log rows / no depth upgrade): set **`precon_status: incomplete`**, populate **`exploration_gaps[]`**, **do not** set **`precon_verify_passed: true`**.

On pass: proceed to Phase **5**.

### Phase 5 — Emit

1. Merge ledger → **`{EpicDir}<KEY>-precon.json`** (**schema_version 5**); set **`precon_status: complete | incomplete`**.
2. Generate **`{EpicDir}<KEY>-precon.md`** from ledger **only**:
   - Cluster **`title`** as heading.
   - **`h3.`** per surface section (`Configuration through console` / `WebBroker`).
   - Numbered **`1.`** steps from **`body`**; WebBroker user/account/group as **three** steps when grounded; **`{code}`** from **`code_examples[]`**; sub-bullets from **`branch_notes[]`** (platform URL allowed).
   - **`validation_log`** entries **MAY** use structured objects (`step`, `note`, `at`) in JSON only.
   - **No** preamble (paste instructions, JSON paths) or footer (bundle ids, **`ladder_in_test`**).
3. Traceability: **`satisfies_fixture_ids`** include **`fix-003`** (or discover id for webbroker dealer metrics) when WebBroker authenticated smoke ran; align **`satisfies_check_ids`** with **`served_bundle_ids`** or document config-only subset in **`validation_log`**.
4. Verifier:

```powershell
python automation/tools/precon_verify.py `
  --coverage {EpicDir}<KEY>-coverage.json `
  --precon {EpicDir}<KEY>-precon.json `
  --md {EpicDir}<KEY>-precon.md
```

5. Set **`precon_verify_passed`** from exit code.
6. **`validation_log`**: **`phase5_emit`**.

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
| Environment probe | [`automation/tools/crtqa_env_probe.py`](../../automation/tools/crtqa_env_probe.py) |
| Verifier | [`automation/tools/precon_verify.py`](../../automation/tools/precon_verify.py) |
| WebBroker harness | [`docs/webbroker-harness/`](../../docs/webbroker-harness/) |
| FE UI probe contract | [`docs/fe-ui-probe-contract.json`](../../docs/fe-ui-probe-contract.json) |
| Exploration depth ladder | [`docs/exploration-depth-ladder.json`](../../docs/exploration-depth-ladder.json) |
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
