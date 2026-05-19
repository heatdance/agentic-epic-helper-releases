# Test bench — curated CRTQA snapshots

Human-curated Jira **Test** issue JSON under `<EPIC>/` (e.g. [CRT-639/index.json](CRT-639/index.json)).

## Purpose

- **Benchmark compare** and evaluation targets — not structural input to cold **generation-mode** `TEST-PREP:` (see [docs/harness-principles.md](../../../docs/harness-principles.md) §3).
- **TEST-PREP v3** **`shape_ref=benchmark`** **only** when **both** **`benchmark_suite=`** and **`benchmark_attempt=`** are on the trigger: read for **case titles/structure only**. **Not** production generation input. **MUST NOT** copy **CRTQA-#####** keys into durable epic artefacts.

## Layout

```
test-bench/data/<EPIC>/
  index.json          # issue list + file paths
  CRTQA-10177.json    # snapshot per test
  ...
```

## Operator

Re-fetch from Jira via MCP when snapshots drift; update `fetched_at` in `index.json`. Do not commit secrets or session-specific credentials in snapshot bodies when refreshing.
