# Prompt scaffold: Epic preflight (`EPIC-PREP:`)

Copy into chat with the Epic key:

```text
EPIC-PREP: <!-- EPIC-KEY e.g. CRT-1234 -->
```

**Agent**: Read [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc), then execute **[`.cursor/pipelines/epic-prep.md`](../pipelines/epic-prep.md)** end-to-end for **that key only**. Use **user-mcp-atlassian** (schemas first) and [automation/docs/yogi-url-resolve.md](../../automation/docs/yogi-url-resolve.md) for Yogi. **Delete** `epics/<KEY>/temp/` before finishing. Deliver **`epics/<KEY>/<KEY>-ref.json`**.
