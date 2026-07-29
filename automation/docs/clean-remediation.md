# CLEAN one-time remediation

Use when a prior CLEAN run left **`clean/*`** on the team remote, **`release-*`** on releases, extra **worktrees**, or **`team/team`** out of sync with **`public-*`**.

Normative pipeline: [`.cursor/pipelines/clean.md`](../../.cursor/pipelines/clean.md). Contract: [`docs/clean-contract.json`](../../docs/clean-contract.json).

## Symptoms

| Symptom | Typical cause |
|---------|----------------|
| `git branch` shows `+ team` or `+ public-*` | Stale worktrees under `../cursor-corner-*-build` |
| `git ls-remote team` lists `clean/YYYYMMDD-*` | Old PR-based CLEAN Phase T |
| `team/team` SHA ≠ latest strip export | PR never merged; public built from worktree commit |
| `release-1.1.0` on releases | Legacy naming; U0 delete was best-effort only |
| Local `public-1.1` tracks `release-1.1.0` | Old clone; not removed by supersede of older `public-*` |
| MCP servers missing after full `/clean` | Phase U **`clean_apply_public`** deleted gitignored **`.cursor/mcp.json`** from the shared worktree (fixed: skip when `git check-ignore`) |

## Remediation steps (PowerShell)

Run from repo root on branch **`personal`**.

### 1. Remove worktrees

```powershell
git checkout personal
git worktree remove "c:\Media\Work\cursor-corner-team-build" --force 2>$null
git worktree remove "c:\Media\Work\cursor-corner-public-build" --force 2>$null
git worktree prune
python automation/tools/clean_verify.py --mode preflight
```

### 2. Team remote — single `team` branch

```powershell
python automation/tools/clean_verify.py --mode prune_team_remote
```

Or re-run corrected Phase T after `origin/personal` is current (see [clean.md](../../.cursor/pipelines/clean.md)).

### 3. Releases — legacy branches

```powershell
git fetch releases
python automation/tools/clean_public_supersede.py --legacy-only
python automation/tools/clean_verify.py --mode legacy_remote
```

### 4. Local branch cleanup

```powershell
git checkout personal
git branch -D team public-1.1 public-1.3 clean-team-test 2>$null
```

### 5. Restore operator MCP (after public Phase U)

```powershell
# Project-local (postgres-ctqa, chrome-devtools)
Copy-Item .cursor\mcp.json.example .cursor\mcp.json -Force
# Edit .cursor\mcp.json: set postgres USER/PASSWORD; reload Cursor MCP.

# Atlassian / Figma: merge from team template into global mcp.json (placeholders → your PATs)
# Copy-Item .cursor\mcp.json.team.example $env:USERPROFILE\.cursor\mcp.json -Force  # then edit — do not commit
```

### 6. Acceptance

```powershell
git branch
git ls-remote --heads team
git ls-remote --heads releases
```

Then run **`/clean proceed`** and confirm **`postflight`** OK.
