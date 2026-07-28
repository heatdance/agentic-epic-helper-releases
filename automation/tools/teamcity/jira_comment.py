#!/usr/bin/env python3
"""One shape for every Jira comment the pipeline posts.

Success and failure previously rendered independently, so a ticket accumulated
three different layouts and the artifact list appeared only on some failures.
Both steps now call render_comment with the same block order:

    Corner Epic QA - <EPIC> - <status>

    Build: <url>
    Stage: <where the run got to>
    Artifacts: epic-work
    - <EPIC>-ref.json: yes
    ...
    Coverage: mandated=27 emitted=27 checks=24 density=0.89 unmatched=3
    Next: <one action>
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

HEADER_PREFIX = "Corner Epic QA"
STATUS_READY = "ready"
STATUS_FAILED = "failed"

EPIC_ARTIFACTS = (
    "ref.json",
    "coverage.json",
    "coverage.md",
    "analysis.json",
    "analysis.md",
)

# .teamcity-ci/state/10-analyse-verify.ok -> ("10", "analyse-verify")
_STATE_FILE_RE = re.compile(r"^(\d+)-(.+)\.ok$")


def artifact_status(epic_dir: Path, epic: str) -> dict[str, bool]:
    """Presence of each epic deliverable, checking the dependencies layout first."""
    out: dict[str, bool] = {}
    for name in EPIC_ARTIFACTS:
        filename = f"{epic}-{name}"
        out[name] = any(
            (epic_dir / sub / filename).is_file() if sub else (epic_dir / filename).is_file()
            for sub in ("", "dependencies", "context")
        )
    return out


def resolve_epic_json(epic_dir: Path, epic: str, stem: str) -> Path:
    """Pre-CLOSE dependencies layout first, then archived context, then legacy epic root.

    Returns the dependencies path when nothing exists, so callers report the
    canonical location in error messages.
    """
    candidates = (
        epic_dir / "dependencies" / f"{epic}-{stem}.json",
        epic_dir / "context" / f"{epic}-{stem}.json",
        epic_dir / f"{epic}-{stem}.json",
    )
    for path in candidates:
        if path.is_file():
            return path
    return candidates[0]


def last_completed_stage(state_dir: Path) -> str | None:
    """Label of the highest-numbered step marker, e.g. 'ANALYSE verify'."""
    if not state_dir.is_dir():
        return None
    best: tuple[int, str] | None = None
    for path in state_dir.glob("*.ok"):
        match = _STATE_FILE_RE.match(path.name)
        if not match:
            continue
        order = int(match.group(1))
        label = match.group(2)
        try:
            first = path.read_text(encoding="utf-8").splitlines()[0]
        except (OSError, IndexError):
            first = ""
        if " | " in first:
            label = first.split(" | ", 1)[1].strip() or label
        if best is None or order > best[0]:
            best = (order, label)
    return best[1] if best else None


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def coverage_metrics(repo_root: Path, ref_path: Path, coverage_path: Path) -> str | None:
    """Variation numbers for the Coverage line, or None when they cannot be computed.

    A notification step must never fail over a metric, so every problem here
    degrades to omitting the line.
    """
    ref = _load_json(ref_path) if ref_path.is_file() else None
    coverage = _load_json(coverage_path) if coverage_path.is_file() else None
    if ref is None:
        return None
    tools = str(repo_root / "automation" / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    try:
        from epic_prep_verify import collect_variation_metrics  # type: ignore

        prep = collect_variation_metrics(ref)
    except Exception as exc:  # noqa: BLE001 - notification must survive any import error
        print(f"WARN cannot compute variation metrics: {exc}", file=sys.stderr)
        return None

    parts = [
        f"mandated={prep['mandated_variations']}",
        f"emitted={prep['emitted_variations']}",
    ]
    if coverage is not None:
        try:
            from coverage_verify import variation_density  # type: ignore

            checks_n, mandated_n = variation_density(coverage, ref)
            density = f"{(checks_n / mandated_n):.2f}" if mandated_n else "n/a"
            parts.append(f"checks={checks_n}")
            parts.append(f"density={density}")
        except Exception as exc:  # noqa: BLE001
            print(f"WARN cannot compute variation density: {exc}", file=sys.stderr)
    parts.append(f"unmatched={prep['unmatched_patterns']}")
    return " ".join(parts)


def render_comment(
    *,
    status: str,
    epic: str,
    build_url: str,
    stage: str | None = None,
    artifacts: dict[str, bool] | None = None,
    metrics: str | None = None,
    next_action: str,
    notes: tuple[str, ...] = (),
) -> str:
    lines = [f"{HEADER_PREFIX} - {epic} - {status}", ""]
    lines.append(f"Build: {build_url}")
    lines.append(f"Stage: {stage or 'unknown'}")

    if artifacts is None:
        lines.append("Artifacts: none in this build")
    else:
        lines.append("Artifacts: epic-work")
        for name in EPIC_ARTIFACTS:
            flag = "yes" if artifacts.get(name) else "no"
            lines.append(f"- {epic}-{name}: {flag}")

    if metrics:
        lines.append(f"Coverage: {metrics}")

    lines.append(f"Next: {next_action}")
    for note in notes:
        lines.append(f"Note: {note}")
    return "\n".join(lines)
