#!/usr/bin/env bash
set -u

# shellcheck source=automation/tools/teamcity/corner-tc-overview.sh
source automation/tools/teamcity/corner-tc-overview.sh
corner_tc_step_begin "COVERAGE verify"

EPIC="${EPIC_KEY:-}"
if [ -z "$EPIC" ]; then
  echo "ERROR: EPIC_KEY is empty"
  exit 1
fi

COV="epics/${EPIC}/${EPIC}-coverage.json"
REF="epics/${EPIC}/${EPIC}-ref.json"

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
