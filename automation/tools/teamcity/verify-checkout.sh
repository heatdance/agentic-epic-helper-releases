#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$PWD}"
export REPO_ROOT

# TeamCity: password params may be absent from env until loaded from properties file.
# shellcheck source=automation/tools/teamcity/load-teamcity-params.sh
source automation/tools/teamcity/load-teamcity-params.sh
_corner_tc_load_params

# shellcheck source=automation/tools/teamcity/corner-tc-overview.sh
source automation/tools/teamcity/corner-tc-overview.sh
corner_tc_step_begin "Verify harness checkout"

# shellcheck source=automation/tools/teamcity/corner-tc-preflight.sh
source automation/tools/teamcity/corner-tc-preflight.sh
corner_tc_state_reset
rm -f "${REPO_ROOT}/.teamcity-ci/jira-success.posted" "${REPO_ROOT}/.teamcity-ci/jira-failure.posted"

echo "PWD=${REPO_ROOT}"
test -f AGENTS.md
test -d automation/tools
test -d epics
test -d .cursor/rules
test -d .cursor/pipelines

python3 --version

if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq not on PATH (install jq on dxAgent image — cannot self-bootstrap without root)"
  exit 1
fi
jq --version

ls automation/tools/epic_prep_verify.py automation/tools/coverage_verify.py

# Self-healing: uv/uvx, cursor-sdk, MCP wheel cache, persisted PATH for later steps.
# shellcheck source=automation/tools/teamcity/bootstrap-agent-env.sh
source automation/tools/teamcity/bootstrap-agent-env.sh

python3 automation/tools/teamcity/write-mcp-config.py

# shellcheck source=automation/tools/teamcity/mcp-smoke.sh
source automation/tools/teamcity/mcp-smoke.sh

corner_tc_mark_step_ok "01-verify-checkout" "Verify harness checkout"
echo "Harness checkout + agent bootstrap OK"
