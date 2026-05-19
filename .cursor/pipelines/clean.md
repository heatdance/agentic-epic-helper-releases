# Pipeline: CLEAN (align, publish personal, team, public)

**Trigger**: user message starts with **`CLEAN:`**. Optional tokens on the same line:

| Token | Meaning |
|-------|---------|
| **`scope=full`** (default) | Phases **0 → S → P → T → U → U5** |
| **`scope=align`** | **S** only |
| **`scope=personal`** | **S → P** |
| **`scope=team`** | **T** (after personal is pushed) |
| **`scope=public`** | **U → U5** (requires current `team/team`) |
| **`version=M.N`** | Force public branch `public-M.N` (e.g. `version=1.2`) |
| **`confirm_major=yes`** | Required after latest `public-M.9` to create `public-{M+1}.0` |
| **`skip_personal_push=yes`** | Run align without commit/push (testing) |
| **`proceed`** | Acknowledge dirty working tree on personal |

**Scope**: One publish run from branch **`personal` only**. **Router**: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc). **Contract**: [`docs/clean-contract.json`](../../docs/clean-contract.json). **Verifier**: [`automation/tools/clean_verify.py`](../../automation/tools/clean_verify.py). **Style (public)**: [`docs/clean-public-style.md`](../../docs/clean-public-style.md). **Remediation (one-time)**: [`automation/docs/clean-remediation.md`](../../automation/docs/clean-remediation.md).

**Hard invariant**: Do **not** run **`CLEAN:`** while checked out on **`team`** or **`public-*`**. End every full run on **`personal`** with **no extra worktrees** and **no `clean/*` or `release-*`** on `team` / `releases` remotes.

**Branch model (three lines only)**: `origin/personal` → `team/team` → `releases/public-M.N` (single current public line). **Sequential checkout** in this repo — **no** worktrees, **no** `clean/*` PR branches.

**Ephemeral**: [`automation/temp/clean/`](../../automation/temp/clean/) only. Delete before team/public commits. Durable JSON must **not** reference paths under `automation/temp/clean/`.

**Replaces**: former **`SYNC:`** and **`PUBLIC-SCRUB:`**. Do not invoke those triggers.

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
2. **`git branch --show-current`** must be **`personal`**. Else **`git checkout personal`**
3. **`git fetch origin team releases`**
4. Remove stale worktrees if present:
   - `git worktree remove ../cursor-corner-team-build --force` (ignore errors)
   - `git worktree remove ../cursor-corner-public-build --force` (ignore errors)
   - `git worktree prune`
5. **`python automation/tools/clean_verify.py --mode preflight`** (fails if extra worktrees remain)
6. If working tree dirty: show **`git status -sb`**; **stop** until **`proceed`** on the trigger line
7. Parse **`scope=`** (default `full`)

---

## Phase S — Align

### S1 — File-map

1. Ensure **`automation/temp/clean/`** exists.
2. SoT: [`docs/clean-publish-tier-matrix.json`](../../docs/clean-publish-tier-matrix.json).
3. **`python automation/tools/clean_file_map.py`** → **`automation/temp/clean/file-map.json`**
4. **`python automation/tools/clean_verify.py --mode file_map`**

### S2 — Harness align (T0–T6)

After each tier subprocess: **`clean_verify.py --mode align`** (retry until pass; escalate after **10** failures).

| Pipeline id | Trigger | Playbook |
|-------------|---------|----------|
| `epic-prep` | **`EPIC-PREP:`** | [epic-prep.md](epic-prep.md) |
| `coverage` | **`COVERAGE:`** | [coverage.md](coverage.md) |
| `analysis` | **`ANALYSE:`** | [analysis.md](analysis.md) |
| `test-discover` | **`TEST-DISCOVER:`** | [test-discover.md](test-discover.md) |
| `test-precon` | **`TEST-PRECON:`** | [test-precon.md](test-precon.md) |
| `test-prep` | **`TEST-PREP:`** | [test-prep.md](test-prep.md) |
| `close` | **`CLOSE:`** | [close.md](close.md) |
| `clean` | **`CLEAN:`** | [clean.md](clean.md) (this file) |

**S exit**: **`align`** OK. If **`scope=align`**, delete **`automation/temp/clean/`** when done; **stop**.

---

## Phase P — Personal commit and push

Skip if **`scope=align`** or **`skip_personal_push=yes`**.

1. Stay on **`personal`**
2. **`python automation/tools/clean_verify.py --mode secret_scan`**
3. **`git add -A`** · commit **`clean: align harness before publish`**
4. **`git push origin personal`**
5. Delete **`automation/temp/clean/`** before Phase T

If **`scope=personal`**, **stop**.

---

## Phase T — Team strip and direct push

**Input**: `origin/personal` tip. **Output**: `team/team` updated in place. **No new branch names.**

```text
git fetch origin personal
git fetch team team
git checkout team
```

If local **`team`** is missing: **`git branch -f team team/team`** then **`git checkout team`**.

```text
git reset --hard origin/personal
python automation/tools/clean_apply_team.py --root .
python automation/tools/clean_verify.py --mode team --root .
git add -A
git commit -m "clean: team harness export"
TEAM_SHA=$(git rev-parse HEAD)
git push team team
python automation/tools/clean_verify.py --mode prune_team_remote
python automation/tools/clean_verify.py --mode team_tip --sha %TEAM_SHA%
git checkout personal
```

- **`prune_team_remote`**: deletes every head on **`team`** remote except **`team`** (removes prior `clean/*` PR branches).
- Record **`TEAM_SHA`** for Phase U gate.

If **`scope=team`**, run **`postflight`** (Phase U5) or at minimum **`git checkout personal`**; **stop**.

---

## Phase U — Public sterilize (from `team/team` only)

### U0 — Semver and legacy

```text
git fetch releases team
python automation/tools/clean_verify.py --mode semver_next --json
```

Parse **`target_branch`**, **`superseded_branch`**, **`export_version`**.

```text
python automation/tools/clean_public_supersede.py --legacy-only
python automation/tools/clean_verify.py --mode legacy_remote
```

**Abort** if **`legacy_remote`** fails (any **`release-*`** still on `releases`).

**Gate**: **`python automation/tools/clean_verify.py --mode team_tip --sha <TEAM_SHA>`** must pass before creating the public branch.

### U1 — Checkout public target from team tip

```text
git checkout -B <target_branch> team/team
```

Example: **`git checkout -B public-1.4 team/team`**.

### U2 — Transform and verify (in place)

Mechanical public transform (no agent improvisation for readmes):

- Seeds from [`docs/clean-public-content/`](../../docs/clean-public-content/) (entry docs + pipeline `*-readme.md`)
- Template overlays from [`epics/templates/public/`](../../epics/templates/public/) per [`docs/clean-contract.json`](../../docs/clean-contract.json) `public.template_overlays`
- Deletes `.cursor/mcp.json.example` and other `public.delete_paths`

```text
python automation/tools/clean_apply_public.py --root . --export-version <export_version> --source-branch team --source-sha <TEAM_SHA>
python automation/tools/clean_verify.py --mode public --root .
git add -A
git commit -m "public-export: <export_version>"
python automation/tools/clean_verify.py --mode public --root .
git push -u releases <target_branch>:<target_branch>
```

### U4b — Supersede

Only when **`superseded_branch`** is non-null from semver JSON.

```text
python automation/tools/clean_public_supersede.py --target <target_branch> --superseded <superseded_branch>
python automation/tools/clean_verify.py --mode public_remote --superseded <superseded_branch>
```

**Re-publish same `version=M.N`:** **`superseded_branch`** is **`null`** — skip U4b.

```text
git checkout personal
git branch -D <superseded_branch>
```

Also delete stale local names if present: **`release-1.1.0`**, **`public-1.1`** (legacy tracking branches).

---

## Phase U5 — Postflight (mandatory)

```text
git checkout personal
Remove-Item -Recurse -Force automation/temp/clean -ErrorAction SilentlyContinue
python automation/tools/clean_verify.py --mode postflight
```

**Done when**: on **`personal`**; **`postflight`** OK; remotes match [branch_policy](../../docs/clean-contract.json).

---

## Abort criteria

- Branch ≠ **`personal`** at start (or not returned to **`personal`** at end).
- Extra worktrees after Phase 0 cleanup.
- **`secret_scan`** / **`align`** fails after retry budget.
- Phase U without passing **`team_tip`** for recorded **`TEAM_SHA`**.
- **`legacy_remote`** fails after U0.
- **`postflight`** fails (`clean/*`, `release-*`, or multiple `public-*` on remotes).
- Operator declines dirty-tree **`proceed`**.

---

## Phases checklist

| # | Phase | Done when |
|---|--------|-----------|
| 0 | Preflight | On `personal`; no worktrees; preflight OK |
| S | Align | `align` OK |
| P | Personal | Pushed `origin/personal` |
| T | Team | `team` verify OK; `team/team` pushed; `prune_team_remote` OK |
| U | Public | From `team/team`; pushed `releases/<target>`; supersede + `legacy_remote` OK |
| U5 | Postflight | On `personal`; `postflight` OK |

---

## Downstream

- **Contributors** clone [agentic-epic-helper-team](https://github.com/heatdance/agentic-epic-helper-team) branch **`team`** — no `clean/*` flow.
- **Public** consumers clone [agentic-epic-helper-releases](https://github.com/heatdance/agentic-epic-helper-releases) branch **`public-M.N`** (single current line) — guide-only.
- **Maintainers** work on **`personal`**; re-run **`CLEAN:`** after harness changes worth publishing.
