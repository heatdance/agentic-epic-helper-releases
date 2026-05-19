# CLOSE prompt scaffold

**Trigger line:** `CLOSE: <EPIC-KEY>` (optional `benchmark_suite=` / `benchmark_attempt=`; optional `heal=no`).

**Playbook (follow exactly):** [`.cursor/pipelines/close.md`](../pipelines/close.md)

**Contract / verifier:** [docs/close-contract.json](../../docs/close-contract.json) · [automation/docs/close-verify.md](../../automation/docs/close-verify.md)

## Session rules

1. **Preflight** — `close_verify.py --mode preflight`; stop if `context/` already has ref json.
2. **L0–L4** — one subprocess per **(level, bundle_id)**; jq slices only; append **findings** to `-close.json`.
3. **Finalize** — whitelist corrections only; regenerate **four** root `.md`; set `epic_verdict`.
4. **Archive** — `close_archive.py`; verify `emit`; delete `temp/`.

**Forbidden:** MCP, creds, new scenarios, oracle rewrites, loading full epic JSON in one turn.

**Output:** `{EpicDir}` with four `.md` at root; all json under `{EpicDir}context/` including `-close.json`.
