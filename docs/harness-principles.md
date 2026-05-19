# Corner QA harness principles

**Audience:** Operators and AI agents working in this repository. **Functional/process only**—no people rosters; no secrets (see [docs/project.json](project.json) `content_policy`).

This file is the **canonical doctrine** for **how** we use pipelines, benchmarks, coverage vs E2E tests, and references. It does **not** replace playbook step-by-step text in [`.cursor/pipelines/`](../.cursor/pipelines/)—those stay normative for triggers.

**Related:** [`docs/benchmark-contract.md`](benchmark-contract.md) (`EpicDir` resolution), [`.cursor/rules/pipeline-router.mdc`](../.cursor/rules/pipeline-router.mdc), [`docs/harness-map.json`](harness-map.json).

---

## 1. Purpose

- Align every session on **generation vs benchmark**, **coverage vs manual E2E drafts**, **reference ownership**, and **benchmark cold paths**—without depending on polluted or shortened chat history.
- Separate **session log** ([`qa-handoff.md`](../qa-handoff.md)) from **stable invariants** (this doc).

---

## 2. Generation vs benchmark (two modes)

| Concept | **Generation** (normal pipelines) | **Benchmark** (measurement / improvement) |
|---------|-----------------------------------|----------------------------------------|
| **Trigger** | `EPIC-PREP:`, `COVERAGE:`, `ANALYSE:`, `TEST-DISCOVER:`, `TEST-PRECON:`, `TEST-PREP:`, … **without** both `benchmark_suite=` and `benchmark_attempt=` on the **same line** | Same triggers **with** both **`benchmark_suite=<id>`** and **`benchmark_attempt=<n>`** on the same line |
| **`EpicDir` (durable + temp)** | `epics/<KEY>/` | `.cursor/benchmark/runs/<suite_id>/attempt-<nn>/shadow/<KEY>/` — see [`docs/benchmark-contract.md`](benchmark-contract.md) |
| **Use of `epics/<KEY>/`** | Read/write artefacts there per playbooks | **Do not read** or **write** `epics/<KEY>/` during benchmark evaluation; use **shadow** tree + **MCP** + **human reference** only |
| **CRTQA Tests** | **Assumed not to exist** yet; **must not** drive bundling or structure | Reference artefacts (e.g. curated snapshots) are **human-provided targets** for compare—not inputs to a cold `TEST-PREP:` generation run |

**Rule of thumb:** If the user did not put **both** benchmark tokens on the pipeline line, you are in **generation** mode for path purposes.

---

## 3. CRTQA Tests in generation mode

- In **generation** (`TEST-PREP:` without benchmark tokens on the line), **`TEST-PREP` must not rely** on existing **CRTQA Test** issues for **bundle design** or traceability semantics. Operators create those tests **after** coverage and drafts, not before.
- **v2:** **`TEST-PREP`** **does not** run Jira CRTQA test search in generation — set **`jira_test_search.skipped: true`**, **`existing_tests_considered: []`**. Reference tests (e.g. curated CRTQA snapshots) are **out of pipeline scope** for cold runs; humans link Jira after drafts.

---

## 4. Coverage vs E2E test drafts

| Artefact | Role |
|----------|------|
| **Coverage** (`-coverage.json` / Smart Checklist) | **Full** manual-ideal checklist—what could be verified in principle. **Must not hallucinate:** ground only in available requirements and tool-backed text. |
| **E2E test drafts** (`TEST-PREP` output) | **Fewer** manual tests that cover **topics/sections** of the checklist—not every line—with **maximum execution context** (how to use DB, dxCore, instruments, shells, etc.) and **minimal** proof steps. |

**Not** one Jira test per checklist bullet by default; **not** one giant bundle that exceeds a reasonable manual session.

**Duration:** **Hard cap 30 minutes** per manual test; **typical 5–15 minutes**.

**Bundling default:** roughly **one E2E bundle per top-level `##` section** in the Smart Checklist, unless subsections differ **strongly** in functionality (refine in playbooks later).

**Traceability:** For test prep, treat **coverage** as the **source of truth** for mapping bundles to checks; avoid organizing bundles **only** by requirement-key groupings.

**Parity:** For multi-shell cases (e.g. dxTrade / Web Broker / Adaptive), **one parity bundle** is acceptable when the epic’s core is **calculation / formula** behaviour—not exhaustive cross-surface consistency as the primary goal.

**Undecided expected values:** Use **`[TBD]`** (or playbook equivalents) where output is not yet decided.

**Checklist IDs vs quality:** `reverse_validation.coverage_gaps` can be empty while **topic-level** E2E quality is still wrong—**chk** completeness is necessary, not sufficient. **TEST-PREP v3.1** adds mechanical gates (`test_prep_verify.py`: one Action/Result per `case_outline` row for ladder/rounding bundles, duplicate-action detection, excluded primary ↔ `coverage_gaps[]`, plan class lint)—still not sufficient for human-test gold quality.

**Obligations handoff (EPIC-PREP → COVERAGE):** **EPIC-PREP** emits **`obligations_proposed[]`** (ref schema v4) from per-requirement subprocesses — invariants, ladders, rounding, etc. **COVERAGE** must **row-complete** every **`primary_candidate`** in **`obligations_coverage`** (coverage schema v2) as a **primary** check, keyed deferral, or **`excluded_checks_with_reason`** — not blanket Dimensions `!` lines. Verifiers: [`epic_prep_verify.py`](../automation/tools/epic_prep_verify.py), [`coverage_verify.py`](../automation/tools/coverage_verify.py). **Production** pipelines **must not** ingest CRTQA tests or bench JSON except in **benchmark** mode (both tokens on the trigger).

---

## 5. `ANALYSE:` (v2)

- Runs **after** **`COVERAGE:`** (coverage JSON **required**). **Not** human BA — no hypothesis questions in generation mode.
- **Role:** coverage-grounded **gap auditor** + bounded Confluence resolve (max 8 gaps/run) + **`exploration_suppressed[]`** for discover/precon. Contract: [`docs/analysis-gap-contract.json`](analysis-gap-contract.json). Verifier: [`analysis_verify.py`](../automation/tools/analysis_verify.py).
- **Human `.md`:** **Gaps** + **Actions** only by default; **`known_issues=yes`** on trigger for Jira mining (off by default).
- **Machine contract:** **`-analysis.json` schema v2** is authoritative for downstream; use **`jq`** slices.
- Direction remains **right-to-left** for **gaps** (coverage/ref pointers), not epic-summary invention.

---

## 6. Reference and oracle data (human-owned)

- **Gold / reference / “good” examples** are **human-owned**. Agents may **normalize** or convert them to machine-readable JSON; agents **must not invent** oracle content or pretend a benchmark target exists without operator-provided material.
- **Target layout (future):** consolidate under **`.cursor/benchmark/data/<KEY>/`** with a manifest and **`coverage/`** + **`tests/`** subtrees; retire scattered legacy locations under `coverage-bench` / `test-bench` **when implemented**—schema is a separate change set.
- **Thin `*-gold.json`** under `.cursor/benchmark/data/` is mainly for **compare_runs** thresholds; do not conflate with full Jira snapshots or pipeline inputs.

---

## 7. Benchmark evaluation specifics

- **Inputs:** **Human-curated reference** + **MCP** (Jira/Confluence as needed). **Do not** use `epics/<KEY>/` as a source or sink for benchmark runs.
- **Finalize:** **Report-only**—produce reports / delta queues; **no** mandatory hard gate that blocks publishing a run summary based on pass/fail (operator still reads output).
- **Self-heal loop:** Benchmark outputs should feed **correcting summaries** so agents (or humans) can patch **playbooks** and this doc; human review is **occasional**, not every edit.
- **Variance:** Prefer **~3** attempts when comparing harness changes; full statistical treatment is optional.
- **`/crtqa-benchmark`:** Prepares suite layout, **control hub**, and paste lines; hub lives in the session that ran the command. *(Operator practice may run **all phases of one run index in one session**; command prose may still describe “cold” rows—**align docs** in a later pass.)*

---

## 8. Discovery closure contract (`TEST-DISCOVER:`)

**TEST-DISCOVER** is a **closure engine** over **coverage obligations**, not a Jira or tooling inventory. It runs after **`EPIC-PREP:`** and **`COVERAGE:`** (and may follow optional **`ANALYSE:`** or human coverage polish). The **universe** of work is **primary** `checks[]` and **primary** `coverage_matrix[]` rows in **`-coverage.json`** only—do not add obligations from Jira breadth.

Three lanes (epic-agnostic; content varies per Epic):

| Lane | Question | Durable fields (schema v3) |
|------|----------|----------------------------|
| **Obligations** | What must we be able to prove? (from coverage) | **`obligation_ledger[]`** |
| **Affordances** | How can we observe each proof? (tools, surfaces, probes) | **`verification_affordances[]`**, **`tooling`** |
| **Fixture needs** | What must exist in the environment before observation is meaningful? | **`fixture_needs[]`** (from coverage/ref + setup-depth probes)—**not** CRTQA tickets by default |

**CRTQA index (opt-in):** In **generation** mode (no benchmark tokens on the trigger line), **MUST NOT** populate **`reference_index[]`** / **`precondition_signals`** or **`prerequisite_edges`** unless the operator adds **`crtqa_index=yes`** on the same line as **`TEST-DISCOVER:`**. In **benchmark** mode (both **`benchmark_suite=`** and **`benchmark_attempt=`**), CRTQA Jira indexing **may** run automatically for compare runs. See §2–§3: generation **must not** treat existing CRTQA Tests as structural prerequisites.

**Finished** means every primary obligation has a **disposition** (`affordance_mapped`, `fixture_need_mapped`, `prerequisite_mapped` when CRTQA index on, `tooling_blocked`, or `scope_gap`), and **`discover_verify.py`** passes for the target **`discovery_status`**. In generation, **`discovery_status: complete`** additionally requires **setup depth** honesty (fixture needs not stuck at shallow depth without **`setup_depth_gaps`**)—not merely “found a Pre-Condition issue in Jira.” When **`-ref.json`** marks **Adaptive** **`affected`**, **`complete`** also requires bounded **Chrome** smoke on CTQA Adaptive (**shared principal** from Confluence—no **`adaptive_creds`** token). Configuration fixture kinds use kind-specific probes in [`docs/discover-fixture-probes.json`](discover-fixture-probes.json), not **`console_guide`** alone. **`discovery_status: incomplete`** is valid when gaps are explicit (e.g. Adaptive not probed, setup depth insufficient).

**Self-heal** = iterate the closure loop until the **verifier** passes or **no-progress** / iteration cap → emit with honest gaps. **Not** unbounded Jira search.

**Outputs:** **`-discover.json`** (schema v3: **`fixture_needs`**, **`obligation_ledger`**, **`obligation_closure`** including **`setup_depth_gaps`**, optional **`reference_index`** when CRTQA index on). Playbook: [`.cursor/pipelines/test-discover.md`](../.cursor/pipelines/test-discover.md). Verifier: [`automation/tools/discover_verify.py`](../automation/tools/discover_verify.py).

**Phase 0 hard stop:** Agents run **`crtqa_env_probe.py --coverage`** (both machine gates; labels **`required_for_epic`**), then MCP **`list_tables`** when postgres is required, then **`Get-CrtqaConsoleStatus.ps1`** when console is required, then **Phase 0b/0c** FE gates ([`docs/fe-ui-probe-contract.json`](fe-ui-probe-contract.json)): missing **`dxtrade5_creds`** / **`webbroker_creds`** when Chrome UI is required → **STOP** unless operator re-runs with **`fe_exploration_waived=yes`** after ack. **`fe_credentials.supplied`** (token on trigger) **≠** **`fe_ui_sessions.authenticated`** (post-login smoke). With creds, Chrome MCP must pass post-login smoke before Step **E** may claim **`probe_executed`** on dxTrade5/WebBroker fixture kinds. Recommended operator prep: tunnel tab → **`/crtqa-console start`** → **`/crtqa-env`**. **`TEST-DISCOVER: <KEY> proceed`** re-runs Phase 0 fresh. **`discovery_status: incomplete`** applies only **after** Phase 0 passed.

**Not in scope for discover:** authoring full ordered precondition recipes or **`test_skeleton[]`** bundling—that is **TEST-PRECON** (`-precon.json` / `-precon.md`). Discover does not replace **coverage** as traceability SoT.

---

## 9. Precondition authoring and chain (`TEST-PRECON:`)

**Exploration map (deepening):** **DISCOVER** (what must be satisfiable) → **PRECON** (how to set up once) → **PREP** (how to verify each bundle). Each layer **must produce strictly deeper evidence** than the previous ([`docs/exploration-depth-ladder.json`](exploration-depth-ladder.json)): `smoke` → `discover_probe` → `precon_drill` → `prep_verify_view`. **Authenticated ≠ explored.**

**Recommended chain:** `EPIC-PREP` → `COVERAGE` → optional `ANALYSE` → optional `TEST-DISCOVER` → optional **`TEST-PRECON`** → `TEST-PREP` → optional **`CLOSE`**.

**`CLOSE:`** — backward documentation integrity ladder + archive. Post-close: four human `.md` at `{EpicDir}` root; all JSON under `{EpicDir}context/` ([`docs/close-contract.json`](close-contract.json)). **No** MCP. Does not re-run **ANALYSE**. Rerunning upstream pipelines on a closed epic breaks paths unless JSON is moved back from `context/`.

- **`TEST-PRECON:` (v5)** — **Phase 0c** = **`smoke` only**. **Phase 2b** authors **`test_skeleton[].case_outline[]`**, **`session_placeholders`**, **`command_patterns`**. **Phase 4R/4D/4C** reach **`precon_drill`**. Schema v5: [`precon-ref.json`](../epics/templates/precon-ref.json). Verifier: [`precon_verify.py`](../automation/tools/precon_verify.py).
- **`TEST-PREP`** **SHOULD** load **`-precon.json`** (thin precon cite; **`case_outline`** merged in **8a½**; adopt **`test_skeleton[]`** in **8a**).

---

## 10. Verification outlines (`TEST-PREP:` v3)

**Default output:** **CRTQA-shaped executable outlines** ([`docs/test-prep-draft-profiles.json`](test-prep-draft-profiles.json) **`crtqa_outline`**). Legacy: **`draft_profile=teaching`**. **TBD policy:** [`docs/test-prep-tbd-contract.json`](test-prep-tbd-contract.json) — session placeholders and `[oracle:TBD]` only; full **case_outline** expansion (no whole-scenario deferrals).

**Exploration depth:** **DISCOVER** → **PRECON** → **PREP** per [`exploration-depth-ladder.json`](exploration-depth-ladder.json). **8a¾** = **`prep_verify_view`**. **No live `execution trade`** during PREP — literary ladder **templates** with placeholders are **required** for **`stateful_ladder`**.

**Greenfield:** no live **CRTQA Jira** fetch; no **`[REQUIRES: CRTQA-*]`** or CRTQA keys in durable drafts. **`shape_ref=benchmark`** is allowed **only** when **both** **`benchmark_suite=`** and **`benchmark_attempt=`** are on the **same line** as **`TEST-PREP:`** / **`TEST-PRECON:`** — read local bench data for titles/structure only; **never** in production generation triggers.

**Obligation gate:** If **`-coverage.json`** **`obligations_coverage`** shows uncovered **`primary_candidate`** rows, **`TEST-PREP:`** must use **`map_only=yes`** or **STOP** with operator message — do not invent checks to fill gaps.

**Verification ladder:** **8a½** plan + **`case_outline[]`** → **`--mode plan`** → **8a¾** → **`--mode explore`** → **8b** (per bundle or per check) → **8c** merge → **`--mode draft` / `merge` / `tests`**. **Yogi tags only in `draft.results[]`**.

**Phase 0 FE:** [`docs/fe-ui-probe-contract.json`](fe-ui-probe-contract.json); cred tokens on trigger.

Playbook: [`.cursor/pipelines/test-prep.md`](../.cursor/pipelines/test-prep.md). Verifier: [`automation/docs/test-prep-verify.md`](../automation/docs/test-prep-verify.md).

---

## 11. `qa-handoff.md` vs this document

| File | Purpose |
|------|---------|
| [`qa-handoff.md`](../qa-handoff.md) | **Session log**—current focus, blockers, next steps, what changed **this** week |
| **This file** | **Stable harness doctrine**—read when working on pipelines, benchmarks, or epic deliverable shape |

Do **not** copy full sections of this file into `qa-handoff.md` (drift risk). Link or point to **§ sections** here instead.

---

## 12. JSON inspection (jq)

Large epic and harness artefacts (`*-coverage.json`, `*-discover.json`, etc.) must not be loaded wholesale into agent context for **inspection**.

- **Project first:** agents run **`jq`** filters (see [automation/docs/jq.md](../automation/docs/jq.md)) and summarize stdout; default threshold **~60 lines** or any subset/array filter need.
- **All epic pipelines** (including **TEST-PRECON** and **TEST-PREP**) follow the same inspect norm; playbook load steps **MUST NOT** contradict **MUST** in [`.cursor/rules/jq-json.mdc`](../.cursor/rules/jq-json.mdc).
- **Edit separately:** writing or emitting durable JSON still uses Read/write on the file; jq is optional for spot-checks.
- **Verifiers stay authoritative:** `discover_verify.py`, `benchmark_verify.py`, `crtqa_env_probe.py`, and other pipeline gates are not replaced by jq.
- **Install:** system **PATH** per machine (`winget install --id jqlang.jq -e` on Windows) — not vendored in repo, not MCP.

Rule detail: [`.cursor/rules/jq-json.mdc`](../.cursor/rules/jq-json.mdc).

---

## 13. Agent output contract

- **BLUF:** Answer / decision first, then support.
- **Paths:** Cap **arbitrary repo path lists** to **~three** unless the user asked for an audit or inventory.
- **Two layers:** Default reply = BLUF + structured facts (complete, not fluffy). Deeper quotes, long file dumps, or exhaustive lists go **after** or **on request**—not a vague summary that drops checks.
- **Skimmable:** Aim for a **~1 minute** read for the default layer on typical replies (per operator preference).

---

## 14. Session context in Cursor (realistic model)

There is **no separate IDE “cache”** that injects a first-prompt summary on every later turn. The model sees **rules**, **user messages**, **tool results**, and **chat history** (lossy when long).

**Practical approach for this repo:**

1. **Always-on** rules stay **short** and **point here** for doctrine.
2. On the **first substantive** pipeline/benchmark/harness task in a session, **read this file** (or the `harness-map` package that loads it).
3. **Later turns** use **rules + prior chat**; re-open this file when behaviour might have changed or the task is **new**.

**Never** treat a **one-line chat “summary”** from an earlier assistant message as authoritative when it conflicts with **this file** or playbooks.

---

## 14. Related paths (minimal)

| Role | Path |
|------|------|
| Router / triggers | [`.cursor/rules/pipeline-router.mdc`](../.cursor/rules/pipeline-router.mdc) |
| Benchmark root | [`.cursor/benchmark/README.md`](../.cursor/benchmark/README.md) |
| Command | [`.cursor/commands/crtqa-benchmark.md`](../.cursor/commands/crtqa-benchmark.md) |
| Entry map | [`docs/harness-map.json`](harness-map.json) |
| Playbooks | [`.cursor/pipelines/`](../.cursor/pipelines/) |
| TEST-DISCOVER verifier | [`automation/tools/discover_verify.py`](../automation/tools/discover_verify.py) |
| TEST-PRECON verifier | [`automation/tools/precon_verify.py`](../automation/tools/precon_verify.py) |
| jq filters / install | [automation/docs/jq.md](../automation/docs/jq.md) |

---

*Schema: living document; update in the same change set when pipeline or benchmark **behaviour** changes per [`.cursor/rules/harness-maintenance.mdc`](../.cursor/rules/harness-maintenance.mdc).*
