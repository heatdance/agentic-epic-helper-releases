# Agentic QA harness (public guide)

This repository is a **redacted export**: pipeline **ideas**, template **shapes**, and harness **concepts** only. It is not configured for any employer, product line, or environment.

Clone it to study how multi-phase agent playbooks, JSON artefacts, and verification loops can be organizedΓÇönot to run production QA unchanged.

## What you get

- **Pipeline guides** ΓÇö `.cursor/pipelines/*-readme.md` describe purpose, inputs, methodology, and outputs for each phase (epic prep through close).
- **Template schemas** ΓÇö `epics/templates/*.json` show field names and relationships you can adapt to your issue tracker and tools.
- **Router sketch** ΓÇö `.cursor/rules/pipeline-router.mdc` is guide-only; wire real triggers in your private harness.

## What is intentionally missing

- Runnable verifiers, environment probes, MCP connection examples tied to a specific stack, and operator session files.
- Org-specific hostnames, credentials, and live epic data.

## Suggested learning path

1. Read [HOW-TO.md](HOW-TO.md) for how the phases chain together.
2. Skim [AGENTS.md](AGENTS.md) for how an agent should route context.
3. Open the readme for the phase you care about (e.g. `epic-prep-readme.md`, then `coverage-readme.md`).
4. Copy `epics/templates/` into your project and rename fields to match your toolchain.

## Licence and intent

Use as a pattern library. Implement your own automation, MCP integrations, and review gates before relying on agents for regulated or production QA work.
