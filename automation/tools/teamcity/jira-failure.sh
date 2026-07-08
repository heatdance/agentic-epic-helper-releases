#!/usr/bin/env bash
set -eu

REPO_ROOT="${REPO_ROOT:-$PWD}"
# shellcheck source=automation/tools/teamcity/load-teamcity-params.sh
source "${REPO_ROOT}/automation/tools/teamcity/load-teamcity-params.sh"
_corner_tc_load_params

# shellcheck source=automation/tools/teamcity/jira-notify-guard.sh
source "${REPO_ROOT}/automation/tools/teamcity/jira-notify-guard.sh"
_jira_notify_skip_if_success_posted

export EPIC_KEY="${EPIC_KEY:-}"
export QA_TASK_KEY="${QA_TASK_KEY:?QA_TASK_KEY empty}"
export JIRA_API_TOKEN="${JIRA_API_TOKEN:?JIRA_API_TOKEN empty}"
export JIRA_BASE_URL="${JIRA_BASE_URL:-https://jira.in.devexperts.com}"
export TEAMCITY_BUILD_URL="${TEAMCITY_BUILD_URL:-unknown}"

python3 automation/tools/teamcity/jira_failure.py
_jira_notify_mark_failure_posted
