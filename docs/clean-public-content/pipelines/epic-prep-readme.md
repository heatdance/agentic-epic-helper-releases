# Epic preparation (guide)

## Purpose

Turn a vague epic into a structured requirement map that humans and agents can trust before coverage work. The ref artefact records what was fetched, what obligations are proposed, and where upstream references live.

## When to use

After you have an epic key in your issue tracker and access to requirements in wiki fields, linked pages, or exports. In your private harness, trigger this phase with a convention such as `EPIC-PREP:`.

## Inputs

- Epic key (placeholder: `YOUR-EPIC-KEY`)
- Optional: code-search hints (project and repository slugs you configure locally)
- Template: `epics/templates/epic-ref.json`

## Process steps

1. Fetch authoritative issue data and linked requirement pages via your MCP or manual exportΓÇödo not paraphrase from memory.
2. Build a single ref JSON: requirements list, traversal notes, and draft obligations aligned to your obligation taxonomy.
3. Run a schema verifier you maintain against the template version you adopted.
4. Stop when requirements are missing or ambiguous; record gaps instead of inventing acceptance text.

## Outputs

- `epics/<KEY>/<KEY>-ref.json` aligned to your template schema version
- Optional human-readable companion markdown if your process uses one

## Build your own

Copy `epics/templates/epic-ref.json`, implement `epic_prep_verify.py` (or equivalent), and register the trigger in your router. Replace wiki/issue MCP tools with your stack; keep generation mode free of live test-issue keys unless you explicitly enable an index feature in your private contract.
