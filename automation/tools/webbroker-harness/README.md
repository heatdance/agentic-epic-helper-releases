# WebBroker harness tools

## Location parity (`check_locations_parity.py`)

From repository root:

```bash
python automation/tools/webbroker-harness/check_locations_parity.py
```

Uses by default:

- `docs/webbroker-harness/concept-map.json`
- `docs/webbroker-harness/locations/ctqa.json`

**Pass:** every `priority: "compass"` feature has a `locations` entry; keys are a subset of concept-map feature ids; each compass row has `primary_path_ok: true` **or** non-empty `drift_notes`.

Optional: `--repo PATH` if the repo root is not three levels above this script.

## Bootstrap (optional)

`bootstrap_ctqa_locations.py` can emit a skeleton `ctqa.json` with login-gated drift. It does **not** replace live Chrome DevTools MCP verification.
