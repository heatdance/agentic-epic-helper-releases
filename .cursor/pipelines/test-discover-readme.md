# Test discover (guide)

## Purpose

Close the loop between coverage obligations and what was actually explored in your environmentsΓÇöfixtures, UI surfaces, admin tools, and optional readonly data probesΓÇöwithout writing final test steps yet.

## When to use

When coverage (and usually analysis) exist and you need an obligation-closure map before precon/prep. Optional in lighter processes. Trigger with `TEST-DISCOVER:` locally.

## Inputs

- Ref and coverage JSON
- Template: `epics/templates/discover-ref.json`
- Operator-supplied credentials for UI gates (never stored in durable JSON)

## Process steps

1. Run cold gates your harness defines: environment reachability, optional readonly DB probe, optional admin shell handshake, optional browser smoke for affected UI.
2. Record disposition per primary obligation row; cap exploration depth per your contract.
3. Set `discovery_status` to complete only when verifier rules pass.
4. Emit a single discover JSON; do not embed secrets or temp paths.

## Outputs

- `epics/<KEY>/<KEY>-discover.json`

## Build your own

Rename tooling fields in the template to match your MCP names (`postgres_readonly`, `remote_admin_shell`, etc.). Implement `discover_verify.py` and phase-0 playbooks in a private repo; this export only shows the artefact shape.
