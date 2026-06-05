#!/usr/bin/env python3
"""State I/O and row enrichment for CRTQA stats v5."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from crtqa_stats.categories import classify_epic, load_categories, tcd_size_band
from crtqa_stats.gather import (
    AGGREGATE_LANES,
    QA_LANES,
    SINGLE_TASK_LANES,
    classify_task_summary,
    estimate_from_fields,
    issue_fields,
    logged_hours_for_lane,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
CONTRACT_PATH = REPO_ROOT / "docs" / "crtqa-stats-contract.json"
SCHEMA_VERSION = 5


def load_contract(path: Path | None = None) -> dict[str, Any]:
    p = path or CONTRACT_PATH
    data = json.loads(p.read_text(encoding="utf-8"))
    if int(data.get("schema_version", 0)) != SCHEMA_VERSION:
        raise ValueError(f"Expected contract schema_version {SCHEMA_VERSION}")
    return data


def _stats_root(contract: dict[str, Any]) -> Path:
    rel = (contract.get("paths") or {}).get("stats_root", "stats/crtqa-stats")
    return REPO_ROOT / rel


def state_path_for_user(jira_user: str, contract: dict[str, Any] | None = None) -> Path:
    c = contract or load_contract()
    tmpl = (c.get("paths") or {}).get(
        "state_template", "stats/crtqa-stats/state/last-sync-{jira_user}.json"
    )
    return REPO_ROOT / tmpl.format(jira_user=jira_user)


def latest_path_for_user(jira_user: str, contract: dict[str, Any] | None = None) -> Path:
    c = contract or load_contract()
    tmpl = (c.get("paths") or {}).get(
        "latest_template", "stats/crtqa-stats/latest-{jira_user}.md"
    )
    return REPO_ROOT / tmpl.format(jira_user=jira_user)


def latest_team_path(contract: dict[str, Any] | None = None) -> Path:
    c = contract or load_contract()
    rel = (c.get("paths") or {}).get("latest_team", "stats/crtqa-stats/latest-team.md")
    return REPO_ROOT / rel


def team_users_from_contract(contract: dict[str, Any] | None = None) -> list[str]:
    c = contract or load_contract()
    defaults = ["mshpak", "amukanova", "mtavadze", "arodzevich", "mshram"]
    raw = c.get("team_users") or defaults
    return sorted({str(u).strip() for u in raw if str(u).strip()})


def discover_team_users_with_state(
    contract: dict[str, Any] | None = None,
    *,
    restrict_to_roster: bool = True,
) -> list[str]:
    """Users with state files — roster first, then any last-sync-*.json on disk."""
    c = contract or load_contract()
    roster = set(team_users_from_contract(c))
    found: set[str] = set()
    for user in roster:
        if state_exists(user, c):
            found.add(user)
    state_dir = _stats_root(c) / "state"
    if state_dir.is_dir():
        for path in state_dir.glob("last-sync-*.json"):
            user = path.stem.replace("last-sync-", "", 1)
            if not restrict_to_roster or user in roster:
                found.add(user)
    return sorted(found)


def baseline_readiness_for_user(jira_user: str, contract: dict[str, Any] | None = None) -> dict[str, Any]:
    """Checklist row for incremental Phase 1 staleness gate."""
    c = contract or load_contract()
    latest = latest_path_for_user(jira_user, c)
    state_path = state_path_for_user(jira_user, c)
    row: dict[str, Any] = {
        "jira_user": jira_user,
        "latest_path": str(latest.relative_to(REPO_ROOT)).replace("\\", "/"),
        "state_path": str(state_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "latest_exists": latest.is_file(),
        "state_exists": state_path.is_file(),
        "latest_generated": None,
        "state_last_sync_utc": None,
    }
    if latest.is_file():
        for line in latest.read_text(encoding="utf-8").splitlines():
            if "**Generated:**" in line:
                row["latest_generated"] = line.split("**Generated:**", 1)[1].strip()
                break
    if state_path.is_file():
        data = json.loads(state_path.read_text(encoding="utf-8"))
        meta = data.get("report_meta") or {}
        row["state_last_sync_utc"] = meta.get("last_sync_utc")
    row["ready"] = bool(row["latest_exists"] and row["state_exists"])
    return row


def raw_run_path(jira_user: str, contract: dict[str, Any] | None = None) -> Path:
    c = contract or load_contract()
    tmpl = (c.get("paths") or {}).get(
        "raw_template", "stats/crtqa-stats/raw/{jira_user}/run-{utc}.jsonl"
    )
    utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return REPO_ROOT / tmpl.format(jira_user=jira_user, utc=utc)


def state_exists(jira_user: str, contract: dict[str, Any] | None = None) -> bool:
    return state_path_for_user(jira_user, contract).is_file()


def load_state(jira_user: str, contract: dict[str, Any] | None = None) -> dict[str, Any]:
    path = state_path_for_user(jira_user, contract)
    if not path.is_file():
        raise FileNotFoundError(
            f"No state at {path}; run initial_assessment for {jira_user} first."
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    if int(data.get("schema_version", 0)) != SCHEMA_VERSION:
        raise ValueError(
            f"State schema_version {data.get('schema_version')} incompatible; "
            "delete state and run initial_assessment."
        )
    return data


def save_state(state: dict[str, Any], contract: dict[str, Any] | None = None) -> Path:
    user = str(state["jira_user"])
    path = state_path_for_user(user, contract)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def new_state_skeleton(jira_user: str, contract: dict[str, Any] | None = None) -> dict[str, Any]:
    c = contract or load_contract()
    return {
        "schema_version": SCHEMA_VERSION,
        "jira_user": jira_user,
        "included_issue_keys": [],
        "rows": [],
        "corpus_epic_keys": [],
        "epic_classifications": [],
        "report_meta": {
            "tests_scanned": 0,
            "last_mode": None,
            "last_sync_utc": None,
        },
        "attestation_by_epic": {},
        "contract_schema_version": c.get("schema_version"),
    }


def enrich_row_from_issue(
    issue: dict[str, Any],
    *,
    jira_user: str,
    epic_link: str,
    role: str,
    contract: dict[str, Any] | None = None,
    category_id: str | None = None,
) -> dict[str, Any]:
    """Build a v5 state row from a Jira issue payload."""
    c = contract or load_contract()
    fields = issue_fields(issue)
    key = str(issue.get("key") or fields.get("key") or "")
    summary = str(fields.get("summary") or "")
    it_obj = fields.get("issuetype") or issue.get("issue_type") or {}
    issuetype = it_obj.get("name") if isinstance(it_obj, dict) else str(it_obj or "")
    artifact_rules = c.get("artifact_rules") or []
    exclude_rules = c.get("exclude_from_qa") or []
    lane = classify_task_summary(
        summary, issuetype, artifact_rules, exclude_rules
    )
    if lane == "excluded":
        raise ValueError(f"Issue {key} is excluded from QA scope")
    default_h = float(c.get("default_estimate_hours", 8))
    est, est_src, est_anoms = estimate_from_fields(fields, default_h)
    wl = fields.get("worklog")
    logged, others, scope, log_anoms = logged_hours_for_lane(
        lane, artifact_rules, wl, fields.get("timetracking"), jira_user
    )
    small_max = float(c.get("corpus_tcd_small_max_hours", 16))
    size_id = tcd_size_band(est, small_max) if lane == "tcd" else None
    cat = category_id
    if cat is None:
        epic_cls = classify_epic(epic_link)
        cat = epic_cls["category_id"]
    status = fields.get("status") or {}
    status_name = status.get("name") if isinstance(status, dict) else str(status or "")
    return {
        "issue": key,
        "epic_link": epic_link,
        "lane": lane,
        "role": role,
        "category_id": cat,
        "size_id": size_id,
        "draft_estimate_hours": est,
        "estimate_source": est_src,
        "hours_logged": logged,
        "others_logged_hours": others,
        "logged_scope": scope,
        "summary": summary,
        "status": status_name,
        "anomalies": sorted(set(est_anoms + log_anoms)),
    }


def epic_user_logged_hours(rows: list[dict[str, Any]], epic_key: str) -> float:
    total = 0.0
    for r in rows:
        if str(r.get("epic_link")) != epic_key:
            continue
        if r.get("lane") not in QA_LANES:
            continue
        total += float(r.get("hours_logged") or 0)
    return round(total, 2)


def apply_corpus_gate(
    epic_keys: list[str],
    task_rows: list[dict[str, Any]],
    *,
    require_user_logged: bool = True,
) -> list[str]:
    """Return epic keys that pass corpus gate (user QA logged > 0)."""
    if not require_user_logged:
        return list(epic_keys)
    out: list[str] = []
    for ek in epic_keys:
        if epic_user_logged_hours(task_rows, ek) > 0:
            out.append(ek)
    return sorted(out)


def rows_for_report(state: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize state rows for render_report inventory."""
    inv: list[dict[str, Any]] = []
    for r in state.get("rows") or []:
        if r.get("lane") not in QA_LANES:
            continue
        est = float(r.get("draft_estimate_hours") or r.get("estimate_hours") or 0)
        log = float(r.get("hours_logged") or 0)
        cat = r.get("category_id") or "other"
        sz = r.get("size_id")
        if not sz:
            sz = tcd_size_band(est, 16.0)
        inv.append(
            {
                "issue": r.get("issue"),
                "epic": str(r.get("epic_link") or ""),
                "role": r.get("role") or "corpus",
                "category_id": cat,
                "size_id": sz,
                "estimate": est,
                "logged": log,
            }
        )
    return inv


def corpus_display_rows(state: dict[str, Any]) -> list[dict[str, Any]]:
    """Corpus-role rows only (for medians)."""
    return [r for r in rows_for_report(state) if r.get("role") == "corpus"]


def incremental_missing_state_message(jira_user: str) -> str:
    return (
        f"No state file for `{jira_user}`. Run `/crtqa-stats` with "
        f"`mode=initial_assessment` first."
    )
