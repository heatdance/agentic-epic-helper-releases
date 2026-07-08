#!/usr/bin/env bash
set -euo pipefail

echo "PWD=$PWD"
test -f AGENTS.md
test -d automation/tools
test -d epics
test -d .cursor/rules
test -d .cursor/pipelines

python3 --version

if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq not on PATH (required by harness playbooks)"
  exit 1
fi
jq --version

if ! command -v uvx >/dev/null 2>&1; then
  if command -v uv >/dev/null 2>&1; then
    echo "uvx not found; uv present — OK if uv run works"
  else
    echo "ERROR: uvx (or uv) not on PATH — install uv for mcp-atlassian"
    exit 1
  fi
else
  echo "uvx: $(command -v uvx)"
fi

ls automation/tools/epic_prep_verify.py automation/tools/coverage_verify.py

python3 automation/tools/teamcity/write-mcp-config.py

# shellcheck source=automation/tools/teamcity/mcp-smoke.sh
source automation/tools/teamcity/mcp-smoke.sh

echo "Harness checkout + agent bootstrap OK"
