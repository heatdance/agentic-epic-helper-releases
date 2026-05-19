# Corner Trader — QA workspace

Devexperts QA working area for **Corner Trader**: templates, automation docs, and a Cursor harness for agent-assisted work (this repo is not necessarily the application source tree).

## Branches

Three tiers: **personal** (full workspace), **team** (shareable private harness without personal data), **public-*** (scrubbed knowledge export). Tier matrix: [docs/clean-publish-tier-matrix.md](docs/clean-publish-tier-matrix.md).

| Branch | Remote | Role |
|--------|--------|------|
| **`personal`** | [agentic-epic-helper](https://github.com/heatdance/agentic-epic-helper) (`origin`) | **Personal production** — day-to-day work: epics, stats, calibrate gold, temp, and harness changes. Commit and push here first. |
| **`team`** | [agentic-epic-helper-team](https://github.com/heatdance/agentic-epic-helper-team) (`team`) | **Team private share** — runnable harness without personal epics, stats corpus, or scratch. Updated via **`CLEAN:`** (direct push to `team/team` from `personal`). |
| **`public-M.N`** (e.g. `public-1.2`) | [agentic-epic-helper-releases](https://github.com/heatdance/agentic-epic-helper-releases) (`releases`) | **Public guide export** — methodology and template shapes only. Updated only via **`CLEAN:`** from **`personal`**. |

**Checkout (personal):** `git fetch origin && git checkout personal` (tracks `origin/personal`).

## Start here

| Who | First reads |
|-----|-------------|
| **Humans** | [qa-handoff.md](qa-handoff.md) (session focus), [HOW-TO.md](HOW-TO.md) (pipelines, stats, calibrate; CTQA prep: tunnel [README](automation/tools/tunnel/README.md), **`/crtqa-console`**, **`/crtqa-env`**; **jq** on PATH: [automation/docs/jq.md](automation/docs/jq.md)) |
| **AI agents** | [AGENTS.md](AGENTS.md) (map + MCP policy), [docs/harness-principles.md](docs/harness-principles.md) (harness doctrine for pipelines & calibrate), [docs/harness-map.json](docs/harness-map.json) (keyword → which files to open; tiers T0–T2) |

## Satellite / planned

- [corner-map/README.md](corner-map/README.md) — seed spec for a future **Phase 5 change-map** repo (workflow, diagrams in [corner-map/docs/architecture.md](corner-map/docs/architecture.md)); intended to move to its own workspace.

## Product and QA context (JSON)

- [docs/project.json](docs/project.json) — product / **fork-of DXtrade XT** Confluence anchors (CT / XT), Bitbucket defaults.
- [docs/qa-project.json](docs/qa-project.json) — Corner QA scope (QAPORTAL Corner subtree), workflow pointers (functional summaries only).
- [docs/corner-platform-map.json](docs/corner-platform-map.json) — **SoT** for environment hostnames/paths, Jira project/dashboard links, Stash repo ladder, QAPORTAL child index (no secrets in repo).
- [docs/mcp-atlassian-tools.md](docs/mcp-atlassian-tools.md) — **`user-mcp-atlassian`** tool surface (read-only), Stash **browse-first** ladder, where server debugging lives (outside this repo).
- [docs/harness-principles.md](docs/harness-principles.md) — **Harness doctrine** (production generation vs operator calibrate, coverage vs E2E tests, reference ownership).
- [docs/dxcore-console-harness.json](docs/dxcore-console-harness.json) — **dxCore console** agent map (tiers, forks, Confluence trust; harness-map package **`dxcore_console`**).
- [docs/dxtrade5-harness/README.md](docs/dxtrade5-harness/README.md) — **dxTrade5 web UI** three-stage map (concept → IA → locations; harness-map package **`dxtrade5_harness`**). Stage 3 parity: `python automation/tools/dxtrade5-harness/check_locations_parity.py`.

## Pipelines (chat triggers)

All playbooks: [.cursor/pipelines/](.cursor/pipelines/)

| Trigger | Playbook |
|---------|----------|
| `EPIC-PREP:` + Epic key | [epic-prep.md](.cursor/pipelines/epic-prep.md) — v4 obligations; [epic-prep-verify.md](automation/docs/epic-prep-verify.md) |
| `COVERAGE:` + Epic key | [coverage.md](.cursor/pipelines/coverage.md) — v2 obligations_coverage; [coverage-verify.md](automation/docs/coverage-verify.md) |
| `ANALYSE:` + Epic key | [analysis.md](.cursor/pipelines/analysis.md) v2 — requires coverage; [analysis-verify.md](automation/docs/analysis-verify.md) |
| `TEST-DISCOVER:` + Epic key | [test-discover.md](.cursor/pipelines/test-discover.md) — schema v3 **`fixture_needs`**; CRTQA index opt-in (`crtqa_index=yes`); [discover_verify.py](automation/tools/discover_verify.py); may end **`incomplete`** when setup depth insufficient |
| `TEST-PRECON:` + Epic key | [test-precon.md](.cursor/pipelines/test-precon.md) v5 — [exploration-depth-ladder.json](docs/exploration-depth-ladder.json); Phase 4R/4D/4C; [precon_verify.py](automation/tools/precon_verify.py) `--discover` |
| `TEST-PREP:` + Epic key | [test-prep.md](.cursor/pipelines/test-prep.md) — v3 executable outlines (default); [test-prep-draft-profiles.json](docs/test-prep-draft-profiles.json) |
| `/crtqa-calibrate` | [crtqa-calibrate.md](.cursor/commands/crtqa-calibrate.md) — prod vs gold; [calibrate.md](.cursor/pipelines/calibrate.md); gold under [.cursor/calibrate/](.cursor/calibrate/README.md) |
| `CLOSE:` + Epic key | [close.md](.cursor/pipelines/close.md) — optional; documentation integrity ladder + archive to `context/`; **no** MCP |
| `CLEAN:` | [clean.md](.cursor/pipelines/clean.md) — optional `scope=full` \| `align` \| `personal` \| `team` \| `public`; `version=M.N`; **`personal` branch only** — align harness, push personal, publish team + public ([clean-verify.md](automation/docs/clean-verify.md)) |

Router: [.cursor/rules/pipeline-router.mdc](.cursor/rules/pipeline-router.mdc).

**Public export**: [docs/public-export-manifest.example.json](docs/public-export-manifest.example.json) (example on `personal`/`team`; live manifest on **`public-*`** after **`CLEAN:`**).

## Stats (CRTQA TCD)

Measure ROI of the agentic epic helper on done **Test Case Development** work: **manual corpus** vs **AI-assisted comparison**, sized by **draft estimate hours** (not Jira Story Points).

- Operator steps: [HOW-TO.md §1](HOW-TO.md) (modes, read order for `latest.md`).
- Summary: [stats/crtqa-stats/README.md](stats/crtqa-stats/README.md) — **`/crtqa-stats`** playbook [crtqa-stats.md](.cursor/commands/crtqa-stats.md); rollup [crtqa_stats_rollup.py](automation/tools/crtqa_stats_rollup.py) + [automation/docs/crtqa-stats.md](automation/docs/crtqa-stats.md).
- Output: committed [`stats/crtqa-stats/latest.md`](stats/crtqa-stats/latest.md); state under `stats/crtqa-stats/state/` (gitignored).

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
