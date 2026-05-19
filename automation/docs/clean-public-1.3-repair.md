# Corrective plan — public-1.3 republish (no semver bump)

**Status:** Executed 2026-05-19. Remote: `releases/public-1.3` @ `c656ade`.

## Faults addressed

| # | Fault | Fix applied |
|---|--------|-------------|
| 1 | `.cursor/mcp.json.example` with `postgres-ctqa` / DB `ctqa` | File **deleted** on public tree |
| 2 | `discover-ref.json` CTQA field names and automation doc paths | **Neutralized** (`postgres_readonly`, `remote_admin_shell`, placeholder doc paths) |
| 3 | Thin guide prose (1–2 sentences per section) | **Expanded** README, HOW-TO, AGENTS, all `*-readme.md` per [clean-public-style.md](../../docs/clean-public-style.md) |
| 4 | `tests-ref.json` employer-specific format_norms | **Generalized** to `executable_outline` profile |

## Republish procedure (for future same-semver fixes)

1. `git checkout -B public-1.3 releases/public-1.3`
2. Apply edits; confirm no tracked `ctqa` / `postgres-ctqa` / `mcp.json.example`
3. `git commit` · `git push releases public-1.3:public-1.3` (no `semver_next` increment)
4. `git checkout personal`

## Verification

```powershell
git ls-remote releases public-1.3
git ls-tree -r releases/public-1.3 --name-only | Select-String mcp
# expect empty
```
