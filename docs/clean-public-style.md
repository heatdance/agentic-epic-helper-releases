# CLEAN — public export style guide

Normative prose for **Phase U** of [`CLEAN:`](.cursor/pipelines/clean.md). Agents transform the team tree into a **guide**, not a turnkey solution.

## Voice

- Second person or neutral (“you”, “a team”).
- Explain **why** a phase exists and **what shape** outputs take.
- Do **not** paste executable playbooks, verifier CLIs, or org-specific hostnames.

## Forbidden in public files

- Employer or product names (Devexperts, Corner Trader, DXtrade, WebBroker, etc.).
- Internal URLs (`*.in.devexperts`, `display-dev.dxfeed`, internal Stash paths).
- Real Jira keys (`CRT-1234`, `CRTQA-456`).
- Passwords, tokens, `Bearer ` literals, real MCP connection strings.
- Links to private repos except the public **releases** repo as “example export”.

Use placeholders: `YOUR-EPIC-KEY`, `your-org.confluence.example`, `PROJECT_KEY/repo_slug`.

## Pipeline readme structure (`<id>-readme.md`)

Each file replaces a full playbook under `.cursor/pipelines/`.

1. **Purpose** — one short paragraph.
2. **When to use** — trigger name only (e.g. `EPIC-PREP:`), no copy-paste blocks.
3. **Inputs** — generic artifacts (e.g. “epic ref JSON at `epics/<KEY>/<KEY>-ref.json`”).
4. **Process steps** — numbered phases as **methodology** (discovery, verification, merge), not agent subprocess instructions.
5. **Outputs** — file names and schema role, not full JSON samples with real keys.
6. **Build your own** — suggest verifier script, templates folder, and human review; do not ship working automation.

## Golden stub — `epic-prep-readme.md`

```markdown
# Epic preparation (guide)

## Purpose
Turn a vague epic into a structured requirement map your agents and humans can trust before coverage work.

## When to use
After you have a Jira (or equivalent) epic key and access to requirements in wiki or issue fields.

## Inputs
- Epic key (placeholder: YOUR-EPIC-KEY)
- Optional: code search hints (project/repo slugs you configure locally)

## Process steps
1. Fetch authoritative issue and linked requirement pages via your MCP or exports.
2. Build a single ref JSON: requirements list, traversal notes, proposed obligations (draft).
3. Run a schema verifier you maintain against `epics/templates/epic-ref.json`.
4. Stop if requirements are missing—do not invent acceptance text.

## Outputs
- `epics/<KEY>/<KEY>-ref.json` aligned to your template schema version.

## Build your own
Copy `epics/templates/epic-ref.json`, add `epic_prep_verify.py` (or equivalent), and wire a `EPIC-PREP:` rule in your router. Replace Confluence/Jira MCP with your stack.
```

## Golden stub — public `README.md` intro

```markdown
# Agentic QA harness (public guide)

This repository is a **redacted export**: pipeline **ideas**, template **shapes**, and harness **concepts** only. It is not configured for any employer, product line, or environment.

Clone it to study how multi-phase agent playbooks, JSON artefacts, and verification loops can be organized—not to run production QA unchanged.
```

## Golden stub — `docs/project.example.json`

```json
{
  "_comment": "Replace with your product Confluence space, upstream fork docs, and default code host. Do not commit real internal IDs in public forks.",
  "product_name": "YOUR_PRODUCT",
  "confluence": {
    "product_space": "YOUR_SPACE",
    "home_page_id": "000000000"
  },
  "sources": {
    "default_repo": "PROJECT_KEY/repo_slug"
  }
}
```

## Review checklist (human)

- [ ] No blocklist `rg` hits outside allowed globs.
- [ ] Every former playbook has a matching `*-readme.md`.
- [ ] README states guide-only intent.
- [ ] No `clean.md` or `CLEAN:` trigger in public router.
