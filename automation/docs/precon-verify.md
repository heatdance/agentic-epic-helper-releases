# TEST-PRECON — mechanical verifier

Playbook: [`.cursor/pipelines/test-precon.md`](../../.cursor/pipelines/test-precon.md). Depth ladder: [`docs/exploration-depth-ladder.json`](../../docs/exploration-depth-ladder.json).

## CLI

**Phase 4V loop** (ledger or durable JSON):

```powershell
python automation/tools/precon_verify.py `
  --coverage epics/CRT-639/CRT-639-coverage.json `
  --precon epics/CRT-639/temp/precon-ledger.json `
  --discover epics/CRT-639/CRT-639-discover.json
```

**Before emit:**

```powershell
python automation/tools/precon_verify.py `
  --coverage epics/CRT-639/CRT-639-coverage.json `
  --precon epics/CRT-639/CRT-639-precon.json `
  --discover epics/CRT-639/CRT-639-discover.json `
  --md epics/CRT-639/CRT-639-precon.md
```

Exit **0** = pass. Non-zero = re-run Phase **4R/4D/4C** subprocesses (max **3** cluster iterations).

## Exploration depth checks (v4)

| Check | Failure when |
|-------|----------------|
| FE `outcome: pass` | `depth_level` below `precon_drill` or missing `view_id` (unless gap documented) |
| Post-login smoke | `outcome: pass` without `depth_level: smoke` |
| Discover `probe_executed` | No matching `precon_drill` row per `satisfies_fixture_ids` |
| Required views | Missing `view_id` from ladder per fixture kind |
| Anti-batch | All `exploration_log[].at` identical in cluster |
| Shallow widgets | `widgets_seen` ⊆ nav denylist only |
| Console extended | Discover notes have instrument/account ids but no `show` in console logs |

Document waivers in **`exploration_gaps[]`** with `reason: tooling_blocked` (or `chrome_unavailable`, `waived`).
