#!/usr/bin/env bash
# Mutual guard for Jira success/failure steps in the same checkout (step 11 vs 12).
# IMPORTANT: "continue" paths must return 0 — callers use set -e; return 1 aborts the step.
set -u

REPO_ROOT="${REPO_ROOT:-$PWD}"
NOTIFY_DIR="${REPO_ROOT}/.teamcity-ci"
SUCCESS_MARKER="${NOTIFY_DIR}/jira-success.posted"
FAILURE_MARKER="${NOTIFY_DIR}/jira-failure.posted"

_jira_notify_skip_if_success_posted() {
  if [ -f "$SUCCESS_MARKER" ]; then
    echo "SKIP failure Jira comment: success comment already posted at $(tr -d '\n' <"$SUCCESS_MARKER")"
    echo "TeamCity: set step 12 Execute step to 'Even if some of the previous steps failed'; guard skips on green."
    exit 0
  fi
  return 0
}

_jira_notify_mark_success_posted() {
  mkdir -p "$NOTIFY_DIR"
  date -u +"%Y-%m-%dT%H:%M:%SZ" >"$SUCCESS_MARKER"
  echo "jira-notify: marked success posted ($SUCCESS_MARKER)"
}

_jira_notify_skip_if_failure_posted() {
  if [ -f "$FAILURE_MARKER" ]; then
    echo "SKIP success Jira comment: failure comment already posted at $(tr -d '\n' <"$FAILURE_MARKER")"
    exit 0
  fi
  return 0
}

_jira_notify_mark_failure_posted() {
  mkdir -p "$NOTIFY_DIR"
  date -u +"%Y-%m-%dT%H:%M:%SZ" >"$FAILURE_MARKER"
  echo "jira-notify: marked failure posted ($FAILURE_MARKER)"
}
