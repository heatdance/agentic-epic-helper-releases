"""Headless CRTQA dx console probe over OpenSSH (Linux CI / dxCity agents)."""

from __future__ import annotations

import base64
import json
import os
import shlex
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONFIG_REL = Path("automation/tools/crtqa-console/crtqa-console.config.json")
TEMPLATE_REL = Path(
    "automation/tools/crtqa-console/crtqa-invoke-remote.bash.template"
)
GATE_PROBE_COMMANDS = ("show console_guide", "exit")
_MOTD_MARKERS = (
    "WARNING: This system",
    "Individuals using",
    "authorized clients",
    "Unauthorized access",
    "law enforcement",
)


def _summarize_remote_failure(proc: subprocess.CompletedProcess[str]) -> str:
    stderr = (proc.stderr or "").strip()
    stdout = (proc.stdout or "").strip()
    err_lines = [
        line
        for line in stderr.splitlines()
        if line.strip() and not any(m in line for m in _MOTD_MARKERS)
    ]
    useful = "\n".join(err_lines).strip() or stderr[:500] or "(empty stderr)"
    if stdout:
        useful = f"{useful}\nstdout: {stdout[:400]}"
    return useful[:800]


def _write_dx_transcript(repo: Path, proc: subprocess.CompletedProcess[str]) -> Path:
    gate_dir = repo / "temp" / "crtqa-console"
    gate_dir.mkdir(parents=True, exist_ok=True)
    path = gate_dir / "gate-dx-last.log"
    body = (
        f"exit_code={proc.returncode}\n"
        f"--- stdout ---\n{proc.stdout or ''}\n"
        f"--- stderr ---\n{proc.stderr or ''}\n"
    )
    path.write_text(body, encoding="utf-8")
    return path


def repo_root_from_here() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def load_console_config(repo: Path) -> dict[str, Any]:
    path = repo / CONFIG_REL
    if not path.is_file():
        raise FileNotFoundError(f"Missing {CONFIG_REL}")
    cfg = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(cfg, dict):
        raise ValueError(f"Invalid config JSON: {path}")
    local = repo / CONFIG_REL.parent / "crtqa-console.local.json"
    if local.is_file():
        overlay = json.loads(local.read_text(encoding="utf-8"))
        if isinstance(overlay, dict):
            cfg.update(overlay)
    cfg["sshHost"] = os.environ.get("CRTQA_SSH_HOST") or cfg.get("sshHost") or ""
    cfg["sshUser"] = os.environ.get("CRTQA_SSH_USER") or cfg.get("sshUser") or ""
    cfg["sudoUnixUser"] = (
        os.environ.get("CRTQA_SUDO_UNIX_USER") or cfg.get("sudoUnixUser") or "ctqa"
    )
    cfg["remoteDxCommand"] = (
        os.environ.get("CRTQA_REMOTE_DX_COMMAND")
        or cfg.get("remoteDxCommand")
        or "dx run console"
    )
    cfg["termForRemote"] = (
        os.environ.get("CRTQA_TERM_FOR_REMOTE") or cfg.get("termForRemote") or "xterm"
    )
    return cfg


def openssh_credentials_present() -> bool:
    if os.environ.get("CRTQA_SSH_KEY_PATH"):
        return True
    if os.environ.get("CRTQA_SSH_PRIVATE_KEY"):
        return True
    return False


def _resolve_ssh_key_path() -> tuple[Path | None, tempfile.NamedTemporaryFile | None]:
    explicit = os.environ.get("CRTQA_SSH_KEY_PATH", "").strip()
    if explicit:
        path = Path(explicit)
        if path.is_file():
            return path, None
        raise FileNotFoundError(f"CRTQA_SSH_KEY_PATH not found: {explicit}")

    pem = os.environ.get("CRTQA_SSH_PRIVATE_KEY", "")
    if not pem.strip():
        return None, None

    tmp = tempfile.NamedTemporaryFile(prefix="crtqa-ssh-", suffix=".key", delete=False)
    tmp.write(pem.replace("\r\n", "\n").encode("utf-8"))
    tmp.flush()
    tmp.close()
    path = Path(tmp.name)
    path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    return path, tmp


def _ssh_extra_args() -> list[str]:
    """Extra OpenSSH -o flags (VPN/MTU workaround on some Windows paths)."""
    raw = os.environ.get("CRTQA_SSH_EXTRA_OPTS", "").strip()
    if raw:
        return shlex.split(raw)
    if sys.platform == "win32":
        return ["-o", "MACs=hmac-sha2-256", "-o", "Ciphers=aes256-ctr"]
    return []


def _fill_remote_bootstrap(
    *,
    sudo_password: str,
    commands: tuple[str, ...] | list[str],
    cfg: dict[str, Any],
    repo: Path,
) -> str:
    template_path = repo / TEMPLATE_REL
    if not template_path.is_file():
        raise FileNotFoundError(f"Missing {TEMPLATE_REL}")
    template = template_path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    cmds_block = "\n".join(commands)
    if not cmds_block.rstrip().endswith("exit"):
        cmds_block = f"{cmds_block}\nexit"
    dx_frag = str(cfg["remoteDxCommand"])
    if any(ch in dx_frag for ch in "\"'\\"):
        raise ValueError("remoteDxCommand contains shell metacharacters")
    return (
        template.replace("__PW_B64__", base64.b64encode(sudo_password.encode()).decode())
        .replace("__CMD_B64__", base64.b64encode(cmds_block.encode()).decode())
        .replace("__SUDO__", str(cfg["sudoUnixUser"]))
        .replace("__TERM__", str(cfg["termForRemote"]))
        .replace("__DX__", dx_frag)
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )


def _run_ssh(
    *,
    repo: Path,
    cfg: dict[str, Any],
    remote_script: str | None = None,
    remote_command: list[str] | None = None,
    timeout: int = 180,
) -> subprocess.CompletedProcess[str]:
    key_path, _tmp = _resolve_ssh_key_path()
    if key_path is None:
        raise RuntimeError(
            "OpenSSH credentials missing: set CRTQA_SSH_KEY_PATH or CRTQA_SSH_PRIVATE_KEY"
        )

    ssh_user = str(cfg.get("sshUser") or "").strip()
    ssh_host = str(cfg.get("sshHost") or "").strip()
    if not ssh_user or not ssh_host:
        raise RuntimeError("sshUser/sshHost missing in config and env")

    target = f"{ssh_user}@{ssh_host}"
    ssh_base = [
        "ssh",
        "-i",
        str(key_path),
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        "-o",
        "ConnectTimeout=30",
        *_ssh_extra_args(),
        target,
    ]
    if remote_command is not None:
        cmd = ssh_base + remote_command
        return subprocess.run(
            cmd,
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    if remote_script is not None:
        cmd = ssh_base + ["bash", "-s"]
        # text=False + bytes stdin: on Windows text=True rewrites \n to \r\n for ssh.
        raw = subprocess.run(
            cmd,
            input=remote_script.encode("utf-8"),
            cwd=str(repo),
            capture_output=True,
            text=False,
            timeout=timeout,
            check=False,
        )
        return subprocess.CompletedProcess(
            raw.args,
            raw.returncode,
            (raw.stdout or b"").decode("utf-8", errors="replace"),
            (raw.stderr or b"").decode("utf-8", errors="replace"),
        )
    raise ValueError("remote_script or remote_command required")


def write_gate_status(repo: Path, gate: dict[str, Any]) -> Path:
    gate_dir = repo / "temp" / "crtqa-console"
    gate_dir.mkdir(parents=True, exist_ok=True)
    gate_path = gate_dir / "gate-status.json"
    gate_path.write_text(json.dumps(gate, indent=2, ensure_ascii=False), encoding="utf-8")
    return gate_path


def probe_console_openssh(repo: Path | None = None) -> tuple[bool, str, dict[str, Any]]:
    root = repo or repo_root_from_here()
    checked_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    gate: dict[str, Any] = {
        "schema_version": 1,
        "checked_at": checked_at,
        "transport": "openssh",
        "ssh_echo_ok": False,
        "dx_probe_ok": False,
        "detail": "",
    }

    sudo_password = os.environ.get("CRTQA_SUDO_PASSWORD", "")
    if not sudo_password:
        gate["detail"] = "CRTQA_SUDO_PASSWORD not set (TeamCity password parameter)"
        write_gate_status(root, {**gate, "overall": "fail"})
        return False, gate["detail"], gate

    if not openssh_credentials_present():
        gate["detail"] = (
            "CRTQA_SSH_KEY_PATH or CRTQA_SSH_PRIVATE_KEY not set "
            "(see automation/docs/crtqa-console-ci.md)"
        )
        write_gate_status(root, {**gate, "overall": "fail"})
        return False, gate["detail"], gate

    try:
        cfg = load_console_config(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        gate["detail"] = f"config load failed: {exc}"
        write_gate_status(root, {**gate, "overall": "fail"})
        return False, gate["detail"], gate

    try:
        echo = _run_ssh(
            repo=root,
            cfg=cfg,
            remote_command=["echo", "crtqa_ssh_ok"],
            timeout=60,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        gate["detail"] = f"SSH echo failed: {exc}"
        write_gate_status(root, {**gate, "overall": "fail"})
        return False, gate["detail"], gate

    if echo.returncode != 0 or "crtqa_ssh_ok" not in (echo.stdout or ""):
        err = (echo.stderr or echo.stdout or "").strip()
        gate["detail"] = f"SSH echo failed (exit {echo.returncode}): {err[:400]}"
        write_gate_status(root, {**gate, "overall": "fail"})
        return False, gate["detail"], gate

    gate["ssh_echo_ok"] = True

    try:
        bootstrap = _fill_remote_bootstrap(
            sudo_password=sudo_password,
            commands=GATE_PROBE_COMMANDS,
            cfg=cfg,
            repo=root,
        )
        dx = _run_ssh(repo=root, cfg=cfg, remote_script=bootstrap, timeout=180)
    except (subprocess.TimeoutExpired, OSError) as exc:
        gate["detail"] = f"dx console probe failed: {exc}"
        write_gate_status(root, {**gate, "overall": "fail"})
        return False, gate["detail"], gate

    stdout = (dx.stdout or "").strip()
    stderr = (dx.stderr or "").strip()
    gate["dx_exit_code"] = dx.returncode
    gate["dx_stdout_bytes"] = len(stdout)

    if dx.returncode != 0:
        transcript = _write_dx_transcript(root, dx)
        summary = _summarize_remote_failure(dx)
        gate["detail"] = (
            f"dx probe exit {dx.returncode}; {summary}; "
            f"see {transcript.relative_to(root)}"
        )
        write_gate_status(root, {**gate, "overall": "fail"})
        return False, gate["detail"], gate

    if len(stdout) < 20:
        gate["detail"] = "dx probe returned too little stdout (console may be down)"
        write_gate_status(root, {**gate, "overall": "fail"})
        return False, gate["detail"], gate

    gate["dx_probe_ok"] = True
    gate["detail"] = "openssh + dx show console_guide OK"
    gate["overall"] = "pass"
    write_gate_status(root, gate)
    return True, gate["detail"], gate


def main() -> int:
    ok, symptom, _ = probe_console_openssh()
    print(symptom)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
