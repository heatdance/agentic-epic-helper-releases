#!/usr/bin/env python3
"""Tests for jira_failure.build_failure_comment."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR / "teamcity"))

from jira_failure import build_failure_comment  # noqa: E402


class BuildFailureCommentTests(unittest.TestCase):
    def test_partial_when_ref_and_coverage_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            epic_dir = root / "epics" / "CRT-659"
            epic_dir.mkdir(parents=True)
            (epic_dir / "CRT-659-ref.json").write_text("{}", encoding="utf-8")
            (epic_dir / "CRT-659-coverage.json").write_text("{}", encoding="utf-8")

            comment = build_failure_comment(
                epic="CRT-659",
                build_url="https://dxcity.example/build/1",
                repo_root=root,
            )

        self.assertIn("partial outputs available", comment)
        self.assertIn("CRT-659-coverage.json: yes", comment)
        self.assertIn("CRT-659-analysis.json: no", comment)
        self.assertIn("forbidden oracle enum tokens", comment)

    def test_generic_when_no_epic_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            comment = build_failure_comment(
                epic="CRT-659",
                build_url="https://dxcity.example/build/1",
                repo_root=root,
            )

        self.assertNotIn("partial outputs available", comment)
        self.assertIn("pipeline failed for CRT-659", comment)
        self.assertIn("partial outputs may be in TeamCity artifacts epic-work", comment)

    def test_generic_when_epic_unknown(self) -> None:
        comment = build_failure_comment(
            epic="?",
            build_url="unknown",
            repo_root=Path("."),
        )
        self.assertNotIn("partial outputs available", comment)
        self.assertIn("pipeline failed for ?", comment)


if __name__ == "__main__":
    unittest.main()
