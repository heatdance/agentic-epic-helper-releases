# corner-harness-verify

Structural checks for **grounding-kit adaptation** (coaches, corner rules, hooks, inject snapshot). **Does not** replace epic pipeline verifiers.

Playbook charter: [docs/grounding-integration.json](../../docs/grounding-integration.json). Operator hooks: [HOW-TO.md](../../HOW-TO.md) (workspace hooks blurb).

## When to run

| When | Profile |
|------|---------|
| After changing coaches, `inject-corner`, hooks, or corner rules | `full` |
| Quick check after editing contract JSON only | `minimal` |
| Pass 0 regression block | `full` (with Python verifiers listed in charter) |

## CLI

From repo root (PowerShell):

```powershell
powershell -NoProfile -File .cursor/scripts/corner-harness-verify.ps1 -Profile minimal
powershell -NoProfile -File .cursor/scripts/corner-harness-verify.ps1 -Profile full
```

Requires **`jq`** on PATH for contract and golden checks (see [jq.md](jq.md)).

## Profiles

| Profile | Checks |
|---------|--------|
| **minimal** | jq present; coach contract versions; coach commands/skills exist; four corner rules; `grounding-integration.json`; `skill-authoring-patterns.json`; karpathy skill + contract; **crtqa-helper** contract v1 + command/skill + `coverage-reinforce.md` + affordances tool; teach command/skill + `auto-tests-contract.json`; `auto-tests/specs/schema.json` + `smoke-manifest.json` (32 rows) |
| **full** | minimal + coach/teach/**crtqa-helper** golden JSON + `examples.md` + `refresh-inject-corner.ps1` + hooks sessionStart-only + inject size/docClose/ASCII + hook scripts |

## Not in scope

- `epic_prep_verify.py`, `coverage_verify.py`, etc. — run those per pipeline or [grounding-integration.json](../../docs/grounding-integration.json) `regression_commands[]`
- Machine `docClose.pending` detection (static false by design)

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | All checks for the profile passed |
| 1 | One or more checks failed (names printed) |
