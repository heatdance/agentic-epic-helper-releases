# CTQA PostgreSQL tunnel + probe

For QA engineers using the same stack (Cursor, MCP, CTQA DB over SSH). **PuTTY** is the default SSH client on Windows because OpenSSH on some PCs hits TLS/MAC issues against the same host where PuTTY works.

**Org-wide MCP and tokens** (separate from this database): [AI with Cursor](https://confluence.in.devexperts.com/spaces/QAPORTAL/pages/497112528/AI+with+Cursor) on QAPORTAL.

## Prerequisites

| Item | Notes |
|------|------|
| Python | 3.10+ on PATH |
| PuTTY | `plink.exe` (default install: `C:\Program Files\PuTTY\`) |
| Node.js | For Cursor MCP `npx` (**`postgres-ctqa`**) |
| Cursor | **`postgres-ctqa`** in **gitignored** `.cursor/mcp.json` and/or **global** `~/.cursor/mcp.json` (Windows: `%USERPROFILE%\.cursor\mcp.json`) — use **§ MCP — PostgreSQL (Cursor)** below; **`chrome-devtools`** for optional discover/precon/prep UI — [automation/docs/chrome-devtools-mcp.md](../../docs/chrome-devtools-mcp.md) |

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

`-n` / `--dry-run` prints the exact command without connecting.

## DB probe (Tab 2)

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

## MCP — PostgreSQL (Cursor)

Configure **`postgres-ctqa`** in **Cursor’s global** and/or **project** MCP file so the repo stays free of DB credentials.

**Where to edit**

| OS | Global `mcp.json` |
|----|-------------------|
| Windows | `%USERPROFILE%\.cursor\mcp.json` |
| macOS / Linux | `~/.cursor/mcp.json` |

Project **`.cursor/mcp.json`** is **gitignored** and is optional. Cursor **merges** global and project; do **not** define the same server twice with conflicting URLs.

**Terminal checklist (order matters)**

1. Start the **SSH tunnel** (§ One-liner tunnel) and leave that window open.
2. Optionally run **§ DB probe** to confirm connectivity (`CTQA_PG_PASSWORD`, then `--probe-only`).
3. Merge the **`postgres-ctqa`** server from the snippet below into **`mcpServers`** in global and/or gitignored `.cursor/mcp.json`.
4. **SSL:** use **`sslmode=disable`** on **`127.0.0.1`** through SSH (traffic is encrypted inside the tunnel; avoids Node/pg self-signed certificate errors with MCP). Do **not** disable SSL for untunneled internet database connections.
5. **Reload MCP** — Restart Cursor or refresh MCP servers (**Cursor Settings → MCP**). Check **MCP Logs** if the server fails to start (`npx` must be on PATH for package-based MCP servers started by Cursor).

**Snippet (placeholders)**

Uses [`@sarmadparvez/postgresql-mcp`](https://www.npmjs.com/package/@sarmadparvez/postgresql-mcp). Append **`?mode=readonly`** so write-oriented tools stay disabled at the MCP layer; still prefer a database role limited to **`SELECT`**.

Replace **`USER`**, **`PASSWORD`** (URL-encode special characters), and **`15432`** if your local forward differs:

```json
{
  "mcpServers": {
    "postgres-ctqa": {
      "command": "npx",
      "args": [
        "-y",
        "@sarmadparvez/postgresql-mcp",
        "postgresql://USER:PASSWORD@127.0.0.1:15432/ctqa?sslmode=disable&mode=readonly"
      ]
    }
  }
}
```

There is **no** committed **`.cursor/mcp/`** template folder—keep the copy-paste block here authoritative.

Your URL must match the tunnel: **`127.0.0.1`** and **`sslmode=disable`** as shown.

## TEST-DISCOVER — optional readonly SQL

When **`TEST-DISCOVER:`** links a **`weighted_avg_fx_spot_account`** fixture and the chk has **`sql`** in **`evidence_need`**, agents may run **one** allowlisted readonly query via **`postgres-ctqa`** after tunnel + MCP are up. Normative probe steps: [`docs/discover-fixture-probes.json`](../../../docs/discover-fixture-probes.json). **Console read-only shows remain required** for **`probe_executed`** on config kinds—SQL does not replace them. Add concrete table/column allowlists here when validated on CTQA; until then, prefer console-only depth.

## Zipping this workspace for other QA projects

1. Zip the repo (or your standard QA harness subtree).
2. Each engineer installs **Python**, **Node**, **PuTTY**, **Cursor**.
3. Add **`postgres-ctqa`** using **§ MCP — PostgreSQL** above to **gitignored** `.cursor/mcp.json` and/or **global** `~/.cursor/mcp.json` (Windows: `%USERPROFILE%\.cursor\mcp.json`).
4. Document **Tab 1** = tunnel, **Tab 2** = probe / Cursor with MCP.
5. Do **not** commit real passwords; use env vars for probes and local-only MCP edits.

## Dry-run (print plink command)

```powershell
python automation/tools/tunnel/ctqa_pg.py -n YOUR_AD_USER@ctqa.prosp.devexperts.com
```

On PowerShell, if you run `plink` manually, use the call operator: `& "C:\Program Files\PuTTY\plink.exe" ...`.
