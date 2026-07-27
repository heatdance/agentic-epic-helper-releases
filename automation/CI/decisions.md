# Decisions — Corner Epic QA CI v1

ADR-style record of v1 scope. Change via operator entrust + doc update.

## D1 — Trigger on CRTQA comment, not CRT epic

**Decision:** Dispatch watches **CRTQA** tasks for comment **`Agent: Coverage`**. Epic key parsed from QA task **summary** (`CRT-\d+`).

**Rationale:** Corner QA workflow assigns CRTQA tasks per epic; Epic Link field not reliably populated.

**Status:** Accepted, verified in production Dispatch logs.

---

## D2 — Chain stops at ANALYSE

**Decision:** CI runs **EPIC-PREP → COVERAGE → Console gate → GROUND → ANALYSE** only.

**Out of scope v1:** TEST-DISCOVER, TEST-PREP, CLOSE, `COVERAGE fix_breadth=yes`, human `coverage_frozen_at` / `scenario_groups[]`.

**Rationale:** Unattended first pass delivers coverage + analysis drafts; human review and test prep stay in IDE `/epic-helper` or manual pipelines.

**Status:** Accepted.

---

## D3 — Jira comment only, no REST attachment

**Decision:** Success/fail feedback via **Jira comment** pointing to TeamCity **`epic-work`** artifacts. No Jira REST file attach.

**Rationale:** Operator PAT received HTTP 403 on attach API; manual UI attach works but is not automatable with current token scope.

**Status:** Accepted v1; revisit if Jira admin grants attachment scope.

---

## D4 — TeamCity REST queue, not runBuild service message

**Decision:** Dispatch uses `POST /app/rest/buildQueue` with Bearer `TC_REST_TOKEN`.

**Rationale:** `##teamcity[runBuild ...]` logged QUEUE but did not enqueue Pipeline in dxCity 2026.1 testing.

**Status:** Accepted.

---

## D5 — OpenSSH console transport on Linux agents

**Decision:** Pipeline console gate and GROUND use **`CRTQA_CONSOLE_TRANSPORT=openssh`** and B64 SSH key — not Windows PuTTY multiplex.

**Rationale:** dxCity agents are Linux; desktop `/crtqa-console` flow is Windows-only.

**Status:** Accepted; see [crtqa-console-ci.md](../docs/crtqa-console-ci.md).

---

## D6 — Dedup at Dispatch by comment id

**Decision:** `CRTQA-xxxx#commentId` in `processed_comment_ids.txt`; Pipeline does not dedup.

**Rationale:** One Pipeline per triggering comment; manual Pipeline bypasses Dispatch.

**Status:** Accepted.

---

## D7 — Documentation tier personal + team only

**Decision:** `automation/CI/**`, `automation/tools/teamcity/**`, and `automation/docs/crtqa-console-ci.md` **deleted on public** export.

**Rationale:** Internal dxCity/Stash/CRTQA operational detail not needed in public guide export.

**Status:** Accepted — encoded in [clean-publish-tier-matrix.json](../../docs/clean-publish-tier-matrix.json).

---

## D8 — Stash `AI/agentic-feature-helper` branch `team` as CI checkout

**Decision:** TeamCity VCS checks out Stash **`team`**, not GitHub team mirror.

**Rationale:** dxCity integrated with internal Stash; harness pushes via `git push stash`.

**Status:** Accepted.

---

## D9 — MCP + project rules mandatory for CI agents

**Decision:** Pipeline agent steps use [`run_pipeline_agent.py`](../tools/teamcity/run_pipeline_agent.py) with **inline** `user-mcp-atlassian` stdio MCP and `setting_sources=["project"]`. Step 1 bootstraps gitignored `.cursor/mcp.json` and Jira smoke. Single **`JIRA_API_TOKEN`** PAT feeds MCP and Jira comment scripts.

**Rationale:** Bare `Agent.prompt` + `LocalAgentOptions(cwd=…)` only did not load `.cursor/rules/` (pipeline-router) or Atlassian MCP; playbooks require MCP for Jira/Confluence/Bitbucket. `status: finished` without `epics/<KEY>/*` was a false green before `--require` post-checks.

**Status:** Accepted (MCP patch).

---

## D10 — Self-healing dxAgent bootstrap

**Decision:** Step 1 runs [`bootstrap-agent-env.sh`](../tools/teamcity/bootstrap-agent-env.sh) to install `uv`/`uvx` and `cursor-sdk` on the agent when missing, warm MCP wheels, and write `.teamcity-ci/bootstrap.env` for later steps.

**Rationale:** dxAgent images do not ship `uv`; failing step 1 blocked the entire chain. Image-level prereqs reduced to `jq`, `curl`/`wget`, writable `$HOME`.

**Status:** Accepted (`749977d`).

---

## D11 — TeamCity password params exposed as env

**Decision:** Pipeline exposes `env.JIRA_API_TOKEN=%JIRA_API_TOKEN%` (and `env.CURSOR_API_KEY`, `env.EPIC_KEY`) on the build configuration. Scripts also read `TEAMCITY_BUILD_PROPERTIES_FILE` via [`read_teamcity_params.py`](../tools/teamcity/read_teamcity_params.py).

**Rationale:** dxCity does not inject password configuration parameters into VCS-hosted script environments unless referenced as env vars or properties file.

**Status:** Accepted (`3a730ae`).

---

## D12 — Jira notify without `not(success())` in dxCity UI

**Decision:** Step 11/12 mutual exclusion uses **Execute step** dropdown settings plus [`jira-notify-guard.sh`](../tools/teamcity/jira-notify-guard.sh) marker file. Parameter-based execution conditions in dxCity UI **cannot** express `not(success())`.

**Rationale:** Operators only see parameter equals/contains dialogs — not build-status expressions. Script guard prevents duplicate failure comments when step 12 runs on green builds.

**Status:** Accepted (`792f519`). Optional future: single `jira-notify.sh` TeamCity step.

---

## D13 — Jira build URL self-resolve

**Decision:** Steps 11/12 load env via [`jira-env.sh`](../tools/teamcity/jira-env.sh). [`read_teamcity_params.py`](../tools/teamcity/read_teamcity_params.py) maps TeamCity built-in `teamcity.build.url` → `TEAMCITY_BUILD_URL` when the env var is empty. [`jira_success.py`](../tools/teamcity/jira_success.py) / [`jira_failure.py`](../tools/teamcity/jira_failure.py) call the same resolver as belt-and-suspenders.

**Rationale:** QA pipeline steps 1–10 succeeded but Jira notify failed instantly when operators did not manually export `%teamcity.build.url%` in step 11/12 UI. Built-in TeamCity URL is always in the properties file — scripts should not depend on per-step copy-paste.

**Status:** Accepted (2026-07).

---

## D14 — COVERAGE verify UX (prompt addendum + partial Jira fail)

**Decision:** [`coverage-agent.sh`](../tools/teamcity/coverage-agent.sh) CI addendum forbids internal oracle enum tokens in `smart_checklist_markdown`. [`jira_failure.py`](../tools/teamcity/jira_failure.py) `build_failure_comment()` emits a **partial** comment when `epics/{EPIC}/` contains ref and/or coverage JSON, listing present/missing artefacts and verify rerun hints. **`coverage_verify.py` unchanged.**

**Rationale:** CRTQA-10194 / CRT-659 failed step 5 with `forbidden oracle token` after agent exit 0 — quality gate is correct; operators need prevention (A) and actionable failure notify (B) without weakening draft_truth gates.

**Status:** Accepted (2026-07).

---

## D15 — Jira notify guard must return 0 to continue

**Decision:** [`jira-notify-guard.sh`](../tools/teamcity/jira-notify-guard.sh) skip helpers **return 0** when the peer marker is absent (continue to POST). Only when a marker exists do they `exit 0` (skip comment).

**Rationale:** Callers `jira-success.sh` / `jira-failure.sh` use `set -e`. The original `return 1` “do not skip” idiom aborted the step immediately after preflight — steps 1–10 green, no Jira comment (CRTQA-10028 / CRT-634).

**Status:** Accepted (2026-07).

---

## D16 — Script-level step contracts via state markers

**Decision:** TeamCity wrappers enforce upstream dependencies in-script using shared helpers:
- [`corner-tc-preflight.sh`](../tools/teamcity/corner-tc-preflight.sh) for env/file/upstream assertions.
- [`corner-tc-state.sh`](../tools/teamcity/corner-tc-state.sh) for `.teamcity-ci/state/*.ok` markers.

Downstream steps fail fast with `ERROR: contract violation: ...` when required upstream markers are absent.

**Rationale:** TeamCity UI settings can drift (`Stop build on failure`, step execute modes). Contract checks in scripts prevent hidden coupling and late cascading failures.

**Status:** Accepted (2026-07).

---

## D17 — Per-app Atlassian PATs + fail-hard snippet honesty

**Decision:**

1. TeamCity Pipeline requires **three** password params: `JIRA_API_TOKEN`, `CONFLUENCE_API_TOKEN`, `BITBUCKET_API_TOKEN` — wired separately into MCP `*_PERSONAL_TOKEN` env (no silent reuse of the Jira PAT for Confluence/Stash on Data Center).
2. Step 1 [`mcp-smoke.sh`](../tools/teamcity/mcp-smoke.sh) probes Jira issue + Confluence `/rest/api/user/current` + Stash `CAN/corner` — fail fast on 401/403.
3. [`epic_prep_verify.py --ci-strict`](../tools/epic_prep_verify.py) (TeamCity EPIC-PREP verify) rejects self-issued `validation_log.deferral_accepted` when snippets failed (override only via `ALLOW_SNIPPET_DEFERRAL=yes`).
4. [`jira_success.py`](../tools/teamcity/jira_success.py) refuses “coverage is ready” when any `requirements[].snippet_status != ok`.
5. Coverage semantic gates (SD1–SD6) reject tag-level stub skeletons and bare machine `! reason:` enums.

**Rationale:** Pipeline build 43 for CRT-635 was green with a stub Smart Checklist because one Jira PAT returned Confluence/Stash **401**, the agent wrote `deferral_accepted`, and notify posted success. Auth fix alone is insufficient without honesty gates.

**Status:** Accepted (2026-07).

---

## D18 — Variation-based coverage (obligation = variation)

**Decision:**

1. EPIC-PREP extracts **`parameter_inventory[]`** from snippet structure (not a field-name whitelist) and applies [`docs/variation-catalogue.json`](../../docs/variation-catalogue.json) so each mandated variation becomes one `obligations_proposed[]` row with **`variation: { rule_id, kind, parameter }`**.
2. COVERAGE keeps **1:1** obligation→check; Dimensions may cite **`variation_catalogue_rule`**; each variation check needs a `>` oracle line from inventory `spec_text`; paste may end with **`## Not attempted`**.
3. **`page_id`** via MCP `confluence_search` is first-class; **`page_id_unresolved`** is recoverable and **not deferrable** after search.
4. GROUND probes setup/console checks (including `chk-s*` / `environment_setup`); optional **`data_setup_recipe`**.
5. Verifiers print **`mandated_variations` / `emitted` / `unmatched_patterns`** and **`variation_density`** (TeamCity build statistics).
6. Root `-coverage.md` remains machine-generated; engineer-final Smart Checklist lives on CRTQA (one pipeline pass).

**Rationale:** Formulation bans (SD1–SD6) cleaned structure but agents minimized text. Useful coverage is basic positive/negative/boundary variations per requirement group, not a paraphrase of the spec — and not a full middle-QA edge-case catalogue.

**Status:** Accepted (2026-07).

---

## Deferred / revisit

| Item | Notes |
|------|-------|
| Jira attachment API | Needs PAT scope or app user |
| Stash repo visibility | Infra / AI project admins |
| `fix_breadth` CI loop | Optional Round 2 — not v1 |
| Full `/epic-helper` parity | Requires human gates automation |
