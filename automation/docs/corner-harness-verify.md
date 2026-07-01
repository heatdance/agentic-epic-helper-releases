# corner-harness-verify

PowerShell hygiene check for Corner harness wiring. Run from repo root.

## Usage

```powershell
powershell -NoProfile -File .cursor/scripts/corner-harness-verify.ps1
powershell -NoProfile -File .cursor/scripts/corner-harness-verify.ps1 -Profile full
```

## Profiles

| Profile | Checks |
|---------|--------|
| **minimal** | jq present; corner rules; grounding-integration JSON; seven slash commands exist; removed commands/skills absent; epic-helper contract v5 + affordances; epic-stats contract paths; auto-tests contract + smoke specs |
| **full** | minimal + epic-helper golden; hooks sessionStart-only; inject-corner size/docClose; hook scripts |

Exit **0** when all checks pass; **1** with failed check names on stderr.
