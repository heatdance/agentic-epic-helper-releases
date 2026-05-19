"""Shared CTQA environment gate probes (Postgres tunnel + crtqa console multiplex)."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1

POSTGRES_GATE = "postgres_ctqa_tunnel"
CONSOLE_GATE = "crtqa_dx_console_session"

_ENGINE_KEYWORDS = frozenset(
    {
        "engine",
        "risk",
        "export",
        "sql",
        "db",
        "settlement",
        "parity",
        "backend",
        "postgres",
        "database",
    }
)
_CONSOLE_KEYWORDS = frozenset(
    {
        "console",
        "dxcore",
        "publisher",
        "position_metrics",
        "execution trade",
        "weighted average",
        "weighted_average",
        "ladder",
    }
)


def repo_root_from_here() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def tooling_intent_from_coverage(coverage: dict[str, Any] | None) -> dict[str, str]:
    """Mirror test-discover.md tooling intent rubric (generation defaults)."""
    postgres = "skipped"
    console = "skipped"
    if not coverage:
        return {
            "postgres_ctqa": "required",
            "crtqa_dx_console": "required",
            "chrome_devtools": "skipped",
            "figma": "skipped",
        }

    archetype = str(coverage.get("archetype") or "").lower()
    text_blobs: list[str] = []
    for key in ("checks", "coverage_matrix"):
        for row in coverage.get(key) or []:
            if not isinstance(row, dict):
                continue
            for field in (
                "scenario_line",
                "capability",
                "notes_from_epic",
                "subsection",
                "section",
            ):
                val = row.get(field)
                if val:
                    text_blobs.append(str(val).lower())
            for surf in row.get("surfaces") or []:
                text_blobs.append(str(surf).lower())
            if row.get("calculation_contract") == "ladder_present":
                text_blobs.append("ladder_present")
            text_blobs.extend(str(k).lower() for k in row.get("requirement_keys") or [])

    joined = " ".join(text_blobs)

    if archetype == "metrics_calculation" and any(
        w in joined for w in ("engine", "sql", "db", "risk", "settlement")
    ):
        postgres = "required"
    if any(w in joined for w in _ENGINE_KEYWORDS):
        postgres = "required"
    for row in coverage.get("coverage_matrix") or []:
        if not isinstance(row, dict):
            continue
        if row.get("verification_role") == "primary" and "api" in [
            str(s).lower() for s in row.get("surfaces") or []
        ]:
            postgres = "required"

    if any(w in joined for w in _CONSOLE_KEYWORDS):
        console = "required"
    if "ladder_present" in joined:
        console = "required"

    surfaces: set[str] = set()
    for row in list(coverage.get("checks") or []) + list(coverage.get("coverage_matrix") or []):
        if isinstance(row, dict):
            surfaces.update(str(s).lower() for s in row.get("surfaces") or [])

    chrome = "required" if surfaces & {"dxtrade5", "webbroker", "adaptive"} else "skipped"

    return {
        "postgres_ctqa": postgres,
        "crtqa_dx_console": console,
        "chrome_devtools": chrome,
        "figma": "skipped",
    }


def probe_postgres_tunnel(
    host: str = "127.0.0.1",
    port: int | None = None,
    timeout_s: float = 2.0,
) -> tuple[bool, str]:
    port = port or int(os.environ.get("CTQA_LOCAL_PG_PORT", "15432"))
    try:
        with socket.create_connection((host, port), timeout=timeout_s):
            return True, f"TCP {host}:{port} accepting connections"
    except OSError as exc:
        return False, f"TCP {host}:{port} not reachable ({exc.__class__.__name__})"


def probe_console_multiplex(repo: Path | None = None) -> tuple[bool, str, dict[str, Any]]:
    root = repo or repo_root_from_here()
    status_script = root / "automation" / "tools" / "crtqa-console" / "Get-CrtqaConsoleStatus.ps1"
    if not status_script.is_file():
        return False, "Get-CrtqaConsoleStatus.ps1 not found", {}

    cmd = [
        "pwsh",
        "-NoProfile",
        "-File",
        str(status_script),
        "-Quiet",
    ]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return False, f"console status script failed ({exc})", {}

    gate_path = root / "temp" / "crtqa-console" / "gate-status.json"
    gate_doc: dict[str, Any] = {}
    if gate_path.is_file():
        try:
            loaded = json.loads(gate_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                gate_doc = loaded
        except (OSError, json.JSONDecodeError):
            pass

    if proc.returncode == 0:
        detail = gate_doc.get("detail") or "multiplex session healthy"
        return True, str(detail), gate_doc

    err = (proc.stderr or proc.stdout or "").strip()
    symptom = gate_doc.get("detail") or err or "console multiplex check failed"
    return False, str(symptom)[:500], gate_doc


def _recovery_block(
    gate_id: str,
    *,
    symptom: str,
    required_when_note: str,
    actions: list[str],
    documentation_refs: list[str],
) -> dict[str, Any]:
    return {
        "gate_id": gate_id,
        "status": "fail",
        "symptom": symptom,
        "required_for_epic": True,
        "recovery": {
            "gate_id": gate_id,
            "blocks_test_prep": True,
            "symptom": symptom,
            "required_when_note": required_when_note,
            "actions": actions,
            "documentation_refs": documentation_refs,
        },
    }


def _pass_gate(gate_id: str, symptom: str, required_for_epic: bool) -> dict[str, Any]:
    return {
        "gate_id": gate_id,
        "status": "pass",
        "symptom": symptom,
        "required_for_epic": required_for_epic,
        "recovery": None,
    }


def build_gate_results(
    coverage: dict[str, Any] | None = None,
    *,
    repo: Path | None = None,
) -> dict[str, Any]:
    intent = tooling_intent_from_coverage(coverage)
    checked_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    pg_ok, pg_symptom = probe_postgres_tunnel()
    console_ok, console_symptom, _ = probe_console_multiplex(repo)

    gates: list[dict[str, Any]] = []

    pg_required = intent.get("postgres_ctqa") == "required"
    if pg_ok:
        gates.append(_pass_gate(POSTGRES_GATE, pg_symptom, pg_required))
    else:
        gates.append(
            _recovery_block(
                POSTGRES_GATE,
                symptom=pg_symptom,
                required_when_note=(
                    "TEST-DISCOVER Phase 0 requires Postgres when coverage implies engine/SQL/DB work."
                    if pg_required
                    else "Postgres tunnel recommended for CTQA backend checks."
                ),
                actions=[
                    "Start CTQA Postgres SSH tunnel (leave the tab open): "
                    "python automation/tools/tunnel/ctqa_pg.py YOUR_AD_USER@ctqa.prosp.devexperts.com",
                    "Add postgres-ctqa to .cursor/mcp.json per automation/tools/tunnel/README.md; reload MCP in Cursor.",
                    "Re-run /crtqa-env (or python automation/tools/crtqa_env_probe.py).",
                ],
                documentation_refs=[
                    "automation/tools/tunnel/README.md",
                    ".cursor/mcp.json.example",
                ],
            )
        )

    console_required = intent.get("crtqa_dx_console") == "required"
    if console_ok:
        gates.append(_pass_gate(CONSOLE_GATE, console_symptom, console_required))
    else:
        gates.append(
            _recovery_block(
                CONSOLE_GATE,
                symptom=console_symptom,
                required_when_note=(
                    "TEST-DISCOVER Phase 0 requires crtqa console when coverage mentions console/ladder/dxcore."
                    if console_required
                    else "Console multiplex recommended for dxCore setup probes."
                ),
                actions=[
                    "Run /crtqa-console start (desktop SSH password dialog ~30s; agent cannot complete this for you).",
                    "Re-run /crtqa-env to confirm gate-status.json shows pass.",
                    "Then TEST-DISCOVER: <KEY> or TEST-DISCOVER: <KEY> proceed if you already hit a Phase 0 stop.",
                ],
                documentation_refs=[
                    "automation/tools/crtqa-console/README.md",
                    ".cursor/commands/crtqa-console.md",
                ],
            )
        )

    for g in gates:
        if coverage is None:
            g["required_for_epic"] = True
        else:
            gid = g["gate_id"]
            if gid == POSTGRES_GATE:
                g["required_for_epic"] = intent.get("postgres_ctqa") == "required"
            elif gid == CONSOLE_GATE:
                g["required_for_epic"] = intent.get("crtqa_dx_console") == "required"

    blocking_fail = any(
        g["status"] == "fail" and g.get("required_for_epic") for g in gates
    )
    any_fail = any(g["status"] == "fail" for g in gates)
    overall = "fail" if any_fail else "pass"

    doc = {
        "schema_version": SCHEMA_VERSION,
        "checked_at": checked_at,
        "overall": overall,
        "blocking_fail": blocking_fail,
        "tooling_intent": intent,
        "gates": gates,
    }
    doc["checklist_markdown"] = format_checklist_markdown(doc)
    return doc


def format_checklist_markdown(doc: dict[str, Any]) -> str:
    lines = [
        "## CTQA environment checklist",
        "",
        f"**Overall:** {doc.get('overall')} | **Checked:** {doc.get('checked_at')}",
        "",
    ]
    intent = doc.get("tooling_intent") or {}
    if intent:
        lines.append(
            f"*Epic tooling intent (when coverage provided):* "
            f"postgres={intent.get('postgres_ctqa')}, "
            f"console={intent.get('crtqa_dx_console')}"
        )
        lines.append("")

    for i, gate in enumerate(doc.get("gates") or [], start=1):
        gid = gate.get("gate_id", "unknown")
        status = gate.get("status", "?")
        req = "required for epic" if gate.get("required_for_epic") else "informational"
        icon = "PASS" if status == "pass" else "FAIL"
        lines.append(f"### {i}. [{icon}] `{gid}` ({req})")
        lines.append("")
        lines.append(f"- **Symptom:** {gate.get('symptom', '')}")
        rec = gate.get("recovery")
        if rec and isinstance(rec, dict):
            lines.append("- **Actions:**")
            for j, action in enumerate(rec.get("actions") or [], start=1):
                lines.append(f"  {j}. {action}")
        lines.append("")

    if doc.get("overall") == "pass":
        lines.append(
            "Ready for **TEST-DISCOVER: <KEY>** or **TEST-PRECON: <KEY>** "
            "(after `-coverage.json` exists)."
        )
    else:
        lines.append(
            "Fix failed items above, then re-run **/crtqa-env**. "
            "Do not run TEST-DISCOVER or TEST-PRECON until required gates pass."
        )
    return "\n".join(lines)


def load_coverage(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None
