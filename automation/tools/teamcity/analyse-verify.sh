#!/usr/bin/env bash
set -u

# shellcheck source=automation/tools/teamcity/corner-tc-overview.sh
source automation/tools/teamcity/corner-tc-overview.sh
corner_tc_step_begin "ANALYSE verify"

# shellcheck source=automation/tools/teamcity/corner-tc-preflight.sh
source automation/tools/teamcity/corner-tc-preflight.sh
corner_tc_require_step_ok "09-analyse-agent" "ANALYSE agent"

# shellcheck source=automation/tools/teamcity/corner-tc-epic-paths.sh
source automation/tools/teamcity/corner-tc-epic-paths.sh

EPIC="${EPIC_KEY:-}"
if [ -z "$EPIC" ]; then
  echo "ERROR: EPIC_KEY is empty"
  exit 1
fi

ANALYSIS="$(corner_tc_resolve_json "$EPIC" analysis)"
COV="$(corner_tc_resolve_json "$EPIC" coverage)"
REF="$(corner_tc_resolve_json "$EPIC" ref)"

if [ ! -f "$ANALYSIS" ]; then
  echo "ERROR: $ANALYSIS not created"
  exit 1
fi
if [ ! -f "$COV" ] || [ ! -f "$REF" ]; then
  echo "ERROR: missing $COV or $REF"
  exit 1
fi

python3 automation/tools/analysis_verify.py \
  --mode draft_truth \
  --strict-topology \
  --strict-principal \
  --analysis "$ANALYSIS" \
  --coverage "$COV" \
  --ref "$REF" || exit 1
corner_tc_mark_step_ok "10-analyse-verify" "ANALYSE verify"
echo "ANALYSE verify OK"
