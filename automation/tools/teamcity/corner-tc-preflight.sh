#!/usr/bin/env bash
# Shared contract checks for TeamCity pipeline steps.
set -u

# shellcheck source=automation/tools/teamcity/corner-tc-state.sh
source "${REPO_ROOT:-$PWD}/automation/tools/teamcity/corner-tc-state.sh"

corner_tc_contract_fail() {
  local msg="$1"
  echo "ERROR: contract violation: ${msg}" >&2
  exit 1
}

corner_tc_require_env() {
  local name
  for name in "$@"; do
    if [ -z "${!name:-}" ]; then
      corner_tc_contract_fail "env ${name} is required"
    fi
  done
}

corner_tc_require_file() {
  local file="$1"
  if [ ! -f "$file" ]; then
    corner_tc_contract_fail "required file missing: ${file}"
  fi
}

corner_tc_require_step_ok() {
  local step_id="$1"
  local label="${2:-$1}"
  if ! corner_tc_has_step_ok "$step_id"; then
    corner_tc_contract_fail "upstream step marker missing: ${step_id} (${label})"
  fi
}
