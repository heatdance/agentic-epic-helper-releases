#!/usr/bin/env bash
set -eu

export EPIC_KEY="${EPIC_KEY:-}"
export QA_TASK_KEY="${QA_TASK_KEY:?QA_TASK_KEY empty}"
export JIRA_API_TOKEN="${JIRA_API_TOKEN:?JIRA_API_TOKEN empty}"
export JIRA_BASE_URL="${JIRA_BASE_URL:-https://jira.in.devexperts.com}"
export TEAMCITY_BUILD_URL="${TEAMCITY_BUILD_URL:-unknown}"

python3 automation/tools/teamcity/jira_failure.py
