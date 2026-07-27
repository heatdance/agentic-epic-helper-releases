#!/usr/bin/env bash
set -euo pipefail

# shellcheck source=automation/tools/teamcity/agent-env.sh
source automation/tools/teamcity/agent-env.sh

# shellcheck source=automation/tools/teamcity/corner-tc-overview.sh
source automation/tools/teamcity/corner-tc-overview.sh
corner_tc_step_begin "COVERAGE agent"

# shellcheck source=automation/tools/teamcity/corner-tc-preflight.sh
source automation/tools/teamcity/corner-tc-preflight.sh
corner_tc_require_step_ok "03-epic-prep-verify" "EPIC-PREP verify"

# shellcheck source=automation/tools/teamcity/corner-tc-epic-paths.sh
source automation/tools/teamcity/corner-tc-epic-paths.sh

EPIC="$EPIC_KEY"
REF_PATH="$(corner_tc_dep_json "$EPIC" ref)"
COV_PATH="$(corner_tc_dep_json "$EPIC" coverage)"
MD_PATH="$(corner_tc_coverage_md "$EPIC")"
PROMPT=$(cat <<EOF
COVERAGE: ${EPIC} strict_topology=yes strict_principal=yes

Follow the playbook .cursor/pipelines/coverage.md end-to-end for epic ${EPIC}.
Use user-mcp-atlassian MCP only for authoritative Jira/Confluence/Bitbucket content.
Requires existing ${REF_PATH}.
Write ${COV_PATH} and ${MD_PATH} (JSON under dependencies/; coverage.md at epic root).
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
  --require "epics/%EPIC_KEY%/dependencies/%EPIC_KEY%-ref.json" \
  --require "epics/%EPIC_KEY%/dependencies/%EPIC_KEY%-coverage.json" \
  --require "epics/%EPIC_KEY%/%EPIC_KEY%-coverage.md"

corner_tc_mark_step_ok "04-coverage-agent" "COVERAGE agent"
echo "COVERAGE agent finished"
