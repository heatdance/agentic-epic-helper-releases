# crtqa-helper orchestrator

**Slash command:** `/crtqa-helper` · **Contract:** [`docs/crtqa-helper-contract.json`](../../docs/crtqa-helper-contract.json)

## Purpose

Resume-capable stage machine for one epic per chat: env probe → full pipeline chain with **three human gates**, **one automated stage per agent turn**.

## Operator UX

```text
/crtqa-helper CRT-1234          # bind epic; env + EPIC-PREP when env OK
/crtqa-helper resume            # next stage or clear gate
/crtqa-helper resume <comment>  # ingests to epics/<KEY>/helper/operator-feedback.md
```

## Scratch (gitignored)

`epics/<KEY>/helper/` — `session.json`, `operator-feedback.md`, `stage-log.jsonl`, `affordances-slice.json`. Archived to `epics/<KEY>/context/helper/` by [`close_archive.py`](../tools/close_archive.py) on **CLOSE:**.

## Tools

| Script | Role |
|--------|------|
| [`crtqa_env_probe.py`](../tools/crtqa_env_probe.py) | Env gate |
| [`crtqa_helper_affordances.py`](../tools/crtqa_helper_affordances.py) | Post-discover slice for **COVERAGE-REINFORCE:** |

## Verify

```powershell
powershell -NoProfile -File .cursor/scripts/corner-harness-verify.ps1 -Profile full
```

Maintainer golden: [`fixtures/operator-assist/crtqa-helper-golden.json`](../tools/fixtures/operator-assist/crtqa-helper-golden.json).
