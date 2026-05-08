# Benchmarks (Corner QA)

**Start here (operators / agents):** **[`/crtqa-benchmark`](../commands/crtqa-benchmark.md)** (**questionnaire → `CONTROL_HUB.md` orchestration**) and **[`docs/benchmark-contract.md`](../../docs/benchmark-contract.md)** — shadow hub layout and **`benchmark_suite`** / **`benchmark_attempt`** tokens on production pipeline lines.

Second: **[`BENCHMARK_RUNBOOK.md`](BENCHMARK_RUNBOOK.md)** (hub §1 default; legacy **`BENCHMARK:`** appendix).

---

Playbooks cover **coverage-bench** (legacy suites), **hub shadow**, and **test-bench**.

| Bench | Folder | Role |
|-------|--------|------|
| **Coverage-bench** | [`coverage-bench/`](coverage-bench/HOW-TO.md) | Legacy **`BENCHMARK:`** queues, **`coverage-bench/runs/run-<id>/attempts/`** snapshots, [`compare_runs.py`](coverage-bench/scripts/compare_runs.py) with **`--suite-id`**. |
| **Hub shadow** | **`.cursor/benchmark/runs/<suite_id>/`** | Per [docs/benchmark-contract.md](../../docs/benchmark-contract.md): **`benchmark_suite=`** / **`benchmark_attempt=`** on production pipelines → durable tree under **`attempt-<nn>/shadow/<KEY>/`**; wrappers for tooling in **`attempt-<nn>/_machine/attempts/<KEY>/`**; aggregate metrics in **`_aggregate/crossref/`**. Entry doc: **[`/crtqa-benchmark`](../commands/crtqa-benchmark.md)**. |
| **Test-bench** | [`test-bench/`](test-bench/HOW-TO.md) | Atomic **`BENCHMARK-TEST-*`** queues; hub test metrics **`compare_runs.py --kind test --suite-run-dir`** (+ [`pipeline/validator-test.md`](test-bench/pipeline/validator-test.md)). |

**Canonical gold:** **[`data/README.md`](data/README.md)** — **`.cursor/benchmark/data/<KEY>-gold.json`** (legacy **`coverage-bench/data/`** for older suites).

**Human narratives:** **`.cursor/benchmark/run-results/<run-key>/report.md`** (and optional **`pipeline-delta-queue.json`**) — **not** under the suite folder; **`run-key`** defaults to **`suite_id`** ([run-results/README.md](run-results/README.md)). Legacy flat **`run-results/*.md`** files remain valid for PATH **B** smokes (**gitignored** except template **README**).

---

## Migration: `coverage-bench/runs/` → hub **`runs/<suite>/`**

- **Legacy (unchanged):** **`.cursor/benchmark/coverage-bench/runs/run-<suite_id>/attempts/<KEY>/run-*.json`** — **`compare_runs.py --benchmark-root … --suite-id`**; history under **`coverage-bench/history/`** when hub flags are **not** used.
- **New hub:** **`.cursor/benchmark/runs/<suite_id>/attempt-<nn>/_machine/attempts/<KEY>/run-*.json`** — same JSON wrapper (`phase`, `artifact`, …); **`compare_runs.py --suite-run-dir .cursor/benchmark/runs/<suite_id>`** writes **`_aggregate/crossref/`** and append-only **`../history/`** (i.e. **`.cursor/benchmark/history/`**).

Do **not** mix snapshot layouts for the same spreadsheet without renaming suite ids—pick one convention per orchestration doc.

---

## Git hygiene

**Tracked:** harness **`.md`**, **`coverage-bench/scripts/`**, **`templates/`**, **`data/README.md`**, **`data/.gitkeep`**, and—under **`.cursor/benchmark/runs/<suite_id>/`**—**`_manifest.json`**, **`CONTROL_HUB.md`**, **`DONE_HANDOFF_PROMPT.md`** (agent **`DONE.json`** handoff blocks), **`FINALIZE_PROMPT.md`** (**no** suite-root **`report.md`**). Optionally commit curated **`run-results/<run-key>/`** content if team policy adjusts **`.gitignore`**.

**Ignored** (see repo **`.gitignore`**): hub **`runs/*/attempt-*/`** (shadow, PROMPT, DONE, `_machine`, etc.), **`runs/*/_aggregate/`**, **`.cursor/benchmark/history/`**, legacy **`coverage-bench`** / **`test-bench`** machine dirs (**`runs/`**, **`crossref/`**, **`digest/`**, **`history/`**), **`run-results/`** subtree except **`run-results/README.md`**, **`*-gold.json`** under **`data/`** and **`coverage-bench/data/`**, and **`**/temp/`** under benchmark.
