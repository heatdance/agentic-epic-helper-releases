# QA handoff — Corner Trader workspace

Last updated: 2026-07-29 (back on personal; /clean replaces CLEAN; team = Stash only).

## Current focus

**Branch truth:** work on **`personal`** only for latest harness. Stash **`team/team`** is intentionally not updated with these personal advances. GitHub team repo is gone; remote **`team`** points at Stash `AI/agentic-feature-helper`.

**Publish:** use slash **`/clean`** (not `CLEAN:` / `/clean-release`). Playbook still at `.cursor/pipelines/clean.md`.

**crtqa-console:** host shell (`Invoke-CrtqaHostShell.ps1`) + `docs/crtqa-console-contract.json` (`host_logs`) — WIP on personal, not pushed to team.

## Resume

- On branch **`personal`** (includes stash tip + maintainer layer + local WIP)
- Do **not** push personal tip to `team` until explicitly publishing via `/clean`

## Next

1. When ready to share with squad: `/clean scope=team` (or full) from personal — only then updates Stash team
2. CRT-677: authenticated rolling-transactions call
3. Optional: push `origin/personal` when ready (local is ahead of origin)

## Pointers

- `/clean`: [.cursor/commands/clean.md](.cursor/commands/clean.md)
- Console contract: [docs/crtqa-console-contract.json](docs/crtqa-console-contract.json)
- Remotes: `origin` (personal), `team` (Stash), `releases` (public)
