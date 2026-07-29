# Lesson 1 — Logical roles (credentials overlay)

**Goal:** Name actors for smoke tests; keep secrets out of git.

## What you created

| File | Committed? |
|------|------------|
| `dependencies/credentials.local.example.json` | Yes |
| `dependencies/credentials.local.json` | No (gitignored) |

## Why

Tests refer to **`dxtf_bot`**, not a raw username. One place to rotate CT QA credentials.

## Exercise (completed)

- [x] Pick role id `dxtf_bot` for dxTrade5 on `ct_qa`
- [x] Fill local overlay; verify `git status` does not list the local file
- [x] Manual login works on CT QA

## Checkpoint

Reply with role id + surface when starting a new chat; run `` so session reloads.
