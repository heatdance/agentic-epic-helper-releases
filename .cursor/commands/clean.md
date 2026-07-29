---
description: Publish harness from personal to Stash team and the next public-* release (maintainer only).
---

# /clean

Run the publish playbook from branch **`personal`**. Playbook: [`.cursor/pipelines/clean.md`](../pipelines/clean.md). Contract: [`docs/clean-contract.json`](../../docs/clean-contract.json).

## Agent action

1. Confirm **`git branch --show-current`** is **`personal`**. If not, **stop**.
2. Preflight: `python automation/tools/clean_verify.py --mode preflight`
3. Run full playbook for **`/clean`** (optional tokens: `scope=align|personal|team|public|full`, `confirm_major=yes`, `proceed` on dirty tree).

## Remotes (three lines)

| Tier | Remote | Branch | Repo |
|------|--------|--------|------|
| Personal | `origin` | `personal` | GitHub `agentic-epic-helper` |
| Team | `team` | `team` | Stash `AI/agentic-feature-helper` |
| Public | `releases` | `public-M.N` | GitHub `agentic-epic-helper-releases` |

## Human gates

| Gate | Operator |
|------|----------|
| Dirty tree | Add **`proceed`** |
| Major public bump | Add **`confirm_major=yes`** |
| Bad prior publish | [automation/docs/clean-remediation.md](../../automation/docs/clean-remediation.md) first |

Related: [docs/clean-publish-tier-matrix.md](../../docs/clean-publish-tier-matrix.md).
