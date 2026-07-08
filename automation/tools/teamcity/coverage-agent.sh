#!/usr/bin/env bash
set -euo pipefail

# shellcheck source=automation/tools/teamcity/agent-env.sh
source automation/tools/teamcity/agent-env.sh

EPIC="$EPIC_KEY"
PROMPT=$(cat <<EOF
COVERAGE: ${EPIC} strict_topology=yes strict_principal=yes

Follow the playbook .cursor/pipelines/coverage.md end-to-end for epic ${EPIC}.
Use user-mcp-atlassian MCP only for authoritative Jira/Confluence/Bitbucket content.
Requires existing epics/${EPIC}/${EPIC}-ref.json.
Write epics/${EPIC}/${EPIC}-coverage.json and epics/${EPIC}/${EPIC}-coverage.md.
Delete epics/${EPIC}/temp/ when done.

CI addendum: smart_checklist_markdown and -coverage.md must NOT contain internal oracle enum tokens
(first_tier_quote, text_configuration_closest_gte_qty, midpoint_invariant, mark_from_midpoint,
console_show_prices_first_tier, console_agent_event_quote, console_agent_event_text_configuration,
backup_midpoint_at_eod, unresolved). Use human-readable > Oracle: lines only; enums belong in JSON
checks[].oracle_rule / human_oracle_label. Contract: docs/coverage-draft-truth-contract.json
forbidden_in_smart_checklist_markdown.
EOF
)

python3 automation/tools/teamcity/run_pipeline_agent.py \
  --prompt "$PROMPT" \
  --require "epics/%EPIC_KEY%/%EPIC_KEY%-ref.json" \
  --require "epics/%EPIC_KEY%/%EPIC_KEY%-coverage.json" \
  --require "epics/%EPIC_KEY%/%EPIC_KEY%-coverage.md"

echo "COVERAGE agent finished"
