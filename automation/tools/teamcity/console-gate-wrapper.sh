#!/usr/bin/env bash
# Console gate for Pipeline (VCS checkout). TeamCity step exports CRTQA_* env vars first.
set -u

export CRTQA_CONSOLE_TRANSPORT="${CRTQA_CONSOLE_TRANSPORT:-openssh}"

KEYFILE=$(mktemp /tmp/crtqa-ssh-XXXXXX) || exit 1
chmod 600 "$KEYFILE"
cleanup() { rm -f "$KEYFILE"; }
trap cleanup EXIT

B64="${CRTQA_SSH_PRIVATE_KEY_B64:-}"
if [ -z "$B64" ]; then
  echo "ERROR: CRTQA_SSH_PRIVATE_KEY_B64 empty"
  exit 1
fi

printf '%s' "$B64" | base64 -d > "$KEYFILE"
export CRTQA_SSH_KEY_PATH="$KEYFILE"

echo "Console gate transport=$CRTQA_CONSOLE_TRANSPORT user=${CRTQA_SSH_USER:-?}"

python3 automation/tools/crtqa_console_probe.py --format text
RC=$?

if [ "$RC" -eq 0 ]; then
  echo "Console gate OK"
else
  echo "Console gate FAILED (exit $RC)"
fi
exit "$RC"
