# Corner QA harness principles

**Audience:** Operators and AI agents working in this repository. **Functional/process only**—no people rosters; no secrets (see [docs/project.json](project.json) `content_policy`).

This file is the **canonical doctrine** for **how** we use pipelines, calibration, coverage vs E2E tests, and references. It does **not** replace playbook step-by-step text in [`.cursor/pipelines/`](../.cursor/pipelines/)—those stay normative for triggers.

**Related:** [`docs/calibrate-contract.json`](calibrate-contract.json), [`.cursor/rules/pipeline-router.mdc`](../.cursor/rules/pipeline-router.mdc), [`docs/harness-map.json`](harness-map.json).

---

## 1. Purpose

- Align every session on **production pipelines** (`epics/<KEY>/`), **operator calibration** (`/epic-calibrate`), **coverage vs manual E2E drafts**, and **reference ownership**—without depending on polluted or shortened chat history.
- Separate **session log** ([`qa-handoff.md`](../qa-handoff.md)) from **stable invariants** (this doc).

---

## 2. Production pipelines (generation)

| Concept | Rule |
|---------|------|
| **Triggers** | `EPIC-PREP:`, `COVERAGE:`, `GROUND:`, `ANALYSE:`, `TEST-DISCOVER:`, `TEST-PREP:`, `CLOSE:` — see [pipeline-router](../.cursor/rules/pipeline-router.mdc). **`TEST-PRECON:`** and **`COVERAGE-REINFORCE:`** legacy only. |
| **Draft+truth (v3)** | Bounded loop **COVERAGE → GROUND → ANALYSE** (max **2** rounds) → **human coverage review** (+ **`scenario_groups[]`**) → **DISCOVER linker** → **TEST-PREP scenario_intent** → CLOSE. No PRECON; no generation UI exploration. Master: [docs/draft-truth-contract.json](draft-truth-contract.json). **`/epic-calibrate`** out-of-band after CLOSE. |
| **`EpicDir`** | Always `epics/<KEY>/` (after **CLOSE:** JSON under `epics/<KEY>/context/`) |
| **EPIC-PREP topology** | `-ref.json` emits **`epic_archetype`** and **`verification_topology`** (surfaces, oracle rules, delivery notes, reuse hints) per [docs/epic-prep-topology-contract.json](epic-prep-topology-contract.json); **COVERAGE** copies archetype, sets **`emit_layout`**, dual markdown spine per [docs/coverage-topology-contract.json](coverage-topology-contract.json); `coverage_verify.py --strict-topology` when ref has topology |
| **EPIC-PREP principal (good draft)** | `-ref.json` also encodes **principal QA decisions**: per-obligation **`downstream_hints`**, **`principal_coverage_threads[]`**, **`verification_focus_proposed`** per [docs/epic-prep-principal-contract.json](epic-prep-principal-contract.json). Target is a **good draft** handoff—not gold parity; manual QA refinement expected; **`strict_principal=yes`** opt-in gates skipping primary obligations harder. Downstream pipelines consume in Round 2 steps 2–8. |
| **COVERAGE principal (Round 2 step 2)** | **COVERAGE** copies **`verification_focus_proposed`** verbatim to **`epic_verification_focus`**, materializes **`principal_coverage_threads[]`** as ordered H2 spine (setup before surfaces on **`shell_first`**), and requires **keyed deferrals** with **`obligation_ids[]`** per [docs/coverage-principal-contract.json](coverage-principal-contract.json); **`coverage_verify.py --strict-principal`** opt-in. |
| **ANALYSE principal (Round 2 step 3)** | **ANALYSE** consumes ref deferral obligations and coverage keyed deferrals: **`deferred_check`** gaps with **`pointers.obligation_id`**, delivery gaps enriched with **`linked_obligation_ids`**, **`exploration_suppressed`** reason **`deferral_obligation_keyed`** per [docs/analysis-principal-contract.json](analysis-principal-contract.json); **`analysis_verify.py --strict-principal`** opt-in; no silent zero gaps when deferrals exist. |
| **TEST-DISCOVER principal (Round 2 step 4)** | **TEST-DISCOVER** consumes ref **`downstream_hints.needs_environment_provision`** into **`fixture_needs[]`** with **`linked_obligation_ids`**, and ANALYSE **`deferral_obligation_keyed`** into honest ledger disposition per [docs/discover-principal-contract.json](discover-principal-contract.json); **`discover_verify.py --strict-principal`** opt-in. |
| **COVERAGE-REINFORCE principal (Round 2 step 5)** | **COVERAGE-REINFORCE** merges discover provision **`fixture_needs`** into pass-2 setup **`linker_trace_lines`** + human **`detail_lines`** (operator-hints catalog) and skip-deepens deferral-keyed checks per [docs/coverage-reinforce-principal-contract.json](coverage-reinforce-principal-contract.json); **`coverage_verify.py --mode reinforce --strict-principal`** opt-in. |
| **TEST-PRECON principal (Round 2 step 6)** | **TEST-PRECON** consumes ref **`downstream_hints`** (personas, provisioning, dual-account contrast), discover **`ref_principal_provision`** fixtures, and reinforce setup **`detail_lines`** into **`session_placeholders`** and **`pc-setup`** cluster per [docs/precon-principal-contract.json](precon-principal-contract.json); **`precon_verify.py --strict-principal`** / **`--mode principal`** opt-in. |
| **TEST-PREP principal (Round 2 step 7)** | **TEST-PREP** adopts PRECON **`tb-setup`** / **`pc-setup`**, pastes **`session_placeholders`**, persona-splits mixed retail/dealer bundles, and skip-deepens deferral-keyed checks per [docs/test-prep-principal-contract.json](test-prep-principal-contract.json); **`test_prep_verify.py --strict-principal`** / **`--mode principal`** opt-in. |
| **CLOSE principal (Round 2 step 8)** | **CLOSE** Phase **E¾** terminal cross-artifact principal lint: provision chain, placeholder parity, deferral alignment, delegated tests-leg checks per [docs/close-principal-contract.json](close-principal-contract.json); **`close_verify.py --mode principal --strict-principal`** opt-in on **`strict_principal=yes`**. |
| **CRTQA Tests** | **Assumed not to exist** yet during **TEST-PREP**; operators create Jira tests **after** drafts |

---

## 3. CRTQA Tests in generation mode

- **`TEST-PREP` must not rely** on existing **CRTQA Test** issues for **bundle design** or traceability semantics. Operators create those tests **after** coverage and drafts, not before.
- **v2:** **`TEST-PREP`** **does not** run Jira CRTQA test search in generation — set **`jira_test_search.skipped: true`**, **`existing_tests_considered: []`**. Reference tests (e.g. curated CRTQA snapshots) are **out of pipeline scope** for cold runs; humans link Jira after drafts.

---

## 4. Coverage vs E2E test drafts

| Artefact | Role |
|----------|------|
| **Coverage** (`dependencies/<KEY>-coverage.json` + root Smart Checklist) | **Full** manual-ideal checklist with **atomic observables** (one obligation → one check for `widget_ui`). **Paste** (`<KEY>-coverage.md` at epic root only): collapsed **`## Prerequisites`**, `###` subsection grouping, short bullets — **no** `## Primary focus` in paste; focus stays in JSON. **Must not hallucinate** or emit tag-level stubs when snippets are OK. Operator hints in **`checks[].detail_lines`** only. Machine trace in JSON only — [docs/coverage-operator-hints.json](coverage-operator-hints.json). |
| **E2E test drafts** (`TEST-PREP` output) | **Fewer** scenario-group tests (`scenario_groups[]` → one bundle each): plain-English **intent** actions, requirement-linked results, formulas when inferable — **not** fake CRTQA executable steps. |

**Not** one Jira test per checklist bullet by default; **not** one giant bundle that exceeds a reasonable manual session.

**Duration:** **Hard cap 30 minutes** per manual test; **typical 5–15 minutes**.

**Bundling default:** roughly **one E2E bundle per top-level `##` section** in the Smart Checklist, unless subsections differ **strongly** in functionality (refine in playbooks later).

**Traceability:** For test prep, treat **coverage** as the **source of truth** for mapping bundles to checks; avoid organizing bundles **only** by requirement-key groupings.

**Parity:** For multi-shell cases (e.g. dxTrade / Web Broker / Adaptive), **one parity bundle** is acceptable when the epic’s core is **calculation / formula** behaviour—not exhaustive cross-surface consistency as the primary goal.

**Undecided expected values:** Use **`[TBD]`** (or playbook equivalents) where output is not yet decided.

**Checklist IDs vs quality:** `reverse_validation.coverage_gaps` can be empty while **topic-level** E2E quality is still wrong—**chk** completeness is necessary, not sufficient. **TEST-PREP v3.1** adds mechanical gates (`test_prep_verify.py`: one Action/Result per `case_outline` row for ladder/rounding bundles, duplicate-action detection, excluded primary ↔ `coverage_gaps[]`, plan class lint)—still not sufficient for human-test gold quality.

**Obligations handoff (EPIC-PREP → COVERAGE):** **EPIC-PREP** emits field-level **`obligations_proposed[]`** (`assertion_fragment`, `emit_subsection`) and sets **`requirements[].observable_yield`** when snippets name ≥2 UI parameters. **COVERAGE** maps **1 primary obligation → 1 atomic check**; verifiers reject tag-level stubs (**even when snippets failed**), bare machine `! reason:` enums, lone stub subsections, availability checks outside **`## Prerequisites`** on `widget_ui`, and **`## Rounding and display policy`** on `shell_first`. Taxonomy (sections) comes from Jira/topology; decomposition (field checks) from snippets — a structured skeleton without field yield is **invalid**.

**Derived truth beats declared numbers:** breadth thresholds are recomputed from **`snippet_text`** on every run. **`parameter_inventory[]`** may add to the derived inventory but never narrow it, a snippet under 60% of its attested source fails, and **`requirement_passes[]`** must record one entry per resolved requirement so the mandatory per-requirement fan-out is checkable. Oracle detail lines name their parameter and differ between variations of it; availability placement is exempted per check, not per ref. When a gate reports a shortfall, the fix is a fuller transcription — never a lower threshold. Rationale: [automation/CI/decisions.md](../automation/CI/decisions.md) D18–D19. Layout: [docs/epic-artifact-layout.json](epic-artifact-layout.json). Emit: [coverage_md_sync.py](../automation/tools/coverage_md_sync.py). Contract: [docs/coverage-obligation-contract.json](coverage-obligation-contract.json).

---

## 5. `ANALYSE:` (v2)

- Runs **after** **`COVERAGE:`** (coverage JSON **required**). **Not** human BA — no hypothesis questions in generation mode.
- **Role:** coverage-grounded **gap auditor** + bounded Confluence resolve (max 8 gaps/run) + **`exploration_suppressed[]`** for discover/precon. Contracts: [`docs/analysis-gap-contract.json`](analysis-gap-contract.json), topology [`docs/analysis-topology-contract.json`](analysis-topology-contract.json) (`delivery_known_fail`, `delivery_excluded`, `surface_oracle_unresolved`), principal [`docs/analysis-principal-contract.json`](analysis-principal-contract.json) (keyed deferrals, delivery **`linked_obligation_ids`**). Verifier: [`analysis_verify.py`](../automation/tools/analysis_verify.py) (`--strict-topology` when ref has delivery/oracle topology; **`--strict-principal`** opt-in when ref has deferrals/principal fields).
- **Human `.md`:** **Gaps** + **Actions** only by default; **`known_issues=yes`** on trigger for Jira mining (off by default).
- **Machine contract:** **`-analysis.json` schema v2** is authoritative for downstream; use **`jq`** slices.
- Direction remains **right-to-left** for **gaps** (coverage/ref pointers), not epic-summary invention.

---

## 6. Reference and oracle data (human-owned)

- **Gold** for calibration lives under **`.cursor/calibrate/<KEY>-gold/`** — operator-curated after reviewing production output. Required: **`<KEY>-coverage.json`**, **`<KEY>-tests.json`**. Optional: precon, analysis, thin **`*-gold-meta.json`** (threshold hints only).
- Agents may **normalize** paths or MCP-fetched content into gold JSON; **must not invent** oracle numerics or copy secrets into the repo.
- **Production** artefacts under **`epics/<KEY>/`** are the **subject** of calibration, not a substitute for gold.

---

## 7. Calibration (`/epic-calibrate`)

- **When:** After full pipeline run (+ optional **CLOSE**); operator has **curated** gold (not a prod copy).
- **Inputs:** `epics/<KEY>/` (`context/*.json` when archived) vs `.cursor/calibrate/<KEY>-gold/`.
- **No harness corrections** when: `gold_distinct` passes **and** `compare` reports `NO_ACTIONABLE_DELTA` (`actionable_delta_count: 0`). That is **success**, not a failed run.
- **`GOLD_NOT_DISTINCT`:** Hard stop if required gold JSON is byte- or normalized-identical to prod — prevents endless model-suggested “improvements.”
- **`DELTA_REVIEW`:** Up to **3** prioritized lessons; each **must** cite mechanical `compare.signals[]` (`diff_evidence`); **no** auto-edit of playbooks in the command.
- **Epic debt** (temp/, CLOSE info orphans) — report only; **not** harness lessons without gold≠prod evidence.
- **Verifier:** [`calibrate_verify.py`](../automation/tools/calibrate_verify.py) — `gold_gate`, `gold_distinct`, `prod_gate`, `compare`.
- Playbook: [`.cursor/pipelines/calibrate.md`](../.cursor/pipelines/calibrate.md). Contract: [`docs/calibrate-contract.json`](calibrate-contract.json) schema v2.

---

## 8. Discovery linker contract (`TEST-DISCOVER:`)

**TEST-DISCOVER** is a **deterministic linker** over **frozen coverage** — not a browser exploration phase. It runs **after human coverage review** (`coverage.sources.coverage_frozen_at`). The **universe** is **primary** `checks[]` in **`-coverage.json`** only.

| Lane | Question | Durable fields |
|------|----------|----------------|
| **Obligations** | What must we prove? | **`obligation_ledger[]`** |
| **Affordances** | How observe? (harness refs, GROUND probes, oracle ids) | **`verification_affordances[]`** |
| **Fixture needs** | What env class? (classified only) | **`fixture_needs[]`** at **`classified_only`** |

**Forbidden on DISCOVER:** Phase 0 env gates, Chrome MCP, **`setup_depth: probe_executed`**, **`fe_credentials`**, coverage mutation. Contract: [`docs/discover-linker-contract.json`](discover-linker-contract.json). Verifier: **`discover_verify.py --mode linker`**.

**Finished** means every primary check has ledger **disposition** ≠ `pending` and linker verifier passes. Delivery blockers from ANALYSE/coverage → **`tooling_blocked`**.

**Not in scope:** test drafts, **`scenario_groups[]`**, or live probes — **TEST-PREP** / coverage freeze.

**Outputs:** **`-discover.json`** schema v3 with **`sources.discovery_mode: linker_only`**. Playbook: [`.cursor/pipelines/test-discover.md`](../.cursor/pipelines/test-discover.md).

---

## 9. Production chain and helper (`draft_truth_v3`)

**Recommended chain:** `EPIC-PREP` → `COVERAGE` → **`GROUND`** → `ANALYSE` → *(optional `COVERAGE fix_breadth=yes`, max **2** rounds)* → **human coverage review** (edit **`scenario_groups[]`**, set **`coverage_frozen_at`**) → `TEST-DISCOVER` (**linker only**) → `TEST-PREP` (**`scenario_intent`**) → `CLOSE`. Master: [`docs/draft-truth-contract.json`](draft-truth-contract.json).

**`/epic-helper` v4:** one pipeline **per agent turn**; **two** human gates (env, coverage review); scratch `epics/<KEY>/helper/` → `context/helper/` on CLOSE. Contract: [`epic-helper-contract.json`](epic-helper-contract.json).

**`CLOSE:`** — backward documentation integrity ladder + archive. Post-close: **three** human `.md` at `{EpicDir}` root (coverage, analysis, tests); all JSON under `{EpicDir}context/` ([`docs/close-contract.json`](close-contract.json)). **No** `-precon.json` required in v3. Optional **`strict_topology=yes`** / **`strict_principal=yes`** for legacy cross-artifact lint. **No** MCP. Does not re-run **ANALYSE**.

**`TEST-PRECON:` (legacy):** retained for calibrate/benchmark fixtures only — **not** in production chain. Playbook marked LEGACY.

**Console gate:** [`crtqa_console_probe.py`](automation/tools/crtqa_console_probe.py) — epic-helper cold start and GROUND; recovery **`/crtqa-console start`**. Not a blocking gate for TEST-PREP generation.

**Corner Epic QA CI (dxCity):** Unattended **subset** triggered by **`Agent: Coverage`** on **CRTQA** — **EPIC-PREP → COVERAGE → console gate → GROUND → ANALYSE** only; **no** human coverage review, **no** DISCOVER/PREP/CLOSE. Agents use inline Atlassian MCP + project rules via [`run_pipeline_agent.py`](../automation/tools/teamcity/run_pipeline_agent.py) and dxAgent bootstrap ([`automation/CI/README.md`](../automation/CI/README.md)). Deliverables via TeamCity artifacts + Jira comment. Playbook semantics unchanged; CI is not a substitute for `/epic-helper` or human Smart Checklist review.

---

## 10. Scenario intent drafts (`TEST-PREP:` v3)

**Default output:** **`scenario_intent`** profile ([`docs/test-prep-scenario-intent-contract.json`](test-prep-scenario-intent-contract.json)). One **`test_bundles[]`** per **`scenario_groups[]`** on frozen coverage. **Actions:** what must be achieved (plain English). **Results:** requirement keys + observable claims; formulas in results/peculiarities with **`formula_provenance`** (`agent_inferred` | `ground_verified`). **Deferrals:** **`excluded_checks_with_reason`** only — no fake action rows.

**Legacy:** **`draft_profile=crtqa_outline`** or **`teaching`** for calibrate/benchmark only.

**No generation exploration:** no Phase 0 env gates, no Chrome MCP, no **`prep_verify_view`** in TEST-PREP. UI detail is operator refinement or future UI-GROUND.

**Greenfield:** no live **CRTQA Jira** fetch; no **`[REQUIRES: CRTQA-*]`** in durable drafts.

**Obligation gate:** uncovered **`primary_candidate`** rows → **`map_only=yes`** or **STOP**.

**Verifier:** **`test_prep_verify.py --mode scenario_intent`**. Contract: [`docs/scenario-groups-contract.json`](scenario-groups-contract.json).

Playbook: [`.cursor/pipelines/test-prep.md`](../.cursor/pipelines/test-prep.md). Verifier doc: [`automation/docs/test-prep-verify.md`](../automation/docs/test-prep-verify.md).

---

## 11. `qa-handoff.md` vs this document

| File | Purpose |
|------|---------|
| [`qa-handoff.md`](../qa-handoff.md) | **Session log**—current focus, blockers, next steps, what changed **this** week |
| **This file** | **Stable harness doctrine**—read when working on pipelines, calibrate, or epic deliverable shape |

Do **not** copy full sections of this file into `qa-handoff.md` (drift risk). Link or point to **§ sections** here instead.

---

## 12. JSON inspection (jq)

Large epic and harness artefacts (`*-coverage.json`, `*-discover.json`, etc.) must not be loaded wholesale into agent context for **inspection**.

- **Project first:** agents run **`jq`** filters (see [automation/docs/jq.md](../automation/docs/jq.md)) and summarize stdout; default threshold **~60 lines** or any subset/array filter need.
- **All epic pipelines** (including **TEST-PRECON** and **TEST-PREP**) follow the same inspect norm; playbook load steps **MUST NOT** contradict **MUST** in [`.cursor/rules/jq-json.mdc`](../.cursor/rules/jq-json.mdc).
- **Edit separately:** writing or emitting durable JSON still uses Read/write on the file; jq is optional for spot-checks.
- **Verifiers stay authoritative:** `discover_verify.py`, `calibrate_verify.py`, `crtqa_console_probe.py`, and other pipeline gates are not replaced by jq.
- **Install:** system **PATH** per machine (`winget install --id jqlang.jq -e` on Windows) — not vendored in repo, not MCP.

Rule detail: [`.cursor/rules/jq-json.mdc`](../.cursor/rules/jq-json.mdc).

---

## 13. Agent output contract

- **BLUF:** Answer / decision first, then support.
- **Paths:** Cap **arbitrary repo path lists** to **~three** unless the user asked for an audit or inventory.
- **Two layers:** Default reply = BLUF + structured facts (complete, not fluffy). Deeper quotes, long file dumps, or exhaustive lists go **after** or **on request**—not a vague summary that drops checks.
- **Skimmable:** Aim for a **~1 minute** read for the default layer on typical replies (per operator preference).

---

## 14. Conversation vs Action (operator discipline)

Adapted from [grounding-kit](https://github.com/heatdance/grounding-kit); charter: [`docs/grounding-integration.json`](grounding-integration.json).

| Mode | Examples | Agent duty |
|------|----------|------------|
| **Conversation** | Questions, review-only | No epic or harness edits; no `qa-handoff` churn for chat-only turns |
| **Action** | `EPIC-PREP:` … `CLOSE:`, slash commands, harness doc edits, epic artefacts | Playbooks + verifiers; update handoff before session end |

**Pipeline triggers** (`EPIC-PREP:` … `CLOSE:`, `CLEAN:`, slash commands in [`grounding-integration.json`](grounding-integration.json)) are **high confidence for declared scope** — see [`.cursor/rules/intent-corner.mdc`](../.cursor/rules/intent-corner.mdc).

### Action-close (harness or session work)

When an **Action** changes durable harness files or ends a substantive session:

1. Update [`qa-handoff.md`](../qa-handoff.md) — **Resume**, **Next**, **Anchors** (≤15 lines) + dated bullet under Last updated.
2. If paths/keywords changed → [`docs/harness-map.json`](harness-map.json), [`AGENTS.md`](../AGENTS.md), [`README.md`](../README.md) per [harness-maintenance](../.cursor/rules/harness-maintenance.mdc).
3. If epic-helper behavior changed → bump `epicHelper.version` in [`docs/epic-helper-contract.json`](epic-helper-contract.json) + [epic-helper-golden.json](../automation/tools/fixtures/operator-assist/epic-helper-golden.json).

Epic pipeline runs do **not** require a machine `log.research[]` trail.

---

## 15. Session context in Cursor (realistic model)

There is **no separate IDE “cache”** that injects a first-prompt summary on every later turn. The model sees **rules**, **user messages**, **tool results**, and **chat history** (lossy when long). Optional: [`.cursor/docs/inject-corner.json`](../.cursor/docs/inject-corner.json) when hooks are enabled (pass 2).

**Practical approach for this repo:**

1. **Always-on** rules stay **short** and **point here** for doctrine.
2. On the **first substantive** pipeline/calibrate/harness task in a session, **read this file** (or the `harness-map` package that loads it).
3. **Later turns** use **rules + prior chat**; re-open this file when behaviour might have changed or the task is **new**.

**Never** treat a **one-line chat “summary”** from an earlier assistant message as authoritative when it conflicts with **this file** or playbooks.

---

## 16. Related paths (minimal)

| Role | Path |
|------|------|
| Router / triggers | [`.cursor/rules/pipeline-router.mdc`](../.cursor/rules/pipeline-router.mdc) |
| Calibrate | [`.cursor/calibrate/README.md`](../.cursor/calibrate/README.md) |
| Command | [`.cursor/commands/epic-calibrate.md`](../.cursor/commands/epic-calibrate.md) |
| Entry map | [`docs/harness-map.json`](harness-map.json) |
| Playbooks | [`.cursor/pipelines/`](../.cursor/pipelines/) |
| TEST-DISCOVER verifier | [`automation/tools/discover_verify.py`](../automation/tools/discover_verify.py) |
| TEST-PRECON verifier | [`automation/tools/precon_verify.py`](../automation/tools/precon_verify.py) |
| jq filters / install | [automation/docs/jq.md](../automation/docs/jq.md) |
| Grounding charter | [docs/grounding-integration.json](grounding-integration.json) |
| Corner harness verify | [automation/docs/corner-harness-verify.md](../automation/docs/corner-harness-verify.md) |
| Smoke automation | [docs/auto-tests-contract.json](auto-tests-contract.json) · [`auto-tests/`](../auto-tests/) |

---

*Schema: living document; update in the same change set when pipeline or calibrate **behaviour** changes per [`.cursor/rules/harness-maintenance.mdc`](../.cursor/rules/harness-maintenance.mdc).*
