#!/usr/bin/env python3
"""Parse Jira payloads and classify QA tasks for CRTQA stats v5."""

from __future__ import annotations

import re
from typing import Any

EPIC_KEY_RE = re.compile(r"\b(CRT-\d+)\b", re.IGNORECASE)
HOURS_PER_SP = 8
MULTI_PERSON_OTHERS_HOURS_STRICT = 2.0
QA_LANES = (
    "tcd",
    "epic_testing",
    "epic_validation",
    "release_notes",
    "update_test",
)
SINGLE_TASK_LANES = ("tcd", "epic_testing", "epic_validation")
AGGREGATE_LANES = ("release_notes", "update_test")


def _summary_has_any(summary: str, needles: list[str]) -> bool:
    s = summary.lower()
    return any(n.lower() in s for n in needles)


def is_excluded_qa_task(summary: str, issuetype: str | None, exclude_rules: list[dict]) -> bool:
    it = (issuetype or "").lower()
    for rule in exclude_rules:
        if rule.get("issuetype", "").lower() != it:
            continue
        if _summary_has_any(summary, rule.get("summary_needles") or []):
            return True
    return False


def logged_hours_for_lane(
    lane: str,
    artifact_rules: list[dict],
    worklog_payload: dict[str, Any] | None,
    timetracking: dict[str, Any] | None,
    username: str,
) -> tuple[float, float, str, list[str]]:
    """Return (logged_hours, others_hours, logged_scope, anomalies)."""
    scope = "user_worklog"
    for rule in artifact_rules:
        if rule.get("lane") == lane:
            scope = str(rule.get("logged_scope") or "user_worklog")
            break
    anomalies: list[str] = []
    tt = timetracking or {}
    if scope == "issue_time_spent":
        spent_raw = tt.get("time_spent") or tt.get("timeSpent")
        spent = parse_jira_duration(spent_raw)
        if spent is None and tt.get("timeSpentSeconds") is not None:
            try:
                spent = round(int(tt["timeSpentSeconds"]) / 3600, 2)
            except (TypeError, ValueError):
                spent = None
        if spent is None and tt.get("time_spent_seconds") is not None:
            try:
                spent = round(int(tt["time_spent_seconds"]) / 3600, 2)
            except (TypeError, ValueError):
                spent = None
        user_h, others_h, wl_anoms = logged_from_worklogs(worklog_payload, username)
        anomalies.extend(wl_anoms)
        if spent is None:
            spent = 0.0
            if spent_raw:
                anomalies.append("logged_unparsed")
        return spent, others_h, scope, anomalies
    user_h, others_h, wl_anoms = logged_from_worklogs(worklog_payload, username)
    anomalies.extend(wl_anoms)
    return user_h, others_h, scope, anomalies


def classify_task_with_rules(
    summary: str, issuetype: str | None, artifact_rules: list[dict]
) -> str:
    it = (issuetype or "").lower()
    for rule in artifact_rules:
        if rule.get("issuetype", "").lower() != it:
            continue
        if _summary_has_any(summary, rule.get("summary_needles") or []):
            return str(rule["lane"])
    s = summary.lower()
    if "release notes" in s or "release note" in s:
        return "release_notes" if it == "test execution" else "other"
    if it == "qa task" and "update test" in s:
        return "update_test"
    if "test case development" in s and it == "test execution":
        return "tcd"
    return "other"


def parse_jira_duration(value: str | None) -> float | None:
    if not value or not str(value).strip():
        return None
    s = str(value).strip().lower()
    total_seconds = 0
    for amount, unit in re.findall(r"(\d+(?:\.\d+)?)\s*([wdhm])", s):
        n = float(amount)
        if unit == "w":
            total_seconds += n * 5 * 8 * 3600
        elif unit == "d":
            total_seconds += n * 8 * 3600
        elif unit == "h":
            total_seconds += n * 3600
        elif unit == "m":
            total_seconds += n * 60
    if total_seconds > 0:
        return round(total_seconds / 3600, 2)
    if s.isdigit():
        return round(int(s) / 3600, 2)
    return None


def _draft_hours(fields: dict[str, Any]) -> float | None:
    raw = fields.get("customfield_11250")
    if raw is None:
        return None
    if isinstance(raw, dict):
        v = raw.get("value")
    else:
        v = raw
    try:
        h = float(v)
        return h if h > 0 else None
    except (TypeError, ValueError):
        return None


def estimate_from_fields(
    fields: dict[str, Any], default_hours: float = HOURS_PER_SP
) -> tuple[float, str, list[str]]:
    anomalies: list[str] = []
    draft = _draft_hours(fields)
    if draft is not None:
        return draft, "draft", anomalies
    tt = fields.get("timetracking") or {}
    orig = parse_jira_duration(tt.get("original_estimate") or tt.get("originalEstimate"))
    if orig is not None and orig > 0:
        return orig, "original", anomalies
    anomalies.append("estimate_defaulted_1sp")
    return default_hours, "default_8h", anomalies


def logged_from_worklogs(
    worklog_payload: dict[str, Any] | None, username: str
) -> tuple[float, float, list[str]]:
    anomalies: list[str] = []
    if not worklog_payload:
        return 0.0, 0.0, ["no_worklog_payload"]
    logs = worklog_payload.get("worklogs") or []
    user_sec = 0
    others_sec = 0
    user_lower = username.lower()
    for wl in logs:
        author = wl.get("author") or {}
        name = (author.get("name") or author.get("key") or "").lower()
        sec = int(wl.get("timeSpentSeconds") or 0)
        if name == user_lower:
            user_sec += sec
        else:
            others_sec += sec
    user_h = round(user_sec / 3600, 2)
    others_h = round(others_sec / 3600, 2)
    total = int(worklog_payload.get("total") or len(logs))
    if total > len(logs):
        anomalies.append("worklog_pagination_needed")
    if others_h > MULTI_PERSON_OTHERS_HOURS_STRICT:
        anomalies.append("multi_person_task")
    return user_h, others_h, anomalies


def _issue_type_name(linked: dict[str, Any]) -> str:
    it = linked.get("issue_type") or linked.get("issuetype") or {}
    if isinstance(it, dict):
        return str(it.get("name") or "")
    return str(it)


def _linked_key(linked: dict[str, Any]) -> str | None:
    return linked.get("key")


def extract_epics_from_issue(issue: dict[str, Any]) -> tuple[list[str], str, list[str]]:
    anomalies: list[str] = []
    fields = issue.get("fields") if isinstance(issue.get("fields"), dict) else issue
    links = fields.get("issuelinks") or issue.get("issuelinks") or []
    epics: set[str] = set()
    used_tests_link = False

    for link in links:
        ltype = (link.get("type") or {}).get("name") or ""
        for side in ("inward_issue", "outward_issue"):
            linked = link.get(side)
            if not linked:
                continue
            lk = _linked_key(linked)
            if not lk:
                continue
            lf = linked.get("fields") or linked
            it_name = _issue_type_name(lf)
            if it_name.lower() == "epic" and lk.upper().startswith("CRT-"):
                epics.add(lk.upper())
                if ltype == "Tests" or "test" in ltype.lower():
                    used_tests_link = True
                else:
                    anomalies.append("epic_link_not_tests_type")

    summary = str(fields.get("summary") or issue.get("summary") or "")
    summary_hits = {m.group(1).upper() for m in EPIC_KEY_RE.finditer(summary)}
    if summary_hits and not epics:
        epics |= summary_hits
        method = "summary_regex"
    elif epics:
        method = "tests_link" if used_tests_link else "issuelink"
    else:
        method = "none"

    if len(epics) > 1:
        anomalies.append("multiple_epics")
    if epics:
        return sorted(epics), method, anomalies

    anomalies.append("no_epic_link")
    return [], "none", anomalies


def classify_task_summary(
    summary: str,
    issuetype: str | None = None,
    artifact_rules: list[dict] | None = None,
    exclude_rules: list[dict] | None = None,
) -> str:
    if exclude_rules and is_excluded_qa_task(summary, issuetype, exclude_rules):
        return "excluded"
    if artifact_rules:
        return classify_task_with_rules(summary, issuetype, artifact_rules)
    s = summary.lower()
    it = (issuetype or "").lower()
    if "release notes" in s or "release note" in s:
        return "release_notes"
    if it == "qa task" and "update test" in s:
        return "update_test"
    if "test case development" in s:
        return "tcd"
    if "epic testing" in s:
        return "epic_testing"
    if "epic validation" in s:
        return "epic_validation"
    return "other"


def issue_fields(raw: dict[str, Any]) -> dict[str, Any]:
    if isinstance(raw.get("fields"), dict):
        merged = dict(raw["fields"])
        for k in ("key", "worklog", "timetracking", "customfield_11250", "summary", "status"):
            if k in raw and k not in merged:
                merged[k] = raw[k]
        return merged
    return raw
