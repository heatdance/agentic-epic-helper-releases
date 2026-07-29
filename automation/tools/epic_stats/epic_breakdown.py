#!/usr/bin/env python3
"""Epic breakdown table builders for CRTQA stats v5 reports."""

from __future__ import annotations

from typing import Any

from epic_stats.apply_categories import resolve_classification
from epic_stats.categories import (
    TOP_CATEGORY_ORDER,
    category_justification,
    category_size_label,
    epic_size_from_rows,
)
from epic_stats.gather import QA_LANES
from epic_stats.ingest import load_contract, rows_for_report

NOTE_SUMMARY_MAX = 120
CAT_ORDER = {c: i for i, c in enumerate(TOP_CATEGORY_ORDER)}


def _truncate(text: str, limit: int = NOTE_SUMMARY_MAX) -> str:
    t = " ".join(str(text or "").split())
    if len(t) <= limit:
        return t
    return t[: limit - 1].rstrip() + "…"


def _pipe_escape(text: str) -> str:
    return str(text or "").replace("|", "\\|").replace("\n", " ")


def _epic_summary(state: dict[str, Any], epic_key: str) -> str:
    meta = (state.get("epic_meta") or {}).get(epic_key) or {}
    return str(meta.get("summary") or epic_key)


def _classification_for_epic(state: dict[str, Any], epic_key: str) -> dict[str, Any]:
    return resolve_classification(epic_key, state)


def _aggregate_role_rows(
    state_rows: list[dict[str, Any]], epic_key: str, role: str
) -> dict[str, Any] | None:
    rows = [
        r
        for r in state_rows
        if str(r.get("epic_link") or "").upper() == epic_key.upper()
        and r.get("role") == role
        and r.get("lane") in QA_LANES
    ]
    if not rows:
        return None
    draft = sum(float(r.get("draft_estimate_hours") or 0) for r in rows)
    logged = sum(float(r.get("hours_logged") or 0) for r in rows)
    size_rows = [
        {"estimate": float(r.get("draft_estimate_hours") or 0), "draft_estimate_hours": float(r.get("draft_estimate_hours") or 0)}
        for r in rows
    ]
    return {
        "draft": round(draft, 2),
        "logged": round(logged, 2),
        "size_id": epic_size_from_rows(size_rows),
    }


def _sort_key(row: dict[str, Any]) -> tuple:
    cat = row.get("category_id") or "other"
    sz = row.get("size_id") or "small_tcd"
    return (CAT_ORDER.get(cat, 99), 0 if sz == "small_tcd" else 1, row.get("epic_key") or "")


def build_corpus_breakdown_rows(state: dict[str, Any]) -> list[dict[str, Any]]:
    state_rows = state.get("rows") or []
    out: list[dict[str, Any]] = []
    for epic_key in sorted(state.get("corpus_epic_keys") or []):
        agg = _aggregate_role_rows(state_rows, epic_key, "corpus")
        if not agg:
            continue
        cls = _classification_for_epic(state, epic_key)
        note1 = _truncate(_epic_summary(state, epic_key))
        note2 = category_justification(cls)
        out.append(
            {
                "epic_key": epic_key,
                "category_id": cls["category_id"],
                "size_id": agg["size_id"],
                "category_label": category_size_label(cls["category_id"], agg["size_id"]),
                "draft": agg["draft"],
                "logged": agg["logged"],
                "note": f"{note1}<br>{note2}",
                "attested_only": False,
            }
        )
    out.sort(key=_sort_key)
    return out


def build_ai_breakdown_rows(state: dict[str, Any]) -> list[dict[str, Any]]:
    state_rows = state.get("rows") or []
    attested = {
        str(k).upper()
        for k, v in (state.get("attestation_by_epic") or {}).items()
        if v.get("ai_assisted")
    }
    comparison_epics = {
        str(r.get("epic_link") or "").upper()
        for r in state_rows
        if r.get("role") == "comparison" and r.get("epic_link")
    }
    epic_keys = sorted(attested | comparison_epics)
    out: list[dict[str, Any]] = []
    for epic_key in epic_keys:
        agg = _aggregate_role_rows(state_rows, epic_key, "comparison")
        cls = _classification_for_epic(state, epic_key)
        note1 = _truncate(_epic_summary(state, epic_key))
        note2 = category_justification(cls)
        if epic_key in attested and not agg:
            note2 = (
                f"AI-assisted; excluded from corpus at initial assessment. {note2}"
            )
            out.append(
                {
                    "epic_key": epic_key,
                    "category_id": cls["category_id"],
                    "size_id": "small_tcd",
                    "category_label": category_size_label(cls["category_id"], "small_tcd"),
                    "draft": None,
                    "logged": None,
                    "note": f"{note1}<br>{note2}",
                    "attested_only": True,
                }
            )
            continue
        if not agg:
            continue
        out.append(
            {
                "epic_key": epic_key,
                "category_id": cls["category_id"],
                "size_id": agg["size_id"],
                "category_label": category_size_label(cls["category_id"], agg["size_id"]),
                "draft": agg["draft"],
                "logged": agg["logged"],
                "note": f"{note1}<br>{note2}",
                "attested_only": False,
            }
        )
    out.sort(key=_sort_key)
    return out


def jira_browse_url(epic_key: str) -> str:
    contract = load_contract()
    tmpl = contract.get("jira_browse_url_template") or "https://jira.in.devexperts.com/browse/{issue_key}"
    return tmpl.format(issue_key=epic_key)


def render_breakdown_section(title: str, rows: list[dict[str, Any]], *, empty_message: str) -> list[str]:
    lines = [f"## {title}", ""]
    if not rows:
        lines.append(empty_message)
        lines.append("")
        return lines
    lines.extend(
        [
            "| Epic | Category | Draft (h) | Logged (h) | Note |",
            "|------|----------|----------:|-----------:|------|",
        ]
    )
    for r in rows:
        ek = r["epic_key"]
        link = f"[{ek}]({jira_browse_url(ek)})"
        draft = "—" if r.get("draft") is None else f"{float(r['draft']):.2f}"
        logged = "—" if r.get("logged") is None else f"{float(r['logged']):.2f}"
        note = _pipe_escape(r.get("note") or "")
        lines.append(
            f"| {link} | {r.get('category_label', 'Other+S')} | {draft} | {logged} | {note} |"
        )
    lines.append("")
    return lines


def render_epic_breakdown_sections(state: dict[str, Any]) -> list[str]:
    corpus_rows = build_corpus_breakdown_rows(state)
    ai_rows = build_ai_breakdown_rows(state)
    lines: list[str] = []
    lines.extend(
        render_breakdown_section(
            "Epic breakdown",
            corpus_rows,
            empty_message="No corpus epics in state.",
        )
    )
    ai_empty = "No AI-assisted epics."
    if not ai_rows:
        inv = rows_for_report(state)
        if any(r.get("role") == "comparison" for r in inv):
            ai_empty = "No AI-assisted epics with breakdown rows."
    lines.extend(
        render_breakdown_section(
            "AI Epic breakdown",
            ai_rows,
            empty_message=ai_empty,
        )
    )
    return lines
