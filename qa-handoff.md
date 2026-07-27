# QA handoff — Corner Trader workspace

Last updated: 2026-07-27 (D18 variation-based coverage).

## Current focus

**D18:** obligation = catalogue variation (not spec paraphrase); `parameter_inventory` + `docs/variation-catalogue.json`; page_id via `confluence_search`; GROUND probes setup checks; `variation_density` in verifier/TeamCity stats.

## Resume

- Implement/push D18 on `_stash-team-merge` → `stash/team`
- Operator: re-run CRT-635 after push; confirm Confluence+Bitbucket PATs still set (D17)

## Next

1. Push D18; re-run Pipeline CRT-635
2. Expect: ok snippets for CB keys via search, variation_density in logs, field variations with `>` oracle lines
3. Engineer extends paste on CRTQA (repo md remains machine)

## Pointers

- D18: [automation/CI/decisions.md](automation/CI/decisions.md)
- Catalogue: [docs/variation-catalogue.json](docs/variation-catalogue.json)
- Fixtures: `crt635-target-good-*`, `crt635-skeleton-bad-*`, `crt677-watchlist-portability-ref.json`
