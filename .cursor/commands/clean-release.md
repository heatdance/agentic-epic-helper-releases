---
description: Publish harness from personal branch to team/team and the next public-* release tag.
---

# /clean-release

Run the **CLEAN** publish pipeline from branch **`personal`**. Playbook trigger remains **`CLEAN:`** — see [`.cursor/pipelines/clean.md`](../pipelines/clean.md).

## Agent action

1. Confirm **`git branch --show-current`** is **`personal`**. If not, **stop**.
2. Preflight: `python automation/tools/clean_verify.py --mode preflight`
3. Run full playbook for **`CLEAN:`** (optional tokens: `scope=align|personal|team|public|full`, `confirm_major=yes`, `proceed` on dirty tree).

## Human gates

| Gate | Operator |
|------|----------|
| Dirty tree | Add **`proceed`** on the trigger line |
| Major public bump | Add **`confirm_major=yes`** |
| Bad prior publish | [automation/docs/clean-remediation.md](../../automation/docs/clean-remediation.md) first |

Related: [docs/clean-contract.json](../../docs/clean-contract.json), [docs/clean-publish-tier-matrix.md](../../docs/clean-publish-tier-matrix.md).
