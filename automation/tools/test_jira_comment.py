#!/usr/bin/env python3
"""Tests for the shared Jira comment shape."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR / "teamcity"))

from jira_comment import (  # noqa: E402
    EPIC_ARTIFACTS,
    HEADER_PREFIX,
    STATUS_FAILED,
    STATUS_READY,
    artifact_status,
    last_completed_stage,
    render_comment,
    resolve_epic_json,
)


def _render(status: str, **kwargs) -> str:
    base = {
        "status": status,
        "epic": "CRT-635",
        "build_url": "https://dxcity.example/build/1",
        "stage": "green through ANALYSE verify",
        "next_action": "do the thing",
    }
    base.update(kwargs)
    return render_comment(**base)


class RenderCommentTests(unittest.TestCase):
    def test_both_outcomes_share_block_order(self) -> None:
        artifacts = {name: True for name in EPIC_ARTIFACTS}
        ready = _render(STATUS_READY, artifacts=artifacts).splitlines()
        failed = _render(STATUS_FAILED, artifacts=artifacts).splitlines()

        self.assertTrue(ready[0].startswith(f"{HEADER_PREFIX} - CRT-635 - "))
        self.assertEqual(ready[0].rsplit(" - ", 1)[1], STATUS_READY)
        self.assertEqual(failed[0].rsplit(" - ", 1)[1], STATUS_FAILED)
        for lines in (ready, failed):
            self.assertTrue(lines[2].startswith("Build: "))
            self.assertTrue(lines[3].startswith("Stage: "))
            self.assertEqual(lines[4], "Artifacts: epic-work")
            self.assertTrue(lines[-1].startswith("Next: "))

    def test_artifacts_always_listed_for_every_deliverable(self) -> None:
        comment = _render(STATUS_FAILED, artifacts={"ref.json": True})
        for name in EPIC_ARTIFACTS:
            self.assertIn(f"- CRT-635-{name}: ", comment)
        self.assertIn("- CRT-635-ref.json: yes", comment)
        self.assertIn("- CRT-635-analysis.md: no", comment)

    def test_no_epic_dir_states_absence_instead_of_dropping_the_block(self) -> None:
        comment = _render(STATUS_FAILED, artifacts=None)
        self.assertIn("Artifacts: none in this build", comment)

    def test_coverage_line_only_when_metrics_available(self) -> None:
        self.assertNotIn("Coverage:", _render(STATUS_READY))
        self.assertIn(
            "Coverage: mandated=27 emitted=27",
            _render(STATUS_READY, metrics="mandated=27 emitted=27"),
        )

    def test_notes_follow_next_action(self) -> None:
        comment = _render(STATUS_FAILED, notes=("check the oracle tokens",)).splitlines()
        self.assertTrue(comment[-2].startswith("Next: "))
        self.assertEqual(comment[-1], "Note: check the oracle tokens")


class StateAndPathTests(unittest.TestCase):
    def test_last_stage_uses_highest_step_number_not_lexical_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp)
            (state / "03-epic-prep-verify.ok").write_text(
                "2026-07-28T09:00:00Z | EPIC-PREP verify\n", encoding="utf-8"
            )
            (state / "10-analyse-verify.ok").write_text(
                "2026-07-28T09:23:49Z | ANALYSE verify\n", encoding="utf-8"
            )

            self.assertEqual(last_completed_stage(state), "ANALYSE verify")

    def test_last_stage_none_without_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(last_completed_stage(Path(tmp)))

    def test_artifact_status_finds_dependencies_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            epic_dir = Path(tmp) / "CRT-635"
            (epic_dir / "dependencies").mkdir(parents=True)
            (epic_dir / "dependencies" / "CRT-635-ref.json").write_text("{}", encoding="utf-8")
            (epic_dir / "CRT-635-coverage.md").write_text("x", encoding="utf-8")

            status = artifact_status(epic_dir, "CRT-635")

        self.assertTrue(status["ref.json"])
        self.assertTrue(status["coverage.md"])
        self.assertFalse(status["coverage.json"])

    def test_resolve_epic_json_prefers_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            epic_dir = Path(tmp) / "CRT-635"
            (epic_dir / "dependencies").mkdir(parents=True)
            (epic_dir / "dependencies" / "CRT-635-ref.json").write_text("{}", encoding="utf-8")
            (epic_dir / "CRT-635-ref.json").write_text("{}", encoding="utf-8")

            resolved = resolve_epic_json(epic_dir, "CRT-635", "ref")

        self.assertEqual(resolved.parent.name, "dependencies")


if __name__ == "__main__":
    unittest.main()
