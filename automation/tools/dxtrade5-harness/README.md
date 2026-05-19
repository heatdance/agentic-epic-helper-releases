# dxTrade5 harness — automation helpers

| Script | Purpose |
|--------|---------|
| [check_locations_parity.py](check_locations_parity.py) | Ensure every **compass** feature in `docs/dxtrade5-harness/concept-map.json` has an entry in `docs/dxtrade5-harness/locations/ctqa.json` with `primary_path_ok` or non-empty `drift_notes`. Run from repo root: `python automation/tools/dxtrade5-harness/check_locations_parity.py` |
| [bootstrap_ctqa_locations.py](bootstrap_ctqa_locations.py) | Regenerate a **bootstrap** `locations/ctqa.json` from concept + IA maps (login gate placeholders). Use only when intentionally resetting Stage 3; prefer editing `ctqa.json` after live waves. |
