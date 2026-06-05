#!/usr/bin/env python3
"""Fetch Done TCD candidates for CRTQA stats incremental_update (Jira REST)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TOOLS = REPO / "automation" / "tools"
sys.path.insert(0, str(TOOLS))

from crtqa_stats.gather import (  # noqa: E402
    classify_task_summary,
    issue_fields,
    logged_hours_for_lane,
)
from crtqa_stats.ingest import load_contract, load_state  # noqa: E402
from crtqa_stats.jira_rest import (  # noqa: E402
    ISSUE_DETAIL_FIELDS,
    jira_request,
    jira_search,
    load_jira_env,
    normalize_issue,
)

EPIC_IN_SUMMARY = re.compile(r"\b(CRT-\d+)\b", re.I)


def epic_from_issue(issue: dict) -> str | None:
    fields = issue_fields(issue)
    el = fields.get("customfield_10006")
    if isinstance(el, str) and el.upper().startswith("CRT-"):
        return el.upper()
    if isinstance(el, dict) and el.get("key"):
        return str(el["key"]).upper()
    m = EPIC_IN_SUMMARY.search(str(fields.get("summary") or issue.get("summary") or ""))
    return m.group(1).upper() if m else None


def _eligible_epics(state: dict) -> set[str]:
    corpus = {str(k).upper() for k in (state.get("corpus_epic_keys") or [])}
    attested = {
        str(k).upper()
        for k, v in (state.get("attestation_by_epic") or {}).items()
        if v.get("ai_assisted")
    }
    return corpus | attested


def fetch_incremental(jira_user: str, out_dir: Path) -> dict:
    contract = load_contract()
    state = load_state(jira_user, contract)
    included = {str(k).upper() for k in (state.get("included_issue_keys") or [])}
    eligible_epics = _eligible_epics(state)

    base, token = load_jira_env()
    jql = str(contract.get("incremental_tcd_jql_template") or "")
    limit = int(contract.get("batch_size_search") or 50)
    artifact_rules = contract.get("artifact_rules") or []
    exclude_rules = contract.get("exclude_from_qa") or []

    candidates: list[dict] = []
    start = 0
    total = 1
    while start < total:
        page = jira_search(base, token, jql, ISSUE_DETAIL_FIELDS, start, limit)
        total = int(page.get("total") or 0)
        for raw in page.get("issues") or []:
            key = str(raw.get("key") or "").upper()
            if not key or key in included:
                continue
            detail = normalize_issue(
                jira_request(base, token, f"/rest/api/2/issue/{key}", {"fields": ISSUE_DETAIL_FIELDS})
            )
            fields = issue_fields(detail)
            summary = str(fields.get("summary") or "")
            it_obj = fields.get("issuetype") or detail.get("issue_type") or {}
            issuetype = it_obj.get("name") if isinstance(it_obj, dict) else str(it_obj or "")
            lane = classify_task_summary(summary, issuetype, artifact_rules, exclude_rules)
            if lane != "tcd":
                continue
            epic = epic_from_issue(detail)
            if not epic or epic not in eligible_epics:
                continue
            logged, others, scope, anoms = logged_hours_for_lane(
                lane,
                artifact_rules,
                fields.get("worklog"),
                fields.get("timetracking"),
                jira_user,
            )
            if logged <= 0:
                continue
            est = fields.get("customfield_11250")
            try:
                est_h = float(est) if est is not None else float(contract.get("default_estimate_hours", 8))
            except (TypeError, ValueError):
                est_h = float(contract.get("default_estimate_hours", 8))
            candidates.append(
                {
                    "key": key,
                    "epic": epic,
                    "summary": summary,
                    "logged_hours": round(float(logged), 2),
                    "estimate_hours": est_h,
                    "others_logged_hours": round(float(others), 2),
                    "logged_scope": scope,
                    "anomalies": anoms,
                }
            )
            issue_path = out_dir / "issues" / f"{key}.json"
            issue_path.parent.mkdir(parents=True, exist_ok=True)
            issue_path.write_text(json.dumps(detail, indent=2), encoding="utf-8")
        start += limit

    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "jira_user": jira_user,
        "eligible_epics": sorted(eligible_epics),
        "included_issue_keys_count": len(included),
        "candidates": candidates,
    }
    (out_dir / "candidates.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--jira-user", required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    args = p.parse_args()
    report = fetch_incremental(args.jira_user, args.out_dir)
    print(
        json.dumps(
            {
                "jira_user": report["jira_user"],
                "candidates": len(report["candidates"]),
                "eligible_epics": len(report["eligible_epics"]),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
