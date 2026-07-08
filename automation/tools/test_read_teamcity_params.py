#!/usr/bin/env python3
"""Tests for read_teamcity_params.py TeamCity property export helpers."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
READ_PARAMS = TOOLS_DIR / "teamcity" / "read_teamcity_params.py"


class ReadTeamcityParamsTests(unittest.TestCase):
    def test_teamcity_build_url_alias_export(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".properties", delete=False) as fh:
            fh.write("teamcity.build.url=https://dxcity.example/viewLog.html?buildId=123\n")
            props_path = fh.name
        self.addCleanup(lambda: os.unlink(props_path))
        env = os.environ.copy()
        env.pop("TEAMCITY_BUILD_URL", None)
        env["TEAMCITY_BUILD_PROPERTIES_FILE"] = props_path
        result = subprocess.run(
            [sys.executable, str(READ_PARAMS)],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn(
            "export TEAMCITY_BUILD_URL='https://dxcity.example/viewLog.html?buildId=123'",
            result.stdout,
        )

    def test_resolve_prefers_env_over_properties(self) -> None:
        sys.path.insert(0, str(TOOLS_DIR / "teamcity"))
        try:
            from read_teamcity_params import resolve_teamcity_build_url

            props = {"teamcity.build.url": "https://from-props.example/"}
            with mock.patch.dict(os.environ, {"TEAMCITY_BUILD_URL": "https://from-env.example/"}):
                self.assertEqual(
                    resolve_teamcity_build_url(props=props),
                    "https://from-env.example/",
                )
        finally:
            sys.path.pop(0)


if __name__ == "__main__":
    unittest.main()
