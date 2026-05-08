#!/usr/bin/env python3
"""Placeholder for test-bench metrics aggregation (TBD).

Operators: use qualitative review per
`.cursor/benchmark/test-bench/pipeline/validator-test.md`.

When implemented, this script should consume `test-bench/runs/run-*/` or hub
shadow `-tests.json` snapshots similarly to `coverage-bench/scripts/compare_runs.py`.
"""

from __future__ import annotations

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Test-bench snapshot compare (not implemented).",
    )
    parser.parse_args()
    print(
        "compare_test_runs.py is not implemented yet — see "
        ".cursor/benchmark/test-bench/pipeline/validator-test.md",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
