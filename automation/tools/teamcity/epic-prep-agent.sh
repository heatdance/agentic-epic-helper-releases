#!/usr/bin/env bash
set -euo pipefail

# shellcheck source=automation/tools/teamcity/agent-env.sh
source automation/tools/teamcity/agent-env.sh

# shellcheck source=automation/tools/teamcity/corner-tc-overview.sh
source automation/tools/teamcity/corner-tc-overview.sh
corner_tc_step_begin "EPIC-PREP agent"

# shellcheck source=automation/tools/teamcity/corner-tc-preflight.sh
source automation/tools/teamcity/corner-tc-preflight.sh
corner_tc_require_step_ok "01-verify-checkout" "Verify harness checkout"

# shellcheck source=automation/tools/teamcity/corner-tc-epic-paths.sh
source automation/tools/teamcity/corner-tc-epic-paths.sh

EPIC="$EPIC_KEY"
REF_PATH="$(corner_tc_dep_json "$EPIC" ref)"
PROMPT=$(cat <<EOF
EPIC-PREP: ${EPIC} strict_topology=yes strict_principal=yes

Follow the playbook .cursor/pipelines/epic-prep.md end-to-end for epic ${EPIC}.
Use user-mcp-atlassian MCP only for Jira, Confluence, and Bitbucket discovery — do not invent ticket or page content.
Run step 3c as one subprocess per requirement and record each in requirement_passes[]; a single sweep over all requirements fails the finalize gate.
Transcribe every row of each parameter table into snippet_text and parameter_inventory[] — the verifier re-derives the inventory from snippet_text and fails on omitted rows.
Write ${REF_PATH} under epics/${EPIC}/dependencies/ (pre-CLOSE JSON layout).
Delete epics/${EPIC}/temp/ when done (success or abort after temp was created).
EOF
)

python3 automation/tools/teamcity/run_pipeline_agent.py \
  --prompt "$PROMPT" \
  --require "epics/%EPIC_KEY%/dependencies/%EPIC_KEY%-ref.json"

corner_tc_mark_step_ok "02-epic-prep-agent" "EPIC-PREP agent"
echo "EPIC-PREP agent finished"
