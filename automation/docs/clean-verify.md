# CLEAN verifier (`clean_verify.py`)

Normative contract: [docs/clean-contract.json](../../docs/clean-contract.json). Playbook: [`.cursor/pipelines/clean.md`](../../.cursor/pipelines/clean.md). Tier matrix: [docs/clean-publish-tier-matrix.json](../../docs/clean-publish-tier-matrix.json).

## Modes

| Mode | Purpose |
|------|---------|
| `preflight` | On **`personal`**; remotes `origin`, `team`, `releases` configured |
| `secret_scan` | Forbidden paths and secret-like strings before personal commit |
| `semver_next` | Next public branch; `--json` → `target_branch`, `superseded_branch`, `export_version` |
| `file_map` | Validate `automation/temp/clean/file-map.json` (schema v2 + matrix ref) |
| `align` | Personal harness: router `CLEAN:`, harness-map, HOW-TO, no stale scrub/sync |
| `team` | Team worktree: no CLEAN, no personal/releases URLs, no calibrate gold, T1 contributor docs |
| `public` | Public sterilization + blocklist on worktree root |
| `public_remote` | After U4b: `--superseded public-M.N` must be absent on `releases` |

## Examples

```bash
python automation/tools/clean_verify.py --mode preflight
python automation/tools/clean_verify.py --mode semver_next --json
python automation/tools/clean_verify.py --mode semver_next --version 1.2
python automation/tools/clean_verify.py --mode align
python automation/tools/clean_verify.py --mode team --root ../cursor-corner-team-build
python automation/tools/clean_verify.py --mode public --root ../cursor-corner-public-build
python automation/tools/clean_verify.py --mode public_remote --superseded public-1.1
python automation/tools/clean_verify.py --mode file_map --map automation/temp/clean/file-map.json
```

## Helpers

| Script | Role |
|--------|------|
| `clean_file_map.py` | S1 inventory from tier matrix + `git ls-files` |
| `clean_apply_team.py` | Team strip + `clean_apply_t1_docs --tier team` |
| `clean_apply_t1_docs.py` | Render contributor T1 from `docs/clean-entry-templates/` |
| `clean_apply_public.py` | Public sterilize + neutral T1 |
| `clean_public_supersede.py` | U4b delete previous `public-*` on releases + local |

Exit **0** = pass; **1** = fail (playbook retries or aborts).

## Style guide

Public Phase U prose: [docs/clean-public-style.md](../../docs/clean-public-style.md).
