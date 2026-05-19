# Corner QA — how to run the main processes

This workspace uses **Cursor** with Jira and Confluence so people and agents can prepare epics, draft coverage and tests, compare effort over time, and occasionally measure how stable those outputs are. **Workspace rules load automatically** in Cursor; you do not need to open them to start a run.

**Organization-wide Cursor MCP** (tokens, server layout, global settings): [AI with Cursor](https://confluence.in.devexperts.com/spaces/QAPORTAL/pages/497112528/AI+with+Cursor) on QAPORTAL.

### Operator prerequisites

- **jq** (optional per person, recommended for agent-assisted epic work): install **once on your own PC** so `jq` is on system **PATH** in any terminal — agents use it to slice large JSON instead of loading whole epic files. **Windows:** `winget install --id jqlang.jq -e`. **macOS:** `brew install jq`. **Linux:** your distro package or [jqlang.org/download](https://jqlang.org/download/). Verify with `jq --version`; restart Cursor or open a new terminal if the command is not found. Details and example filters: [automation/docs/jq.md](automation/docs/jq.md).

**Where detail lives (agents and humans):** [AGENTS.md](AGENTS.md) (map) · [epics/README.md](epics/README.md) (per-artifact layout) · [docs/harness-map.json](docs/harness-map.json) (keyword → files) · [docs/harness-principles.md](docs/harness-principles.md) (doctrine) · playbooks under [.cursor/pipelines/](.cursor/pipelines/) (trigger on the line, e.g. `CLOSE: CRT-639`).

---

## 1. Stats (CRTQA Test Case Development time) — v4

**Purpose:** Measure time saved on done **Test Case Development** (CRTQA TCD under CRT epics where you are test lead) when using the **agentic epic helper**, vs a **manual corpus** and vs **draft estimates**. Draft hours come from Jira **`customfield_11250`**; **Devex SP** = draft ÷ 8. **Association, not causation.**

**Which mode**

| Mode | When |
|------|------|
| `initial_assessment` | First baseline: all done TCD tasks for your epics |
| `incremental_update` | Routine: only **new** done tasks since last run (report still refreshes if there are none) |
| `full_refresh` | Re-pull Jira for the **same** included keys (redo assessment, fix draft/logged fields, or after v4 upgrade) — epic roles unchanged unless you re-attest |

**Workflow (conceptual)**

1. Confirm **included CRTQA keys**; per epic on first run: **already AI-assisted?** (yes → **comparison**, no → **corpus**).
2. Ingest **draft** (`customfield_11250`) and **logged** (`timetracking.time_spent`). Do **not** use `timetracking.original_estimate` for draft or size.
3. Agent (or you) runs rollup: `python automation/tools/crtqa_stats_rollup.py --append-longitudinal`.

**Reading [`stats/crtqa-stats/latest.md`](stats/crtqa-stats/latest.md)**

1. Header — **`report_profile`** (`task_detail` \| `directional` \| `benchmark`) and what the run can claim.
2. **Task-level** table — draft vs logged, **vs draft** hours, **attribution** (`estimate_only` vs corpus-backed).
3. Charts — draft vs logged (always when draft exists); corpus benchmark chart when n≥4 manual tasks in a category.
4. Benchmark tables — **% saved vs corpus** only when corpus **≥ 4** in that category×size; otherwise “benchmark pending” for that row only.

**How to run it**

```
/crtqa-stats mode=initial_assessment jira_user=<you>
/crtqa-stats mode=incremental_update jira_user=<you>
/crtqa-stats mode=full_refresh jira_user=<you>
```

Playbook: [`.cursor/commands/crtqa-stats.md`](.cursor/commands/crtqa-stats.md). Rollup details: [automation/docs/crtqa-stats.md](automation/docs/crtqa-stats.md). Operator summary: [stats/crtqa-stats/README.md](stats/crtqa-stats/README.md).

**Git:** `latest.md` is committed; `stats/crtqa-stats/state/` and `raw/` are local (gitignored).

---

## 2. Pipelines (QA work per Epic)

**Purpose:** Build a reusable artifact chain per Epic—requirements map, verification checklist, optional gap analysis, discovery/precondition maps, draft regression tests, optional **Close** (integrity + archive). Close does not run the app or Playwright.

**Typical order**

| Step | Trigger | Main output |
|------|---------|-------------|
| 1 | `EPIC-PREP:` | `epics/<KEY>/<KEY>-ref.json` |
| 2 | `COVERAGE:` | `-coverage.json` / `-coverage.md` |
| 3 | `ANALYSE:` (optional) | `-analysis.json` / `-analysis.md` |
| 4 | `TEST-DISCOVER:` | `-discover.json` |
| 5 | `TEST-PRECON:` (optional) | `-precon.json` / `-precon.md` |
| 6 | `TEST-PREP:` | `-tests.json` / `-tests.md` |
| 7 | `CLOSE:` (optional) | JSON → `context/`; four `.md` at epic root |

Run **one Epic per chat**. Paste the trigger and key on the first line, for example: `COVERAGE: CRT-639`.

### Trigger reference

| Trigger | Needs (under `epics/<KEY>/`) | Optional on same line |
|---------|------------------------------|----------------------|
| `EPIC-PREP:` *KEY* | — | `repo=`, `focus=` |
| `COVERAGE:` *KEY* | `-ref.json` | `repo=`, `focus=` |
| `ANALYSE:` *KEY* | `-coverage.json` | `known_issues=yes`, `resolve=no`, `include_closed=yes` |
| `TEST-DISCOVER:` *KEY* | `-ref.json`, `-coverage.json` | FE creds (below), `proceed`, `fe_exploration_waived=yes`, `crtqa_index=yes`, `discover_override=yes` |
| `TEST-PRECON:` *KEY* | `-coverage.json` | Same FE tokens; SHOULD `-discover.json`, `-ref.json` |
| `TEST-PREP:` *KEY* | `-coverage.json` (obligations_coverage) | Same FE tokens; SHOULD `-precon.json`; `map_only=yes`, `draft_profile=teaching` |
| `CLOSE:` *KEY* | `-ref`, `-coverage`, `-discover`, `-precon`, `-tests` at epic root | `heal=no` (default: apply fixes) |
| `CLEAN:` | — | `scope=full` (default) \| `align` \| `personal` \| `team` \| `public`; `version=M.N`; **`personal` branch only** |

Playbooks: [.cursor/pipelines/](.cursor/pipelines/). Layout: [epics/README.md](epics/README.md). For benchmark shadow runs, add `benchmark_suite=` and `benchmark_attempt=` on the same line (see [§3](#3-benchmark-repeatability-and-variance)).

**Publish track:** **`CLEAN:`** aligns harness pointers, pushes **`personal`**, updates [agentic-epic-helper-team](https://github.com/heatdance/agentic-epic-helper-team) (`team` branch via PR after bootstrap), and publishes **`public-M.N`** to [agentic-epic-helper-releases](https://github.com/heatdance/agentic-epic-helper-releases). Not for day-to-day Epic QA.

### Operator prep (Discovery, Precondition, Prep)

Do **once per session**, then run `TEST-DISCOVER:` → `TEST-PRECON:` → `TEST-PREP:` in separate chats (recommended order).

1. **Postgres tunnel** (leave open):  
   `python automation/tools/tunnel/ctqa_pg.py YOUR_AD_USER@ctqa.prosp.devexperts.com`  
   Reload **postgres-ctqa** MCP — [tunnel README](automation/tools/tunnel/README.md).
2. **Console:** `/crtqa-console start` (SSH password in dialog, ~30s).
3. **Check:** `/crtqa-env` — fix any FAIL before pipelines.
4. **Chrome:** enable **chrome-devtools** MCP when dxTrade5 or WebBroker is in scope ([fe-ui-probe-contract](docs/fe-ui-probe-contract.json)). Configured ≠ logged in.

**FE credentials** — append to the trigger line when UI is in scope (never commit secrets to the repo):

| Token | Meaning |
|-------|---------|
| `dxtrade5_creds=<user>/<password>` | CTQA retail |
| `webbroker_creds=<user>/<password>` | CTQA dealer |
| `fe_exploration_waived=yes` | After Phase 0b stop + your ack — shell-only UI |
| `proceed` | After Phase 0 infra stop — re-run Phase 0, then continue |

Example: `TEST-DISCOVER: CRT-639 dxtrade5_creds=USER/PASS webbroker_creds=USER/PASS` — reuse the same suffix for `TEST-PRECON:` and `TEST-PREP:`.

**Adaptive** has no cred token (CTQA shared principal) — [corner-platform-map](docs/corner-platform-map.json).

**Exploration depth:** Phase 0c is login smoke only; Precondition drills setup; Prep opens verification grids before drafting ([exploration-depth-ladder](docs/exploration-depth-ladder.json)).

**If Phase 0 stops:** add cred tokens or `fe_exploration_waived=yes`; for tunnel/console failures, fix infra and resend with `proceed`.

### After Close

When `CLOSE:` has run, JSON lives under `epics/<KEY>/context/`. Only these stay at epic root: `-coverage.md`, `-analysis.md`, `-tests.md`, `-precon.md`. Do not rerun upstream pipelines unless you restore JSON to the epic root first.

---

## 3. Benchmark (repeatability and variance)

**Purpose:** Run the same **prep / coverage / (optional) analyse / discover / precon / Test Prep / (optional) Close** steps more than once under controlled conditions to see how much outputs **vary** (for example across sessions or attempts), without mixing that noise into normal epic folders.

**Workflow (conceptual):** Answer a short **questionnaire** so the run is defined (profile, number of attempts, epics, methodology). A **control hub** chat creates the suite layout and ordered **lines to paste** into **fresh** chats. Each pasted line runs the same pipeline triggers as production, usually with **benchmark suite** tokens on the line. When attempts finish, you **verify** completion markers and run **finalize / compare** steps from the hub instructions to produce a consolidated view.

**How to run it**

- In the coordinating chat, run `**/crtqa-benchmark`** and follow the prompts.
- For each row the hub gives you, open a **new** chat, paste the **single line** it provides (it will include the usual `**EPIC-PREP:`**, `**COVERAGE:**`, `**ANALYSE:**`, `**TEST-DISCOVER:**`, `**TEST-PRECON:**`, `**TEST-PREP:**`, or `**CLOSE:**` trigger plus `**benchmark_suite=**` and `**benchmark_attempt=**` when applicable).
- Finish with the hub’s **finalize** instructions so results are **checked and compared** across attempts.

