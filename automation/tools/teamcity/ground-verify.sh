#!/usr/bin/env bash
set -u

# shellcheck source=automation/tools/teamcity/corner-tc-overview.sh
source automation/tools/teamcity/corner-tc-overview.sh
corner_tc_step_begin "GROUND verify"

# shellcheck source=automation/tools/teamcity/corner-tc-preflight.sh
source automation/tools/teamcity/corner-tc-preflight.sh
corner_tc_require_step_ok "07-ground-agent" "GROUND agent"

# shellcheck source=automation/tools/teamcity/corner-tc-epic-paths.sh
source automation/tools/teamcity/corner-tc-epic-paths.sh

EPIC="${EPIC_KEY:-}"
if [ -z "$EPIC" ]; then
  echo "ERROR: EPIC_KEY is empty"
  exit 1
fi

COV="$(corner_tc_resolve_json "$EPIC" coverage)"
REF="$(corner_tc_resolve_json "$EPIC" ref)"

if [ ! -f "$COV" ] || [ ! -f "$REF" ]; then
  echo "ERROR: missing $COV or $REF"
  exit 1
fi

python3 automation/tools/ground_verify.py --mode emit --coverage "$COV" --ref "$REF" || exit 1
corner_tc_mark_step_ok "08-ground-verify" "GROUND verify"
echo "GROUND verify OK"
