# Benchmark rework — analytical memos

> **Update:** Subsequent harness work tracks **`.cursor/benchmark/`** sources in git (machine outputs still ignored per **`.gitignore`**). Memo prose about “everything under benchmark gitignored” is **historical**; use **`WS-*` docs** as rationale, **not** current git policy unless cross-checked.

Generated **2026-05-08** per roadmap “Benchmark harness analysis” (plan execution: analytical work only, no harness implementation).

| ID | Topic | File |
|----|--------|------|
| WS-A | Path coupling audit (`epics/` vs shadow target) | [WS-A-findings.md](./WS-A-findings.md) |
| WS-B | Isolation / variance semantics | [WS-B-findings.md](./WS-B-findings.md) |
| WS-C | Vendor-neutral hub (manifest, DONE.json, subcommands) | [WS-C-findings.md](./WS-C-findings.md) |
| WS-D | Directory layout migration | [WS-D-findings.md](./WS-D-findings.md) |
| WS-E | TEST-PREP / test-bench shadow parity | [WS-E-findings.md](./WS-E-findings.md) |
| WS-F | Gold relocation + compare_runs / history | [WS-F-findings.md](./WS-F-findings.md) |

Artifacts here are disposable analysis notes under `automation/temp/`; scrub before **PUBLIC-SCRUB** per [`.cursor/pipelines/public-scrub.md`](../../../.cursor/pipelines/public-scrub.md).
