#!/usr/bin/env bash
# Shared env for TeamCity pipeline agent steps.
set -u

: "${EPIC_KEY:?EPIC_KEY empty}"
: "${CURSOR_API_KEY:?CURSOR_API_KEY empty}"

export REPO_ROOT="${REPO_ROOT:-$PWD}"

# Each TeamCity step is a fresh shell — re-apply bootstrap PATH/tools from step 1 marker.
# shellcheck source=automation/tools/teamcity/bootstrap-agent-env.sh
source "${REPO_ROOT}/automation/tools/teamcity/bootstrap-agent-env.sh"

export AGENT_MAX_WAIT_MINUTES="${AGENT_MAX_WAIT_MINUTES:-45}"

if ! [[ "$AGENT_MAX_WAIT_MINUTES" =~ ^[0-9]+$ ]] || [ "$AGENT_MAX_WAIT_MINUTES" -lt 1 ]; then
  echo "ERROR: AGENT_MAX_WAIT_MINUTES must be a positive integer"
  exit 1
fi
