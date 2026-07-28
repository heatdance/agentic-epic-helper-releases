#!/usr/bin/env python3
"""Tests for jira_success ref resolution."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR / "teamcity"))

import jira_success  # noqa: E402


class ResolveRefTests(unittest.TestCase):
    def test_repo_root_is_the_repo_not_automation(self) -> None:
        """REPO_ROOT must hold epics/, not automation/ (step 11 looked one level too deep)."""
        self.assertTrue((jira_success.REPO_ROOT / "epics").is_dir())
        self.assertNotEqual(jira_success.REPO_ROOT.name, "automation")

    def test_prefers_dependencies_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dep = root / "epics" / "CRT-661" / "dependencies"
            dep.mkdir(parents=True)
            (dep / "CRT-661-ref.json").write_text("{}", encoding="utf-8")

            resolved = jira_success._resolve_ref("CRT-661", repo_root=root)

        self.assertEqual(resolved.parent.name, "dependencies")

    def test_falls_back_to_legacy_epic_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            epic_dir = root / "epics" / "CRT-661"
            epic_dir.mkdir(parents=True)
            (epic_dir / "CRT-661-ref.json").write_text("{}", encoding="utf-8")

            resolved = jira_success._resolve_ref("CRT-661", repo_root=root)

        self.assertEqual(resolved.parent.name, "CRT-661")

    def test_missing_ref_reports_dependencies_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            resolved = jira_success._resolve_ref("CRT-661", repo_root=root)

        self.assertFalse(resolved.is_file())
        self.assertEqual(resolved.parent.name, "dependencies")


if __name__ == "__main__":
    unittest.main()
