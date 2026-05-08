# Benchmark validator: TEST-PREP (scaffold)

**Status:** manual checklist here; **machine metrics** via **`compare_runs.py --kind test --suite-run-dir`** (writes **`*-test-metrics.json`** under hub **`_aggregate/crossref/`**). Use both when driving **`TEST-PREP:`** / **`BENCHMARK-TEST-*`** tokens ([`benchmark-test-prep.md`](benchmark-test-prep.md)).

## Triggers (conventions; not in `pipeline-router.mdc`)

- Inspect **`{EpicDir}<KEY>-tests.json`** / **`-tests.md`** after **`BENCHMARK-TEST-FINALIZE`** or per-row queue steps.
- **`{EpicDir}`** resolves per [docs/benchmark-contract.md](../../../../docs/benchmark-contract.md) when **`benchmark_suite`** + **`benchmark_attempt`** were used on **`TEST-PREP:`** lines; otherwise **`epics/<KEY>/`**.

## Checks (manual)

1. **`sources.map_only`** / **`sources.coverage_loaded`** sane for map-only rows.
2. **`test_bundles[]`**: each targeted **`bundle_id`** has **`authoring.subprocess_completed`** when the queue row completed.
3. No **`/temp/`** substrings in durable JSON.
4. **`-tests.md`** present at finalize for every epic in the suite manifest.

## Future

Extend **`--kind test`** gold / structured assertions (see **`CRT-*-gold.json`** patterns in prep/coverage) and deeper bundle diffing — mirror [`validator.md`](../../coverage-bench/pipeline/validator.md) style deterministic field diffs + markdown Jaccard where stable.
