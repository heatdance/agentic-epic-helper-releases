# Prompt scaffold: Epic coverage (`COVERAGE:`)

```text
COVERAGE: <!-- EPIC-KEY e.g. CRT-639 -->
```

**Agent**: [`.cursor/pipelines/coverage.md`](../pipelines/coverage.md) end-to-end. **Requires** `{EpicDir}<KEY>-ref.json` (**schema v4**, `obligations_proposed[]`).

Optional: **`repo=`**, **`focus=`**, **`benchmark_suite=`** + **`benchmark_attempt=`**.

## Subprocess checklist

1. Load ref + Jira (**1**, **1½** obligations map)
2. Hygiene, archetype, focus (**2**–**3a**)
3. Matrix (**4**); **invariants subprocess** (**4b**) when ref has `kind: invariant`
4. Snippets, XT, Bitbucket (**5**–**7**)
5. E2E spine (**8**); **per-`##` section** check drafts (**9**) → merge `temp/coverage-section-*.json`
6. Dimensions (**10**) — no blanket multi-group `!` when invariants exist
7. Prune, grounding, anti-patterns (**11**–**13**)
8. **`coverage_verify.py --mode obligations`** (**13b**)
9. Emit + **`coverage_verify.py --mode emit`** (**14**); delete **`temp/`**

**Forbidden**: CRTQA, `-tests.json`, bench JSON in production.

Contract: [docs/coverage-obligation-contract.json](../../docs/coverage-obligation-contract.json). Verifier: [automation/docs/coverage-verify.md](../../automation/docs/coverage-verify.md).
