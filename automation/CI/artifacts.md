# Artifacts — epic-work

## TeamCity rule

```
epics/%EPIC_KEY% => epic-work
```

Configure **publish artifacts even if build fails** so partial epic outputs remain available for debugging.

## Typical green-run contents

Exact file count depends on epic and agent behaviour; verified v1 success published **5 files** under `epic-work`:

| File | Description |
|------|-------------|
| `{EPIC}-ref.json` | EPIC-PREP handoff |
| `{EPIC}-coverage.json` | Coverage draft+truth |
| `{EPIC}-coverage.md` | Human Smart Checklist markdown |
| `{EPIC}-analysis.json` | ANALYSE output |
| `{EPIC}-analysis.md` | Analysis markdown |

GROUND mutates `runtime_probes` inside coverage JSON — no separate GROUND-only markdown at epic root in default chain.

## Download

From build overview → **Artifacts** tab → `epic-work/`.

**UI quirk:** artifact list may appear empty until page refresh even when log shows `Publishing N files`. Direct artifact download URL from build still works.

## Dispatch artifacts

Dispatch publishes:

```
dispatch-state/processed_comment_ids.txt => dispatch-state
```

Used for dedup across scheduled runs — not consumed by QA for deliverables.

## Security

Artifacts may contain epic summaries and check lists — treat as internal QA content. No credentials should appear in epic JSON; if leaked tokens appear in logs, rotate secrets and scrub build log access.
