#!/usr/bin/env bash
# TeamCity: Corner Epic QA Console Gate (standalone test for step 6).
# Requires parameters: CRTQA_CONSOLE_TRANSPORT, CRTQA_SSH_USER,
# CRTQA_SSH_PRIVATE_KEY, CRTQA_SUDO_PASSWORD (see automation/docs/crtqa-console-ci.md).

set -u

export CRTQA_CONSOLE_TRANSPORT="${CRTQA_CONSOLE_TRANSPORT:-openssh}"
export CRTQA_SSH_USER="%CRTQA_SSH_USER%"

KEYFILE=$(mktemp)
chmod 600 "$KEYFILE"
cleanup() { rm -f "$KEYFILE"; }
trap cleanup EXIT

printf '%s' "%CRTQA_SSH_PRIVATE_KEY%" > "$KEYFILE"
export CRTQA_SSH_KEY_PATH="$KEYFILE"
export CRTQA_SUDO_PASSWORD="%CRTQA_SUDO_PASSWORD%"

echo "Console gate transport=$CRTQA_CONSOLE_TRANSPORT user=$CRTQA_SSH_USER"

python3 automation/tools/crtqa_console_probe.py --format both
RC=$?

if [ "$RC" -eq 0 ]; then
  echo "Console gate OK"
else
  echo "Console gate FAILED (exit $RC)"
fi

exit "$RC"
