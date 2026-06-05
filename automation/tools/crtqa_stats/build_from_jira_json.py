#!/usr/bin/env python3
"""Build v5 initial_assessment state from merged Jira JSON (MCP fetch artifacts)."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[3]
TOOLS = REPO / "automation" / "tools"
sys.path.insert(0, str(TOOLS))

from crtqa_stats.categories import classify_epic  # noqa: E402
from crtqa_stats.gather import (  # noqa: E402
    AGGREGATE_LANES,
    QA_LANES,
    SINGLE_TASK_LANES,
    classify_task_summary,
    extract_epics_from_issue,
    issue_fields,
)
from crtqa_stats.ingest import (  # noqa: E402
    apply_corpus_gate,
    enrich_row_from_issue,
    load_contract,
    new_state_skeleton,
    raw_run_path,
    save_state,
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _merge_test_pages(paths: list[Path]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    seen: set[str] = set()
    for p in paths:
        data = _load_json(p)
        payload = data.get("result")
        if isinstance(payload, str):
            data = json.loads(payload)
        elif payload is not None:
            data = payload
        for issue in data.get("issues") or []:
            k = issue.get("key")
            if k and k not in seen:
                seen.add(k)
                issues.append(issue)
    return issues


def _epics_from_tests(tests: list[dict[str, Any]]) -> dict[str, set[str]]:
    epic_to_tests: dict[str, set[str]] = defaultdict(set)
    for t in tests:
        epics, _, _ = extract_epics_from_issue(t)
        for ek in epics:
            epic_to_tests[ek].add(str(t.get("key") or ""))
    return epic_to_tests


def _display_rows(
    epic_tasks: dict[str, list[dict[str, Any]]],
    metrics: dict[str, dict[str, Any]],
    gated_epics: list[str],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for epic in gated_epics:
        by_lane: dict[str, list[str]] = defaultdict(list)
        for t in epic_tasks.get(epic, []):
            lane = t.get("lane") or "other"
            key = t.get("key")
            if lane in QA_LANES and key:
                by_lane[lane].append(key)
        for lane in SINGLE_TASK_LANES:
            for key in sorted(by_lane.get(lane, [])):
                if key in metrics:
                    row = dict(metrics[key])
                    row["epic_key"] = epic
                    out.append(row)
        for lane in AGGREGATE_LANES:
            keys = sorted(by_lane.get(lane, []))
            if not keys:
                continue
            if len(keys) == 1 and keys[0] in metrics:
                row = dict(metrics[keys[0]])
                row["epic_key"] = epic
                out.append(row)
            else:
                est_sum = 0.0
                log_sum = 0.0
                for k in keys:
                    m = metrics.get(k, {})
                    est_sum += float(m.get("estimate_hours") or m.get("draft_estimate_hours") or 0)
                    log_sum += float(m.get("logged_hours") or m.get("hours_logged") or 0)
                out.append(
                    {
                        "epic_key": epic,
                        "task_key": "Multiple",
                        "task_keys": keys,
                        "lane": lane,
                        "estimate_hours": est_sum,
                        "estimate_source": "aggregated",
                        "logged_hours": log_sum,
                        "anomalies": [],
                    }
                )
    return out


def _metrics_to_state_rows(
    display: list[dict[str, Any]],
    epic_classifications: dict[str, dict[str, Any]],
    jira_user: str,
    contract: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for d in display:
        ek = str(d.get("epic_key") or "")
        cat = epic_classifications.get(ek, {}).get("category_id", "other")
        task_key = d.get("task_key") or "Multiple"
        est = float(d.get("estimate_hours") or d.get("draft_estimate_hours") or 8)
        log = float(d.get("logged_hours") or d.get("hours_logged") or 0)
        lane = d.get("lane") or "tcd"
        from crtqa_stats.categories import tcd_size_band

        rows.append(
            {
                "issue": task_key,
                "epic_link": ek,
                "lane": lane,
                "role": "corpus",
                "category_id": cat,
                "size_id": tcd_size_band(est, float(contract.get("corpus_tcd_small_max_hours", 16))),
                "draft_estimate_hours": est,
                "estimate_source": d.get("estimate_source") or "unknown",
                "hours_logged": log,
                "others_logged_hours": float(d.get("others_logged_hours") or 0),
                "summary": d.get("summary") or "",
                "anomalies": d.get("anomalies") or [],
            }
        )
    return rows


def build_state(
    jira_user: str,
    test_pages: list[Path],
    epic_tasks_path: Path,
    metrics_path: Path,
    epic_meta_path: Path | None = None,
) -> dict[str, Any]:
    contract = load_contract()
    tests = _merge_test_pages(test_pages)
    epic_to_tests = _epics_from_tests(tests)
    epic_tasks_raw = _load_json(epic_tasks_path)
    metrics_raw = _load_json(metrics_path)

    epic_meta: dict[str, Any] = {}
    if epic_meta_path and epic_meta_path.is_file():
        epic_meta = _load_json(epic_meta_path)

    epic_classifications: dict[str, dict[str, Any]] = {}
    for ek in sorted(epic_to_tests.keys()):
        epic_classifications[ek] = classify_epic(ek, epic_meta.get(ek))

    # Build flat task rows with user logged for gate
    all_task_rows: list[dict[str, Any]] = []
    for epic, tasks in epic_tasks_raw.items():
        for t in tasks:
            key = t.get("key")
            if not key or key not in metrics_raw:
                continue
            m = metrics_raw[key]
            all_task_rows.append(
                {
                    "issue": key,
                    "epic_link": epic,
                    "lane": t.get("lane"),
                    "hours_logged": m.get("hours_logged") or m.get("logged_hours") or 0,
                }
            )

    gated = apply_corpus_gate(
        sorted(epic_to_tests.keys()),
        all_task_rows,
        require_user_logged=bool(contract.get("corpus_require_user_logged", True)),
    )

    display = _display_rows(epic_tasks_raw, metrics_raw, gated)
    state = new_state_skeleton(jira_user, contract)
    state["rows"] = _metrics_to_state_rows(display, epic_classifications, jira_user, contract)
    state["included_issue_keys"] = sorted(
        {r["issue"] for r in state["rows"] if r["issue"] != "Multiple"}
        | {k for r in state["rows"] if r["issue"] == "Multiple" for k in (metrics_raw.get(r["issue"]) or [])}
    )
    # Fix included keys from display multiples
    keys: set[str] = set()
    for d in display:
        if d.get("task_key") == "Multiple":
            keys.update(d.get("task_keys") or [])
        elif d.get("task_key"):
            keys.add(str(d["task_key"]))
    state["included_issue_keys"] = sorted(keys)
    state["corpus_epic_keys"] = gated
    state["epic_classifications"] = [epic_classifications[ek] for ek in gated]
    state["report_meta"] = {
        "tests_scanned": len(tests),
        "last_mode": "initial_assessment",
        "last_sync_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "epics_discovered": len(epic_to_tests),
        "epics_gated": len(gated),
        "epics_dropped_zero_logged": len(epic_to_tests) - len(gated),
    }
    return state


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--jira-user", required=True)
    p.add_argument("--test-pages", nargs="+", type=Path, required=True)
    p.add_argument("--epic-tasks", type=Path, required=True)
    p.add_argument("--metrics", type=Path, required=True)
    p.add_argument("--epic-meta", type=Path, default=None)
    args = p.parse_args()
    state = build_state(
        args.jira_user,
        args.test_pages,
        args.epic_tasks,
        args.metrics,
        args.epic_meta,
    )
    path = save_state(state)
    print(json.dumps(state["report_meta"], indent=2))
    print(f"rows={len(state['rows'])} epics={len(state['corpus_epic_keys'])} -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
