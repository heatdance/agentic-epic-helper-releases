# CLEAN verifier (`clean_verify.py`)

Normative contract: [docs/clean-contract.json](../../docs/clean-contract.json). Playbook: [`.cursor/pipelines/clean.md`](../../.cursor/pipelines/clean.md).

## Modes

| Mode | Purpose |
|------|---------|
| `preflight` | On **`personal`**; remotes `origin`, `team`, `releases` configured |
| `secret_scan` | Forbidden paths and secret-like strings before personal commit |
| `semver_next` | Print next public branch (e.g. `public-1.2`); `--version M.N` override; `--confirm-major yes` after `public-M.9` |
| `file_map` | Validate `automation/temp/clean/file-map.json` |
| `align` | Router, harness-map, HOW-TO, no stale PUBLIC-SCRUB/SYNC; `clean.md` present |
| `team` | Team strip rules on worktree root (`--root`) |
| `public` | Public sterilization + blocklist `rg` on worktree root |

## Examples

```bash
python automation/tools/clean_verify.py --mode preflight
python automation/tools/clean_verify.py --mode semver_next
python automation/tools/clean_verify.py --mode align
python automation/tools/clean_verify.py --mode team --root ../cursor-corner-team-build
python automation/tools/clean_verify.py --mode public --root ../cursor-corner-public-build
python automation/tools/clean_verify.py --mode file_map --map automation/temp/clean/file-map.json
```

Exit **0** = pass; **1** = fail (playbook retries or aborts).

## Style guide

Public Phase U prose: [docs/clean-public-style.md](../../docs/clean-public-style.md).
