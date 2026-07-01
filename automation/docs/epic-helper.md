# epic-helper orchestrator

**Slash command:** `/epic-helper` · **Contract:** [`docs/epic-helper-contract.json`](../../docs/epic-helper-contract.json) (**v6**)

One epic per chat; **draft_truth_v3** chain with **two human gates** (console multiplex, coverage_review). **One automated stage per agent turn.**

Operator UX and stage map: [`.cursor/commands/epic-helper.md`](../../.cursor/commands/epic-helper.md).

## Console gate

Cold start and GROUND use [`crtqa_console_probe.py`](../tools/crtqa_console_probe.py) — multiplex session only. Recovery: **`/crtqa-console start`**.

## Scratch (gitignored)

`epics/<KEY>/helper/` — archived to `context/helper/` on **CLOSE:** via [`close_archive.py`](../tools/close_archive.py).

## Verify

```powershell
powershell -NoProfile -File .cursor/scripts/corner-harness-verify.ps1 -Profile full
```

Golden: [`fixtures/operator-assist/epic-helper-golden.json`](../tools/fixtures/operator-assist/epic-helper-golden.json).
