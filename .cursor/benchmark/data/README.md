# Benchmark gold (`<KEY>-gold.json`)

Stable **oracle** JSON files for coverage-bench **`compare_runs.py`** thresholds and validators. One file per epic when you benchmark that epic:

```text
.cursor/benchmark/data/<KEY>-gold.json
```

Example: **`CRT-639-gold.json`** next to this README.

## Schema

Use **[`coverage-bench/HOW-TO.md`](../coverage-bench/HOW-TO.md) § Gold file schema** — `structured_assertions`, `structured_assertions.thresholds`, `pipeline`, etc.

## Resolution in tooling

[`compare_runs.py`](../coverage-bench/scripts/compare_runs.py) searches (in order):

1. Explicit **`--gold-root`** (directory containing `<KEY>-gold.json`)
2. **This directory** (`.cursor/benchmark/data/`)
3. Legacy **`coverage-bench/data/`**

`*.gitignore` ignores **`*-gold.json`** here so local oracles are not committed by default; this README documents the canonical path operator-side.
