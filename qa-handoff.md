# QA handoff — Corner Trader workspace

Last updated: 2026-07-28 (D19 derived truth beats declared numbers).

## Current focus

**D19:** breadth thresholds now come from the source, not from agent-declared fields. `parameter_inventory` is re-derived from `snippet_text` and unioned with the declared list (`parameter_inventory_undercut`); `requirement_passes[]` makes the mandatory EPIC-PREP step 3c fan-out checkable; `snippet_text` under 60% of attested `source_chars` fails; availability placement is exempted per check, not per ref; oracle detail lines must name their parameter and differ between variations.

**D18** stays in force (obligation = catalogue variation, `docs/variation-catalogue.json`, `variation_density` metrics) — D19 closes the loopholes that let build 46 pass with 9 field checks.

## Resume

- Push D19 on `_stash-team-merge` → `stash/team`, then re-run Pipeline CRT-635
- Confluence + Bitbucket PATs must still be set (D17)

## Next

1. Re-run CRT-635 and read the build statistics: `corner.mandated_variations` should rise well above the previous 8–9 once the full parameter tables are transcribed
2. If EPIC-PREP now fails on `parameter_inventory_undercut` or `snippet_truncated`, that is the gate working — the fix is a fuller transcription, not a lower threshold
3. Only if `mandated_variations` stays low with all gates green: raise `AGENT_MODEL` on the EPIC-PREP step (default `composer-2.5` in `run_pipeline_agent.py`)
4. Engineer extends the paste on CRTQA; repo `-coverage.md` stays machine-generated

## Known drift (not caused by D19)

Four documented fixture commands in `automation/tools/fixtures/coverage/README.md` fail at HEAD: the 594 topology example points at `epics/CRT-594/CRT-594-ref.json` (absent on this branch), two principal fixtures carry `## Primary focus` in the paste, and the 594 reinforce fixture misses `oracle_rule` mentions in `detail_lines`. Verified against a clean HEAD worktree before the D19 edits.

## Pointers

- D18 / D19: [automation/CI/decisions.md](automation/CI/decisions.md)
- Catalogue: [docs/variation-catalogue.json](docs/variation-catalogue.json)
- Fixtures: `crt635-target-good-*`, `crt635-skeleton-bad-*`, `crt635-undercut-bad-ref.json`, `crt677-watchlist-portability-ref.json`
