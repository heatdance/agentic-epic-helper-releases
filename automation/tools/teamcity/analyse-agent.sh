#!/usr/bin/env bash
set -euo pipefail

# shellcheck source=automation/tools/teamcity/agent-env.sh
source automation/tools/teamcity/agent-env.sh

EPIC="$EPIC_KEY"
PROMPT=$(cat <<EOF
ANALYSE: ${EPIC} strict_topology=yes strict_principal=yes

Follow the playbook .cursor/pipelines/analysis.md end-to-end for epic ${EPIC}.
Use user-mcp-atlassian MCP only for authoritative discovery.
Requires epics/${EPIC}/${EPIC}-coverage.json with runtime_probes when console checks exist.
Write epics/${EPIC}/${EPIC}-analysis.json and epics/${EPIC}/${EPIC}-analysis.md.
Delete epics/${EPIC}/temp/ when done.
EOF
)

python3 automation/tools/teamcity/run_pipeline_agent.py \
  --prompt "$PROMPT" \
  --require "epics/%EPIC_KEY%/%EPIC_KEY%-analysis.json" \
  --require "epics/%EPIC_KEY%/%EPIC_KEY%-analysis.md"

echo "ANALYSE agent finished"
