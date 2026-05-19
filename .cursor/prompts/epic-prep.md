# Prompt scaffold: Epic preflight (`EPIC-PREP:`)

Copy into chat with the Epic key:

```text
EPIC-PREP: <!-- EPIC-KEY e.g. CRT-1234 -->
```

**Agent**: Read [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc), then execute **[`.cursor/pipelines/epic-prep.md`](../pipelines/epic-prep.md)** end-to-end for **that key only**.

Optional on the **same line**:

- **`repo=WORKSPACE/SLUG`** — Bitbucket prep search
- **`focus=...`** — merge into synthesis / obligations reconcile

Default durable path: **`epics/<KEY>/<KEY>-ref.json`**.

## Subprocess checklist (orchestrator)

1. Jira + Yogi snippets (**3**, **3b**)
2. **One subprocess per requirement** → `temp/epic-obligation-<REQKEY>.json` (**3c**); optional nested (**3d**)
3. Merge → **`obligations_proposed[]`**; **synthesis** (**3e**); **client_shell_impact** (**2b**)
4. Design, precision, Bitbucket (**4**–**5b**), XT (**6**–**7**), **reconcile** (**6b**)
5. Finalize: **`epic_prep_verify.py --mode ref`** then delete **`{EpicDir}temp/`**

**Forbidden**: `-coverage`, `-discover`, `-precon`, `-tests`, CRTQA keys in durable JSON.

Kinds: [docs/epic-obligation-kinds.json](../../docs/epic-obligation-kinds.json). Verifier: [automation/docs/epic-prep-verify.md](../../automation/docs/epic-prep-verify.md).

Use **user-mcp-atlassian** (schemas first) and [automation/docs/yogi-url-resolve.md](../../automation/docs/yogi-url-resolve.md) for Yogi.
