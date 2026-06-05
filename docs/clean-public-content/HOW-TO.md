# How to use this export

This tree is a **methodology sample**, not a turnkey QA system. The steps below help humans and agents orient without implying any specific employer toolchain.

## Phase chain (typical)

| Order | Guide | Role |
|-------|--------|------|
| 1 | [epic-prep-readme.md](.cursor/pipelines/epic-prep-readme.md) | Requirement map and proposed obligations |
| 2 | [coverage-readme.md](.cursor/pipelines/coverage-readme.md) | Verification checklist / smart checklist shape |
| 3 | [analysis-readme.md](.cursor/pipelines/analysis-readme.md) | Gap analysis before deep exploration |
| 4 | [test-discover-readme.md](.cursor/pipelines/test-discover-readme.md) | Optional obligation-closure and fixture map |
| 5 | [coverage-reinforce-readme.md](.cursor/pipelines/coverage-reinforce-readme.md) | Second coverage pass using discover affordances + operator feedback |
| 6 | [test-precon-readme.md](.cursor/pipelines/test-precon-readme.md) | Preconditions and session placeholders |
| 7 | [test-prep-readme.md](.cursor/pipelines/test-prep-readme.md) | Regression test draft bundles |
| 8 | [close-readme.md](.cursor/pipelines/close-readme.md) | Integrity review and archive pattern |

You may skip optional phases when your risk model allows; document that choice in your private harness.

## Setup in your organization

1. **Fork or copy** `epics/templates/` and adjust schema version fields to match your verifiers.
2. **Author playbooks** in a private repo with real triggers (e.g. `EPIC-PREP:`), MCP servers, and environment gates.
3. **Add verification scripts** that validate JSON against templates before agents or humans publish artefacts.
4. **Connect issue tracking** so requirement text is fetched from authoritative sourcesΓÇönever invented in generation mode.

## MCP and environments (generic)

- Use **issue/wiki MCP** or exports for requirements; keep tokens out of git.
- Optional **readonly database MCP** through your own tunnelΓÇödefine server names and allowlists locally; this export does not ship connection templates.
- Optional **browser MCP** for UI exploration during discover/precon/prepΓÇöconfigure in gitignored project or global IDE config.

## Style and redaction

Public prose rules: [docs/clean-public-style.md](docs/clean-public-style.md). When you maintain a private harness, keep hostnames, product brands, and credentials out of public forks.

## Related patterns (conceptual)

**Orchestrator pattern:** A private harness may bind one epic per chat session and advance **one pipeline stage per agent turn**, with human gates for environment readiness, coverage draft review, and UI credentials. Session state lives in gitignored scratch under the epic folder and archives with close. This export does not ship slash commands or session tooling — only the phase ordering above.

**Calibration pattern:** After a full artefact chain, operators may compare production outputs to curated **gold** JSON in a local folder and run a questionnaire-style review to surface harness drift. Gold and compare tooling are maintainer-local; this export describes the idea, not executable calibrate commands.

## Related files

- [AGENTS.md](AGENTS.md) ΓÇö short agent map  
- [epics/README.md](epics/README.md) ΓÇö artefact layout (if present)  
- [docs/public-export-manifest.json](docs/public-export-manifest.json) ΓÇö export metadata for this branch  
