# CLEAN publish tier matrix

Normative path → tier actions for **`CLEAN:`**. Machine-readable source: [clean-publish-tier-matrix.json](clean-publish-tier-matrix.json).

## Audiences

| Variant | Branch / remote | Entry docs |
|---------|-----------------|------------|
| **maintainer** | `personal` / `origin` | Live [README.md](../README.md), [HOW-TO.md](../HOW-TO.md), [AGENTS.md](../AGENTS.md) — includes three-repo table and `CLEAN:` |
| **contributor** | `team` / `team` | Generated from [clean-entry-templates/](clean-entry-templates/) — clone `team` branch; no `CLEAN:` / publish vocabulary |
| **visitor** | `public-M.N` / `releases` | Guide-only; [clean_apply_public.py](../automation/tools/clean_apply_public.py) |

## Mind map (high level)

```text
personal (full)
├── epics/CRT-*          → deleted on team/public
├── qa-handoff.md        → deleted on team/public
├── .cursor/calibrate/*-gold → deleted on team/public
├── clean.md             → personal only
└── T1 docs              → rewrite on team/public (not copy)

team (runnable harness)
├── templates + pipelines + verifiers
├── calibrate command (no gold)
└── example JSON for org maps

public (guide export)
├── *-readme.md only
├── no verifiers / no MCP commands tree
└── neutral README/HOW-TO/AGENTS
```

Phase **S1** merges this matrix with `git ls-files` into `automation/temp/clean/file-map.json`.
