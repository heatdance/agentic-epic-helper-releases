# AGENTS.md — Corner Trader QA workspace

Short map for coding agents. **Do not** treat this file as the full spec; follow links (**progressive disclosure**). Prose here is **functional/process only**—no people rosters (see [docs/project.json](docs/project.json) `content_policy`).

## Project

Devexperts — **Corner Trader**. This repository is a **QA workspace**: templates, harness, automation docs, and session continuity—not necessarily the application source tree. Product vs upstream relationship and Confluence anchors: **[docs/project.json](docs/project.json)** (Corner **CT** space; fork base **DXtrade XT** in **XT** space).

## Where things live

### Canonical JSON

| Area | Path |
|------|------|
| Product / fork context (Confluence-backed) | [docs/project.json](docs/project.json) |
| Corner QA scope, envs, Jira mapping (Confluence-backed) | [docs/qa-project.json](docs/qa-project.json) |
| Environments, code streams (Stash), Jira index, Confluence index (MCP-backed) | [docs/corner-platform-map.json](docs/corner-platform-map.json) |
| Atlassian MCP — tool list, safety ladder, Stash search vs browse | [docs/mcp-atlassian-tools.md](docs/mcp-atlassian-tools.md) |
| Tiered context escalation (keywords → which files to read) | [docs/harness-map.json](docs/harness-map.json) |
| **dxCore console** agent map (truth tiers + forks + Confluence trust; T1 **`dxcore_console`**) | [docs/dxcore-console-harness.json](docs/dxcore-console-harness.json) |
| **dxTrade5 web UI** agent map (concept → IA → locations; T1 **`dxtrade5_harness`**) | [docs/dxtrade5-harness/](docs/dxtrade5-harness/) — [README](docs/dxtrade5-harness/README.md), [dxtrade5-harness.json](docs/dxtrade5-harness/dxtrade5-harness.json), [concept-map.json](docs/dxtrade5-harness/concept-map.json) |
| **WebBroker dealer web UI** agent map (concept → IA → locations; T1 **`webbroker_harness`**) | [docs/webbroker-harness/](docs/webbroker-harness/) — [README](docs/webbroker-harness/README.md), [webbroker-harness.json](docs/webbroker-harness/webbroker-harness.json), [concept-map.json](docs/webbroker-harness/concept-map.json) |
| **Epic artifact layout** (pre-CLOSE: `dependencies/` + root `-coverage.md`) | [docs/epic-artifact-layout.json](docs/epic-artifact-layout.json) · resolver [automation/tools/epic_paths.py](automation/tools/epic_paths.py) |
| **Grounding integration** (shipped core, regression gate) | [docs/grounding-integration.json](docs/grounding-integration.json) · verify `powershell -File .cursor/scripts/corner-harness-verify.ps1` |
| **Delivery smoke automation** (pytest + Playwright; not `automation/`) | [auto-tests/](auto-tests/) · [docs/auto-tests-contract.json](docs/auto-tests-contract.json) |
| **Epic orchestrator** (`/epic-helper`, one stage per turn) | [docs/epic-helper-contract.json](docs/epic-helper-contract.json) (**v7**) · [epic-helper.md](.cursor/commands/epic-helper.md) · [automation/docs/epic-helper.md](automation/docs/epic-helper.md) |
| **CLEAN publish tier matrix** (personal / team / public path actions) | [docs/clean-publish-tier-matrix.md](docs/clean-publish-tier-matrix.md) |
| **Calibrate contract** (operator gold vs prod) | [docs/calibrate-contract.json](docs/calibrate-contract.json) |
| **Corner release notes** (six PMOPROC JQLs per fixVersion, three lanes; **personal-only** `releases/**`) | [releases/README.md](releases/README.md) · [docs/release-notes-contract.json](docs/release-notes-contract.json) · **`/release-notes`** [release-notes.md](.cursor/commands/release-notes.md) · [release_notes.py](automation/tools/release_notes.py) |
| Public export manifest (example; live file on `public-*` only) | [docs/public-export-manifest.example.json](docs/public-export-manifest.example.json) |

### Deliverables and references

| Area | Path |
|------|------|
| Jira Smart Checklist norms + COVERAGE playbook | [`.cursor/pipelines/coverage.md`](.cursor/pipelines/coverage.md) (*Smart Checklist markdown*) |
| Test case draft format (norms + schema template) | [epics/templates/tests-ref.json](epics/templates/tests-ref.json) (**format_norms**); pipeline [`.cursor/pipelines/test-prep.md`](.cursor/pipelines/test-prep.md) |
| Defect report format reference | [docs/dr-ref](docs/dr-ref) |
| Automation documentation | [automation/docs/](automation/docs/) |

### Pipelines (agent playbooks)

| Area | Path |
|------|------|
| All pipelines + triggers | [`.cursor/pipelines/`](.cursor/pipelines/) — [`epic-prep.md`](.cursor/pipelines/epic-prep.md) (`EPIC-PREP:`), [`coverage.md`](.cursor/pipelines/coverage.md) (`COVERAGE:`; optional `fix_breadth=yes`), [`ground.md`](.cursor/pipelines/ground.md) (`GROUND:`), [`analysis.md`](.cursor/pipelines/analysis.md) (`ANALYSE:`), [`test-discover.md`](.cursor/pipelines/test-discover.md) (`TEST-DISCOVER:` **linker**), [`test-prep.md`](.cursor/pipelines/test-prep.md) (`TEST-PREP:` **scenario_intent**), [`close.md`](.cursor/pipelines/close.md) (`CLOSE:`), [`test-precon.md`](.cursor/pipelines/test-precon.md) (`TEST-PRECON:` **legacy**), [`coverage-reinforce.md`](.cursor/pipelines/coverage-reinforce.md) (`COVERAGE-REINFORCE:` **legacy opt-in**), [`clean.md`](.cursor/pipelines/clean.md) (`/clean` — **`personal` only**). **Draft+truth master:** [`docs/draft-truth-contract.json`](docs/draft-truth-contract.json) |

### Epics

| Area | Path |
|------|------|
| Epic handoff JSON (schema v4) | [epics/templates/epic-ref.json](epics/templates/epic-ref.json) · **`obligations_proposed[]`** · **`downstream_hints`** · **`verification_focus_proposed`** · **`principal_coverage_threads`** · **`epic_archetype`** · **`verification_topology`** · [docs/epic-prep-topology-contract.json](docs/epic-prep-topology-contract.json) · [docs/epic-prep-principal-contract.json](docs/epic-prep-principal-contract.json) · [docs/epic-obligation-kinds.json](docs/epic-obligation-kinds.json) · [epic-prep-verify.md](automation/docs/epic-prep-verify.md) · optional **`strict_principal=yes`** on `EPIC-PREP:` |
| Epic coverage (schema v2) | [epics/templates/coverage-ref.json](epics/templates/coverage-ref.json) · **`obligations_coverage`** · **`principal_provenance`** · [coverage-obligation-contract.json](docs/coverage-obligation-contract.json) · [coverage-topology-contract.json](docs/coverage-topology-contract.json) · [coverage-principal-contract.json](docs/coverage-principal-contract.json) · [coverage-verify.md](automation/docs/coverage-verify.md) (`--strict-topology`, `--strict-principal`) · optional **`strict_principal=yes`** on `COVERAGE:` |
| Epic requirement analysis (v2) | [analysis-ref.json](epics/templates/analysis-ref.json) · [analysis-gap-contract.json](docs/analysis-gap-contract.json) · [analysis-topology-contract.json](docs/analysis-topology-contract.json) · [analysis-principal-contract.json](docs/analysis-principal-contract.json) · [analysis-verify.md](automation/docs/analysis-verify.md) (`--strict-topology`, `--strict-principal`) · optional **`strict_principal=yes`** on `ANALYSE:` · `exploration_suppressed[]` |
| Epic optional discovery (linker — obligation closure map) | [epics/templates/discover-ref.json](epics/templates/discover-ref.json) v3 · [docs/discover-linker-contract.json](docs/discover-linker-contract.json) · `epics/<KEY>/<KEY>-discover.json` · `TEST-DISCOVER:` (**linker only**, no browser) · **`fixture_needs`** at **`classified_only`** max · verifier [discover_verify.py](automation/tools/discover_verify.py) (`--mode linker`) |
| Epic scenario groups (coverage freeze) | [docs/scenario-groups-contract.json](docs/scenario-groups-contract.json) · **`scenario_groups[]`** on `-coverage.json` · phase 8.6 in [coverage.md](.cursor/pipelines/coverage.md) |
| Epic regression test drafts (scenario intent v3.1) | [tests-ref.json](epics/templates/tests-ref.json) schema v4 · [test-prep-scenario-intent-contract.json](docs/test-prep-scenario-intent-contract.json) · `-tests.json` / `-tests.md` · `TEST-PREP:` default **`scenario_intent`** · verifier [test_prep_verify.py](automation/tools/test_prep_verify.py) (`--mode scenario_intent`) |
| Epic precondition (legacy) | [precon-ref.json](epics/templates/precon-ref.json) · **not in v3 chain** · [test-precon.md](.cursor/pipelines/test-precon.md) LEGACY |
| Epic regression test drafts (v3) | [epics/templates/tests-ref.json](epics/templates/tests-ref.json) schema v4 · [test-prep-topology-contract.json](docs/test-prep-topology-contract.json) · [test-prep-principal-contract.json](docs/test-prep-principal-contract.json) · [test-prep-draft-profiles.json](docs/test-prep-draft-profiles.json) · [test-prep-tbd-contract.json](docs/test-prep-tbd-contract.json) · `-tests.json` / `-tests.md` · `TEST-PREP:` |
| Epic close (integrity + archive) | [epics/templates/close-ref.json](epics/templates/close-ref.json) · `epics/<KEY>/context/<KEY>-close.json` · **three** root `.md` after CLOSE (coverage, analysis, tests); pre-CLOSE JSON under `epics/<KEY>/dependencies/` · trigger `CLOSE:` |

### Automation tools

| Area | Path |
|------|------|
| Yogi URL resolve + lightweight snippets | [automation/docs/yogi-url-resolve.md](automation/docs/yogi-url-resolve.md) · [yogi-tool/](automation/tools/yogi-tool/) (`yogi_resolve.py`, `yogi_snippet.py`, `yogi_extract.py`) |
| CTQA console multiplex probe | [crtqa_console_probe.py](automation/tools/crtqa_console_probe.py) — epic-helper + GROUND gate |
| CTQA **`dx run console`** / host shell · slash **`/crtqa-console`** | [README](automation/tools/crtqa-console/README.md) · [contract + host logs](docs/crtqa-console-contract.json) · `Start-` / `Get-CrtqaConsoleStatus` / `Invoke-CrtqaHostShell` / `Stop-` |
| Corner Epic QA CI (dxCity) | [automation/CI/README.md](automation/CI/README.md) · [teamcity scripts](automation/tools/teamcity/) |
| **jq** JSON projection (system PATH; agent inspect) | [automation/docs/jq.md](automation/docs/jq.md) · `winget install --id jqlang.jq -e` (Windows); rule [`.cursor/rules/jq-json.mdc`](.cursor/rules/jq-json.mdc) |
| **Jira Structure formulas** (Roadmap QA columns + QA End Date) | [docs/jira-structure-contract.json](docs/jira-structure-contract.json) · [automation/structure/](automation/structure/) · [automation/docs/jira-structure.md](automation/docs/jira-structure.md) |
| Agent scratch / temp | [automation/temp/](automation/temp/) |
| **CRTQA TCD stats (v5)** | [docs/epic-stats-contract.json](docs/epic-stats-contract.json) · `/epic-stats` [epic-stats.md](.cursor/commands/epic-stats.md) · [stats/epic-stats/README.md](stats/epic-stats/README.md) · [automation/docs/epic-stats.md](automation/docs/epic-stats.md) · per-user [epic_stats_rollup.py](automation/tools/epic_stats_rollup.py) · team [epic_stats_team_rollup.py](automation/tools/epic_stats_team_rollup.py) |

### Cursor

| Area | Path |
|------|------|
| Rules (harness) | [.cursor/rules/](.cursor/rules/) |
| Prompt scaffolds | [.cursor/prompts/](.cursor/prompts/) (e.g. [corner-adhoc-qa.md](.cursor/prompts/corner-adhoc-qa.md) for unstructured ticket/incident questions) |
| Custom commands | [.cursor/commands/](.cursor/commands/) — **`/epic-helper`**, **`/epic-stats`**, **`/epic-calibrate`**, **`/clean`**, **`/release-notes`**, **`/crtqa-console`** |
| Corner harness hygiene (hooks) | [corner-harness-verify.ps1](.cursor/scripts/corner-harness-verify.ps1) · [automation/docs/corner-harness-verify.md](automation/docs/corner-harness-verify.md) |
| Calibrate verifier | [calibrate_verify.py](automation/tools/calibrate_verify.py) · [automation/docs/calibrate.md](automation/docs/calibrate.md) |
| EPIC-PREP verifier | [epic_prep_verify.py](automation/tools/epic_prep_verify.py) · [automation/docs/epic-prep-verify.md](automation/docs/epic-prep-verify.md) |
| COVERAGE verifier | [coverage_verify.py](automation/tools/coverage_verify.py) · [automation/docs/coverage-verify.md](automation/docs/coverage-verify.md) (`--mode draft_truth`, `--strict-topology`, `--strict-principal`, `--mode reinforce`) · md sync [coverage_md_sync.py](automation/tools/coverage_md_sync.py) · [coverage-operator-hints.json](docs/coverage-operator-hints.json) |
| GROUND verifier | [ground_verify.py](automation/tools/ground_verify.py) · [automation/docs/ground-verify.md](automation/docs/ground-verify.md) (`--mode emit`) |
| ANALYSE verifier | [analysis_verify.py](automation/tools/analysis_verify.py) · [automation/docs/analysis-verify.md](automation/docs/analysis-verify.md) |
| TEST-DISCOVER verifier | [discover_verify.py](automation/tools/discover_verify.py) · [automation/docs/discover-verify.md](automation/docs/discover-verify.md) (`--mode linker`) |
| TEST-PREP verifier | [test_prep_verify.py](automation/tools/test_prep_verify.py) · [automation/docs/test-prep-verify.md](automation/docs/test-prep-verify.md) (`--mode scenario_intent` default; legacy `--mode plan` / `crtqa_outline`) |
| CLOSE verifier | [close_verify.py](automation/tools/close_verify.py) · [automation/docs/close-verify.md](automation/docs/close-verify.md) (`--mode topology --strict-topology` · `--mode principal --strict-principal`) · [close_archive.py](automation/tools/close_archive.py) |
| CLEAN verifier | [clean_verify.py](automation/tools/clean_verify.py) · [clean-verify.md](automation/docs/clean-verify.md) · [clean-remediation.md](automation/docs/clean-remediation.md) · `clean_file_map.py`, `clean_apply_team.py`, `clean_stats_personal.py`, `clean_apply_t1_docs.py`, `clean_apply_public.py`, `clean_public_supersede.py` |
| Humans: Cursor + main processes | [HOW-TO.md](HOW-TO.md) |
| Chrome DevTools MCP (**`chrome-devtools`**, ad-hoc UI) | [automation/docs/chrome-devtools-mcp.md](automation/docs/chrome-devtools-mcp.md); merge into `.cursor/mcp.json` — see [`.cursor/mcp.json.example`](.cursor/mcp.json.example) |

## Context escalation

1. Follow **[docs/harness-map.json](docs/harness-map.json)**: **T0** (`qa-handoff.md`, this file), then T1 `match_any_package` keywords; prefer the clearest single package, and follow that file’s **`rules`** (Jira-key MCP fetch, extra [docs/corner-platform-map.json](docs/corner-platform-map.json) when repro/env/repo scope applies)—do not open every doc by default.
2. **Corner QA on Confluence** is scoped to **QAPORTAL** page **497097273** (“Corner”) **and descendants** unless the user widens scope—see [docs/qa-project.json](docs/qa-project.json).
3. **Fork / platform** context: [docs/project.json](docs/project.json) → **CT** and **XT** Confluence spaces via MCP when needed.
4. **Hosts, repos, Jira projects** (which env, which Stash repo): [docs/corner-platform-map.json](docs/corner-platform-map.json) — credentials stay on Confluence only.

## How to start a session

1. Read **[qa-handoff.md](qa-handoff.md)** for current focus, blockers, and next steps.
2. For any substantive **pipeline**, **calibrate**, or **epic deliverable** work, read **[docs/harness-principles.md](docs/harness-principles.md)** once per session (or follow the matching **`harness-map.json`** package that includes it)—**stable doctrine**, not duplicated in `qa-handoff.md`.
3. Open only the **task-specific** docs or code paths you need—avoid loading the whole tree into context.
4. For substantive work, **update `qa-handoff.md`** before closing the session.

## MCP

### Jira and Confluence

All **discovery and retrieval** for Jira issues and Confluence pages (search, fetch, issue fields) must use **user-mcp-atlassian**. Read each tool’s schema before calling. Do not invent ticket or page content. **Do not** copy secrets from Atlassian into repo files.

### Figma (optional)

When tasks include **Figma file/frame/layer** URLs, use the **workspace-configured Figma MCP** if it is enabled in Cursor. Workflow: **[automation/docs/figma-mcp.md](automation/docs/figma-mcp.md)**. Do not store OAuth tokens or secrets in the repo.

### Chrome DevTools (optional, ad-hoc)

**Chrome DevTools MCP** (register as **`chrome-devtools`**) supports ad-hoc UI exploration (manual execution, legacy PRECON, harness maps)—not **TEST-PREP scenario_intent** generation or **`CLOSE:`**. **Setup:** [automation/docs/chrome-devtools-mcp.md](automation/docs/chrome-devtools-mcp.md) and **[`.cursor/mcp.json.example`](.cursor/mcp.json.example)**.

### PostgreSQL / CTQA (archived — not in v3 pipeline)

Legacy tunnel + env probe tooling: [automation/archive/legacy-ctqa-env/README.md](automation/archive/legacy-ctqa-env/README.md). Not used by `/epic-helper` or GROUND.

## Codebase exploration

Prefer **narrow** search and **bounded** file reads; summarize findings instead of pasting large files. See [.cursor/prompts/codebase-context.md](.cursor/prompts/codebase-context.md) for a reusable scaffold.

## Rules in this repo

Persistent agent behavior is under [.cursor/rules/](.cursor/rules/): `harness-context`, **`jq-json`**, **`pipeline-router`** (trigger → playbook), `mcp-atlassian-search`, **`dxcore-console-harness`** (optional), **`dxtrade5-harness`** (optional), **`webbroker_harness`** (optional), `qa-artifacts`, `harness-maintenance`. **Stable doctrine:** [docs/harness-principles.md](docs/harness-principles.md). Keep **AGENTS.md** short; extend detail in linked JSON and Confluence via MCP.
