#!/usr/bin/env bash
# TeamCity password params are not always present in env for VCS-hosted scripts unless
# referenced in the step UI or exposed as env.* — load from agent properties file.
set -u

_corner_tc_load_params() {
  local tmp exports=0
  tmp="$(mktemp)"
  if python3 "${REPO_ROOT:-$PWD}/automation/tools/teamcity/read_teamcity_params.py" "$tmp"; then
    if [ -s "$tmp" ]; then
      # shellcheck source=/dev/null
      source "$tmp"
      exports=1
      echo "Loaded TeamCity params from properties file ($(wc -l <"$tmp" | tr -d ' ') exports)"
    fi
  fi
  rm -f "$tmp"
  return 0
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  REPO_ROOT="${REPO_ROOT:-$PWD}"
  _corner_tc_load_params
fi
