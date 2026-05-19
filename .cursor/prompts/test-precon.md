# TEST-PRECON subprocess scaffold (v5 — case outlines)

**Playbook:** [`.cursor/pipelines/test-precon.md`](../pipelines/test-precon.md)

**Ladder:** [`docs/exploration-depth-ladder.json`](../../docs/exploration-depth-ladder.json)

**Verifier:** [`automation/tools/precon_verify.py`](../../automation/tools/precon_verify.py) + [`--discover`](../../automation/docs/precon-verify.md)

## Orchestrator

0. **MUST** `jq` project **`-coverage.json`**, optional **`-discover.json`**, **`-ref.json`**, **`-analysis.json`** per [automation/docs/jq.md](../../automation/docs/jq.md) before Read (phase 1); see playbook Phase 1 filters.
1. Phase **0** → smoke only (`depth_level: smoke` in 0c logs only).
2. Phase **2** skeleton → **2b** case outlines (one subprocess per bundle) → **`session_placeholders`**, **`command_patterns`** on epic root.
3. Phase **3** clusters.
4. Per cluster: **4R** → **4D** → **4C** → **4V** (max 3) → **4A** author.
5. Phase **5** emit **schema_version 5** + `precon_verify.py --md`.

## Subprocess 2b (case outline per bundle)

**Write:** `{EpicDir}temp/precon-outline-<bundle_id>.json` → merge into `test_skeleton[].case_outline[]`.

Required per row: `case_id`, `check_id`, `title`, `intent`; optional `pattern_ref` (e.g. `ladder_step`).

Optional **`shape_ref=benchmark`** on trigger **only with both benchmark tokens**: titles from bench JSON only. **Phase 2b**: seed **`case_outline[]`** from coverage **`checks[]`** + ref **`obligations_proposed[]`**.

## Subprocess 4R (replay discover fixture)

**Write:** `{EpicDir}temp/precon-explore-<cluster_id>-<fix_id>.json`

```json
{
  "cluster_id": "pc-001",
  "discover_fixture_id": "fix-003",
  "exploration_log": [
    {
      "depth_level": "discover_probe",
      "replay_of": "discover_probe",
      "discover_fixture_id": "fix-003",
      "surface": "webbroker",
      "view_id": "position_book_drilled",
      "action": "...",
      "outcome": "pass",
      "login_state": "authenticated",
      "widgets_seen": []
    }
  ]
}
```

Re-run discover probe steps from [`discover-fixture-probes.json`](../../docs/discover-fixture-probes.json) in the browser/console — do not only read discover JSON.

## Subprocess 4D (FE deepen per surface)

**Write:** `{EpicDir}temp/precon-explore-<cluster_id>-<surface>.json`

- Chrome: **lock** → navigate → snapshot → **unlock** after each navigation.
- One **`precon_drill`** row per required **`view_id`** from ladder.
- Distinct ISO **`at`** per row.
- WebBroker: drill into User Management forms, not menu labels only.

## Subprocess 4C (console)

**Write:** `{EpicDir}temp/precon-explore-<cluster_id>-console.json`

- Read-only extended `show` when discover notes have account/instrument/group evidence.
- No mutating commands.

## Subprocess 4A (author)

Only set **`provenance: exploration`** when **`precon_drill`** logs exist for that step's surface/intent.
