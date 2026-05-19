# Session handoff: harness, benchmark vs generation, tests shape, communication (2026-05-15)

> **Retired (2026-05-19):** Harness **benchmark** shadow runs removed. Use **`/crtqa-calibrate`**, [`.cursor/calibrate/README.md`](../.cursor/calibrate/README.md), [docs/calibrate-contract.json](../docs/calibrate-contract.json). Content below is historical.

**Purpose:** Exhaustive context from one Cursor session—**pre-implementation only**. No harness/pipeline edits were made in this chat; this file is the thinking artifact for a later implementation pass.

**Audience:** Future agents and the operator; assume they did not read the polluted start of the original thread.

---

## 1. BLUF

1. **Production pipelines** (`EPIC-PREP`, `COVERAGE`, `ANALYSE`, `TEST-PREP`, …) run on **an Epic key + MCP** only. In **generation mode**, **CRTQA Test issues do not exist yet** and **`TEST-PREP` must never rely on them** for structure or bundling.

2. **Benchmark / reference data** (human-curated snapshots under benchmark trees, future consolidated oracle layout) exists to **measure and improve** harness behaviour **after** cold runs—not as input during normal `TEST-PREP:` execution.

3. **Coverage** = full manual-ideal checklist (Smart Checklist). **E2E test drafts** = **fewer** manual tests that cover **topics/sections** of that checklist—not every bullet—with **maximum execution context** (DB, dxCore, instruments, etc.) and **minimal** proof steps. **Not** one Jira test per checklist line; **not** one giant bundle.

4. **Hard cap: 30 minutes** per manual test; **typical 5–15 minutes**. Bundling default: roughly **one E2E bundle per top-level `##` section** unless subsections differ **strongly** in functionality (refine later).

5. **Explicit conceptual fork:** **Benchmark execution** (shadow, compare, self-heal reports) vs **test preparation / generation** (normal `epics/<KEY>/` artefacts). Implementation details TBD; the **distinction** is project doctrine.

6. **Benchmark cold policy:** During benchmark evaluation, use **human reference + MCP only**; **do not read or write** `epics/<KEY>/` (shadow writes live under `.cursor/benchmark/runs/.../shadow/`).

7. **Reference / gold** is **human-owned**; agents may **normalize** to machine-readable formats; agents **must not invent** oracle or “good result” content.

8. **Finalize benchmark runs:** **Report-only**—always produce report / `pipeline-delta-queue` style output; **no** hard gate blocking completion on pass/fail.

9. **`qa-handoff.md`** = **session/work log**. **General harness invariants** belong in a **separate** doc (to be added later)—so the operator does not re-explain the same doctrine every session.

10. **Agent communication:** BLUF first, structured bullets, cap arbitrary file-path dumps (~3), progressive disclosure; full substance without filler.

11. **Open implementation work:** invariant doc + `AGENTS` link; router/playbook language for the fork; optional Jira Test search wording; align `/crtqa-benchmark` with **one session per run** vs per-row cold chats; consolidate oracle tree under `.cursor/benchmark/data/<EPIC>/`; richer test compare; output contract rule/skill.

---

## 2. Problem statement (historical / thread pollution)

Early assistant turns in the source chat conflated:

- **Thin `benchmark/data/*-gold.json`** files (substring/oracle gates for `compare_runs.py`) with  
- **Full Jira Test snapshots** (e.g. under `test-bench/data/CRT-639/`) and  
- **Runtime pipeline inputs**.

That led to wrong guidance such as “pipeline should read test-bench” or “gold must be fed before `TEST-PREP`.”

**Correct model (operator):**

| Mode | Inputs | CRTQA Tests |
|------|--------|-------------|
| **Generation** (normal `TEST-PREP:`) | Epic, Jira/Confluence via MCP, prior artefacts in `epics/<KEY>/` as produced by earlier phases | **Assumed not to exist**; must not drive bundling |
| **Benchmark** | Same pipeline triggers + **optional** `benchmark_suite` / `benchmark_attempt`; evaluation compares outputs to **human reference**; **no** `epics/`reads/writes | Reference is **corrected human output**, not a prereq for generation |

Readers of **only** the messy opening of the thread should use **this document** and operator corrections—not the first replies—as SoT.

---

## 3. CRT-639 exemplar (illustration only)

This epic was used as a **worked example** of shape mismatch—not as a permanent spec for all epics.

**Reference set (human, full Jira bodies):** `.cursor/benchmark/test-bench/data/CRT-639/` — `index.json` plus snapshots CRTQA-10177, -10182, -10183, -10184 (and conceptually CRTQA-10176 as precondition class, not always in index).

**Abstract patterns in those tests:**

- **10177:** Multi-scenario **trade ladder**; **per-step** avg / realized PL; opening-side emphasis; zero-cross with remainder, flat, partial; **sell-first mirror**; verify via **`position_metrics_from_publisher`** (concept—not requiring pasted commands in pipeline output).
- **10182:** **Open PL** and **% PL Gross** with explicit formulas; **six** long/short × sign-style cases; recalc from publisher / portfolio metrics.
- **10183:** Dedicated **rounding** matrix—avg (**7 dp**), Open PL, Realized PL (**floor 2 dp** USD); ties to requirement/DXINV refs in prose.
- **10184:** **Instrument/account group** move with different mark-up → **weighted average unchanged** on existing position.
- **Chain:** Preconditions reference **10176** + prior tests where applicable.

**What cold `CRT-639-tests.json` + coverage tended toward:** Few **merged** bundles (tb-001 lumped prep + ladder + FIFO stress), **chk-ID traceability** satisfied while **scenario depth** (separate rounding test, group-change test, case grids) was thin or absent; optional note admitted **stub** subprocess behaviour.

**Coverage markdown:** Often had **account group** on **chk-001** detail lines but **no** primary scenario for **10184-style immutability**; **Dimensions** chk could defer multi-account while user cares about **post-trade group change**—different concern.

**Lesson for harness:** Satisfying **checklist IDs** ≠ reproducing **acceptable manual-test anatomy**; playbooks must encode **topic-level E2E** + **time budget**, not only matrix traceability.

---

## 4. Decisions table

| Topic | Decision | Notes / source |
|-------|----------|----------------|
| Generation vs CRTQA Tests | **`TEST-PREP` in generation mode must never rely on CRTQA Tests.** They **do not exist** at generation time. | User correction |
| Fork | **Benchmark execution** and **test preparation (generation)** are separate worlds; implementation later; **concept locked** | User |
| Coverage role | **Full** manual-ideal checklist | User |
| E2E drafts role | **Fewer** tests; cover **topics/sections** of coverage **not** every line; rich **context** for executing checklist (tools, consoles, DB…); **minimal** verification steps | User |
| Mega-bundle | **Incorrect** for manual time budget | User |
| Duration | **Hard cap 30 min** per test; **typical 5–15 min** | User |
| Section → bundle | Default **one E2E per top-level `##`**, split if **subsections very different** functionally; **detail later** | User |
| `ANALYSE` | May run **any time** after coverage; direction **right-to-left** (coverage → map → requirements → Yogi → epic) to find gaps; compensates for lack of human abstract thinking | User |
| `COVERAGE` | **Never** hallucinate or guess; **only** grounded in available requirements | User |
| Scope of doctrine | **General** project context first, not only epic-specific tuning | User |
| Requirement keys in TEST-PREP | **Coverage is SoT**; avoid organizing bundles by requirement-key grouping during test-prep | User |
| Reference ownership | **Human** owns gold/reference; agents may **transform** to agent-readable files; **never invent** reference | User |
| Precondition artefact | Future **test precon** pipeline; **benchmark should evaluate** separation from regression bundles; **10176-class** expectations | User + discussion |
| Pipeline chain (implemented) | **EPIC-PREP** → **COVERAGE** → optional **ANALYSE** → **TEST-DISCOVER** → **TEST-PRECON** → **TEST-PREP** → optional **CLOSE** | Harness 2026-05 |
| TEST-EXEC (retired) | Former env/Playwright materialization pipeline — **removed**; replaced by **`CLOSE:`** (documentation integrity + archive, no MCP) | 2026-05 doc recon |
| Tooling-gather vision (deferred) | Scan env (MCP) for SQL, dxCore, IPF… to feed prep — **not** a pipeline; explore/discover/precon cover setup depth | Historical user idea |
| Benchmark mimics workflow | **Without** relying on artefacts previously produced by the same workflow run in `epics/` | User |
| Benchmark inputs | **Human reference + MCP**; **forbid read AND write** under `epics/<KEY>/` | User **A** |
| Jira Test search (generation) | **(i)** Keep as **optional / best-effort audit**, **not** structural dependency | User **B** |
| Oracle layout (target) | **Single** tree: `.cursor/benchmark/data/<EPIC>/` with **manifest** + `coverage/` + `tests/`; **stop** scattering oracles under legacy `coverage-bench` / `test-bench` data (implementation + delete/migrate **later**) | User |
| Oracle schema | **Discuss later** | User |
| Parity bundles | **One** bundle for dxTrade / Web Broker / Adaptive **parity** acceptable; **formula/calculation** core > cross-surface consistency theatre | User |
| TBD in drafts | **OK** when specific output undecided | User |
| Benchmark finalize | **Report-only** | User (Q17) |
| Variance methodology | **Fresh session** per run; **all phases of one run in same session**; **cannot** swap models (tokens); user runs prompts for that run **in one session** | User |
| `/crtqa-benchmark` | **Prep prompts + run space**; **control hub** in the session that invoked it | User |
| Doc drift | Repo **`crtqa-benchmark`** text implies **one cold chat per row**; **operator practice** = **one session per run index** with all stages—**fix docs later** | User |
| `N` attempts | **~3** acceptable; statistics not a focus | User |
| Self-heal | Benchmark product = **correcting summary** → agent edits playbooks; human **occasionally** reviews (not every change) | User |
| Minor gold substring wording | **Low priority**; don’t burn tokens on tiny wording mismatches | User |
| Extra security invariants | **None** beyond existing repo rules | User |
| **Communication** | BLUF; necessary detail without harmful trimming; scannable in **~1 minute** default layer; progressive disclosure; cap path lists | User + practice research |
| **Readable vs complete** | **Two layers:** default answer = BLUF + structured facts (no harmful trimming); deeper enumeration / long quotes **below** or **on request**—not a vague “summary” that drops checks | Session discussion |
| **Benchmark external data** | Human-curated reference is allowed; benchmark run does **not** assume prior **pipeline** outputs in `epics/` | User |
| **Implementation order (suggestion)** | Teach agents **invariant doc + pipeline doctrine** before expanding **compare_runs** / oracle migration—reduces measuring the wrong signal | Mid-thread suggestion; not formally voted by user |

---

## 5. Harness gaps identified (pre-fix)

- **T0 / entry** (`qa-handoff`, `AGENTS`, rules) do not state the **two-world** model (generation vs benchmark) or **CRTQA-nonexistence** in generation.
- **`test-bench/data/.../index.json` `purpose` field** has read as if snapshots were **inputs for TEST-PREP**—misleading vs operator doctrine.
- **`harness-map.json`:** No **benchmark_operator** (or similar) package pointing to benchmark README, contract, cold-read policy.
- **`compare_runs.py`:** Test phase metrics are **structural** (bundle counts, subprocess flags)—weak vs **human test shape**.
- **`test-bench/scripts/README.md`:** `compare_test_runs.py` **not yet implemented** / stub.
- **Pipeline text** (`test-prep.md` reverse validation): **chk-ID completeness** can read “healthy” while **topic-level E2E** quality fails—needs doctrine + future metrics.

---

## 6. Non-goals of this session

- No edits to playbooks, router, `AGENTS.md`, `HOW-TO`, rules, or benchmark code.
- No migration of oracle files.
- No new skills/rules committed—**context capture only**.

---

## 7. Open items for implementation (checklist)

- [ ] Add **invariant harness doc** (generation vs benchmark, CRTQA rule, coverage vs E2E, reference ownership, cold benchmark policy, `qa-handoff` vs invariants); link from `AGENTS.md` / T0.
- [ ] Update **pipeline-router** + **`TEST-PREP` / `COVERAGE`** language: generation fork; optional Jira Test audit; topic/section bundling + **30 min hard cap** heuristic.
- [ ] Update **`/crtqa-benchmark`** (and related HOW-TO bullets): **one session per run index** vs one-row-per-chat if that remains operator intent; reduce contradiction.
- [ ] Fix **`test-bench` index** purpose text when oracle layout moves.
- [ ] Implement **`.cursor/benchmark/data/<EPIC>/`** layout (`manifest`, `coverage/`, `tests/`); migrate/delete scattered bench data **per later design**.
- [ ] Extend **benchmark compare** for **tests**: human `tests/` subtree vs shadow `-tests.json` (motifs / structure—not console plagiarism).
- [ ] Optional **Cursor rule or skill**: **output contract** (BLUF, max paths, tables vs prose).
- [ ] Future: **test precon** pipeline, **tooling gather** pipeline—sequence per user vision.
- [ ] (Ordering) Prefer **clarifying harness invariants + playbooks** before **heavy benchmark compare / oracle file moves**—so metrics reflect the right doctrine.

---

## 8. Appendix — Turn map (condensed)

1. **Opening:** Mismatch between `CRT-639-tests.json`, gold JSON, and user expectations; `account group` in coverage vs gold; **test-prep** bundling vs CRTQA manuals.
2. **Correction:** Benchmark vs pipeline confusion; **no prereq gold** for cold `TEST-PREP`; reference is for **improvement**.
3. **Deeper CRT-639:** Compare to `test-bench/data/CRT-639` snapshots; patterns vs pipeline; **`chk` traceability insufficient** for good manuals.
4. **Harness audit:** AGENTS, harness-map, rules—**what’s missing** on session start; **two-world** doctrine absent; misleading test-bench index.
5. **Q&A doctrine:** Extended answers (**generation**, coverage vs E2E, **30 min**, ANALYSE, references, future pipelines, benchmark cold **no epics**, oracle consolidation, **qa-handoff** role, retired TEST-EXEC / **CLOSE**, report-only finalize, optional Jira search, **A/B** confirmations).
6. **`/crtqa-benchmark`:** Operator description of control hub + run space.
7. **Communication:** Density vs completeness; BLUF, progressive disclosure, cap references, harness-level **output contract** as future lever.

---

## 9. Related paths (minimal)

| Role | Path |
|------|------|
| Operator start | `AGENTS.md`, `qa-handoff.md`, `HOW-TO.md`, `docs/harness-map.json` |
| Benchmark contract | `docs/benchmark-contract.md`, `.cursor/benchmark/README.md`, `.cursor/commands/crtqa-benchmark.md` |
| Reference example (epic) | `.cursor/benchmark/test-bench/data/CRT-639/` |
| Pipelines | `.cursor/pipelines/test-prep.md`, `.cursor/pipelines/coverage.md` |

---

*End of session handoff document.*
