# CLEAN publish tier matrix

Normative path → tier actions for **`CLEAN:`**. Machine-readable source: [clean-publish-tier-matrix.json](clean-publish-tier-matrix.json).

## Branch intent (operator-confirmed)

| Tier | Who | Goal |
|------|-----|------|
| **personal** | You only | Private backup: everything tracked except gitignore; **your** epics, handoff, **`releases/**` + `/release-notes`** (maintainer Jira batches only), calibrate gold, **`latest.md`** |
| **team** | Squad on **private** `agentic-epic-helper-team` | **Shared team truth** in `project.json` / `qa-project.json` / `corner-platform-map.json`; full harness **works on clone** after tokens/creds; **no** your epics, release-notes, publish flow, or **your** stats report/state |
| **public** | External readers | Generalized methodology: same paths/names, neutral **`*-readme.md`**; **no** exact playbooks, verifiers, org maps, MCP setup, **`/crtqa-stats`**, or release-notes |

Policy fields: `tier_goals` and `team.org_maps_policy` in [clean-contract.json](clean-contract.json).

## Audiences

| Variant | Branch / remote | Entry docs |
|---------|-----------------|------------|
| **maintainer** | `personal` / `origin` | Live [README.md](../README.md), [HOW-TO.md](../HOW-TO.md), [AGENTS.md](../AGENTS.md) — includes three-repo table and `CLEAN:` |
| **contributor** | `team` / `team` | Generated from [clean-entry-templates/](clean-entry-templates/) — clone `team` branch; no `CLEAN:` / `/release-notes` |
| **visitor** | `public-M.N` / `releases` | Guide-only; [clean_apply_public.py](../automation/tools/clean_apply_public.py) |

## Mind map (high level)

```text
personal (full)
├── epics/CRT-*              → deleted on team/public
├── qa-handoff.md            → deleted on team/public
├── releases/** + /release-notes → personal only
├── .cursor/calibrate/*-gold → deleted on team/public
├── clean.md                 → personal only
├── org maps (project, qa-project, corner-platform-map) → keep on team; stubs on public
└── stats/crtqa-stats        → full on personal; toolkit on team (no latest/raw/state); gone on public

team (runnable harness)
├── templates + pipelines + verifiers + org maps
├── /crtqa-stats + rollup (empty state for each colleague)
└── calibrate command (no gold)

public (guide export)
├── *-readme.md only
├── no verifiers / no MCP commands tree / no stats / no release-notes
└── neutral README/HOW-TO/AGENTS
```

## Path rules (selected)

| Match | personal | team | public |
|-------|----------|------|--------|
| `releases/**` | keep | delete | delete |
| `/release-notes` command + contract + `release_notes.py` | keep | delete | delete |
| `docs/project.json`, `qa-project.json`, `corner-platform-map.json` | keep | **keep** | example stubs only |
| `stats/crtqa-stats/**` | keep | keep toolkit; drop `latest.md`, `raw/**`, `state/**` | delete |

Phase **S1** merges this matrix with `git ls-files` into `automation/temp/clean/file-map.json`.
