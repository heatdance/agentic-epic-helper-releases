#!/usr/bin/env bash
# Regression: skip-if-* must not return 1 under set -e when markers are absent (D15).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

export REPO_ROOT="$TMP"
# shellcheck source=automation/tools/teamcity/jira-notify-guard.sh
source "${ROOT}/automation/tools/teamcity/jira-notify-guard.sh"

# Fresh checkout: neither marker — both skip helpers must continue (return 0).
_jira_notify_skip_if_failure_posted
_jira_notify_skip_if_success_posted

_jira_notify_mark_success_posted
# Failure path should exit 0 (skip) when success already posted.
set +e
(
  set -euo pipefail
  # shellcheck source=automation/tools/teamcity/jira-notify-guard.sh
  source "${ROOT}/automation/tools/teamcity/jira-notify-guard.sh"
  _jira_notify_skip_if_success_posted
  echo "ERROR: expected exit 0 skip, continued" >&2
  exit 2
)
rc=$?
set -e
if [ "$rc" -ne 0 ]; then
  echo "ERROR: skip-on-success-marker exited $rc (want 0)" >&2
  exit 1
fi

echo "test_jira_notify_guard OK"
