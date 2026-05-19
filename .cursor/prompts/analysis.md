# Prompt scaffold: Requirement analysis (`ANALYSE:`)

```text
ANALYSE: <!-- EPIC-KEY e.g. CRT-642 -->
```

**Agent**: [`.cursor/pipelines/analysis.md`](../pipelines/analysis.md) v2 end-to-end.

**Requires** `{EpicDir}<KEY>-coverage.json` (from **`COVERAGE:`**) and usually **`-ref.json`**.

Optional on the **same line**:

- **`known_issues=yes`** — Jira search + optional coverage `>` Known issue lines (default **off**)
- **`include_closed=yes`** — with known_issues only
- **`resolve=no`** — audit-only (skip Confluence resolve subprocesses; default **on**)

## Checklist

1. `jq` project **`-coverage.json`** + **`-ref.json`**
2. Phase **2–3** — deterministic work queue → **`gaps[]`** (high confidence only)
3. Phase **4b** — **one subprocess per resolvable gap** (max 8) → `temp/analysis-resolve-*.json`
4. Phase **5** — **`exploration_suppressed[]`** for deferred checks
5. Phases **6–8** only if **`known_issues=yes`**
6. Phase **9** — tool-backed coverage write-back only
7. **`analysis_verify.py`** gaps + downstream + emit — then delete **`temp/`**

**Emit:** gaps-first **`.md`** — no Summary / Questions sections.

Contract: [docs/analysis-gap-contract.json](../../docs/analysis-gap-contract.json). Verifier: [automation/docs/analysis-verify.md](../../automation/docs/analysis-verify.md).
