#!/usr/bin/env bash
set -euo pipefail

# shellcheck source=automation/tools/teamcity/agent-env.sh
source automation/tools/teamcity/agent-env.sh

python3 -m pip install --user -q cursor-sdk

EPIC="$EPIC_KEY"
PROMPT=$(cat <<EOF
COVERAGE: ${EPIC} strict_topology=yes strict_principal=yes

Follow the playbook .cursor/pipelines/coverage.md end-to-end for epic ${EPIC}.
Use user-mcp-atlassian MCP only for authoritative Jira/Confluence/Bitbucket content.
Requires existing epics/${EPIC}/${EPIC}-ref.json.
Write epics/${EPIC}/${EPIC}-coverage.json and epics/${EPIC}/${EPIC}-coverage.md.
Delete epics/${EPIC}/temp/ when done.
EOF
)

python3 automation/tools/teamcity/run_pipeline_agent.py \
  --prompt "$PROMPT" \
  --require "epics/%EPIC_KEY%/%EPIC_KEY%-ref.json" \
  --require "epics/%EPIC_KEY%/%EPIC_KEY%-coverage.json" \
  --require "epics/%EPIC_KEY%/%EPIC_KEY%-coverage.md"

echo "COVERAGE agent finished"
