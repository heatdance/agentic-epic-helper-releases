# better-prompt examples (Corner)

## Weak draft

> Fix the harness for CRT-639

**Interpreted intent:** Unclear whether epic artefacts, playbooks, or verifiers need work.

**Suggested done:**

- State trigger: `EPIC-PREP: CRT-639` vs harness doc edit with file path.
- If pipeline: name verifier + exit 0 (e.g. `epic_prep_verify.py --ref epics/CRT-639/CRT-639-ref.json`).

**Worth adding:**

1. Which artefact is wrong (`-coverage.json`, playbooks, rules)?
2. Is CRT-639 closed (JSON under `context/`)?

## Strong draft (minimal mode)

> `COVERAGE: CRT-639` — `-ref.json` at epic root; repo=BRO/xt; focus=rounding obligations

**Ready to send** — trigger, key, prerequisite, and focus present.
