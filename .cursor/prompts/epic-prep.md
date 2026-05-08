# Prompt scaffold: Epic preflight (`EPIC-PREP:`)

Copy into chat with the Epic key:

```text
EPIC-PREP: <!-- EPIC-KEY e.g. CRT-1234 -->
```

**Agent**: Read [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc), then execute **[`.cursor/pipelines/epic-prep.md`](../pipelines/epic-prep.md)** end-to-end for **that key only**. Optional on the **same line**: **`benchmark_suite=<id>`** + **`benchmark_attempt=<n>`** → durable path is **`{EpicDir}<KEY>-ref.json`** under **`.cursor/benchmark/runs/<id>/attempt-<nn>/shadow/<KEY>/`** (contract: **[docs/benchmark-contract.md](../../docs/benchmark-contract.md)**). Default: **`epics/<KEY>/`**.

Use **user-mcp-atlassian** (schemas first) and [automation/docs/yogi-url-resolve.md](../../automation/docs/yogi-url-resolve.md) for Yogi. **Delete** **`{EpicDir}temp/`** before finishing. Deliver **`{EpicDir}<KEY>-ref.json`**.
