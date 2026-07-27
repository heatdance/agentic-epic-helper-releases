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

# shellcheck source=automation/tools/teamcity/corner-tc-overview.sh
source "${REPO_ROOT}/automation/tools/teamcity/corner-tc-overview.sh"
corner_tc_status_failure

python3 automation/tools/teamcity/jira_failure.py
_jira_notify_mark_failure_posted
