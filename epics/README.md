# Per-epic context (`<EPIC-KEY>-ref.json`)

For **one Epic at a time**, the durable handoff file is **`epics/<EPIC-KEY>/<EPIC-KEY>-ref.json`** while the epic is **open**; after **`CLOSE:`**, JSON moves to **`epics/<KEY>/context/`** (three human **`.md`** stay at epic root). Copy the schema from [templates/epic-ref.json](templates/epic-ref.json).

**Pipeline `EPIC-PREP:`** — playbook: [`.cursor/pipelines/epic-prep.md`](../.cursor/pipelines/epic-prep.md). Verifier: [epic-prep-verify.md](../automation/docs/epic-prep-verify.md).

# Per-epic coverage (`<EPIC-KEY>-coverage.json` / `.md`)

After **`-ref.json`**, pipeline **`COVERAGE:`** produces **`-coverage.json`** + **`-coverage.md`**. At **coverage review** (human gate), edit **`-coverage.md`** and set **`scenario_groups[]`** + **`coverage_frozen_at`**. Playbook: [`.cursor/pipelines/coverage.md`](../.cursor/pipelines/coverage.md).

# Per-epic GROUND (in-place coverage updates)

**`GROUND:`** — console probes on frozen coverage checks; requires CTQA env. Playbook: [`.cursor/pipelines/ground.md`](../.cursor/pipelines/ground.md).

# Per-epic analysis (`<EPIC-KEY>-analysis.json` / `.md`)

After coverage + GROUND, **`ANALYSE:`** produces gap audit. Playbook: [`.cursor/pipelines/analysis.md`](../.cursor/pipelines/analysis.md).

# Per-epic discovery linker (`<EPIC-KEY>-discover.json`)

After frozen coverage, **`TEST-DISCOVER:`** produces **linker map only** — **no browser**. Playbook: [`.cursor/pipelines/test-discover.md`](../.cursor/pipelines/test-discover.md).

# Per-epic test prep (`<EPIC-KEY>-tests.json` / `.md`)

After linker discover, **`TEST-PREP:`** produces **scenario intent drafts** (not final CRTQA steps). Default profile **`scenario_intent`**; one bundle per **`scenario_groups[]`** row. **No env gate** for generation. Playbook: [`.cursor/pipelines/test-prep.md`](../.cursor/pipelines/test-prep.md).

# Per-epic close (`<EPIC-KEY>-close.json`, `context/`)

After **`-tests.json`**, **`CLOSE:`** requires **`-ref.json`**, **`-coverage.json`**, **`-discover.json`**, **`-tests.json`** at epic root (**`-precon.json`** optional legacy). Regenerates **three** root **`.md`**; archives JSON to **`context/`**. Playbook: [`.cursor/pipelines/close.md`](../.cursor/pipelines/close.md).

# Production chain (draft_truth_v3)

```text
EPIC-PREP → COVERAGE → GROUND → ANALYSE → coverage_review (+ scenario_groups[])
  → TEST-DISCOVER (linker) → TEST-PREP (scenario_intent) → CLOSE
```

**Orchestrator:** **`/epic-helper`** — [`.cursor/commands/epic-helper.md`](../.cursor/commands/epic-helper.md).

**Legacy (not in default chain):** **`TEST-PRECON:`**, **`COVERAGE-REINFORCE:`**.

# Repo-wide harness

- **`/clean`** — **`personal` branch only** — [`.cursor/commands/clean.md`](../.cursor/commands/clean.md) · [`.cursor/pipelines/clean.md`](../.cursor/pipelines/clean.md)
- **`/epic-calibrate`** — post-hoc prod vs gold — [automation/docs/calibrate.md](../automation/docs/calibrate.md)

Router: [.cursor/rules/pipeline-router.mdc](../.cursor/rules/pipeline-router.mdc).
