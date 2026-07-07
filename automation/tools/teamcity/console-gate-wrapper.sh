#!/usr/bin/env bash
set -eu

# shellcheck source=automation/tools/teamcity/crtqa-openssh-env.sh
source automation/tools/teamcity/crtqa-openssh-env.sh

python3 automation/tools/crtqa_console_probe.py --format text
RC=$?

if [ "$RC" -eq 0 ]; then
  echo "Console gate OK"
else
  echo "Console gate FAILED (exit $RC)"
fi
exit "$RC"
