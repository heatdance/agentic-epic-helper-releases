#!/usr/bin/env python3
"""Tests for the published-paste fidelity gate in coverage_verify."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR))

import coverage_verify  # noqa: E402

FIXTURES = TOOLS_DIR / "fixtures" / "coverage"


def _contract() -> dict:
    return json.loads(coverage_verify.CONTRACT_PATH.read_text(encoding="utf-8"))


def _coverage(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class PasteFidelityTests(unittest.TestCase):
    def test_target_paste_passes(self) -> None:
        errors = coverage_verify.verify_markdown_paste_fidelity(
            _coverage("crt635-target-good-coverage.json"),
            FIXTURES / "crt635-target-good.md",
            _contract(),
        )

        self.assertEqual(errors, [])

    def test_dropped_console_recipe_fails(self) -> None:
        """The build-47 regression: verified console lines lived in JSON only."""
        errors = coverage_verify.verify_markdown_paste_fidelity(
            _coverage("crt635-paste-drift-bad-coverage.json"),
            FIXTURES / "crt635-paste-drift-bad.md",
            _contract(),
        )

        ids = {e.split(":", 1)[0] for e in errors}
        self.assertEqual(
            ids,
            {
                "markdown_paste_missing_detail",
                "markdown_paste_missing_scenario",
                "markdown_paste_drift",
            },
        )
        self.assertTrue(any("use bro1:bro1_usd" in e for e in errors))

    def test_extra_paste_sections_are_allowed(self) -> None:
        coverage = _coverage("crt635-target-good-coverage.json")
        md = FIXTURES / "crt635-target-good.md"
        extended = TOOLS_DIR / "fixtures" / "coverage" / "_tmp-extended.md"
        extended.write_text(
            md.read_text(encoding="utf-8") + "\n## Not attempted\n\n- Out of epic — reason\n",
            encoding="utf-8",
        )
        try:
            errors = coverage_verify.verify_markdown_paste_fidelity(
                coverage, extended, _contract()
            )
        finally:
            extended.unlink()

        self.assertEqual(errors, [])

    def test_absent_md_is_not_an_error(self) -> None:
        errors = coverage_verify.verify_markdown_paste_fidelity(
            _coverage("crt635-target-good-coverage.json"), None, _contract()
        )

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
