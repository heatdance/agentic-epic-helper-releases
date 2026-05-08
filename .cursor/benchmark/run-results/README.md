# Benchmark run-results (per-run narrative + pipeline queue)

This folder holds **human- and agent-written benchmark outcome summaries**: narratives used to propose **transferable** changes to pipelines (`.cursor/pipelines/*.md`), playbooks, and templates — **without** tailoring the harness to the epics used on one epic alone.

**Runs stay separate:** machine output (shadow snapshots, **`_aggregate/crossref/`**, **`history/`**) lives only under **`.cursor/benchmark/runs/<suite_id>/`**. Reports and structured pipeline handoff live **here**, under **`run-results/<run-key>/`**.

Separate **what you saw on specific epics** (evidence) from **what should change globally** (generalized recommendations). Evidence may cite `crossref/*.json`, gold files, digests — those paths are **not** meant to be copied verbatim into playbooks.

Gold files that steer **pipelines** (stable gates) should favor **`structured_assertions` / thresholds** over long **`required_smart_checklist_substrings`** lists when authoring **`.cursor/benchmark/data/<KEY>-gold.json`** (canonical location; **`coverage-bench/data/`** is legacy). See **[`coverage-bench/HOW-TO.md`](../coverage-bench/HOW-TO.md) § Gold file schema**.

## Run key (`run-key`)

| Source | Meaning |
|--------|---------|
| **Default** | **`suite_id`** — same string as hub folder **`.cursor/benchmark/runs/<suite_id>/`** and **`benchmark_suite=`** on trigger lines. |
| **Optional override** | **`report_run_key`** in suite **`_manifest.json`** — use when you keep the same **`suite_id`** but want a distinct report directory (e.g. second CRT-639 wave). **FINALIZE** uses **`manifest.report_run_key` ?? `manifest.suite_id`**. |

Canonical output directory:

```text
.cursor/benchmark/run-results/<run-key>/
  report.md
  pipeline-delta-queue.json   # optional machine handoff for Plan-mode planning
```

## Rules

1. **Per `run-key` folder:** **`report.md`** (required for finalize narratives) follows the **template sections** below. **`pipeline-delta-queue.json`** is **allowed** exactly one per folder — structured **change requests** for agents in Plan mode ([`templates/pipeline-delta-queue.example.json`](../templates/pipeline-delta-queue.example.json)). Do **not** put snapshot JSON, crossref dumps, MCP exports, or unrelated binaries here. Machine artifacts stay under **`coverage-bench/runs/`**, **`test-bench/runs/`** (PATH **T**), or hub **`runs/<suite_id>/attempt-*/`** (shadow, **`_machine/`**, **`_aggregate/`**). **Git:** content under **`run-results/`** is **gitignored** except **this README** (see repo **`.gitignore`**).
2. **Exception:** **this README** defines conventions — it is not itself a benchmark run summary.
3. **Authoritative metrics JSON** stays under **`runs/<suite_id>/_aggregate/crossref/`** after **`compare_runs.py --suite-run-dir`** (**`*-prep-metrics.json`**, **`*-coverage-metrics.json`**, **`*-test-metrics.json`**). Narratives **cite** those paths by repo-relative posix path; **`pipeline-delta-queue.json`** **`trigger`** fields should reference them too (paths + KPI / threshold keys), not pasted payloads.
4. Playbook-directed edits MUST **rewrite** ephemeral epic prose into norms in **`.cursor/pipelines/`** or **`epics/templates/`** — not paste ticket-shaped bullets without abstraction.

## Naming (preferred vs legacy)

- **Preferred (hub):** **`.cursor/benchmark/run-results/<run-key>/report.md`** with section order below. Embed **`### Pipeline increments (structured)`** (see **[`FINALIZE_PROMPT.example.md`](../templates/FINALIZE_PROMPT.example.md)**) and optionally mirror CRs into **`pipeline-delta-queue.json`** for tooling.
- **Legacy flat files:** **`<suite-id>__{fork}.md`** or **`YYYY-MM-DD_<suite-id>__{fork}.md`** directly under **`run-results/`** remain valid for PATH **B** smoke / historical copies; migrate new hub finalize output to **`run-results/<run-key>/report.md`**.

Where **`fork`** labels (legacy filenames or **Evidence fork** metadata) mean:

- **`coverage`** — prep + coverage variance only.
- **`test`** — TEST-PREP / **`test-bench`**; cite **`compare_runs.py --kind test`** and **`*-test-metrics.json`**.
- **`combined`** — prep + coverage + test-prep (**`coverage_test`** profile).

Quick PATH **B** smokes without a suite folder: **`{REPORT_LABEL}__coverage.md`** etc. (**[`BENCHMARK_RUNBOOK.md`](../BENCHMARK_RUNBOOK.md)**). **`REPORT_LABEL`** is Evidence metadata only.

## `pipeline-delta-queue.json` (minimal contract)

Consumers (e.g. Plan-mode agents) expect top-level **`schema_version`**, **`run_key`**, **`suite_id`**, **`suite_run_dir`**, **`crossref_dir`** (posix paths relative to repo root) and **`change_requests`**: array of objects with at least **`id`**, **`target_files`**, **`trigger`** (metrics path + failing key / gate), **`hypothesis`**, **`proposed_edit`** (string bullets), **`generalization`**, **`verify`** (shell lines). See **`templates/pipeline-delta-queue.example.json`**.

## Template sections (`report.md`; fill when authoring)

Use **these headings in order** so downstream editors do not confuse evidence with playbook work.

### Evidence and scope

- **Fork**: `coverage` | `test` | `combined`
- **Epic keys in this benchmark** — explicit list (e.g. CRT-AAA, CRT-BBB).
- **Paths**: **Metrics:** **`.cursor/benchmark/runs/<suite_id>/_aggregate/crossref/`** (after compare). **Shadow snapshots:** **`runs/<suite_id>/attempt-<nn>/shadow/<KEY>/`**; optional **`_machine/`**. **This report:** **`.cursor/benchmark/run-results/<run-key>/`**. Production **`epics/<KEY>/`** only when the run did **not** use **`benchmark_suite`** + **`benchmark_attempt`**. Optional **`REPORT_LABEL`** for humans only ([`/crtqa-benchmark`](../commands/crtqa-benchmark.md)).

### Epic-scoped observations

Mandatory subsections (may be titled inline as bold lead-ins):

- **Variance methodology** — One explicit line naming the run mode (mirror hub **`_manifest.json`** **`variance_methodology`**): e.g. **`fresh-session stochasticity`** (one cold agent session per orchestrated **`CONTROL_HUB.md`** row / phase per [`docs/benchmark-contract.md`](../../../docs/benchmark-contract.md)) vs **`deterministic replay`**. Required so KPI spread is not over-interpreted.
- **Gold vs runs** — Separate **threshold / structured KPI** outcomes from **legacy investigative** gates (substring / digest-only checks). Tie each row to **`crossref/*-metrics.json`**, validators, or **`.cursor/benchmark/data/<KEY>-gold.json`** (legacy: **`coverage-bench/data/`**), and answer **why** each miss matches or diverges from intent.
- **Variance interpretation** — Expand methodology: **deterministic replay** vs **fresh-session** stochasticity (**isolated chats**, hub **`CONTROL_HUB.md`** + **`attempt-<nn>/PROMPT-*.md`** per phase, or legacy **`BENCHMARK-NEXT`**). Say whether measured spread is trustworthy for dispersion claims.

Further bullets keyed to snapshots, **`epics/<KEY>/`** (if present), digest paths — **documentation only**.

**Do not** lift bullets verbatim into `.cursor/pipelines/*.md`; abstract first under **Generalized pipeline recommendations**.

### Pipeline increments (structured)

For each playbook change proposal, repeat a block (**CR-ID**, **Target**, **Trigger**, **Hypothesis**, **Proposed edit**, **Generalization check**, **Verify**) as defined in **`FINALIZE_PROMPT.example.md`**. Mirror the same CRs into **`pipeline-delta-queue.json`** when Plan-mode tooling should consume them.

### Metrics snapshot *(optional)*

One line linking primary **`coverage-bench/crossref/`** or hub **`_aggregate/crossref/`** payloads (prep / coverage / **`--kind test`**) used for numeric claims.

### Generalized pipeline recommendations

Portable changes only. For **each** bullet:

1. State the **transferable rule** first (e.g. “When upstream omits snippet X, playbook should…”).
2. **Avoid epic keys in the rule title** unless the exception is unavoidably ticket-specific — then put that item instead under **Epic-local follow-ups**.
3. **Map** to a minimal target: [`.cursor/pipelines/epic-prep.md`](../../pipelines/epic-prep.md), [`.cursor/pipelines/coverage.md`](../../pipelines/coverage.md), [`.cursor/pipelines/test-prep.md`](../../pipelines/test-prep.md), or [`epics/templates/`](../../../epics/templates/) as appropriate.

**Generalization checklist** (answer briefly under this section or inline per bullet):

- Would this recommendation still make sense if the benchmark epic keys were different?
- If the suite ran **multiple** epics, did this pattern appear on **≥2** disparate keys? If not and the gap is fragile, defer to epic follow-ups instead of hard-coding playbook text.

**Recommendations only** — no silent repo edits from this file alone.

### Epic-local follow-ups (do not playbook yet)

Findings valid for **specific tickets or gold files** until validated on broader runs. Tracks backlog / hypotheses — **not** ready as global playbook edits.

## Routing

See **[`../BENCHMARK_RUNBOOK.md`](../BENCHMARK_RUNBOOK.md)** — PATH **A** (coverage-focused by default via **`TEST_PREP: no`**), PATH **C**, PATH **B** smokes (**`REPORT_LABEL`** filenames), and optional PATH **T** (`test-bench/runs/` + **`__test.md`**).
