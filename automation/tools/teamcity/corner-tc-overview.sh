#!/usr/bin/env bash
# TeamCity overview: EPIC_KEY + human-readable step in Status column (setParameter + buildStatus).
# Source from pipeline step scripts; see automation/CI/teamcity-setup.md § Overview status.
set -u

_corner_tc_sm_escape() {
  local s="$1"
  s="${s//|/||}"
  s="${s//'/'|\'}"
  printf '%s' "$s"
}

_corner_tc_overview_epic() {
  echo "${EPIC_KEY:-unknown}"
}

corner_tc_step_begin() {
  local label="$1"
  local epic esc_label esc_epic
  epic="$(_corner_tc_overview_epic)"
  esc_label="$(_corner_tc_sm_escape "$label")"
  esc_epic="$(_corner_tc_sm_escape "$epic")"
  echo "##teamcity[setParameter name='env.CORNER_CI_STEP' value='${esc_label}']"
  echo "##teamcity[progressMessage '${esc_epic} - ${esc_label}']"
}

corner_tc_status_success() {
  local epic esc_epic
  epic="$(_corner_tc_overview_epic)"
  esc_epic="$(_corner_tc_sm_escape "$epic")"
  echo "##teamcity[buildStatus text='${esc_epic} - Success']"
}

corner_tc_status_failure() {
  local step epic esc_step esc_epic
  step="${CORNER_CI_STEP:-unknown step}"
  epic="$(_corner_tc_overview_epic)"
  esc_step="$(_corner_tc_sm_escape "$step")"
  esc_epic="$(_corner_tc_sm_escape "$epic")"
  echo "##teamcity[buildStatus text='${esc_epic} - failed at ${esc_step}']"
}
