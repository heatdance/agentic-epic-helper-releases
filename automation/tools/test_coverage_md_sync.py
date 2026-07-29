#!/usr/bin/env python3
"""Tests for operator hint scoping in coverage_md_sync."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR))

import coverage_md_sync  # noqa: E402

FIXTURES = TOOLS_DIR / "fixtures" / "coverage"
CRT_594_WORDING = (
    "CornerTraderFxConfiguration",
    "midpoint must match",
    "Mark column",
    "bid/ask reflects",
    "TextConfiguration tier",
)


def _setup_check_lines(coverage: dict) -> list[str]:
    for chk in coverage["checks"]:
        if str(chk.get("id", "")).startswith("chk-s"):
            return [str(x) for x in (chk.get("detail_lines") or [])]
    raise AssertionError("fixture has no setup check")


class HintScopeTests(unittest.TestCase):
    def test_hints_stay_inside_their_epic(self) -> None:
        """CRT-594 wording must not reach another epic through positional check ids."""
        coverage = json.loads(
            (FIXTURES / "crt635-target-good-coverage.json").read_text(encoding="utf-8")
        )

        coverage_md_sync.sync_coverage(coverage)

        md = coverage["smart_checklist_markdown"]
        for wording in CRT_594_WORDING:
            self.assertNotIn(wording, md)

    def test_verified_setup_lines_survive_the_builder(self) -> None:
        coverage = json.loads(
            (FIXTURES / "crt635-paste-drift-bad-coverage.json").read_text(encoding="utf-8")
        )

        coverage_md_sync.sync_coverage(coverage)

        self.assertIn("use bro1:bro1_usd", coverage["smart_checklist_markdown"])

    def test_bare_setup_check_gets_hints_for_the_scoped_epic(self) -> None:
        coverage = {
            "epic_key": "CRT-594",
            "checks": [
                {
                    "id": "chk-s1",
                    "section": "## Prerequisites",
                    "scenario_line": "- [CRT-594] Account groups configured",
                    "detail_lines": ["> Discover: fixture account_group_environment_setup fx-1."],
                }
            ],
        }

        coverage_md_sync.sync_coverage(coverage)

        lines = _setup_check_lines(coverage)
        self.assertTrue(any("CornerTraderFxConfiguration" in x for x in lines))
        self.assertFalse(any(x.startswith("> Discover:") for x in lines))

    def test_hints_do_not_overwrite_existing_operator_lines(self) -> None:
        coverage = {
            "epic_key": "CRT-594",
            "checks": [
                {
                    "id": "chk-s1",
                    "section": "## Prerequisites",
                    "scenario_line": "- [CRT-594] Account groups configured",
                    "detail_lines": ["> Verified on CTQA: use bro1:bro1_usd"],
                }
            ],
        }

        coverage_md_sync.sync_coverage(coverage)

        self.assertEqual(_setup_check_lines(coverage), ["> Verified on CTQA: use bro1:bro1_usd"])


if __name__ == "__main__":
    unittest.main()
