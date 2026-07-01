# CLEAN verifier (`clean_verify.py`)

Normative contract: [docs/clean-contract.json](../../docs/clean-contract.json) (schema v3). Playbook: [`.cursor/pipelines/clean.md`](../../.cursor/pipelines/clean.md). Remediation: [clean-remediation.md](clean-remediation.md). Tier matrix: [docs/clean-publish-tier-matrix.json](../../docs/clean-publish-tier-matrix.json).

## Modes

| Mode | Purpose |
|------|---------|
| `preflight` | On **`personal`**; remotes configured; **no extra worktrees** |
| `secret_scan` | Forbidden paths and secret-like strings before personal commit |
| `semver_next` | Next public branch; `--json` → `target_branch`, `superseded_branch`, `export_version` |
| `file_map` | Validate `automation/temp/clean/file-map.json` |
| `align` | Personal harness: router `CLEAN:`, harness-map, HOW-TO, no stale scrub/sync |
| `team` | Team tree strip checks on `--root` (usually `.` while on `team` branch) |
| `team_tip` | `--sha <TEAM_SHA>` matches `team/team` (gate before Phase U) |
| `prune_team_remote` | Delete all heads on `team` remote except `team` |
| `public` | Sterilization + blocklist + **forbidden stack patterns** + **no MCP example files** + **readme depth** (sections + entry docs) |
| `public_remote` | After U4b: `--superseded public-M.N` absent on `releases` |
| `legacy_remote` | No `release-*` (or listed legacy names) on `releases` |
| `postflight` | On **`personal`**; no worktrees; branch policy on remotes; `legacy_remote` |

## Examples

```bash
python automation/tools/clean_verify.py --mode preflight
python automation/tools/clean_verify.py --mode semver_next --json
python automation/tools/clean_verify.py --mode align
python automation/tools/clean_stats_personal.py backup
git checkout team
python automation/tools/clean_verify.py --mode team --root .
git push team team
python automation/tools/clean_verify.py --mode prune_team_remote
python automation/tools/clean_verify.py --mode team_tip --sha "$(git rev-parse HEAD)"
git checkout personal
python automation/tools/clean_stats_personal.py restore
python automation/tools/clean_verify.py --mode legacy_remote
python automation/tools/clean_verify.py --mode postflight
```

## Helpers

| Script | Role |
|--------|------|
| `clean_file_map.py` | S1 inventory from tier matrix + `git ls-files` |
| `clean_apply_team.py` | Team strip + `clean_apply_t1_docs --tier team` |
| `clean_stats_personal.py` | Phase T guard: backup/restore gitignored `stats/epic-stats/{state,raw,latest-*}` on **`personal`** |
| `clean_apply_t1_docs.py` | Render contributor T1 from `docs/clean-entry-templates/` |
| `clean_apply_public.py` | Public sterilize; seeds [`docs/clean-public-content/`](../../docs/clean-public-content/); template overlays from `epics/templates/public/` |
| `clean_public_supersede.py` | U4b delete superseded `public-*`, `--legacy-only` for `release-*` |

Exit **0** = pass; **1** = fail (playbook retries or aborts).

## Style guide

Public Phase U prose: [docs/clean-public-style.md](../../docs/clean-public-style.md).
