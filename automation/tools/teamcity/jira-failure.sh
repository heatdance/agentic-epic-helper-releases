#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$PWD}"

# shellcheck source=automation/tools/teamcity/jira-env.sh
source "${REPO_ROOT}/automation/tools/teamcity/jira-env.sh"
_corner_jira_load_env
_corner_jira_require_failure

# shellcheck source=automation/tools/teamcity/jira-notify-guard.sh
source "${REPO_ROOT}/automation/tools/teamcity/jira-notify-guard.sh"
_jira_notify_skip_if_success_posted

# shellcheck source=automation/tools/teamcity/corner-tc-preflight.sh
source "${REPO_ROOT}/automation/tools/teamcity/corner-tc-preflight.sh"

# shellcheck source=automation/tools/teamcity/corner-tc-overview.sh
source "${REPO_ROOT}/automation/tools/teamcity/corner-tc-overview.sh"
if [ -z "${CORNER_CI_STEP:-}" ]; then
  LAST_OK="$(corner_tc_last_ok_label || true)"
  if [ -n "${LAST_OK:-}" ]; then
    export CORNER_CI_STEP="after ${LAST_OK}"
  fi
fi
corner_tc_status_failure

python3 automation/tools/teamcity/jira_failure.py
_jira_notify_mark_failure_posted
corner_tc_mark_step_ok "12-jira-failure" "JIRA fail"
