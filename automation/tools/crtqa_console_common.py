"""Console multiplex gate probe for epic-helper and GROUND."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from crtqa_console_openssh import openssh_credentials_present, probe_console_openssh

SCHEMA_VERSION = 1
CONSOLE_GATE = "crtqa_dx_console_session"
CI_DOC = "automation/docs/crtqa-console-ci.md"


def repo_root_from_here() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _console_transport(repo: Path) -> str:
    explicit = os.environ.get("CRTQA_CONSOLE_TRANSPORT", "").strip().lower()
    if explicit in ("openssh", "plink"):
        return explicit
    if sys.platform != "win32":
        return "openssh"
    if openssh_credentials_present():
        return "openssh"
    return "plink"


def probe_console(repo: Path | None = None) -> tuple[bool, str, dict[str, Any]]:
    root = repo or repo_root_from_here()
    transport = _console_transport(root)
    if transport == "openssh":
        return probe_console_openssh(root)
    return probe_console_multiplex_plink(root)


def probe_console_multiplex_plink(repo: Path | None = None) -> tuple[bool, str, dict[str, Any]]:
    root = repo or repo_root_from_here()
    status_script = root / "automation" / "tools" / "crtqa-console" / "Get-CrtqaConsoleStatus.ps1"
    if not status_script.is_file():
        return False, "Get-CrtqaConsoleStatus.ps1 not found", {}

    cmd = ["pwsh", "-NoProfile", "-File", str(status_script), "-Quiet"]
    try:
        proc = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True, timeout=120)
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


def _recovery_actions(transport: str) -> list[str]:
    if transport == "openssh":
        return [
            "Set TeamCity secrets CRTQA_SSH_PRIVATE_KEY + CRTQA_SUDO_PASSWORD (see crtqa-console-ci.md).",
            "Export CRTQA_CONSOLE_TRANSPORT=openssh on the build agent step.",
            "Re-run python automation/tools/crtqa_console_probe.py on dxAgent.",
            "Then GROUND: <KEY> or full Pipeline.",
        ]
    return [
        "Run /crtqa-console start (desktop SSH password dialog ~30s; agent cannot complete this for you).",
        "Re-run python automation/tools/crtqa_console_probe.py to confirm pass.",
        "Then /epic-helper resume or GROUND: <KEY>.",
    ]


def build_console_gate_results(*, repo: Path | None = None) -> dict[str, Any]:
    checked_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    root = repo or repo_root_from_here()
    transport = _console_transport(root)
    console_ok, console_symptom, gate_doc = probe_console(root)

    if console_ok:
        gate = {
            "gate_id": CONSOLE_GATE,
            "status": "pass",
            "symptom": console_symptom,
            "transport": transport,
            "required_for_epic": True,
            "recovery": None,
        }
    else:
        gate = {
            "gate_id": CONSOLE_GATE,
            "status": "fail",
            "symptom": console_symptom,
            "transport": transport,
            "required_for_epic": True,
            "recovery": {
                "gate_id": CONSOLE_GATE,
                "symptom": console_symptom,
                "required_when_note": "epic-helper and GROUND require crtqa dx console.",
                "actions": _recovery_actions(transport),
                "documentation_refs": [
                    CI_DOC,
                    "automation/tools/crtqa-console/README.md",
                    ".cursor/commands/crtqa-console.md",
                ],
            },
        }

    overall = "pass" if console_ok else "fail"
    doc = {
        "schema_version": SCHEMA_VERSION,
        "checked_at": checked_at,
        "overall": overall,
        "transport": transport,
        "blocking_fail": not console_ok,
        "gates": [gate],
        "gate_status": gate_doc,
    }
    doc["checklist_markdown"] = format_console_checklist_markdown(doc)
    return doc


def format_console_checklist_markdown(doc: dict[str, Any]) -> str:
    lines = [
        "## CTQA console checklist",
        "",
        f"**Overall:** {doc.get('overall')} | **Checked:** {doc.get('checked_at')}",
        "",
    ]
    for i, gate in enumerate(doc.get("gates") or [], start=1):
        gid = gate.get("gate_id", "unknown")
        status = gate.get("status", "?")
        icon = "PASS" if status == "pass" else "FAIL"
        lines.append(f"### {i}. [{icon}] `{gid}`")
        lines.append("")
        lines.append(f"- **Symptom:** {gate.get('symptom', '')}")
        rec = gate.get("recovery")
        if rec and isinstance(rec, dict):
            lines.append("- **Actions:**")
            for j, action in enumerate(rec.get("actions") or [], start=1):
                lines.append(f"  {j}. {action}")
        lines.append("")

    if doc.get("overall") == "pass":
        lines.append("Console ready for **/epic-helper resume**, **GROUND:**, or manual console work.")
    else:
        lines.append("Fix console above, then re-run **crtqa_console_probe.py** or **/epic-helper resume**.")
    return "\n".join(lines)
