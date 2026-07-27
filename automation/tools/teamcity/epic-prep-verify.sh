#!/usr/bin/env bash
set -u

# shellcheck source=automation/tools/teamcity/corner-tc-overview.sh
source automation/tools/teamcity/corner-tc-overview.sh
corner_tc_step_begin "EPIC-PREP verify"

# shellcheck source=automation/tools/teamcity/corner-tc-preflight.sh
source automation/tools/teamcity/corner-tc-preflight.sh
corner_tc_require_step_ok "02-epic-prep-agent" "EPIC-PREP agent"

# shellcheck source=automation/tools/teamcity/corner-tc-epic-paths.sh
source automation/tools/teamcity/corner-tc-epic-paths.sh

EPIC="${EPIC_KEY:-}"
if [ -z "$EPIC" ]; then
  echo "ERROR: EPIC_KEY is empty"
  exit 1
fi

REF="$(corner_tc_resolve_json "$EPIC" ref)"
if [ ! -f "$REF" ]; then
  echo "ERROR: $REF not created by EPIC-PREP agent"
  exit 1
fi

python3 automation/tools/epic_prep_verify.py \
  --mode ref \
  --strict-topology \
  --strict-principal \
  --ref "$REF" || exit 1
corner_tc_mark_step_ok "03-epic-prep-verify" "EPIC-PREP verify"
echo "EPIC-PREP verify OK"
