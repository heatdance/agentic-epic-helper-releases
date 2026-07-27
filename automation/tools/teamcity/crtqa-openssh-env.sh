#!/usr/bin/env bash
# Source from TeamCity steps: exports OpenSSH CRTQA env for console gate + GROUND.
# Requires: CRTQA_SSH_USER, CRTQA_SSH_PRIVATE_KEY_B64, CRTQA_SUDO_PASSWORD

set -u

REPO_ROOT="${REPO_ROOT:-$PWD}"
# shellcheck source=automation/tools/teamcity/load-teamcity-params.sh
source "${REPO_ROOT}/automation/tools/teamcity/load-teamcity-params.sh"
_corner_tc_load_params

# shellcheck source=automation/tools/teamcity/corner-tc-preflight.sh
source "${REPO_ROOT}/automation/tools/teamcity/corner-tc-preflight.sh"

export CRTQA_CONSOLE_TRANSPORT="${CRTQA_CONSOLE_TRANSPORT:-openssh}"
corner_tc_require_env CRTQA_SSH_USER CRTQA_SSH_HOST CRTQA_SSH_PRIVATE_KEY_B64 CRTQA_SUDO_PASSWORD
export CRTQA_SSH_USER="${CRTQA_SSH_USER:?CRTQA_SSH_USER empty}"
export CRTQA_SSH_HOST="${CRTQA_SSH_HOST:?CRTQA_SSH_HOST empty}"

B64="${CRTQA_SSH_PRIVATE_KEY_B64:-}"
if [ -z "$B64" ]; then
  echo "ERROR: CRTQA_SSH_PRIVATE_KEY_B64 empty" >&2
  return 1 2>/dev/null || exit 1
fi

KEYFILE="${CRTQA_KEYFILE:-}"
if [ -z "$KEYFILE" ]; then
  KEYFILE=$(mktemp /tmp/crtqa-ssh-XXXXXX) || exit 1
  chmod 600 "$KEYFILE"
  export CRTQA_KEYFILE="$KEYFILE"
  export CRTQA_KEYFILE_CLEANUP=1
fi

printf '%s' "$B64" | base64 -d > "$KEYFILE"
export CRTQA_SSH_KEY_PATH="$KEYFILE"
export CRTQA_SUDO_PASSWORD="${CRTQA_SUDO_PASSWORD:?CRTQA_SUDO_PASSWORD empty}"

if [ "${CRTQA_KEYFILE_CLEANUP:-}" = "1" ]; then
  cleanup_crtqa_keyfile() { rm -f "${CRTQA_KEYFILE:-}"; }
  trap cleanup_crtqa_keyfile EXIT
fi

echo "CRTQA openssh env ready user=$CRTQA_SSH_USER host=$CRTQA_SSH_HOST keyfile=$CRTQA_SSH_KEY_PATH"
