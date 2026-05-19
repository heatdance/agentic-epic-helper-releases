# dxTrade5 UI harness

Agent-facing **three-stage map** for **dxTrade5**-class web trading UI (Corner Trader QA context): **concept** (what exists) → **IA** (where it lives in product language) → **locations** (verified navigation on a target host).

**Default QA shell** for Stage 3 grounding: `https://ctqa.prosp.devexperts.com/` (see [docs/corner-platform-map.json](../corner-platform-map.json) for full environment policy).

## Truth order

1. **Live UI** on the deployment you are testing — layout and labels win for *where* something is today.
2. **Stage 2** [`ia-map.json`](ia-map.json) — navigation paths in stable wording (menu titles, regions).
3. **Stage 1** [`concept-map.json`](concept-map.json) — capabilities, dependencies, and requirement references for *what* — not DOM selectors.
4. **Confluence** (CT/DR) and **Figma** — orientation and vocabulary; may lag a given build.

Do not treat wiki or design files as executable truth for a specific host without confirming in the browser (Chrome DevTools MCP: [automation/docs/chrome-devtools-mcp.md](../../automation/docs/chrome-devtools-mcp.md)).

## Files

| File | Stage | Role |
|------|-------|------|
| [dxtrade5-harness.json](dxtrade5-harness.json) | Meta | Tier sequence, staleness doctrine, related reads |
| [concept-map.json](concept-map.json) | 1 | Feature IDs, intent, deps, Confluence/Figma source refs — **no selectors** |
| [ia-map.json](ia-map.json) | 2 | Area tree + `feature_paths[]` with `primary_path` per `concept-map` feature |
| [ia-map-stage2.md](ia-map-stage2.md) | 2 | Human-readable duplicate of Stage 2 JSON (kept in sync with `ia-map.json`) |
| [locations/README.md](locations/README.md) | 3 | Stage 3 policy; links **`ctqa.json`**, **PHASE0**, **WAVES** |
| [locations/ctqa.json](locations/ctqa.json) | 3 | CTQA location layer (`wave`, `verify`, `drift_notes`) — load **slices** in LLM context, not the whole file |
| [locations/PHASE0.md](locations/PHASE0.md) | 3 | Operator prep: MCP, role, auth handoff |
| [locations/WAVES.md](locations/WAVES.md) | 3 | Subagent wave briefs (W1–W4) + merge |

Parity (compass vs `locations`): `python automation/tools/dxtrade5-harness/check_locations_parity.py` (repo root).

## Confluence anchors

- **Corner Trader requirements hub:** [Cornertrader Requirements](https://confluence.in.devexperts.com/pages/viewpage.action?pageId=342171997) (CT `342171997`) — TOC hub; child pages hold widget-level specs.
- **dxProduct / dxBro hub:** [dxBro Requirements](https://confluence.in.devexperts.com/pages/viewpage.action?pageId=254224494) (DR `254224494`) — browse subtree for platform-wide WEB/mobile specs (baseline product vocabulary).

## Figma

- **Team project (file enumeration):** [Figma project](https://www.figma.com/files/812379849205775254/project/335034859?fuid=909086425388392671) — open in Figma; use **share link on a file or frame** when you need MCP.
- **Figma MCP** ([automation/docs/figma-mcp.md](../../automation/docs/figma-mcp.md)): `get_figma_data` requires a **`fileKey`** from a `figma.com/file/...` or `figma.com/design/...` URL, not the project-only URL. Add `fileKey` + optional `node-id` to [`concept-map.json`](concept-map.json) as you attach frames to features.

## Harness registry

Tiered discovery: **[docs/harness-map.json](../harness-map.json)** T1 package **`dxtrade5_harness`**.
