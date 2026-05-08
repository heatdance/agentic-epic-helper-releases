# Benchmark runbook

This is for **operators** using Cursor Chat or Agent in this repo—you mainly **paste prompts** (often one step per message) and fill small setup blocks.

**Default path:** **Shadow hub** under `.cursor/benchmark/runs/<suite_id>/` with **`benchmark_suite=`** / **`benchmark_attempt=`** on production pipelines ([docs/benchmark-contract.md](../../docs/benchmark-contract.md), **[`/crtqa-benchmark`](../commands/crtqa-benchmark.md)**).

**Alternative:** Legacy **coverage-bench** **`BENCHMARK:`** / **`BENCHMARK-NEXT:`** queues — **[Appendix: Legacy coverage-bench orchestration](#appendix-legacy-coverage-bench-orchestration)**.

More pointers: [`README.md`](README.md), [`HOW-TO.md`](../../HOW-TO.md).

---

## 1. Shadow hub (default)

Use this when benchmark turns must **not** write under **`epics/<KEY>/`**: durable artifacts live under **`attempt-<nn>/shadow/<KEY>/`**; tooling reads **`attempt-<nn>/_machine/attempts/<KEY>/run-*.json`**.

### 1.1 Read first

1. **[`docs/benchmark-contract.md`](../../docs/benchmark-contract.md)** — **`EpicDir`** resolution (`benchmark_suite` + **`benchmark_attempt`** on the **same line** as **`EPIC-PREP:`** / **`COVERAGE:`** / **`TEST-PREP:`**, etc.).
2. **[`/crtqa-benchmark`](../commands/crtqa-benchmark.md)** — **mandatory questionnaire**, hub layout (**`_manifest.json`**, **`CONTROL_HUB.md`** with **single-line **`TEST-PREP:`** rows** when benchmarking test-prep), **`DONE_HANDOFF_PROMPT.md`** (paste blocks → **agent** writes **`DONE.json`**), **`FINALIZE_PROMPT.md`** (**control hub** verify/compare/**`report.md`**), **`attempt-<nn>/PROMPT-*.md`**, **`_aggregate/`**).

Hard rule (**stochastic benchmarks**): **one cold agent session per orchestrated row** in **`CONTROL_HUB.md`** (EPIC-PREP-only, COVERAGE-only, **`TEST-PREP:`** one line per run — same structure as prep/coverage — or optionally each atomic **`BENCHMARK-TEST-*`** row). Unless you deliberately label **`deterministic replay`** in **`_manifest.json`** **`variance_methodology`** … **Run index** = **`benchmark_attempt`** … ([`docs/benchmark-contract.md`](../../docs/benchmark-contract.md)).

### 1.2 Initialize a suite (`/crtqa-benchmark` — Init)

- Complete **`/crtqa-benchmark`** **Before init (mandatory)** (profile `coverage` \| `test` \| `coverage_test`, **`N`** runs, epics, gold path, **`variance_methodology`**, optional **`suite_id`**).
- Create **`.cursor/benchmark/runs/<suite_id>/`**; copy **[`templates/_manifest.example.json`](templates/_manifest.example.json)** → **`_manifest.json`**; set **`modes`** from profile (profile → **`modes`** table in **[`/crtqa-benchmark`](../commands/crtqa-benchmark.md)**), **`attempts=N`**, **`gold`**, etc.
- Add suite-root **`CONTROL_HUB.md`** (**[`templates/CONTROL_HUB.example.md`](templates/CONTROL_HUB.example.md)**), **`DONE_HANDOFF_PROMPT.md`** (**[`templates/DONE_HANDOFF_PROMPT.example.md`](templates/DONE_HANDOFF_PROMPT.example.md)** — one paste block per run for **agents** to write **`DONE.json`**), and **`FINALIZE_PROMPT.md`** (**[`templates/FINALIZE_PROMPT.example.md`](templates/FINALIZE_PROMPT.example.md)**). Per **`attempt-<nn>/`**, add **`PROMPT-prep.md`**, **`PROMPT-coverage.md`**, **`PROMPT-test.md`** (optional reference — **CONTROL_HUB** carries the canonical **one-line** triggers). Legacy all-in-one: **[`attempt_PROMPT.example.md`](templates/attempt_PROMPT.example.md)** only when methodology allows one chat per run index.

Gold: optional **`.cursor/benchmark/data/<KEY>-gold.json`** — see **[`data/README.md`](data/README.md)**; custom dirs use **`compare_runs.py --gold-root`**.

### 1.3 Run pipelines (follow `CONTROL_HUB.md`)

Execute sessions in **`CONTROL_HUB.md`** execution order. **Paste column = one message line each** — including:

- **`EPIC-PREP:`** / **`COVERAGE:`** (same **`benchmark_suite`** / **`benchmark_attempt`**) — delegates **[`benchmark-epic-prep.md`](coverage-bench/pipeline/benchmark-epic-prep.md)**, **[`benchmark-coverage.md`](coverage-bench/pipeline/benchmark-coverage.md)**.

- **`TEST-PREP:`** — default **single line** **`TEST-PREP: <KEY> benchmark_suite=<suite_id> benchmark_attempt=<n>`** (full playbook under **`{EpicDir}`**; optional **`map_only=yes`** — see **[`benchmark-test-prep.md`](test-bench/pipeline/benchmark-test-prep.md)**). **Optional** multi-row **`BENCHMARK-TEST-*`** expansion for atomic steps.

After each **prep/coverage** row, **`run-*.json`** wrappers may land under **`attempt-<nn>/_machine/attempts/<KEY>/`** with **`phase`** (**`prep`** | **`coverage`**).

**After each full run index** (all phases for **`r`** in that profile): operator pastes the corresponding block from **`DONE_HANDOFF_PROMPT.md`** → **agent** writes **`DONE.json`** (operator does **not** hand-edit **`DONE`**).

### 1.4 Verify and aggregate

1. Paste suite-root **`FINALIZE_PROMPT.md`** into the **control hub** chat, or follow the same steps in **[`/crtqa-benchmark`](../commands/crtqa-benchmark.md)** **Finalize**.
2. **`python automation/tools/benchmark_verify.py --suite-dir .cursor/benchmark/runs/<suite_id>`** (optional **`--strict-manifest`**).
3. For **each epic** with snapshots (when profile includes coverage), from repo root:
   ```bash
   python .cursor/benchmark/coverage-bench/scripts/compare_runs.py --epic <KEY> --kind prep --suite-run-dir .cursor/benchmark/runs/<suite_id>
   python .cursor/benchmark/coverage-bench/scripts/compare_runs.py --epic <KEY> --kind coverage --suite-run-dir .cursor/benchmark/runs/<suite_id>
   ```
   The suite folder name sets **`suite_id`** in metrics; **`--suite-id`** is optional (use only when it must differ from the folder name). Or loop epics via **`benchmark_aggregate.py`** (see **`/crtqa-benchmark`**).
4. **Validators / digests**: follow **[`coverage-bench/pipeline/validator.md`](coverage-bench/pipeline/validator.md)** § hub layout; metrics JSON is under **`_aggregate/crossref/`**; global append-only history under **`.cursor/benchmark/history/`** (**gitignored**).

### 1.5 Write `report.md` (hub)

**Preferred:** **`FINALIZE_PROMPT.md`** run from the **control hub** prompts the **agent** to author **`.cursor/benchmark/run-results/<run-key>/report.md`** (**`run-key`** = **`_manifest.report_run_key`** ?? **`suite_id`**). Use **[`run-results/README.md`](run-results/README.md)** section order and optional **`pipeline-delta-queue.json`**.

- **Variance methodology:** mirror **`_manifest.json`** (**`fresh-session stochasticity`** vs **`deterministic replay`**).
- **Paths:** cite **`runs/<suite_id>/attempt-<nn>/shadow/`**, **`runs/<suite_id>/_aggregate/crossref/`**; **`epics/<KEY>/`** only without benchmark tokens.

**Recommendations only** for harness edits unless a separate ticket says otherwise.

---

## 2. Playbooks vs evidence

Benchmarks often **suggest edits** to **`.cursor/pipelines/*.md`**. **Evidence paths** cite machine snapshots (`_machine/`, legacy **`coverage-bench/runs/`**, hub **`runs/<suite_id>/_aggregate/crossref/`**) and **`epics/<KEY>/`** when legacy mode ran. Gold: **[`data/README.md`](data/README.md)**. **Portable rules** belong in **`run-results/<run-key>/report.md`** per **[`run-results/README.md`](run-results/README.md)** — never paste ticket-shaped checklist lines verbatim into playbooks without abstraction.

---

## Appendix: Legacy coverage-bench orchestration

Use when you already rely on **`BENCHMARK:`** / **`BENCHMARK-NEXT:`**, **`coverage-bench/runs/run-<suite_id>/`**, or you are reproducing older queue docs. Snapshot JSON lives in **`attempts/<KEY>/`**; production **`epics/<KEY>/`** receives durable writes (**no **`benchmark_*`** tokens** on those prep/coverage lines).

Hard rule for the multi-step suite: **only one queue step per message** — see **[`coverage-bench/pipeline/benchmark-suite.md`](coverage-bench/pipeline/benchmark-suite.md)**.

### A. Fill in once per run

```text
--- BENCHMARK SETUP ---
EPICS: CRT-ABC, CRT-XYZ
RUNS: 3
SUITE_ID:
REPORT_LABEL:
TEST_PREP: no
COVERAGE_REPO:
COVERAGE_FOCUS:
PATH: A                           # A | B | C; optional PATH T → §E
--- END SETUP ---
```

**PATH**

| Path | Meaning |
|------|---------|
| **A** | Suite + `compare_runs` **--suite-id** + validators + **mandatory** `run-results` report. **`TEST_PREP: yes`** optional. Fork **`coverage`** vs **`combined`**. |
| **B** | Quick EPIC-PREP → COVERAGE per epic; **`REPORT_LABEL`** required. |
| **C** | Like **A** but skip **TEST-PREP** regardless of **`TEST_PREP`**. |

Optional **PATH T** (**test-bench**) after PATH **A**/**C**: **[`test-bench/pipeline/benchmark-test-prep.md`](test-bench/pipeline/benchmark-test-prep.md)**; **`compare_test_runs.py`** still **TBD** — qualitative **`run-results/<test_suite_id>__test.md`**.

### B. Prompt — PATH **A or C**

````text
Use my --- BENCHMARK SETUP --- above. Repo root is cwd. If EPICS or PATH are missing, ask once. PATH must be **A** or **C**.

Technical: read `.cursor/benchmark/coverage-bench/pipeline/benchmark-suite.md`.

1) Init only: one line **`BENCHMARK:`** with comma-separated EPICS from setup, **`runs=`** from setup, optional **`repo=`** / **`focus=`** from setup. Echo **suite_id** from **`.cursor/benchmark/coverage-bench/runs/run-<suite_id>/support/`**.

2) Until finished: **BENCHMARK-NEXT: <suite_id>** (one step per turn); update **`support/progress.json`**; **`SUMMARY.md`** on finalize.

3) **compare_runs** (each epic):
   python .cursor/benchmark/coverage-bench/scripts/compare_runs.py --benchmark-root .cursor/benchmark/coverage-bench --epic <EPIC_KEY> --kind prep --suite-id <suite_id>
   python .cursor/benchmark/coverage-bench/scripts/compare_runs.py --benchmark-root .cursor/benchmark/coverage-bench --epic <EPIC_KEY> --kind coverage --suite-id <suite_id>

4) Validators: **PREP-VALIDATE** / **COVERAGE-VALIDATE** with **`suite=<suite_id>`**; gold from **`.cursor/benchmark/data/`** or **`coverage-bench/data/`** if present.

5) If **PATH A** and **`TEST_PREP: yes`**: **TEST-PREP: <KEY>** per epic (production paths). **PATH C** or **`TEST_PREP: no`**: skip.

6) **`run-results/<suite_id>__coverage.md`** or **`__combined.md`** per [`run-results/README.md`](run-results/README.md) — include **Variance methodology** (isolated **`BENCHMARK-NEXT`** chats vs replay) in Epic-scoped.

Delete **`epics/<KEY>/temp/`** when playbooks require.
````

### C. Prompt — PATH **B**

````text
Use --- BENCHMARK SETUP --- (PATH B). **REPORT_LABEL** required. Per epic: **EPIC-PREP:** then **COVERAGE:** (optional **repo/focus**). If **TEST_PREP: yes**, **TEST-PREP:**. Then **`run-results/<REPORT_LABEL>__coverage.md`** or **`__combined.md`** per **run-results/README.md** (Gold vs runs, Variance interpretation, Variance methodology).
````

### D. Report only (suite already ran)

````text
**SUITE_ID** = existing `.cursor/benchmark/coverage-bench/runs/run-<suite_id>/`. Rebuild **`run-results/<suite_id>__coverage.md`** or **`__combined.md`** per **run-results/README.md**. Cite **`coverage-bench/runs/…`**, hub **`.cursor/benchmark/runs/<suite_id>/…`** if mixed, **`_aggregate/crossref/`**, **`epics/<KEY>/`**, **`.cursor/benchmark/data/`** as used.
````

### E. PATH **T** (test-bench)

See §A table; outputs under **`test-bench/runs/run-<suite_id>/`** and production **`epics/<KEY>/<KEY>-tests.*`** unless you adopt hub tokens for test-prep.

### F. Where files land (orientation)

| Class | Role | Where |
|------|------|-------|
| **Working tree** | Legacy delegates | **`epics/<KEY>/`** |
| **Shadow durable** | Hub **`EpicDir`** | **`.cursor/benchmark/runs/<suite>/attempt-<nn>/shadow/<KEY>/`** |
| **Snapshots (legacy suite)** | **`compare_runs --suite-id`** | **`coverage-bench/runs/run-<suite_id>/attempts/<KEY>/`** |
| **Snapshots (hub)** | **`compare_runs --suite-run-dir`** | **`.cursor/benchmark/runs/<suite_id>/attempt-<nn>/_machine/attempts/<KEY>/`** |
| **Metrics** | Crossref JSON | **`coverage-bench/crossref/`** *or* **`runs/<suite>/_aggregate/crossref/`** |
| **History** | Append-only JSONL | **`.cursor/benchmark/history/`** (hub) / **`coverage-bench/history/`** (legacy) |
| **Narratives** | Human summaries | Suite **`report.md`** (hub) and/or **`run-results/*.md`** (legacy; **gitignored** except **README**) |
