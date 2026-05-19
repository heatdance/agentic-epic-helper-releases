# Benchmark workspace contract

Normative companion to [`.cursor/benchmark/README.md`](../.cursor/benchmark/README.md). Epic pipelines (`EPIC-PREP`, `COVERAGE`, `ANALYSE`, `TEST-DISCOVER`, `TEST-PRECON`, `TEST-PREP`, `CLOSE`) resolve **all durable artifacts and temp** relative to **EpicDir** (below), not exclusively `epics/<KEY>/`, when benchmark tokens are present.

## EpicDir resolution

`<KEY>` = Jira Epic key from the trigger (normalized uppercase).

**Benchmark mode** — when **both** optional tokens appear on the **same user message line** as the pipeline trigger:

- `benchmark_suite=<suite_id>` — path-safe identifier (match folder under `.cursor/benchmark/runs/`).
- `benchmark_attempt=<n>` — integer attempt index (`1`-based).

Then:

```
EpicDir = <repo>/.cursor/benchmark/runs/<suite_id>/attempt-<nn>/shadow/<KEY>/
```

`<nn>` is `benchmark_attempt` zero-padded to **two** digits (e.g. `1` → `01`). The `shadow/` tree must mirror production layout: `{EpicDir}<KEY>-ref.json`, `{EpicDir}<KEY>-coverage.json`, `{EpicDir}temp/`, etc. After **`CLOSE:`**, same archive as production: four human `.md` at `{EpicDir}` root; JSON under `{EpicDir}context/` (including `-close.json`).

**Same run index, multiple chats:** You may execute **prep**, **coverage**, and **test-prep** in **separate** cold Cursor sessions **as long as each trigger line repeats the identical** `benchmark_suite` **and** `benchmark_attempt`. All phases for run index `r` write under the same **`attempt-<nn>/shadow/<KEY>/`** (`<nn>` zero-padded from `r`).

**Benchmark mode forbids** writing durable or temp QA artifacts under **`epics/<KEY>/`** for that run — use **`EpicDir`** only.

## Production mode (default)

If **either** `benchmark_suite` or `benchmark_attempt` is **missing** from the trigger line:

```
EpicDir = <repo>/epics/<KEY>/
```

Behavior matches historical harness docs (router, qa-artifacts).

## Path notation in playbooks

Pipelines spell concrete files as **`{EpicDir}<KEY>-ref.json`**, **`{EpicDir}temp/`**, **`{EpicDir}tests/`**, … — always interpret **`{EpicDir}`** via this contract.

## Gold files

Orcles live at **`<repo>/.cursor/benchmark/data/<KEY>-gold.json`** (benchmark root scope, shared across suites); see [`.cursor/benchmark/data/README.md`](../.cursor/benchmark/data/README.md). Legacy copies may remain under `coverage-bench/data/` until removed; [`compare_runs.py`](../.cursor/benchmark/coverage-bench/scripts/compare_runs.py) resolves gold from benchmark `data/` when suite-local dirs are used (see `--suite-run-dir`, `--gold-root`).

## Longitudinal KPI history

Append-only JSONL metrics history is written under **`<repo>/.cursor/benchmark/history/<KEY>-prep-history.jsonl`**, **`-coverage-history.jsonl`**, and **`-test-history.jsonl`** when using suite-local compare outputs (implemented in `compare_runs.py`). Per-suite **`_aggregate/crossref/`** holds that run’s metrics JSON only.

## Hub layout (manifest-driven)

See [`.cursor/commands/crtqa-benchmark.md`](../.cursor/commands/crtqa-benchmark.md). Suite folder: `.cursor/benchmark/runs/<suite_id>/` with `_manifest.json`, suite-root **`CONTROL_HUB.md`**, **`DONE_HANDOFF_PROMPT.md`** (**agent** **`DONE.json`** handoff), **`FINALIZE_PROMPT.md`** (**control hub** combine), per-attempt **`attempt-<nn>/`** phase **`PROMPT-*.md`**, **`DONE.json`**, **`shadow/<KEY>/`** durable snapshots, and optional **`_machine/`** JSON wrappers for tooling. The suite folder does **not** host **`report.md`** (narratives are separate).

**Reports (finalize output):** **`.cursor/benchmark/run-results/<run-key>/report.md`** and optional **`pipeline-delta-queue.json`**. **`run-key`** defaults to **`suite_id`** (`_manifest.suite_id`). Optional **`report_run_key`** in `_manifest.json` overrides the directory name when keeping the same suite folder for a new report wave ([`run-results/README.md`](../.cursor/benchmark/run-results/README.md)).

**Compare without `_machine`:** `compare_runs.py --suite-run-dir` prefers **`attempt-<nn>/_machine/attempts/<KEY>/run-*.json`** (`phase` **`prep`**, **`coverage`**, or **`test`**) when present; otherwise it ingests **`shadow/<KEY>/<KEY>-ref.json`**, **`-coverage.json`**, and **`-tests.json`** (plus sibling **`-coverage.md`** for checklist bullets) so finalize can run purely on shadow output.

## References

- [`automation/temp/benchmark-rework-analysis/`](../automation/temp/benchmark-rework-analysis/README.md) — WS-A…F analysis
