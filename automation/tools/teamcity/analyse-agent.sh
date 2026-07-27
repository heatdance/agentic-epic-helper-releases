#!/usr/bin/env bash
set -euo pipefail

# shellcheck source=automation/tools/teamcity/agent-env.sh
source automation/tools/teamcity/agent-env.sh

# shellcheck source=automation/tools/teamcity/corner-tc-overview.sh
source automation/tools/teamcity/corner-tc-overview.sh
corner_tc_step_begin "ANALYSE agent"

# shellcheck source=automation/tools/teamcity/corner-tc-preflight.sh
source automation/tools/teamcity/corner-tc-preflight.sh
corner_tc_require_step_ok "08-ground-verify" "GROUND verify"

# shellcheck source=automation/tools/teamcity/corner-tc-epic-paths.sh
source automation/tools/teamcity/corner-tc-epic-paths.sh

EPIC="$EPIC_KEY"
COV_PATH="$(corner_tc_dep_json "$EPIC" coverage)"
ANALYSIS_JSON="$(corner_tc_dep_json "$EPIC" analysis)"
ANALYSIS_MD="$(corner_tc_resolve_md "$EPIC" analysis)"
PROMPT=$(cat <<EOF
ANALYSE: ${EPIC} strict_topology=yes strict_principal=yes

Follow the playbook .cursor/pipelines/analysis.md end-to-end for epic ${EPIC}.
Use user-mcp-atlassian MCP only for authoritative discovery.
Requires ${COV_PATH} with runtime_probes when console checks exist.
Write ${ANALYSIS_JSON} and ${ANALYSIS_MD} under dependencies/.
Delete epics/${EPIC}/temp/ when done.
EOF
)

python3 automation/tools/teamcity/run_pipeline_agent.py \
  --prompt "$PROMPT" \
  --require "epics/%EPIC_KEY%/dependencies/%EPIC_KEY%-analysis.json" \
  --require "epics/%EPIC_KEY%/dependencies/%EPIC_KEY%-analysis.md"

corner_tc_mark_step_ok "09-analyse-agent" "ANALYSE agent"
echo "ANALYSE agent finished"
