# Chrome DevTools MCP — Corner QA workspace

Functional notes for agents when **discover / precon / prep** (or ad-hoc QA) needs **live Chrome** UI exploration. **`CLOSE:`** does **not** use this MCP. Install is **per machine / Cursor profile**—credentials stay out of git.

## What it is

[**Chrome DevTools MCP**](https://github.com/ChromeDevTools/chrome-devtools-mcp) (`chrome-devtools-mcp` on npm) exposes Chrome automation via **Puppeteer** and DevTools-style tools (click, fill, navigate, snapshots, network, performance, etc.). In Cursor, the server is typically registered as **`chrome-devtools`**.

## Cursor configuration

Merge into **global** `%USERPROFILE%\.cursor\mcp.json` (Windows) or `~/.cursor/mcp.json`, and/or **gitignored** project `.cursor/mcp.json`. Cursor merges **global + project**; do **not** define the same server name twice with conflicting settings.

**Default (browser launched by MCP when a tool needs it):**

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

**Optional:** add flags to `args` after the package name, e.g. `--no-usage-statistics`, `--headless`, `--slim` — see [upstream README](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/README.md).

**Windows:** If the server fails to start from Cursor, ensure **Node** / **`npx`** are on PATH for the Cursor process. Some setups use `cmd /c` wrappers or longer startup timeouts—see upstream **Cursor** / **Copilot** Windows notes in the same README.

**Reload:** **Cursor Settings → MCP** — refresh or restart Cursor after edits.

## How agents should work

1. Read **tool schemas** for **`chrome-devtools`** (or the client’s resolved server name) before calling tools — names differ from Playwright MCP or IDE-embedded browser MCPs.
2. Use MCP tools for **live UI** steps during exploration pipelines (**TEST-DISCOVER**, **TEST-PRECON**, **TEST-PREP** Phase 0 / 8a¾)—not during **`CLOSE:`**.
3. Do **not** paste session cookies, passwords, or tokens into repo files or durable JSON.

## References (external)

- Repository and full tool list: [ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp)

## Repo policy

- **`.cursor/mcp.json`** is **gitignored**; real entries live only locally. See **[`.cursor/mcp.json.example`](../.cursor/mcp.json.example)** in the repo root as a merge template (placeholders only).
