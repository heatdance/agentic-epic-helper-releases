#!/usr/bin/env python3
"""Process QA task list + issue detail JSON into v5 state for initial_assessment."""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TOOLS = REPO / "automation" / "tools"
sys.path.insert(0, str(TOOLS))

from crtqa_stats.apply_categories import (  # noqa: E402
    apply_epic_categories_to_state,
    jira_blob_from_meta,
)
from crtqa_stats.categories import classify_epic, tcd_size_band  # noqa: E402
from crtqa_stats.gather import (  # noqa: E402
    AGGREGATE_LANES,
    QA_LANES,
    SINGLE_TASK_LANES,
    classify_task_summary,
    issue_fields,
)
from crtqa_stats.ingest import enrich_row_from_issue  # noqa: E402
from crtqa_stats.ingest import (  # noqa: E402
    apply_corpus_gate,
    load_contract,
    new_state_skeleton,
    save_state,
)

EPIC_IN_SUMMARY = re.compile(r"\b(CRT-\d+)\b", re.I)


def epic_from_summary(summary: str) -> str | None:
    m = EPIC_IN_SUMMARY.search(summary or "")
    return m.group(1).upper() if m else None


def epic_from_issue(issue: dict) -> str | None:
    fields = issue_fields(issue)
    el = fields.get("customfield_10006")
    if isinstance(el, str) and el.upper().startswith("CRT-"):
        return el.upper()
    if isinstance(el, dict) and el.get("key"):
        return str(el["key"]).upper()
    return epic_from_summary(str(fields.get("summary") or ""))


def _issue_type_name(raw: dict, fields: dict) -> str:
    it_obj = fields.get("issuetype") or raw.get("issue_type") or {}
    if isinstance(it_obj, dict):
        return str(it_obj.get("name") or "")
    return str(it_obj or "")


def main() -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--jira-user", required=True)
    p.add_argument("--tests-count", type=int, required=True)
    p.add_argument("--qa-list", type=Path, required=True, help="MCP jira_search QA tasks JSON")
    p.add_argument("--issues-dir", type=Path, required=True, help="Dir of jira_get_issue JSON files")
    p.add_argument("--epic-meta", type=Path, default=None, help="epic-meta.json from fetch step")
    p.add_argument(
        "--exclude-epics",
        nargs="*",
        default=[],
        help="Epic keys excluded from corpus (e.g. AI-assisted); stored in attestation_by_epic",
    )
    args = p.parse_args()
    exclude_epics = {e.upper() for e in args.exclude_epics}

    contract = load_contract()
    qa_data = json.loads(args.qa_list.read_text(encoding="utf-8"))
    qa_issues = qa_data.get("issues") or []

    artifact_rules = contract.get("artifact_rules") or []
    exclude_rules = contract.get("exclude_from_qa") or []

    epic_tasks: dict[str, list[dict]] = defaultdict(list)
    metrics: dict[str, dict] = {}
    raw_issues: dict[str, dict] = {}

    for f in sorted(args.issues_dir.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        payload = data.get("result")
        if isinstance(payload, str):
            issue = json.loads(payload)
        elif isinstance(data, dict) and data.get("key"):
            issue = data
        else:
            issue = payload or data
        key = issue.get("key")
        if key:
            raw_issues[key] = issue

    for qi in qa_issues:
        key = qi.get("key")
        if not key:
            continue
        issue = raw_issues.get(key)
        if not issue:
            continue
        fields = issue_fields(issue)
        summary = str(fields.get("summary") or qi.get("summary") or "")
        issuetype = _issue_type_name(issue, fields)
        lane = classify_task_summary(summary, issuetype, artifact_rules, exclude_rules)
        if lane in ("excluded", "other"):
            continue
        epic = epic_from_issue(issue)
        if not epic:
            continue
        if epic in exclude_epics:
            if lane != "tcd":
                continue
            try:
                cmp_row = enrich_row_from_issue(
                    issue,
                    jira_user=args.jira_user,
                    epic_link=epic,
                    role="comparison",
                    contract=contract,
                )
            except ValueError:
                continue
            metrics[key] = {
                "task_key": key,
                "epic_key": epic,
                "lane": lane,
                "summary": summary,
                "estimate_hours": cmp_row["draft_estimate_hours"],
                "estimate_source": cmp_row.get("estimate_source"),
                "logged_hours": cmp_row["hours_logged"],
                "others_logged_hours": cmp_row.get("others_logged_hours", 0),
                "anomalies": cmp_row.get("anomalies") or [],
                "role": "comparison",
            }
            continue
        epic_tasks[epic].append({"key": key, "lane": lane, "summary": summary})
        try:
            row = enrich_row_from_issue(
                issue,
                jira_user=args.jira_user,
                epic_link=epic,
                role="corpus",
                contract=contract,
            )
        except ValueError:
            continue
        metrics[key] = {
            "task_key": key,
            "epic_key": epic,
            "lane": lane,
            "summary": summary,
            "estimate_hours": row["draft_estimate_hours"],
            "estimate_source": row.get("estimate_source"),
            "logged_hours": row["hours_logged"],
            "others_logged_hours": row.get("others_logged_hours", 0),
            "anomalies": row.get("anomalies") or [],
        }

    gate_rows = [
        {
            "epic_link": epic,
            "lane": t["lane"],
            "hours_logged": metrics.get(t["key"], {}).get("logged_hours", 0),
        }
        for epic, tasks in epic_tasks.items()
        for t in tasks
        if t["key"] in metrics
    ]
    gated = apply_corpus_gate(
        sorted(epic_tasks.keys()),
        gate_rows,
        require_user_logged=bool(contract.get("corpus_require_user_logged", True)),
    )

    epic_meta: dict = {}
    if args.epic_meta and args.epic_meta.is_file():
        epic_meta = json.loads(args.epic_meta.read_text(encoding="utf-8"))

    epic_classifications = {
        ek: classify_epic(ek, jira_blob_from_meta(epic_meta.get(ek)))
        for ek in gated
    }
    display: list[dict] = []
    for epic in gated:
        by_lane: dict[str, list[str]] = defaultdict(list)
        for t in epic_tasks.get(epic, []):
            if t["key"] in metrics:
                by_lane[t["lane"]].append(t["key"])
        for lane in SINGLE_TASK_LANES:
            for key in sorted(by_lane.get(lane, [])):
                m = dict(metrics[key])
                m["epic_key"] = epic
                display.append(m)
        for lane in AGGREGATE_LANES:
            keys = sorted(by_lane.get(lane, []))
            if not keys:
                continue
            if len(keys) == 1:
                m = dict(metrics[keys[0]])
                m["epic_key"] = epic
                display.append(m)
            else:
                display.append(
                    {
                        "task_key": "Multiple",
                        "task_keys": keys,
                        "epic_key": epic,
                        "lane": lane,
                        "estimate_hours": sum(metrics[k]["estimate_hours"] for k in keys),
                        "estimate_source": "aggregated",
                        "logged_hours": sum(metrics[k]["logged_hours"] for k in keys),
                        "others_logged_hours": sum(metrics[k].get("others_logged_hours", 0) for k in keys),
                        "anomalies": [],
                        "summary": f"Aggregated {lane}",
                    }
                )

    for key, m in sorted(metrics.items()):
        if m.get("role") != "comparison":
            continue
        display.append(dict(m))

    small_max = float(contract.get("corpus_tcd_small_max_hours", 16))
    state = new_state_skeleton(args.jira_user, contract)
    rows = []
    included: set[str] = set()
    for d in display:
        ek = str(d.get("epic_key") or "")
        cat = epic_classifications.get(ek, {}).get("category_id", "other")
        tk = d.get("task_key") or d.get("key")
        est = float(d.get("estimate_hours") or 8)
        log = float(d.get("logged_hours") or 0)
        lane = d.get("lane") or "tcd"
        role = str(d.get("role") or "corpus")
        if tk == "Multiple":
            included.update(d.get("task_keys") or [])
        else:
            included.add(str(tk))
        rows.append(
            {
                "issue": tk,
                "epic_link": ek,
                "lane": lane,
                "role": role,
                "category_id": cat,
                "size_id": tcd_size_band(est, small_max),
                "draft_estimate_hours": est,
                "estimate_source": d.get("estimate_source") or "unknown",
                "hours_logged": log,
                "others_logged_hours": float(d.get("others_logged_hours") or 0),
                "summary": d.get("summary") or "",
                "anomalies": d.get("anomalies") or [],
            }
        )

    state["rows"] = rows
    state["included_issue_keys"] = sorted(included)
    state["corpus_epic_keys"] = gated
    state["epic_classifications"] = [epic_classifications[ek] for ek in gated]
    state["attestation_by_epic"] = {
        ek: {"ai_assisted": True, "reason": "operator_excluded_initial_assessment"}
        for ek in sorted(exclude_epics)
    }
    state["epic_meta"] = epic_meta
    apply_epic_categories_to_state(state, contract)
    state["report_meta"] = {
        "tests_scanned": args.tests_count,
        "last_mode": "initial_assessment",
        "last_sync_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "epics_discovered": len(epic_tasks),
        "epics_gated": len(gated),
        "epics_dropped_zero_logged": len(epic_tasks) - len(gated),
        "epics_excluded_operator": sorted(exclude_epics),
        "qa_tasks_in_scope": len(metrics),
    }

    path = save_state(state)
    print(json.dumps(state["report_meta"], indent=2))
    print(f"rows={len(rows)} epics={len(gated)} -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
