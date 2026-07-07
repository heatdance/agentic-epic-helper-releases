#!/usr/bin/env bash
# TeamCity: Corner Epic QA Console Gate — paste ENTIRE file into build step.
# Required TeamCity parameters (password unless noted):
#   CRTQA_SSH_USER, CRTQA_SSH_PRIVATE_KEY_B64, CRTQA_SUDO_PASSWORD
# Optional: CRTQA_CONSOLE_TRANSPORT (default openssh)

set -u

export CRTQA_CONSOLE_TRANSPORT="${CRTQA_CONSOLE_TRANSPORT:-openssh}"
export CRTQA_SSH_USER="%CRTQA_SSH_USER%"

KEYFILE=$(mktemp /tmp/crtqa-ssh-XXXXXX) || { echo "ERROR: mktemp failed"; exit 1; }
chmod 600 "$KEYFILE"
cleanup() { rm -f "$KEYFILE"; }
trap cleanup EXIT

KEY_B64="%CRTQA_SSH_PRIVATE_KEY_B64%"
TC_PLACEHOLDER='CRTQA_SSH_PRIVATE_KEY_B64'
if [ "$KEY_B64" = "%${TC_PLACEHOLDER}%" ]; then
  KEY_B64=""
fi

if [ -z "$KEY_B64" ]; then
  echo "ERROR: set TeamCity parameter CRTQA_SSH_PRIVATE_KEY_B64 (base64 one-liner)"
  exit 1
fi

if ! printf '%s' "$KEY_B64" | base64 -d > "$KEYFILE" 2>/dev/null; then
  echo "ERROR: CRTQA_SSH_PRIVATE_KEY_B64 is not valid base64"
  exit 1
fi

if ! head -1 "$KEYFILE" | grep -q 'BEGIN.*PRIVATE KEY'; then
  echo "ERROR: decoded key is not a PEM private key"
  exit 1
fi

export CRTQA_SSH_KEY_PATH="$KEYFILE"
export CRTQA_SUDO_PASSWORD="%CRTQA_SUDO_PASSWORD%"

echo "Console gate transport=$CRTQA_CONSOLE_TRANSPORT user=$CRTQA_SSH_USER keyfile=$KEYFILE"

ssh-keygen -y -f "$KEYFILE" >/dev/null 2>&1 || {
  echo "ERROR: ssh-keygen cannot read key"
  exit 1
}

python3 automation/tools/crtqa_console_probe.py --format text
RC=$?

if [ "$RC" -eq 0 ]; then
  echo "Console gate OK"
else
  echo "Console gate FAILED (exit $RC)"
fi

exit "$RC"
