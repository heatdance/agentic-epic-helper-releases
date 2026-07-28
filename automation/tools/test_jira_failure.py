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
    def test_lists_every_artifact_when_epic_dir_exists(self) -> None:
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
                current_step="COVERAGE verify",
            )

        self.assertIn("Corner Epic QA - CRT-659 - failed", comment)
        self.assertIn("Stage: failed at COVERAGE verify", comment)
        self.assertIn("- CRT-659-coverage.json: yes", comment)
        self.assertIn("- CRT-659-analysis.json: no", comment)
        self.assertIn("Next: open the build log", comment)
        self.assertIn("Note: on a COVERAGE verify failure", comment)

    def test_stage_falls_back_to_last_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "epics" / "CRT-659").mkdir(parents=True)
            state = root / ".teamcity-ci" / "state"
            state.mkdir(parents=True)
            (state / "03-epic-prep-verify.ok").write_text(
                "2026-07-28T09:00:00Z | EPIC-PREP verify\n", encoding="utf-8"
            )

            comment = build_failure_comment(
                epic="CRT-659",
                build_url="https://dxcity.example/build/1",
                repo_root=root,
            )

        self.assertIn("Stage: failed after EPIC-PREP verify", comment)

    def test_no_epic_dir_keeps_the_same_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            comment = build_failure_comment(
                epic="CRT-659",
                build_url="https://dxcity.example/build/1",
                repo_root=root,
            )

        self.assertIn("Corner Epic QA - CRT-659 - failed", comment)
        self.assertIn("Artifacts: none in this build", comment)
        self.assertIn("Stage: failed before the first step marker", comment)

    def test_generic_when_epic_unknown(self) -> None:
        comment = build_failure_comment(
            epic="?",
            build_url="unknown",
            repo_root=Path("."),
        )
        self.assertIn("Corner Epic QA - ? - failed", comment)
        self.assertIn("Artifacts: none in this build", comment)


if __name__ == "__main__":
    unittest.main()
