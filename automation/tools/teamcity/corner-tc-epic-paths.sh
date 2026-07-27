#!/usr/bin/env bash
# Epic artifact paths for TeamCity (dependencies layout; legacy root JSON fallback for verify).
set -u

_corner_tc_paths_py() {
  REPO_ROOT="${REPO_ROOT:-$PWD}" python3 - "$@" <<'PY'
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(os.environ.get("REPO_ROOT", os.getcwd())) / "automation" / "tools"))
from epic_paths import coverage_md, dep_json, resolve_json, resolve_md

root = Path(os.environ.get("REPO_ROOT", os.getcwd()))
cmd = sys.argv[1]
epic = sys.argv[2]

if cmd == "dep_json":
    stem = sys.argv[3]
    print(dep_json(epic, stem, root))
elif cmd == "resolve_json":
    stem = sys.argv[3]
    print(resolve_json(epic, stem, root))
elif cmd == "coverage_md":
    print(coverage_md(epic, root))
elif cmd == "resolve_md":
    kind = sys.argv[3]
    print(resolve_md(epic, kind, root))
else:
    raise SystemExit(f"unknown cmd: {cmd}")
PY
}

# Canonical write target (dependencies/ for JSON).
corner_tc_dep_json() {
  _corner_tc_paths_py dep_json "$1" "$2"
}

# Resolve existing JSON (dependencies/ then legacy epic root).
corner_tc_resolve_json() {
  _corner_tc_paths_py resolve_json "$1" "$2"
}

corner_tc_coverage_md() {
  _corner_tc_paths_py coverage_md "$1"
}

corner_tc_resolve_md() {
  _corner_tc_paths_py resolve_md "$1" "$2"
}
