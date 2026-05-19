# Corner QA — how to run the main processes

This workspace uses **Cursor** with Jira and Confluence so people and agents can prepare epics, draft coverage and tests, compare effort over time, and occasionally measure how stable those outputs are. **Workspace rules load automatically** in Cursor; you do not need to open them to start a run.

**Organization-wide Cursor MCP** (tokens, server layout, global settings): [AI with Cursor](https://confluence.in.devexperts.com/spaces/QAPORTAL/pages/497112528/AI+with+Cursor) on QAPORTAL.

### Operator prerequisites

- **jq** (optional per person, recommended for agent-assisted epic work): install **once on your own PC** so `jq` is on system **PATH** in any terminal — agents use it to slice large JSON instead of loading whole epic files. **Windows:** `winget install --id jqlang.jq -e`. **macOS:** `brew install jq`. **Linux:** your distro package or [jqlang.org/download](https://jqlang.org/download/). Verify with `jq --version`; restart Cursor or open a new terminal if the command is not found. Details and example filters: [automation/docs/jq.md](automation/docs/jq.md).

**Where detail lives (agents and humans):** [AGENTS.md](AGENTS.md) (map) · [epics/README.md](epics/README.md) (per-artifact layout) · [docs/harness-map.json](docs/harness-map.json) (keyword → files) · [docs/harness-principles.md](docs/harness-principles.md) (doctrine) · playbooks under [.cursor/pipelines/](.cursor/pipelines/) (trigger on the line, e.g. `CLOSE: CRT-639`).

---

## 1. Stats (CRTQA Test Case Development time)

**Purpose:** Measure **% time saved** on done **Test Case Development** work (CRTQA tasks under CRT epics where you are test lead) when using the **agentic epic helper** (this workspace), against a **manual baseline corpus** from earlier non-AI work. The report is descriptive only—**association, not causation**.

**Workflow (conceptual)**

1. **First run (`initial_assessment`)** — Pull all done TCD tasks; confirm the key list; for **each epic**, say whether it was **already AI-assisted** (yes → **comparison**, not corpus; no → **corpus** baseline). Classify tasks (FE / BE / API / … and story-point size). Build medians and `latest.md`.
2. **Later runs (`incremental_update`)** — Add newly done tasks; confirm each as AI-assisted (default yes). Compare new hours to corpus medians.
3. **Reading results** — **% saved** appears only where the corpus has **≥ 4** tasks in that category (or category×size cell). Sparse categories show “benchmark pending” for that row only; other categories still report normally.

**How to run it**

- Run **`/crtqa-stats`** with **`mode=initial_assessment|incremental_update|full_refresh`** and **`jira_user=<your Jira user>`** (for example `mode=initial_assessment jira_user=arodzevich`).
- Answer **confirmations** (included keys) and **epic attestation** (already AI-assisted?) on the first run; on incremental, confirm **new keys** and AI use per task.
- After the agent writes state, rollup runs: `python automation/tools/crtqa_stats_rollup.py --append-longitudinal` → updates [`stats/crtqa-stats/latest.md`](stats/crtqa-stats/latest.md).

**Docs:** [stats/crtqa-stats/README.md](stats/crtqa-stats/README.md) · [automation/docs/crtqa-stats.md](automation/docs/crtqa-stats.md)

---

## 2. Pipelines (QA work per Epic)

**Purpose:** Turn an Epic into a **chain of structured artifacts** agents (and you) can reuse: a grounded map of requirements and context, an end-to-end checklist of what must be verified, optional gap analysis, discovery and precondition maps, drafted regression tests linked to that checklist, and optionally **Close** (documentation integrity + archive). **No** live app, MCP, or Playwright is required for Close. **Public scrub** and **harness sync** are separate tracks for **publishing** and for **keeping docs and triggers aligned**—not for day-to-day Epic QA.

**Workflow (conceptual, in order)**

1. **Prep** — Gather Jira/Confluence (and optional code pointers) into a single structured **epic map** the next steps can trust.
2. **Coverage** — Draft a **scenario-style checklist** that covers the feature end to end, aligned to that map.
3. **Analysis** (optional) — Coverage-grounded **gap audit**; optional **`known_issues=yes`** to reconcile Jira and append **`>`** lines on coverage.
4. **Test Discovery** — After coverage, map obligations and environment needs into **`-discover.json`** (see [checklist](#discovery-precondition--prep-checklist) below). Phase 0 must pass before the file is written.
5. **Test Precondition** (optional) — Author environment setup and **`test_skeleton[]`** into **`-precon.json`** + **`-precon.md`** for Test Prep; same operator prep as Test Discovery.
6. **Test Prep** — Turn checklist items into **executable-outline** draft test cases (default **`crtqa_outline`**; optional **`draft_profile=teaching`**); uses the same [Discovery / Precondition / Prep checklist](#discovery-precondition--prep-checklist) when UI exploration is required.
7. **Close** (optional) — Backward integrity ladder on JSON artefacts, optional mechanical fixes, regenerate four human **`.md`** files, then archive all JSON under **`epics/<KEY>/context/`**.

**Parallel tracks**

- **Public scrub** — Prepare a **sanitized** copy of the tree for **public** export; use only on the **`release`** branch as defined in team practice.
- **Harness sync** — Reconcile triggers, maps, and entry-point docs after harness changes; use only on **`develop`** or **`main`**, not on **`release`**.

**How to run pipelines**

Open a Cursor chat scoped to this repo and send **one Epic per message** unless you intentionally widen scope. Use these **exact line prefixes** plus the Epic key (for example `CRT-1234`):

| Action | What to type |
|--------|----------------|
| Prep | **`EPIC-PREP:`** *Epic key* — optional **`repo=`** / **`focus=`**; emits **obligations** (ref v4) |
| Coverage | **`COVERAGE:`** *Epic key* — requires **`-ref.json`**; optional **`repo=`** / **`focus=`**; **obligations_coverage** (v2) |
| Analysis | **`ANALYSE:`** *Epic key* — requires **`-coverage.json`**; optional **`known_issues=yes`** (default off), **`resolve=no`**, **`include_closed=yes`** (with known_issues) |
| Test Discovery | **`TEST-DISCOVER:`** *Epic key* |
| Test Precondition | **`TEST-PRECON:`** *Epic key* |
| Test Prep | **`TEST-PREP:`** *Epic key* |
| Close epic | **`CLOSE:`** *Epic key* — optional **`heal=no`** (default: apply mechanical fixes); requires full artifact set at epic root |
| Public scrub | **`PUBLIC-SCRUB:`** — optional **`version=`**, **`source=`** — **only on `release`** |
| Harness sync | **`SYNC:`** — optional **`scope=`** — **only on `develop` or `main`** |

Optional tokens on the **same line** as the trigger (see [checklist](#discovery-precondition--prep-checklist)): **`repo=`**, **`focus=`**, **`map_only=yes`**, **`discover_override=yes`**, **`crtqa_index=yes`** (Test Discovery), **`skip_cold_gate=yes`** (Test Precondition), **`benchmark_suite=`** / **`benchmark_attempt=`** (benchmark runs).

### Discovery, Precondition & Prep checklist

One Epic per chat. Run **environment** steps once per session, then run Test Discovery, Test Precondition, and/or Test Prep in **separate** chats (recommended order: Discovery → Precondition → Prep).

**Environment (steps 1–3)**

1. **Postgres tunnel** — leave open: `python automation/tools/tunnel/ctqa_pg.py YOUR_AD_USER@ctqa.prosp.devexperts.com` ([tunnel README](automation/tools/tunnel/README.md)). Reload **`postgres-ctqa`** MCP in Cursor.
2. **Console** — **`/crtqa-console start`** (SSH password in the desktop dialog, ~30s).
3. **Environment check** — **`/crtqa-env`** — fix any FAIL before running the pipelines below.

**Chrome (step 4)** — enable **`chrome-devtools`** MCP when the epic needs dxTrade5 or WebBroker. Configured ≠ logged in ([fe-ui-probe-contract](docs/fe-ui-probe-contract.json)).

**FE credentials (steps 5–6)** — same tokens on the trigger line for **Test Discovery**, **Test Precondition**, and **Test Prep** when UI is in scope:

| Token | Use |
|-------|-----|
| `dxtrade5_creds=<user>/<password>` | CTQA retail login |
| `webbroker_creds=<user>/<password>` | CTQA dealer login |
| `fe_exploration_waived=yes` | After Phase **0b** stop + ack — UI depth capped at login shell only |
| `proceed` | After Phase **0** tunnel/console stop — re-run Phase **0**, then continue |

**Adaptive** has no cred token (CTQA shared principal on `/adaptive/`) — see [corner-platform-map](docs/corner-platform-map.json) `adaptive_login_policy`.

Example (replace user/password; **never** commit or paste into repo files):

`TEST-DISCOVER: CRT-639 dxtrade5_creds=YOUR_USER/YOUR_PASSWORD webbroker_creds=YOUR_USER/YOUR_PASSWORD`

Use the same cred suffix for **`TEST-PRECON:`** and **`TEST-PREP:`**.

**Triggers (step 7)** — one line per chat:

| Pipeline | Line prefix | Prerequisites |
|----------|-------------|---------------|
| Test Discovery | **`TEST-DISCOVER:`** *Epic key* | `-ref.json`, `-coverage.json` |
| Test Precondition | **`TEST-PRECON:`** *Epic key* | `-coverage.json`; SHOULD `-discover.json`, `-ref.json` |
| Test Prep | **`TEST-PREP:`** *Epic key* (`shape_ref=benchmark` only with benchmark tokens) | `-coverage.json` with **obligations_coverage**; SHOULD `-precon.json` |
| Close epic | **`CLOSE:`** *Epic key* (optional **`heal=no`**) | `-ref.json`, `-coverage.json`, `-discover.json`, `-precon.json`, `-tests.json` at epic root |

**Exploration depth** ([exploration-depth-ladder](docs/exploration-depth-ladder.json)): login smoke is not enough. Test Precondition drills setup UI/forms; Test Prep opens verification grids (**8a¾**) before drafting tests. Allow longer runs when creds are supplied.

**If Phase 0 stops** — missing creds: re-send the trigger with cred tokens or **`fe_exploration_waived=yes`**; tunnel/console: fix infra, then same pipeline with **`proceed`** (repeat cred tokens if UI still applies).

**Closed epics (`CLOSE:` completed)** — After **`CLOSE:`**, JSON artefacts live under **`epics/<KEY>/context/`**; only four human files remain at **`epics/<KEY>/`**: **`-coverage.md`**, **`-analysis.md`**, **`-tests.md`**, **`-precon.md`**. Rerunning **`EPIC-PREP:`**, **`COVERAGE:`**, or other upstream pipelines on a closed epic **will fail or write to wrong paths** unless you move JSON back to the epic root (or use a fresh folder). **`CLOSE:`** is the terminal archive step for that epic folder.

---

## 3. Benchmark (repeatability and variance)

**Purpose:** Run the same **prep / coverage / (optional) analyse / discover / precon / Test Prep / (optional) Close** steps more than once under controlled conditions to see how much outputs **vary** (for example across sessions or attempts), without mixing that noise into normal epic folders.

**Workflow (conceptual):** Answer a short **questionnaire** so the run is defined (profile, number of attempts, epics, methodology). A **control hub** chat creates the suite layout and ordered **lines to paste** into **fresh** chats. Each pasted line runs the same pipeline triggers as production, usually with **benchmark suite** tokens on the line. When attempts finish, you **verify** completion markers and run **finalize / compare** steps from the hub instructions to produce a consolidated view.

**How to run it**

- In the coordinating chat, run **`/crtqa-benchmark`** and follow the prompts.
- For each row the hub gives you, open a **new** chat, paste the **single line** it provides (it will include the usual **`EPIC-PREP:`**, **`COVERAGE:`**, **`ANALYSE:`**, **`TEST-DISCOVER:`**, **`TEST-PRECON:`**, **`TEST-PREP:`**, or **`CLOSE:`** trigger plus **`benchmark_suite=`** and **`benchmark_attempt=`** when applicable).
- Finish with the hub’s **finalize** instructions so results are **checked and compared** across attempts.
