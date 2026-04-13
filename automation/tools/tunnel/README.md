# CTQA PostgreSQL tunnel + probe

For QA engineers using the same stack (Cursor, MCP, CTQA DB over SSH). **PuTTY** is the default SSH client on Windows because OpenSSH on some PCs hits TLS/MAC issues against the same host where PuTTY works.

## Prerequisites

| Item | Notes |
|------|--------|
| Python | 3.10+ on PATH |
| PuTTY | `plink.exe` (default install: `C:\Program Files\PuTTY\`) |
| Node.js | For Cursor MCP `npx` (postgres-ctqa) |
| Cursor | Project `.cursor/mcp.json` (from `.cursor/mcp.json.example`) with `postgres-ctqa` |

Optional for `--probe-only`:

```bash
pip install -r automation/tools/tunnel/requirements.txt
```

## One-liner tunnel (Tab 1)

From the **workspace root**:

```powershell
python automation/tools/tunnel/ctqa_pg.py YOUR_AD_USER@ctqa.prosp.devexperts.com
```

- Uses **plink** automatically on Windows if PuTTY is installed (`--backend ssh` to force OpenSSH).
- Forwards **`127.0.0.1:15432` → `127.0.0.1:5432` on the SSH server** (same as a typical DBeaver tunnel). Override with `--remote-db-host` / `--remote-db-port` if your server needs the DB FQDN instead of loopback.
- Enter your **AD password** when prompted; press **Enter** if the server prints “Press Return to begin session”.
- **Leave this terminal open** while you work.

## DB probe + MCP (Tab 2)

After the tunnel is listening:

```powershell
set CTQA_PG_PASSWORD=your_postgres_role_password
python automation/tools/tunnel/ctqa_pg.py --probe-only
```

Environment variables (optional):

| Variable | Default | Purpose |
|----------|---------|---------|
| `CTQA_PG_PASSWORD` | (required for probe) | DB user password (**not** AD) |
| `CTQA_PG_USER` | `ctqa_core` | DB user |
| `CTQA_PG_DATABASE` | `ctqa` | Database name |
| `CTQA_LOCAL_PG_PORT` | `15432` | Local tunnel port |
| `CTQA_SSH_BACKEND` | `auto` | `plink`, `ssh`, or `auto` |

Custom read-only check:

```powershell
python automation/tools/tunnel/ctqa_pg.py --probe-only --probe-sql "SELECT COUNT(*) FROM ctqa_core.orders"
```

## MCP (Cursor)

Your **`.cursor/mcp.json`** (see **[mcp.json.example](../../.cursor/mcp.json.example)**) should use **`127.0.0.1:15432`** and **`sslmode=disable`** on the URL (traffic is already inside SSH; avoids Node `self-signed certificate` errors). Reload MCP after editing.

## Zipping this workspace for other QA projects

1. Zip the repo (or your standard QA harness subtree).
2. Each engineer installs **Python**, **Node**, **PuTTY**, **Cursor**.
3. Copy **`.cursor/mcp.json.example`** to **`.cursor/mcp.json`** (or merge into user-level `~/.cursor/mcp.json`); set the Postgres password in the URI and omit secrets from shared zips.
4. Document **Tab 1** = tunnel, **Tab 2** = probe / Cursor with MCP.
5. Do **not** commit real passwords; use env vars for probes and local-only MCP edits.

## Dry-run (print plink command)

```powershell
python automation/tools/tunnel/ctqa_pg.py -n YOUR_AD_USER@ctqa.prosp.devexperts.com
```

On PowerShell, if you run `plink` manually, use the call operator: `& "C:\Program Files\PuTTY\plink.exe" ...`.
