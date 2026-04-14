#!/usr/bin/env python3
"""
CTQA PostgreSQL over SSH — PuTTY plink-first on Windows, OpenSSH fallback.

Typical flow (two Cursor terminal tabs; same stack for all QA):

  Tab 1 — tunnel (interactive AD password when plink prompts):
    python automation/tools/tunnel/ctqa_pg.py USER@ctqa.prosp.devexperts.com

  Tab 2 — DB smoke test (after tunnel is up; password from env, not the script):
    set CTQA_PG_PASSWORD=your_db_password
    python automation/tools/tunnel/ctqa_pg.py --probe-only

  Cursor MCP: add postgres-ctqa to global Cursor mcp.json (~/.cursor/mcp.json;
  on Windows, under %USERPROFILE%/.cursor/mcp.json). Template: repo file
  .cursor/mcp/postgres-ctqa.mcp.json. URI: 127.0.0.1:15432, sslmode=disable
  (encrypted inside SSH).

Requires: Python 3.10+, PuTTY (plink) on Windows at default paths or PATH.
Optional probe: pip install -r automation/tools/tunnel/requirements.txt
"""

from __future__ import annotations

import argparse
import os
import shutil
import socket
import subprocess
import sys
import time
from typing import Sequence


def _find_putty_plink() -> str | None:
    pf = os.environ.get("ProgramFiles", r"C:\Program Files")
    pfx86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    for base in (pf, pfx86):
        candidate = os.path.join(base, "PuTTY", "plink.exe")
        if os.path.isfile(candidate):
            return candidate
    return shutil.which("plink")


def parse_jump(jump: str) -> tuple[str, str]:
    if "@" not in jump:
        raise argparse.ArgumentTypeError(
            "JUMP must be user@host (e.g. arodzevich@ctqa.prosp.devexperts.com)"
        )
    user, _, host = jump.partition("@")
    if not user or not host:
        raise argparse.ArgumentTypeError("JUMP must be user@host")
    return user, host


def build_plink_command(
    jump: str,
    *,
    local_bind: str,
    local_port: int,
    remote_db_host: str,
    remote_db_port: int,
) -> list[str]:
    user, host = parse_jump(jump)
    plink = _find_putty_plink()
    if not plink:
        raise FileNotFoundError(
            "plink.exe not found. Install PuTTY or add plink to PATH."
        )
    forward = f"{local_bind}:{local_port}:{remote_db_host}:{remote_db_port}"
    return [plink, "-ssh", "-N", "-L", forward, f"{user}@{host}"]


def build_ssh_command(
    args: argparse.Namespace,
) -> list[str]:
    user, host = parse_jump(args.jump)
    local_spec = f"{args.local_bind}:{args.local_port}"
    remote_target = f"{args.remote_db_host}:{args.remote_db_port}"
    forward = f"{local_spec}:{remote_target}"

    cmd: list[str] = [args.ssh_binary, "-N"]
    if args.exit_on_forward_failure:
        cmd.extend(["-o", "ExitOnForwardFailure=yes"])
    if args.server_alive_interval > 0:
        cmd.extend(
            [
                "-o",
                f"ServerAliveInterval={args.server_alive_interval}",
                "-o",
                f"ServerAliveCountMax={args.server_alive_count_max}",
            ]
        )
    cmd.extend(["-L", forward])
    if args.identity:
        cmd.extend(["-i", os.path.expanduser(args.identity)])
    for extra in args.ssh_option or []:
        cmd.extend(["-o", extra])
    cmd.append(f"{user}@{host}")
    return cmd


def resolve_backend(name: str) -> str:
    if name == "auto":
        if sys.platform == "win32" and _find_putty_plink():
            return "plink"
        if shutil.which("ssh"):
            return "ssh"
        raise RuntimeError(
            "auto: no plink (PuTTY) and no ssh on PATH. Install one of them."
        )
    if name == "plink":
        if not _find_putty_plink():
            raise RuntimeError("backend plink: PuTTY plink.exe not found.")
        return "plink"
    if name == "ssh":
        if not shutil.which("ssh"):
            raise RuntimeError("backend ssh: OpenSSH client not on PATH.")
        return "ssh"
    raise ValueError(name)


def args_ssh_binary_default() -> str:
    return shutil.which("ssh") or "ssh"


def wait_for_port(host: str, port: int, timeout: float = 30.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=2.0):
                return True
        except OSError:
            time.sleep(0.3)
    return False


def run_probe(args: argparse.Namespace) -> int:
    try:
        import psycopg
    except ImportError:
        print(
            "error: probe needs psycopg. Run:\n"
            "  pip install -r automation/tools/tunnel/requirements.txt",
            file=sys.stderr,
        )
        return 1

    password = os.environ.get("CTQA_PG_PASSWORD")
    if not password:
        print(
            "error: set CTQA_PG_PASSWORD to the PostgreSQL user password (DB role, not AD).",
            file=sys.stderr,
        )
        return 1

    user = os.environ.get("CTQA_PG_USER", "ctqa_core")
    db = os.environ.get("CTQA_PG_DATABASE", "ctqa")
    host = args.local_bind
    port = args.local_port

    conninfo = (
        f"host={host} port={port} dbname={db} user={user} password={password} "
        "sslmode=disable connect_timeout=10"
    )
    print(f"Connecting {user}@{host}:{port}/{db} (sslmode=disable)…", file=sys.stderr)
    try:
        conn = psycopg.connect(conninfo)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    cur = conn.cursor()
    cur.execute("SELECT 1 AS ok")
    print(f"probe: {cur.fetchone()}")

    cur.execute(
        """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE' AND table_name ILIKE %s
        ORDER BY table_schema, table_name
        LIMIT 25
        """,
        (args.probe_table_like,),
    )
    rows = cur.fetchall()
    print(f"tables ILIKE {args.probe_table_like!r} (up to 25): {len(rows)}")
    for s, t in rows:
        print(f"  {s}.{t}")

    if args.probe_sql.strip():
        print("--- probe SQL ---")
        cur.execute(args.probe_sql)
        colnames = [d[0] for d in cur.description] if cur.description else []
        out = cur.fetchall()
        for line in out[: args.probe_limit]:
            print(dict(zip(colnames, line)))

    conn.close()
    print("probe: ok", file=sys.stderr)
    return 0


def build_tunnel_command(args: argparse.Namespace) -> list[str]:
    backend = resolve_backend(args.backend)
    if backend == "plink":
        return build_plink_command(
            args.jump,
            local_bind=args.local_bind,
            local_port=args.local_port,
            remote_db_host=args.remote_db_host,
            remote_db_port=args.remote_db_port,
        )
    return build_ssh_command(args)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="CTQA SSH tunnel to Postgres (plink on Windows by default) + optional DB probe.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "jump",
        nargs="?",
        metavar="USER@HOST",
        help="SSH target (required for tunnel mode), e.g. arodzevich@ctqa.prosp.devexperts.com",
    )
    parser.add_argument(
        "--probe-only",
        action="store_true",
        help="Do not start SSH; only run DB probe against existing tunnel (use env CTQA_PG_PASSWORD).",
    )
    parser.add_argument(
        "--local-port",
        type=int,
        default=int(os.environ.get("CTQA_LOCAL_PG_PORT", "15432")),
        help="Local listen port (default: 15432, or CTQA_LOCAL_PG_PORT).",
    )
    parser.add_argument(
        "--local-bind",
        default=os.environ.get("CTQA_LOCAL_PG_BIND", "127.0.0.1"),
        help="Local bind address (default: 127.0.0.1).",
    )
    parser.add_argument(
        "--remote-db-host",
        default=os.environ.get("CTQA_REMOTE_PG_HOST", "127.0.0.1"),
        help="Postgres host as seen from the SSH server (default: 127.0.0.1). "
        "Use ctqa.prosp.devexperts.com if your server reaches DB only via that name.",
    )
    parser.add_argument(
        "--remote-db-port",
        type=int,
        default=int(os.environ.get("CTQA_REMOTE_PG_PORT", "5432")),
        help="Postgres port on remote-db-host (default: 5432).",
    )
    parser.add_argument(
        "--backend",
        choices=("auto", "plink", "ssh"),
        default=os.environ.get("CTQA_SSH_BACKEND", "auto"),
        help="auto = plink on Windows if installed, else ssh (default: auto).",
    )
    parser.add_argument(
        "--ssh-binary",
        default=args_ssh_binary_default(),
        help="Path to ssh when backend is ssh (default: ssh on PATH).",
    )
    parser.add_argument(
        "-i",
        "--identity",
        metavar="FILE",
        help="(ssh only) private key file.",
    )
    parser.add_argument(
        "-o",
        "--ssh-option",
        action="append",
        metavar="KEY=VALUE",
        help="(ssh only) extra -o option, repeatable.",
    )
    parser.add_argument(
        "--no-exit-on-forward-failure",
        action="store_true",
        help="(ssh only) omit ExitOnForwardFailure=yes.",
    )
    parser.add_argument(
        "--server-alive-interval",
        type=int,
        default=60,
        help="(ssh only) ServerAliveInterval seconds (0 disables).",
    )
    parser.add_argument(
        "--server-alive-count-max",
        type=int,
        default=3,
        help="(ssh only) ServerAliveCountMax.",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Print tunnel command and exit.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="(ssh only) insert -v for verbose.",
    )
    # probe-only options
    parser.add_argument(
        "--probe-table-like",
        default="%order%",
        help="(with --probe-only) pattern for listing tables (default: %%order%%).",
    )
    parser.add_argument(
        "--probe-sql",
        default="",
        help="(with --probe-only) extra read-only SQL to run after listing (be careful).",
    )
    parser.add_argument(
        "--probe-limit",
        type=int,
        default=5,
        help="Max rows to print for --probe-sql (default: 5).",
    )

    args = parser.parse_args(list(argv) if argv is not None else None)
    args.exit_on_forward_failure = not args.no_exit_on_forward_failure
    args.ssh_option = args.ssh_option or []

    if args.probe_only:
        return run_probe(args)

    if not args.jump:
        parser.error("tunnel mode requires USER@HOST (or use --probe-only).")

    try:
        parse_jump(args.jump)
    except argparse.ArgumentTypeError as e:
        parser.error(str(e))

    try:
        cmd = build_tunnel_command(args)
    except (FileNotFoundError, RuntimeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 127

    if os.path.basename(cmd[0]).lower() in ("ssh", "ssh.exe"):
        if args.verbose:
            cmd.insert(1, "-v")
        if args.ssh_binary == "ssh" and shutil.which("ssh") is None:
            print("error: `ssh` not on PATH.", file=sys.stderr)
            return 127

    if args.dry_run:
        print(subprocess.list2cmdline(cmd))
        if sys.platform == "win32" and cmd[0].lower().endswith("plink.exe"):
            rest = subprocess.list2cmdline(cmd[1:])
            print(
                f'\nPowerShell: use the call operator, e.g.\n  & "{cmd[0]}" {rest}',
                file=sys.stderr,
            )
        return 0

    exe = os.path.basename(cmd[0]).lower()
    print(
        f"Forwarding {args.local_bind}:{args.local_port} -> "
        f"{args.remote_db_host}:{args.remote_db_port} via {args.jump}",
        file=sys.stderr,
    )
    if exe == "plink.exe":
        print(
            "Using PuTTY plink. Enter AD password when prompted; press Return if asked.",
            file=sys.stderr,
        )
    print("Leave this running. Ctrl+C stops the tunnel.", file=sys.stderr)

    try:
        return subprocess.call(cmd)
    except KeyboardInterrupt:
        print("\nStopped.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
