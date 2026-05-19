# WebBroker UI harness (in progress)

Agent-facing **three-stage** workflow for **dealer WebBroker** web UI—same pattern as [docs/dxtrade5-harness](../dxtrade5-harness/README.md): **concept** → **IA** → **locations** (live browser truth on a target host).

**Use this first:** [`AGENT-STAGE-PLAN.md`](AGENT-STAGE-PLAN.md) — copy the stage you are in into **Plan** mode for structured execution.

**Default CT QA URL (WebBroker app path):** `https://ctqa.prosp.devexperts.com/webbroker/` — see [docs/corner-platform-map.json](../corner-platform-map.json) (`environments[].application_urls.webbroker`).

| Stage | Artifact | Status |
|-------|-----------|--------|
| 1 | [`concept-map.json`](concept-map.json) | Present |
| 2 | [`ia-map.json`](ia-map.json), [`ia-map-stage2.md`](ia-map-stage2.md) | Present |
| 3 | [`locations/README.md`](locations/README.md), [`locations/ctqa.json`](locations/ctqa.json), [`webbroker-harness.json`](webbroker-harness.json) | Present |
