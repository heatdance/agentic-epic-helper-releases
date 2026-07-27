#!/usr/bin/env bash
set -eu

# shellcheck source=automation/tools/teamcity/corner-tc-overview.sh
source automation/tools/teamcity/corner-tc-overview.sh
corner_tc_step_begin "Console gate"

# shellcheck source=automation/tools/teamcity/corner-tc-preflight.sh
source automation/tools/teamcity/corner-tc-preflight.sh
corner_tc_require_step_ok "05-coverage-verify" "COVERAGE verify"

# shellcheck source=automation/tools/teamcity/crtqa-openssh-env.sh
source automation/tools/teamcity/crtqa-openssh-env.sh

python3 automation/tools/crtqa_console_probe.py --format text
RC=$?

if [ "$RC" -eq 0 ]; then
  corner_tc_mark_step_ok "06-console-gate" "Console gate"
  echo "Console gate OK"
else
  echo "Console gate FAILED (exit $RC)"
fi
exit "$RC"
