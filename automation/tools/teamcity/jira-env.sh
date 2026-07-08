#!/usr/bin/env bash
# Shared env load + preflight for Jira notify steps (11 success / 12 failure).
set -u

REPO_ROOT="${REPO_ROOT:-$PWD}"

_corner_jira_flag() {
  if [ -n "${1:-}" ]; then
    echo set
  else
    echo MISSING
  fi
}

_corner_jira_load_env() {
  # shellcheck source=automation/tools/teamcity/load-teamcity-params.sh
  source "${REPO_ROOT}/automation/tools/teamcity/load-teamcity-params.sh"
  _corner_tc_load_params

  export EPIC_KEY="${EPIC_KEY:-}"
  export QA_TASK_KEY="${QA_TASK_KEY:-}"
  export JIRA_API_TOKEN="${JIRA_API_TOKEN:-}"
  export JIRA_BASE_URL="${JIRA_BASE_URL:-https://jira.in.devexperts.com}"

  if [ -z "${TEAMCITY_BUILD_URL:-}" ]; then
    resolved="$(python3 -c "
import sys
sys.path.insert(0, '${REPO_ROOT}/automation/tools/teamcity')
from read_teamcity_params import resolve_teamcity_build_url
print(resolve_teamcity_build_url())
")"
    if [ -n "$resolved" ]; then
      export TEAMCITY_BUILD_URL="$resolved"
    fi
  fi

  echo "Jira preflight: epic=${EPIC_KEY:-?} qa=${QA_TASK_KEY:-?} build_url=$(_corner_jira_flag "${TEAMCITY_BUILD_URL:-}") token=$(_corner_jira_flag "${JIRA_API_TOKEN:-}")"
}

_corner_jira_require_common() {
  if [ -z "${QA_TASK_KEY:-}" ]; then
    echo "ERROR: QA_TASK_KEY empty (set build param QA_TASK_KEY or env.QA_TASK_KEY=%QA_TASK_KEY%)" >&2
    exit 1
  fi
  if [ -z "${JIRA_API_TOKEN:-}" ]; then
    echo "ERROR: JIRA_API_TOKEN empty (set password param and env.JIRA_API_TOKEN=%JIRA_API_TOKEN%)" >&2
    exit 1
  fi
}

_corner_jira_require_success() {
  _corner_jira_require_common
  if [ -z "${EPIC_KEY:-}" ]; then
    echo "ERROR: EPIC_KEY empty" >&2
    exit 1
  fi
  if [ -z "${TEAMCITY_BUILD_URL:-}" ]; then
    echo "ERROR: TEAMCITY_BUILD_URL empty (set env or ensure teamcity.build.url in TeamCity properties)" >&2
    exit 1
  fi
}

_corner_jira_require_failure() {
  _corner_jira_require_common
  if [ -z "${TEAMCITY_BUILD_URL:-}" ]; then
    export TEAMCITY_BUILD_URL="unknown"
    echo "WARN: TEAMCITY_BUILD_URL unset — using 'unknown' in failure comment"
  fi
}
