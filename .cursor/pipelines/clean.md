# Pipeline: CLEAN (align, publish personal, team, public)

**Trigger**: user message starts with **`CLEAN:`**. Optional tokens on the same line:

| Token | Meaning |
|-------|---------|
| **`scope=full`** (default) | Phases **0 → S → P → T → U** |
| **`scope=align`** | **S** only |
| **`scope=personal`** | **S → P** |
| **`scope=team`** | **T** (after personal is pushed) |
| **`scope=public`** | **U** only |
| **`version=M.N`** | Force public branch `public-M.N` (e.g. `version=1.2`) |
| **`confirm_major=yes`** | Required after latest `public-M.9` to create `public-{M+1}.0` |
| **`skip_personal_push=yes`** | Run align without commit/push (testing) |
| **`proceed`** | Acknowledge dirty working tree on personal |

**Scope**: One publish run from branch **`personal` only**. **Router**: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc). **Contract**: [`docs/clean-contract.json`](../../docs/clean-contract.json). **Verifier**: [`automation/tools/clean_verify.py`](../../automation/tools/clean_verify.py). **Style (public)**: [`docs/clean-public-style.md`](../../docs/clean-public-style.md).

**Hard invariant**: Do **not** run **`CLEAN:`** on **`team`** or **`public-*`** branches. Team/public trees are **outputs** of this pipeline.

**Ephemeral**: [`automation/temp/clean/`](../../automation/temp/clean/) only. **Delete recursively** before each tier’s final commit. Durable JSON must **not** reference paths under `automation/temp/clean/`.

**Replaces**: former **`SYNC:`** (align tiers) and **`PUBLIC-SCRUB:`** (public sterilize). Do not invoke those triggers after this playbook ships.

---

## Three remotes

| Tier | Remote | Branch | Repo |
|------|--------|--------|------|
| Personal | `origin` | `personal` | [agentic-epic-helper](https://github.com/heatdance/agentic-epic-helper) |
| Team | `team` | `team` | [agentic-epic-helper-team](https://github.com/heatdance/agentic-epic-helper-team) |
| Public | `releases` | `public-M.N` | [agentic-epic-helper-releases](https://github.com/heatdance/agentic-epic-helper-releases) |

---

## Phase 0 — Preflight (blocking)

1. **`git rev-parse --is-inside-work-tree`**
2. **`git branch --show-current`** must be **`personal`**. Else **stop**: `git checkout personal`
3. **`python automation/tools/clean_verify.py --mode preflight`**
4. If working tree dirty: show **`git status -sb`**; **stop** until operator sends **`proceed`** on the trigger line (or stash unrelated work).
5. Parse **`scope=`** (default `full`).

---

## Phase S — Align (replaces SYNC)

### S1 — File-map

1. Ensure **`automation/temp/clean/`** exists.
2. Run **`python automation/tools/clean_file_map.py`** → writes **`automation/temp/clean/file-map.json`**.
3. **`python automation/tools/clean_verify.py --mode file_map`**
4. **Subagent (optional)**: enrich `role` / `consumers[]` for rows where `action != keep` (one cluster per top-level directory; load only those rows + contract).

### S2 — Harness align (T0–T6)

Run **one subprocess per tier**; after each tier, run **`clean_verify.py --mode align`** and retry until pass (escalate to human after **10** failures per [`clean-contract.json`](../../docs/clean-contract.json) `retry_escalate_after`).

**Normative pipeline registry** — when adding `.cursor/pipelines/*.md`, update this table and T0–T1 in the same change:

| Pipeline id | Trigger | Playbook | `harness-map` package | Temp | Router + AGENTS + README + HOW-TO + qa-artifacts |
|-------------|---------|----------|----------------------|------|--------------------------------------------------|
| `epic-prep` | **`EPIC-PREP:`** | [epic-prep.md](epic-prep.md) | `epic_ref` | `epics/<KEY>/temp/` | Yes |
| `coverage` | **`COVERAGE:`** | [coverage.md](coverage.md) | `coverage_pipeline` | `epics/<KEY>/temp/` | Yes |
| `analysis` | **`ANALYSE:`** | [analysis.md](analysis.md) | `analysis_pipeline` | `epics/<KEY>/temp/` | Yes |
| `test-discover` | **`TEST-DISCOVER:`** | [test-discover.md](test-discover.md) | `test_discover_pipeline` | `epics/<KEY>/temp/` | Yes |
| `test-precon` | **`TEST-PRECON:`** | [test-precon.md](test-precon.md) | `test_precon_pipeline` | `epics/<KEY>/temp/` | Yes |
| `test-prep` | **`TEST-PREP:`** | [test-prep.md](test-prep.md) | `test_prep_pipeline` | `epics/<KEY>/temp/` | Yes |
| `close` | **`CLOSE:`** | [close.md](close.md) | `close_pipeline` | `epics/<KEY>/temp/` | Yes |
| `clean` | **`CLEAN:`** | [clean.md](clean.md) (this file) | `clean_pipeline` | `automation/temp/clean/` | Yes — **`personal` only** |

**T0** — List `.cursor/pipelines/*.md`; each epic pipeline + **`clean`** in router; **`clean_pipeline`** in harness-map; **no** `public-scrub.md` / `sync.md`; **no** `PUBLIC-SCRUB` / `SYNC` in router.

**T1** — [AGENTS.md](../../AGENTS.md), [README.md](../../README.md), [HOW-TO.md](../../HOW-TO.md), [qa-artifacts.mdc](../rules/qa-artifacts.mdc): branch table (team → `team` remote); **`CLEAN:`** only (no scrub/sync).

**T2** — [`.cursor/prompts/`](../prompts/): triggers and links.

**T3** — [`epics/templates/`](../../epics/templates/), [`epics/README.md`](../../epics/README.md).

**T4** — [`automation/tools/`](../../automation/tools/), [`automation/docs/`](../../automation/docs/), tunnel README MCP snippet, [jq.md](../../automation/docs/jq.md).

**T5** — [`.cursor/rules/`](../rules/) inventory vs AGENTS.

**T6** — [harness-maintenance.mdc](../rules/harness-maintenance.mdc); `rg` stale paths.

**S exit**: **`clean_verify.py --mode align`** exit 0.

If **`scope=align`**, delete **`automation/temp/clean/`** only if no later phase in this run; **stop**.

---

## Phase P — Personal commit and push

Skip if **`scope`** is `align` only, or **`skip_personal_push=yes`**.

1. **`python automation/tools/clean_verify.py --mode secret_scan`**
2. **`git add -A`** (respect `.gitignore`)
3. Commit: **`clean: align harness before publish`**
4. **`git push origin personal`**
5. Delete **`automation/temp/clean/`** before team/public work if regenerating maps.

If **`scope=personal`**, **stop**.

---

## Phase T — Team strip and publish

### T1 — Worktree

Prefer isolated worktree (keeps **`personal`** checkout unchanged):

```text
git fetch origin personal
git worktree remove ../cursor-corner-team-build 2>nul
git worktree add -B team ../cursor-corner-team-build origin/personal
```

Work root: **`../cursor-corner-team-build`**.

### T2 — Strip

1. **`python automation/tools/clean_apply_team.py --root ../cursor-corner-team-build`**
2. **Subagent**: refine team **`pipeline-router.mdc`** — remove **`CLEAN:`** row and hard rules for CLEAN (see contract `team.router`).
3. **`python automation/tools/clean_verify.py --mode team --root ../cursor-corner-team-build`** — loop until pass.

### T3 — Commit and push

Inside worktree:

```text
git add -A
git commit -m "clean: team harness export"
```

**Push policy**:

```text
git ls-remote --heads team
```

- **No heads** (bootstrap): **`git push team team:team`** — direct push once per [clean-contract.json](../../docs/clean-contract.json).
- **Else**: **`git push team HEAD:refs/heads/clean/<YYYYMMDD>-<shortsha>`** then **`gh pr create --repo heatdance/agentic-epic-helper-team --base team --head clean/<...> --title "clean: team harness" --body "CLEAN pipeline; operator must merge."`** — **do not** `gh pr merge`. **Stop** with PR URL.

If **`scope=team`**, remove worktree if desired; **stop**.

---

## Phase U — Public sterilize

### U0 — Branch and legacy delete

1. **`python automation/tools/clean_verify.py --mode semver_next`** (add **`--version M.N`** or **`--confirm-major yes`** from trigger). Expect **`public-1.2`** on first run when no `public-*` exists.
2. **`git fetch releases`**
3. Delete legacy branches (ignore errors if missing):

```text
git push releases --delete release-1.0.0 release-1.1.0
```

### U1 — Public worktree

```text
git worktree remove ../cursor-corner-public-build 2>nul
git worktree add -B public-1.2 ../cursor-corner-public-build team/team
```

(Use branch name from semver step, e.g. **`public-1.2`**.)

### U2 — Transform

1. Regenerate file-map if needed (S1) against team tip context.
2. **Mechanical base**: **`python automation/tools/clean_apply_public.py --root ../cursor-corner-public-build --export-version 1.2.0 --source-branch team --source-sha <team-tip-sha>`**
3. **Subagent (one per playbook id)**: rewrite **`<id>-readme.md`** per [clean-public-style.md](../../docs/clean-public-style.md) (plain English, no org names); load only that readme + style guide.
4. **Subagent (docs)**: ensure **`docs/project.example.json`** etc.; remove live org JSON.
5. **`.agents/`** — neutral [dotagentsprotocol.com](https://dotagentsprotocol.com) layer if not present (see former public-scrub tier).
6. Public **`pipeline-router.mdc`**: guide-only; no executable epic triggers (contract `public.router`).
7. **`python automation/tools/clean_verify.py --mode public --root ../cursor-corner-public-build`** — loop until pass.

### U3 — V2 worktree verify

```text
git -C ../cursor-corner-public-build commit -am "public-export: 1.2.0"
git worktree add ../cursor-corner-public-verify <commit-sha>
python automation/tools/clean_verify.py --mode public --root ../cursor-corner-public-verify
git worktree remove ../cursor-corner-public-verify
```

### U4 — Push

```text
git -C ../cursor-corner-public-build push -u releases public-1.2:public-1.2
```

Update root [README.md](../../README.md) on **personal** only if public branch naming docs need bump (next session).

### U5 — Cleanup

Delete **`automation/temp/clean/`**. Remove team/public worktrees when operator confirms.

---

## Abort criteria

- Branch ≠ **`personal`** at start.
- **`secret_scan`** or **`align`** fails after retry budget.
- **`gh`** unavailable when team remote already has branches (PR required).
- **`public`** blocklist fails after retries.
- Operator declines dirty-tree **`proceed`**.

---

## Phases checklist

| # | Phase | Done when |
|---|--------|-----------|
| 0 | Preflight | On `personal`; preflight OK |
| S1 | File-map | `file-map.json` + verify |
| S2 | Align | `align` verify OK |
| P | Personal | Pushed `origin/personal` |
| T | Team | `team` verify OK; pushed or PR opened |
| U0–U4 | Public | `public-*` verify OK; pushed `releases` |
| 5 | Cleanup | `automation/temp/clean/` deleted |

---

## Downstream

- **Contributors** clone **team** repo; merge PRs — no direct push to **`team`** (repo branch protection recommended).
- **Public** consumers clone [agentic-epic-helper-releases](https://github.com/heatdance/agentic-epic-helper-releases) branch **`public-M.N`** — guide-only.
- **You** keep working on **`personal`**; re-run **`CLEAN:`** after harness or epic changes worth publishing.
