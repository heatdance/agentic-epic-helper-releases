# Figma MCP — Corner QA workspace

Functional notes for agents when tasks include **Figma** links (frames, layers, files). Install and OAuth are **per machine / Cursor profile**—not stored in this repo.

## When to use it

- Tickets, Confluence, or checklists link to **figma.com** URLs (often with `node-id=`).
- You need **structured design context** (layout, components, variables) rather than guessing from prose alone.

## How agents should work

1. Confirm the **Figma MCP server** is enabled in Cursor (workspace/user MCP settings). Server name may vary (e.g. configured as `figma` or `mcp-figma`).
2. Use **Figma MCP tools** per each tool’s schema (read descriptors before calling).
3. Pass **copy-link URLs** from Figma (frame or layer). Official docs note the client extracts **node id** from the URL for the MCP server—you do not need to open the URL as a generic browser navigation.
4. Access follows the **authenticated Figma user** (OAuth). Only files that user can open in the browser are available via MCP.

## References (external)

- Setup (Cursor, remote server): [Figma MCP — remote server installation](https://developers.figma.com/docs/figma-mcp-server/remote-server-installation/)
- Tools and prompts: [Tools and Prompts](https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/)
- Plans, rate limits, permission errors: [Plans, access, and permissions](https://developers.figma.com/docs/figma-mcp-server/plans-access-and-permissions/)

## Repo policy

- Do **not** paste **tokens**, OAuth secrets, or private file contents into repo files unless the task explicitly requires a redacted excerpt for QA evidence.
- Prefer **summaries** and **link references** in durable artifacts.

## Status (workspace)

Figma MCP has been **installed and verified** against the team’s Figma project space (OAuth user with appropriate file access). If tools fail, re-check MCP status in Cursor and Figma session permissions.
