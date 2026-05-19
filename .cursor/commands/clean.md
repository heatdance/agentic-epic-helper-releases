---
description: Align harness on personal and publish team + public exports (CLEAN pipeline)
---

# /clean

**BLUF:** Run the **CLEAN** publish pipeline from branch **`personal`**. Sequential checkout: push **`origin/personal`**, direct push **`team/team`**, then **`public-M.N+1`** from **`team/team`** on releases. No `clean/*` branches or worktrees.

## Agent action

1. Confirm **`git branch --show-current`** is **`personal`**. If not, **stop** and ask the operator to checkout `personal`.
2. Run the full playbook: [`.cursor/pipelines/clean.md`](../pipelines/clean.md) for trigger **`CLEAN:`** (same optional tokens).

Preflight:

```powershell
python automation/tools/clean_verify.py --mode preflight
```

Partial runs (operator request):

| Token | Phases |
|-------|--------|
| `scope=align` | Align only |
| `scope=personal` | Align + push personal |
| `scope=team` | Team strip + direct push `team/team` |
| `scope=public` | Public from `team/team` + postflight |
| `scope=full` | All (default) |

## Human gates

| Gate | Operator |
|------|----------|
| Dirty tree | Add **`proceed`** on the trigger line after reviewing `git status` |
| Public `public-1.9` → `public-2.0` | Add **`confirm_major=yes`** |
| Bad prior publish | [automation/docs/clean-remediation.md](../../automation/docs/clean-remediation.md) before full `CLEAN:` |

## Tier docs and supersede

- Publish matrix: [docs/clean-publish-tier-matrix.md](../../docs/clean-publish-tier-matrix.md)
- Team/public **README / HOW-TO / AGENTS** are generated (not copied from personal).
- After each new **`public-M.N`** push, U4b deletes the previous **`public-*`** and legacy **`release-*`** when configured.

## Related

- [docs/clean-contract.json](../../docs/clean-contract.json)
- [automation/docs/clean-verify.md](../../automation/docs/clean-verify.md)
- [automation/docs/clean-remediation.md](../../automation/docs/clean-remediation.md)
- [docs/clean-public-style.md](../../docs/clean-public-style.md)
