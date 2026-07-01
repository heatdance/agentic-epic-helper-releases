# CLEAN publish tier matrix

Normative path → tier actions for **`CLEAN:`**. Machine-readable source: [clean-publish-tier-matrix.json](clean-publish-tier-matrix.json).

## Branch intent (operator-confirmed)

| Tier | Who | Goal |
|------|-----|------|
| **personal** | You only | Private backup: everything tracked except gitignore; **your** epics, handoff, **`releases/**` + `/release-notes`**, calibrate gold, stats, coaches, teach |
| **team** | Squad on **private** `agentic-epic-helper-team` | Runnable harness + **`/epic-helper`** + calibrate; **no** stats, coaches, teach, epics, release-notes, or publish flow |
| **public** | External readers | Guide-only **`*-readme.md`**; orchestrator + calibrate **conceptual** in HOW-TO only; **no** executable helper, stats, coaches, verifiers, org maps, or MCP recipes |

Policy fields: `tier_goals` and `team.org_maps_policy` in [clean-contract.json](clean-contract.json).

## Audiences

| Variant | Branch / remote | Entry docs |
|---------|-----------------|------------|
| **maintainer** | `personal` / `origin` | Live [README.md](../README.md), [HOW-TO.md](../HOW-TO.md), [AGENTS.md](../AGENTS.md) — includes three-repo table and `CLEAN:` |
| **contributor** | `team` / `team` | Generated from [clean-entry-templates/](clean-entry-templates/) — clone `team` branch; no `CLEAN:` / `/release-notes` / stats / coaches |
| **visitor** | `public-M.N` / `releases` | Guide-only; [clean_apply_public.py](../automation/tools/clean_apply_public.py) |

## Mind map (high level)

```text
personal (full)
├── epics/CRT-*              → deleted on team/public
├── qa-handoff.md            → deleted on team/public
├── releases/** + /release-notes → personal only
├── .cursor/calibrate/*-gold → deleted on team/public
├── clean.md                 → personal only
├── stats + coaches + teach  → personal only
├── /epic-helper (full)     → personal + team; conceptual on public HOW-TO only
└── org maps                 → keep on team; stubs on public

team (runnable harness)
├── templates + pipelines + verifiers + org maps + /epic-helper
├── calibrate command (no gold)
└── no stats / coaches / teach / release-notes

public (guide export)
├── *-readme.md only (+ coverage-reinforce-readme)
├── helper + calibrate described in HOW-TO (no commands shipped)
└── no verifiers / MCP setup / stats / coaches
```

## Grounding-kit adaptation (coaches + hooks)

Paths for operator discipline ([grounding-integration.json](grounding-integration.json)). JSON rules in [clean-publish-tier-matrix.json](clean-publish-tier-matrix.json).

| Path pattern | personal | team | public |
|--------------|----------|------|--------|
| `.cursor/commands/.md`, `.md` | keep | delete | delete |
| `/**`, `/**` | keep | delete | delete |
| `docs/.json`, `.json` | keep | delete | delete |
| `docs/epic-helper-contract.json`, `epic-helper` command/skill | keep | keep | delete |
| `automation/tools/epic_helper_affordances.py` | keep | keep | delete |
| `.cursor/hooks.json`, hooks scripts, `corner-harness-verify.ps1` | keep | keep | delete |

## Path rules (selected)

| Match | personal | team | public |
|-------|----------|------|--------|
| `releases/**` | keep | delete | delete |
| `/release-notes` command + contract + `release_notes.py` | keep | delete | delete |
| `stats/epic-stats/**` + epic-stats command/rollup | keep | delete | delete |
| `docs/project.json`, `qa-project.json`, `corner-platform-map.json` | keep | **keep** | example stubs only |

Phase **S1** merges this matrix with `git ls-files` into `automation/temp/clean/file-map.json`.
