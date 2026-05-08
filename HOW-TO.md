# Corner QA — how to run the main processes

This workspace uses **Cursor** with Jira and Confluence so people and agents can prepare epics, draft coverage and tests, compare effort over time, and occasionally measure how stable those outputs are. **Workspace rules load automatically** in Cursor; you do not need to open them to start a run.

**Organization-wide Cursor MCP** (tokens, server layout, global settings): [AI with Cursor](https://confluence.in.devexperts.com/spaces/QAPORTAL/pages/497112528/AI+with+Cursor) on QAPORTAL.

---

## 1. Stats (CRTQA Test Case Development time)

**Purpose:** Roll up how much time logged work took on done **Test Case Development** items in Jira, for epics where you are the test lead, so you can compare patterns (for example assisted versus manual effort) in one place. The report is descriptive only—**association, not causation**.

**Workflow (conceptual):** Identify your Jira identity, find the right epics and tasks, confirm what belongs in the set, note whether each epic’s work was mainly assisted by an agent or mainly manual, categorize the work, accumulate results over time, and refresh a short visual summary plus a table. Small samples are still shown; evidence strength is labeled plainly.

**How to run it**

- Open the command palette and run **`/crtqa-stats`** (or type that in chat if your setup routes it the same way).
- When the flow asks, provide **mode** (first-time baseline versus update versus full refresh), **who you are in Jira**, and answers for **confirmations** and **assisted/manual** attestation where requested.
- Keywords you may see in the tooling or follow-up docs: `initial_assessment`, `incremental_update`, `full_refresh`, `category_policy`, `hybrid`, `static_core`.

---

## 2. Pipelines (QA work per Epic)

**Purpose:** Turn an Epic into a **chain of structured artifacts** agents (and you) can reuse: a grounded map of requirements and context, an end-to-end checklist of what must be verified, reconciliation with known issues, drafted regression tests linked to that checklist, and optionally executable checks when your environment is ready. **Public scrub** and **harness sync** are separate tracks for **publishing** and for **keeping docs and triggers aligned**—not for day-to-day Epic QA.

**Workflow (conceptual, in order)**

1. **Prep** — Gather Jira/Confluence (and optional code pointers) into a single structured **epic map** the next steps can trust.
2. **Coverage** — Draft a **scenario-style checklist** that covers the feature end to end, aligned to that map.
3. **Analysis** — Compare open and recent issues to that checklist; when something in scope is still relevant, carry it forward as a **known-issue** style line in the coverage picture.
4. **Test prep** — Turn checklist items into **draft test cases** with clear trace back to the checklist.
5. **Test execution (optional)** — When URLs, browser automation, and optional database access are available, **materialize or run** checks; this step does not replace human judgment and may be skipped.

**Parallel tracks**

- **Public scrub** — Prepare a **sanitized** copy of the tree for **public** export; use only on the **`release`** branch as defined in team practice.
- **Harness sync** — Reconcile triggers, maps, and entry-point docs after harness changes; use only on **`develop`** or **`main`**, not on **`release`**.

**How to run pipelines**

Open a Cursor chat scoped to this repo and send **one Epic per message** unless you intentionally widen scope. Use these **exact line prefixes** plus the Epic key (for example `CRT-1234`):

| Action | What to type |
|--------|----------------|
| Prep | **`EPIC-PREP:`** *Epic key* — optional **`repo=`** *Bitbucket/Git place* |
| Coverage | **`COVERAGE:`** *Epic key* — optional **`repo=`**, **`focus=`** *free-text focus* |
| Analysis | **`ANALYSE:`** *Epic key* — optional **`include_closed=yes`** |
| Test prep | **`TEST-PREP:`** *Epic key* — optional **`map_only=yes`** |
| Test execution | **`TEST-EXEC:`** *Epic key* — optional **`base_url=`**, **`skip_postgres=yes`**, **`include_blocked=yes`**, **`max_bundles=`** |
| Public scrub | **`PUBLIC-SCRUB:`** — optional **`version=`**, **`source=`** *(branch to merge from)* — **only on `release`** |
| Harness sync | **`SYNC:`** — optional **`scope=`** *(full, pipelines, prompts, templates, tools, mcp)* — **only on `develop` or `main`** |

**Benchmark shadow mode (optional):** On the **same line** as **`EPIC-PREP:`**, **`COVERAGE:`**, or **`TEST-PREP:`**, you may add **`benchmark_suite=`** *id* and **`benchmark_attempt=`** *number* so outputs go to an isolated **shadow** run instead of the normal epic workspace—use when a **benchmark** control hub tells you to.

---

## 3. Benchmark (repeatability and variance)

**Purpose:** Run the same **prep / coverage / test-prep** steps more than once under controlled conditions to see how much outputs **vary** (for example across sessions or attempts), without mixing that noise into normal epic folders.

**Workflow (conceptual):** Answer a short **questionnaire** so the run is defined (profile, number of attempts, epics, methodology). A **control hub** chat creates the suite layout and ordered **lines to paste** into **fresh** chats. Each pasted line runs the same pipeline triggers as production, usually with **benchmark suite** tokens on the line. When attempts finish, you **verify** completion markers and run **finalize / compare** steps from the hub instructions to produce a consolidated view.

**How to run it**

- In the coordinating chat, run **`/crtqa-benchmark`** and follow the prompts.
- For each row the hub gives you, open a **new** chat, paste the **single line** it provides (it will include the usual **`EPIC-PREP:`**, **`COVERAGE:`**, or **`TEST-PREP:`** trigger plus **`benchmark_suite=`** and **`benchmark_attempt=`** when applicable).
- Finish with the hub’s **finalize** instructions so results are **checked and compared** across attempts.

---

## Optional: database access for CTQA

Some optional steps can use a **read-only** Postgres connection through the **SSH tunnel** and a **`postgres-ctqa`** MCP server in Cursor. That setup is **not** part of the three processes above; complete it only when a playbook or **`TEST-EXEC:`** flow needs it. Use the **CTQA PostgreSQL tunnel** documentation in this repository (SSH tunnel, probe, and copy-paste MCP JSON).
