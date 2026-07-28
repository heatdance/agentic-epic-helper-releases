#!/usr/bin/env bash
set -u

# shellcheck source=automation/tools/teamcity/corner-tc-overview.sh
source automation/tools/teamcity/corner-tc-overview.sh
corner_tc_step_begin "COVERAGE verify"

# shellcheck source=automation/tools/teamcity/corner-tc-preflight.sh
source automation/tools/teamcity/corner-tc-preflight.sh
corner_tc_require_step_ok "04-coverage-agent" "COVERAGE agent"

# shellcheck source=automation/tools/teamcity/corner-tc-epic-paths.sh
source automation/tools/teamcity/corner-tc-epic-paths.sh

EPIC="${EPIC_KEY:-}"
if [ -z "$EPIC" ]; then
  echo "ERROR: EPIC_KEY is empty"
  exit 1
fi

COV="$(corner_tc_resolve_json "$EPIC" coverage)"
REF="$(corner_tc_resolve_json "$EPIC" ref)"
MD="$(corner_tc_resolve_md "$EPIC" coverage)"

if [ ! -f "$COV" ]; then
  echo "ERROR: $COV not created"
  exit 1
fi

MD_ARGS=()
if [ -f "$MD" ]; then
  MD_ARGS=(--md "$MD")
else
  echo "WARN: $MD absent; linting smart_checklist_markdown from JSON"
fi

python3 automation/tools/coverage_verify.py \
  --mode draft_truth \
  --strict-topology \
  --strict-principal \
  --ref "$REF" \
  ${MD_ARGS[@]+"${MD_ARGS[@]}"} \
  --coverage "$COV" || exit 1

# draft_truth covers breadth and scenario mapping only. The semantic gates
# (stub wording, availability placement, variation oracles, empty sections) and
# the variation_density statistic live in obligations mode.
python3 automation/tools/coverage_verify.py \
  --mode obligations \
  --ref "$REF" \
  ${MD_ARGS[@]+"${MD_ARGS[@]}"} \
  --coverage "$COV" || exit 1
corner_tc_mark_step_ok "05-coverage-verify" "COVERAGE verify"
echo "COVERAGE verify OK"
