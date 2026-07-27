#!/usr/bin/env bash
# TeamCity step state markers (.teamcity-ci/state/*.ok)
set -u

corner_tc_state_dir() {
  local root="${REPO_ROOT:-$PWD}"
  echo "${root}/.teamcity-ci/state"
}

corner_tc_state_file() {
  local step_id="$1"
  echo "$(corner_tc_state_dir)/${step_id}.ok"
}

corner_tc_state_reset() {
  local state_dir
  state_dir="$(corner_tc_state_dir)"
  rm -rf "$state_dir"
  mkdir -p "$state_dir"
}

corner_tc_mark_step_ok() {
  local step_id="$1"
  local label="${2:-$1}"
  local f
  f="$(corner_tc_state_file "$step_id")"
  mkdir -p "$(dirname "$f")"
  printf '%s | %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$label" >"$f"
  echo "state: OK ${step_id} (${label})"
}

corner_tc_has_step_ok() {
  local step_id="$1"
  local f
  f="$(corner_tc_state_file "$step_id")"
  [ -f "$f" ]
}

corner_tc_last_ok_label() {
  local state_dir
  state_dir="$(corner_tc_state_dir)"
  if [ ! -d "$state_dir" ]; then
    return 0
  fi

  local latest
  latest="$(ls -1 "$state_dir"/*.ok 2>/dev/null | sort | tail -n 1)"
  if [ -z "$latest" ]; then
    return 0
  fi
  awk -F' \| ' 'NR==1{print $2}' "$latest"
}
