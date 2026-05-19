---
description: Align harness on personal and publish team + public exports (CLEAN pipeline)
---

# /clean

**BLUF:** Run the **CLEAN** publish pipeline from branch **`personal`**. Aligns harness pointers, pushes **`origin/personal`**, updates [agentic-epic-helper-team](https://github.com/heatdance/agentic-epic-helper-team), and publishes **`public-M.N`** to [agentic-epic-helper-releases](https://github.com/heatdance/agentic-epic-helper-releases).

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
| `scope=team` | Team strip + push/PR |
| `scope=public` | Public sterilize + push releases |
| `scope=full` | All (default) |

## Human gates

| Gate | Operator |
|------|----------|
| Dirty tree | Add **`proceed`** on the trigger line after reviewing `git status` |
| Team PR | Merge PR on team repo — agent **must not** `gh pr merge` |
| Public `public-1.9` → `public-2.0` | Add **`confirm_major=yes`** |

## Tier docs and supersede

- Publish matrix: [docs/clean-publish-tier-matrix.md](../../docs/clean-publish-tier-matrix.md)
- Team/public **README / HOW-TO / AGENTS** are generated (not copied from personal).
- After each new **`public-M.N`** push, phase **U4b** deletes the previous **`public-*`** branch on `releases` when `superseded_branch` is set (`semver_next --json`).

## Related

- [docs/clean-contract.json](../../docs/clean-contract.json)
- [automation/docs/clean-verify.md](../../automation/docs/clean-verify.md)
- [automation/docs/clean-verify.md](../../automation/docs/clean-verify.md)
- [docs/clean-public-style.md](../../docs/clean-public-style.md)
