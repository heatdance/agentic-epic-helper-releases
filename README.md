# Corner Trader — QA workspace

Devexperts QA working area for **Corner Trader**: templates, automation docs, and a Cursor harness for agent-assisted work (this repo is not necessarily the application source tree).

## Branches (GitHub: [agentic-epic-helper](https://github.com/heatdance/agentic-epic-helper))

| Branch | Role |
|--------|------|
| **`main`** | **Default** on GitHub — **stable** snapshots. Merge from `develop` (e.g. via PR) when a harness change set is ready to publish. |
| **`develop`** | Integration branch for **new work**; commit and push here first, then promote to `main` when stable. |
| **`release`** | **Public export** line: sanitized tree + semver manifest ([`docs/public-export-manifest.json`](docs/public-export-manifest.json), not on `main`/`develop`). Updated only via agent playbook [`PUBLIC-SCRUB:`](.cursor/pipelines/public-scrub.md) while checked out on **`release`** — do not commit scrub results on `main` or `develop`. First-time: `git fetch origin && git checkout -b release origin/develop` (see playbook). |

## Start here

| Who | First reads |
|-----|-------------|
| **Humans** | [qa-handoff.md](qa-handoff.md) (session focus), [HOW-TO.md](HOW-TO.md) (pipelines, stats, benchmark; CTQA prep: tunnel [README](automation/tools/tunnel/README.md), **`/crtqa-console`**, **`/crtqa-env`**; **jq** on PATH: [automation/docs/jq.md](automation/docs/jq.md)) |
| **AI agents** | [AGENTS.md](AGENTS.md) (map + MCP policy), [docs/harness-principles.md](docs/harness-principles.md) (harness doctrine for pipelines & benchmark), [docs/harness-map.json](docs/harness-map.json) (keyword → which files to open; tiers T0–T2) |

## Satellite / planned

- [corner-map/README.md](corner-map/README.md) — seed spec for a future **Phase 5 change-map** repo (workflow, diagrams in [corner-map/docs/architecture.md](corner-map/docs/architecture.md)); intended to move to its own workspace.

## Product and QA context (JSON)

- [docs/project.json](docs/project.json) — product / **fork-of DXtrade XT** Confluence anchors (CT / XT), Bitbucket defaults.
- [docs/qa-project.json](docs/qa-project.json) — Corner QA scope (QAPORTAL Corner subtree), workflow pointers (functional summaries only).
- [docs/corner-platform-map.json](docs/corner-platform-map.json) — **SoT** for environment hostnames/paths, Jira project/dashboard links, Stash repo ladder, QAPORTAL child index (no secrets in repo).
- [docs/mcp-atlassian-tools.md](docs/mcp-atlassian-tools.md) — **`user-mcp-atlassian`** tool surface (read-only), Stash **browse-first** ladder, where server debugging lives (outside this repo).
- [docs/harness-principles.md](docs/harness-principles.md) — **Harness doctrine** (generation vs benchmark, coverage vs E2E tests, reference ownership).
- [docs/dxcore-console-harness.json](docs/dxcore-console-harness.json) — **dxCore console** agent map (tiers, forks, Confluence trust; harness-map package **`dxcore_console`**).
- [docs/dxtrade5-harness/README.md](docs/dxtrade5-harness/README.md) — **dxTrade5 web UI** three-stage map (concept → IA → locations; harness-map package **`dxtrade5_harness`**). Stage 3 parity: `python automation/tools/dxtrade5-harness/check_locations_parity.py`.

## Pipelines (chat triggers)

All playbooks: [.cursor/pipelines/](.cursor/pipelines/)

| Trigger | Playbook |
|---------|----------|
| `EPIC-PREP:` + Epic key | [epic-prep.md](.cursor/pipelines/epic-prep.md) — v4 obligations; [epic-prep-verify.md](automation/docs/epic-prep-verify.md) |
| `COVERAGE:` + Epic key | [coverage.md](.cursor/pipelines/coverage.md) — v2 obligations_coverage; [coverage-verify.md](automation/docs/coverage-verify.md) |
| `ANALYSE:` + Epic key | [analysis.md](.cursor/pipelines/analysis.md) v2 — requires coverage; [analysis-verify.md](automation/docs/analysis-verify.md) |
| `TEST-DISCOVER:` + Epic key | [test-discover.md](.cursor/pipelines/test-discover.md) — schema v3 **`fixture_needs`**; CRTQA index opt-in (`crtqa_index=yes` or benchmark); [discover_verify.py](automation/tools/discover_verify.py); may end **`incomplete`** when setup depth insufficient |
| `TEST-PRECON:` + Epic key | [test-precon.md](.cursor/pipelines/test-precon.md) v5 — [exploration-depth-ladder.json](docs/exploration-depth-ladder.json); Phase 4R/4D/4C; [precon_verify.py](automation/tools/precon_verify.py) `--discover` |
| `TEST-PREP:` + Epic key | [test-prep.md](.cursor/pipelines/test-prep.md) — v3 executable outlines (default); `shape_ref=benchmark` benchmark-only; [test-prep-draft-profiles.json](docs/test-prep-draft-profiles.json) |
| `CLOSE:` + Epic key | [close.md](.cursor/pipelines/close.md) — optional; documentation integrity ladder + archive to `context/`; **no** MCP |
| `PUBLIC-SCRUB:` | [public-scrub.md](.cursor/pipelines/public-scrub.md) — optional `version=X.Y.Z`, `source=develop` or `source=main`; **checkout `release` first**; produces public-safe tree + manifest + [`.agents/`](https://dotagentsprotocol.com/) on **`release` only** |
| `SYNC:` | [sync.md](.cursor/pipelines/sync.md) — optional `scope=full` (default) or `pipelines` / `prompts` / `templates` / `tools` / `mcp`; **develop** or **`main`** only — reconciles router, harness-map, rules, prompts, templates, tool docs, postgres-ctqa MCP story (snippet in [automation/tools/tunnel/README.md](automation/tools/tunnel/README.md)), AGENTS, README, [HOW-TO.md](HOW-TO.md), qa-artifacts (not for **`release`**) |

Router: [.cursor/rules/pipeline-router.mdc](.cursor/rules/pipeline-router.mdc).

**Public export**: Manifest field reference for automation — [docs/public-export-manifest.example.json](docs/public-export-manifest.example.json) (example on internal branches; live `docs/public-export-manifest.json` exists only on **`release`** after a scrub run).

## Stats (CRTQA TCD)

- [stats/crtqa-stats/README.md](stats/crtqa-stats/README.md) — **`/crtqa-stats`**: manual **corpus** baseline vs **AI-assisted comparison**, category + SP strata, **% saved** when corpus n≥4; [`crtqa_stats_rollup.py`](automation/tools/crtqa_stats_rollup.py).

## Epics and templates

- Layout and workflow: [epics/README.md](epics/README.md).
- Schemas: [epics/templates/](epics/templates/) (`epic-ref.json`, `coverage-ref.json`, `analysis-ref.json`, `tests-ref.json`, `close-ref.json`).
- Per-Epic artifacts live under `epics/<KEY>/`.

## Automation

- Tool docs: [automation/docs/](automation/docs/) (e.g. [yogi-url-resolve.md](automation/docs/yogi-url-resolve.md), [jq.md](automation/docs/jq.md), [figma-mcp.md](automation/docs/figma-mcp.md), [chrome-devtools-mcp.md](automation/docs/chrome-devtools-mcp.md)).
- Runnable tools: [automation/tools/](automation/tools/) — **CTQA Postgres SSH tunnel / probe**: [automation/tools/tunnel/README.md](automation/tools/tunnel/README.md) (`ctqa_pg.py`, PuTTY plink default on Windows).
- Scratch: [automation/temp/](automation/temp/) (short-lived; see [automation/temp/README.md](automation/temp/README.md)).

## Rules, prompts, MCP config

- Rules: [.cursor/rules/](.cursor/rules/).
- Prompt scaffolds: [.cursor/prompts/](.cursor/prompts/) (e.g. [corner-adhoc-qa.md](.cursor/prompts/corner-adhoc-qa.md) for ad-hoc ticket/incident Q&A).
- Optional MCP: **`postgres-ctqa`** — snippet in [automation/tools/tunnel/README.md](automation/tools/tunnel/README.md) (*MCP — PostgreSQL*); **`chrome-devtools`** (ad-hoc UI / discover-precon-prep) — [automation/docs/chrome-devtools-mcp.md](automation/docs/chrome-devtools-mcp.md). Merge into **gitignored** `.cursor/mcp.json` and/or **global** `~/.cursor/mcp.json` (Windows: `%USERPROFILE%\.cursor\mcp.json`); template **[`.cursor/mcp.json.example`](.cursor/mcp.json.example)**; SSH tunnel + local URI for Postgres; no secrets in git.

## Reference docs

- Test case draft format: [epics/templates/tests-ref.json](epics/templates/tests-ref.json) (**format_norms**); workflow [test-prep.md](.cursor/pipelines/test-prep.md).
- Defect report format: [docs/dr-ref](docs/dr-ref).

Template references under [docs/](docs/). Automation under [automation/](automation/).
