#!/usr/bin/env bash
set -u

# shellcheck source=automation/tools/teamcity/corner-tc-overview.sh
source automation/tools/teamcity/corner-tc-overview.sh
corner_tc_step_begin "COVERAGE verify"

# shellcheck source=automation/tools/teamcity/corner-tc-epic-paths.sh
source automation/tools/teamcity/corner-tc-epic-paths.sh

EPIC="${EPIC_KEY:-}"
if [ -z "$EPIC" ]; then
  echo "ERROR: EPIC_KEY is empty"
  exit 1
fi

COV="$(corner_tc_resolve_json "$EPIC" coverage)"
REF="$(corner_tc_resolve_json "$EPIC" ref)"

if [ ! -f "$COV" ]; then
  echo "ERROR: $COV not created"
  exit 1
fi

python3 automation/tools/coverage_verify.py \
  --mode draft_truth \
  --strict-topology \
  --strict-principal \
  --ref "$REF" \
  --coverage "$COV" || exit 1
echo "COVERAGE verify OK"
