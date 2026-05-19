#!/usr/bin/env python3
"""
Recompute corpus_cells, enrich rows, and render stats/crtqa-stats/latest.md (schema v4).

Examples:
  python automation/tools/crtqa_stats_rollup.py
  python automation/tools/crtqa_stats_rollup.py --append-longitudinal
  python automation/tools/crtqa_stats_rollup.py --allow-v3-migrate
  python automation/tools/crtqa_stats_rollup.py --repair-draft-from-estimate
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATE = REPO_ROOT / "stats" / "crtqa-stats" / "state" / "last-sync.json"
DEFAULT_LATEST = REPO_ROOT / "stats" / "crtqa-stats" / "latest.md"
DEFAULT_LONGITUDINAL = REPO_ROOT / "stats" / "crtqa-stats" / "state" / "longitudinal.json"
DEFAULT_CATEGORIES = REPO_ROOT / "stats" / "crtqa-stats" / "temp" / "categories.json"
REPRESENTABLE_MIN = 4
HOURS_PER_SP = 8
SCHEMA_V4 = 4

SIZE_LABELS: dict[str, str] = {
    "sp_lt_1": "< 1 SP",
    "sp_1_2": "1–2 SP",
    "sp_3_plus": "3+ SP",
    "sp_unknown": "SP unknown",
}

CATEGORY_LABELS: dict[str, str] = {
    "fe": "Frontend / UI",
    "be": "Backend / console",
    "api": "API / integration",
    "cross_cutting": "Cross-cutting / process",
    "other": "Other / unknown",
}

ATTRIBUTION_LABELS: dict[str, str] = {
    "none": "baseline (corpus)",
    "insufficient": "insufficient data",
    "estimate_only": "vs draft estimate only",
    "corpus_benchmark": "vs manual baseline",
    "corpus_and_estimate": "vs draft and baseline",
}

PROFILE_CLAIMS: dict[str, str] = {
    "task_detail": "Per-task draft vs logged only; corpus benchmark not yet representable.",
    "directional": "Directional corpus compares where n=1–3; per-task draft deltas always shown.",
    "benchmark": "Corpus median benchmarks (n≥4) available for at least one cell.",
}


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    return float(statistics.median(values))


def _float_or_none(v: Any) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _hours(row: dict[str, Any]) -> float | None:
    return _float_or_none(row.get("hours_logged"))


def _draft_hours(row: dict[str, Any]) -> float | None:
    d = _float_or_none(row.get("draft_estimate_hours"))
    if d is not None:
        return d
    e = _float_or_none(row.get("estimate_hours"))
    return e


def size_band_from_draft(draft: float | None) -> str:
    if draft is None:
        return "sp_unknown"
    if draft < HOURS_PER_SP:
        return "sp_lt_1"
    if draft <= 16.0:
        return "sp_1_2"
    return "sp_3_plus"


def devex_sp_from_draft(draft: float | None) -> float | None:
    if draft is None:
        return None
    return round(draft / HOURS_PER_SP, 2)


def _cell_key(category_id: str, size_band_id: str) -> tuple[str, str]:
    return category_id, size_band_id


def _build_pool(
    rows: list[dict[str, Any]], role: str
) -> dict[tuple[str, str], list[float]]:
    pool: dict[tuple[str, str], list[float]] = {}
    for row in rows:
        if row.get("role") != role:
            continue
        h = _hours(row)
        if h is None:
            continue
        cat = str(row.get("category_id") or "other")
        band = str(row.get("size_band_id") or "sp_unknown")
        pool.setdefault(_cell_key(cat, band), []).append(h)
    return pool


def _category_only_pool(
    cell_pool: dict[tuple[str, str], list[float]]
) -> dict[str, list[float]]:
    out: dict[str, list[float]] = {}
    for (cat, _band), vals in cell_pool.items():
        out.setdefault(cat, []).extend(vals)
    return out


def _make_cell(
    category_id: str,
    size_band_id: str,
    corpus_vals: list[float],
    *,
    borrowed_from: str | None = None,
) -> dict[str, Any]:
    n = len(corpus_vals)
    cell: dict[str, Any] = {
        "category_id": category_id,
        "size_band_id": size_band_id,
        "corpus_n": n,
        "median_hours_logged": _median(corpus_vals),
        "representable": n >= REPRESENTABLE_MIN,
    }
    if borrowed_from:
        cell["borrowed_from"] = borrowed_from
    return cell


def compute_corpus_cells(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    corpus_pool = _build_pool(rows, "corpus")
    cat_only = _category_only_pool(corpus_pool)
    cells: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for (cat, band), vals in sorted(corpus_pool.items()):
        seen.add((cat, band))
        if len(vals) >= REPRESENTABLE_MIN:
            cells.append(_make_cell(cat, band, vals))
            continue
        parent = cat_only.get(cat, [])
        if len(parent) >= REPRESENTABLE_MIN:
            cells.append(
                _make_cell(cat, band, parent, borrowed_from="category_only")
            )
        else:
            cells.append(_make_cell(cat, band, vals))

    for cat, vals in sorted(cat_only.items()):
        if any(c == cat for c, _ in seen):
            continue
        cells.append(_make_cell(cat, "sp_unknown", vals))

    return cells


def _cell_lookup(cells: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        _cell_key(str(c["category_id"]), str(c["size_band_id"])): c for c in cells
    }


def _corpus_median_for_row(
    row: dict[str, Any], cells: list[dict[str, Any]]
) -> tuple[float | None, bool]:
    cat = str(row.get("category_id") or "other")
    band = str(row.get("size_band_id") or "sp_unknown")
    cell = _cell_lookup(cells).get((cat, band))
    if not cell:
        return None, False
    if cell.get("representable"):
        return _float_or_none(cell.get("median_hours_logged")), True
    if cell.get("borrowed_from") == "category_only":
        cat_only = _category_only_pool(_build_pool(
            [{"role": "corpus", "category_id": cat, "size_band_id": band,
              "hours_logged": cell.get("median_hours_logged")}],
            "corpus",
        ))
        return _float_or_none(cell.get("median_hours_logged")), False
    return _float_or_none(cell.get("median_hours_logged")), False


def _corpus_median_for_row_v2(
    row: dict[str, Any],
    cells: list[dict[str, Any]],
    corpus_rows: list[dict[str, Any]],
) -> tuple[float | None, bool]:
    cat = str(row.get("category_id") or "other")
    band = str(row.get("size_band_id") or "sp_unknown")
    cell = _cell_lookup(cells).get((cat, band))
    if cell and cell.get("representable"):
        return _float_or_none(cell.get("median_hours_logged")), True
    if cell and cell.get("borrowed_from") == "category_only":
        cat_vals = [
            _hours(r)
            for r in corpus_rows
            if r.get("category_id") == cat and _hours(r) is not None
        ]
        if len(cat_vals) >= REPRESENTABLE_MIN:
            return _median(cat_vals), False
    pool = _build_pool(corpus_rows, "corpus").get((cat, band), [])
    if len(pool) >= REPRESENTABLE_MIN:
        return _median(pool), True
    return (_median(pool) if pool else None), False


def apply_draft_sizing(rows: list[dict[str, Any]]) -> None:
    """Set draft_estimate_hours, devex_sp, size_band_id before corpus cell grouping."""
    for row in rows:
        draft = _draft_hours(row)
        if draft is not None:
            row["draft_estimate_hours"] = draft
            row["estimate_hours"] = draft
        row["devex_sp"] = devex_sp_from_draft(draft)
        row["size_band_id"] = size_band_from_draft(draft)


def enrich_rows(
    rows: list[dict[str, Any]],
    cells: list[dict[str, Any]],
) -> None:
    corpus_rows = [r for r in rows if r.get("role") == "corpus"]
    for row in rows:
        draft = _draft_hours(row)

        logged = _hours(row)
        if draft is not None and logged is not None:
            row["hours_vs_draft"] = round(draft - logged, 2)
        else:
            row["hours_vs_draft"] = None

        role = row.get("role")
        if role == "corpus":
            row["savings_hours_estimate"] = None
            row["savings_hours_corpus"] = None
            row["savings_attribution"] = "none"
            continue

        if role != "comparison":
            row["savings_attribution"] = "insufficient"
            continue

        if draft is None or logged is None:
            row["savings_hours_estimate"] = None
            row["savings_hours_corpus"] = None
            row["savings_attribution"] = "insufficient"
            continue

        est_savings = round(draft - logged, 2)
        row["savings_hours_estimate"] = est_savings

        c_med, representable = _corpus_median_for_row_v2(row, cells, corpus_rows)
        if c_med is not None:
            row["savings_hours_corpus"] = round(c_med - logged, 2)
        else:
            row["savings_hours_corpus"] = None

        if representable and c_med is not None:
            if est_savings > 0 and (c_med - logged) > 0:
                row["savings_attribution"] = "corpus_and_estimate"
            else:
                row["savings_attribution"] = "corpus_benchmark"
        elif est_savings != 0 or draft is not None:
            row["savings_attribution"] = "estimate_only"
        else:
            row["savings_attribution"] = "insufficient"


def compute_report_profile(
    rows: list[dict[str, Any]], cells: list[dict[str, Any]]
) -> tuple[str, dict[str, Any]]:
    total = len(rows)
    corpus_n = sum(1 for r in rows if r.get("role") == "corpus")
    comparison_n = sum(1 for r in rows if r.get("role") == "comparison")
    representable_cells = sum(1 for c in cells if c.get("representable"))

    cat_corpus: dict[str, int] = {}
    for r in rows:
        if r.get("role") != "corpus":
            continue
        cat = str(r.get("category_id") or "other")
        cat_corpus[cat] = cat_corpus.get(cat, 0) + 1

    has_directional = any(1 <= n < REPRESENTABLE_MIN for n in cat_corpus.values())
    has_benchmark = representable_cells > 0

    if total < REPRESENTABLE_MIN or not has_benchmark:
        profile = "task_detail"
        reason = (
            f"total_tasks={total} < {REPRESENTABLE_MIN} or no representable corpus cells"
        )
    elif has_directional and has_benchmark:
        profile = "benchmark"
        reason = "representable cells exist; some categories still directional"
    elif has_directional:
        profile = "directional"
        reason = "corpus present but no cell with n≥4 yet"
    else:
        profile = "benchmark"
        reason = "at least one representable corpus cell"

    meta = {
        "total_tasks": total,
        "corpus_n": corpus_n,
        "comparison_n": comparison_n,
        "representable_cells": representable_cells,
        "profile_reason": reason,
    }
    return profile, meta


def _saved_pct(corpus_median: float | None, comparison_median: float | None) -> str:
    if corpus_median is None or comparison_median is None or corpus_median == 0:
        return "—"
    pct = (corpus_median - comparison_median) / corpus_median * 100.0
    return f"{pct:.1f}%"


def _evidence(corpus_cell: dict[str, Any], comparison_n: int) -> str:
    if corpus_cell.get("borrowed_from"):
        base = "directional"
    elif corpus_cell.get("representable"):
        base = "representable"
    elif (corpus_cell.get("corpus_n") or 0) > 0:
        base = "directional"
    else:
        base = "pending"
    if base == "representable" and comparison_n < 3:
        return "comparison_weak"
    return base


def _fmt_hours(v: float | None) -> str:
    if v is None:
        return "—"
    return f"{v:.2f}"


def _pending_note(corpus_n: int) -> str:
    need = max(0, REPRESENTABLE_MIN - corpus_n)
    if need == 0:
        return "—"
    return f"benchmark pending (need {need} more corpus tasks)"


def _render_task_table(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "## Task-level",
        "",
        "| Issue | Role | Category | Size | Draft h | Devex SP | Logged h | "
        "vs draft | vs corpus | Attribution |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in sorted(rows, key=lambda r: str(r.get("issue") or "")):
        issue = row.get("issue") or "—"
        role = row.get("role") or "—"
        cat = CATEGORY_LABELS.get(str(row.get("category_id")), row.get("category_id"))
        band = SIZE_LABELS.get(str(row.get("size_band_id")), row.get("size_band_id"))
        draft = _fmt_hours(_draft_hours(row))
        dsp = row.get("devex_sp")
        dsp_s = f"{dsp:.2f}" if dsp is not None else "—"
        logged = _fmt_hours(_hours(row))
        vs_d = _fmt_hours(_float_or_none(row.get("hours_vs_draft")))
        vs_c = _fmt_hours(_float_or_none(row.get("savings_hours_corpus")))
        attr = ATTRIBUTION_LABELS.get(
            str(row.get("savings_attribution")), row.get("savings_attribution")
        )
        lines.append(
            f"| {issue} | {role} | {cat} | {band} | {draft} | {dsp_s} | {logged} | "
            f"{vs_d} | {vs_c} | {attr} |"
        )
    lines.append("")
    return lines


def _render_draft_logged_chart(rows: list[dict[str, Any]]) -> list[str]:
    chart_rows = [
        r for r in rows if _draft_hours(r) is not None and _hours(r) is not None
    ]
    if not chart_rows:
        return []
    keys = [str(r.get("issue")) for r in chart_rows]
    drafts = [round(_draft_hours(r) or 0, 2) for r in chart_rows]
    logged = [round(_hours(r) or 0, 2) for r in chart_rows]
    ymax = int(max(max(drafts), max(logged), 1) * 1.2) + 1
    return [
        "## Chart: draft estimate vs logged",
        "",
        "```mermaid",
        "xychart-beta",
        '  title "Draft estimate vs logged (hours)"',
        f"  x-axis {json.dumps(keys)}",
        f'  y-axis "Hours" 0 --> {ymax}',
        f'  bar "Draft estimate" {json.dumps(drafts)}',
        f'  bar "Logged" {json.dumps(logged)}',
        "```",
        "",
    ]


def _render_benchmark_chart(
    rows: list[dict[str, Any]], profile: str
) -> list[str]:
    if profile not in ("benchmark", "directional"):
        return []
    comparison_pool = _build_pool(rows, "comparison")
    cat_only = _category_only_pool(_build_pool(rows, "corpus"))
    cmp_cat_only = _category_only_pool(comparison_pool)
    chart_cats: list[str] = []
    corpus_bars: list[float] = []
    comparison_bars: list[float] = []

    for cat in sorted(set(cat_only) | set(cmp_cat_only)):
        c_vals = cat_only.get(cat, [])
        if len(c_vals) < REPRESENTABLE_MIN:
            continue
        c_med = _median(c_vals)
        m_med = _median(cmp_cat_only.get(cat, []))
        if c_med is None:
            continue
        chart_cats.append(cat)
        corpus_bars.append(round(c_med, 2))
        comparison_bars.append(round(m_med, 2) if m_med is not None else 0.0)

    if not chart_cats:
        return []

    ymax = int(max(max(corpus_bars), max(comparison_bars), 1) * 1.2) + 1
    return [
        "## Chart: corpus vs comparison median by category",
        "",
        "```mermaid",
        "xychart-beta",
        '  title "Median logged hours by category (corpus n≥4)"',
        f"  x-axis {json.dumps(chart_cats)}",
        f'  y-axis "Hours" 0 --> {ymax}',
        f'  bar "Corpus" {json.dumps(corpus_bars)}',
        f'  bar "Comparison" {json.dumps(comparison_bars)}',
        "```",
        "",
    ]


def _render_longitudinal_chart(longitudinal_path: Path) -> list[str]:
    if not longitudinal_path.is_file():
        return []
    try:
        with longitudinal_path.open(encoding="utf-8") as f:
            hist = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(hist, list) or len(hist) < 2:
        return []

    labels: list[str] = []
    hours_vs_draft: list[float] = []
    for i, entry in enumerate(hist):
        if not isinstance(entry, dict):
            continue
        rid = entry.get("run_id") or entry.get("generated_at") or f"run{i + 1}"
        labels.append(str(rid)[-12:] if len(str(rid)) > 12 else str(rid))
        v = entry.get("total_hours_vs_draft_comparison")
        hours_vs_draft.append(round(float(v), 2) if v is not None else 0.0)

    if len(labels) < 2:
        return []

    ymax = int(max(hours_vs_draft + [1]) * 1.2) + 1
    return [
        "## Chart: longitudinal (comparison vs draft)",
        "",
        "```mermaid",
        "xychart-beta",
        '  title "Sum hours under draft (comparison tasks)"',
        f"  x-axis {json.dumps(labels)}",
        f'  y-axis "Hours" 0 --> {ymax}',
        f'  line "vs draft (sum)" {json.dumps(hours_vs_draft)}',
        "```",
        "",
    ]


def render_latest(
    state: dict[str, Any],
    cells: list[dict[str, Any]],
    *,
    longitudinal_path: Path,
) -> str:
    rows = state.get("rows") or []
    if not isinstance(rows, list):
        rows = []

    profile = state.get("report_profile") or "task_detail"
    meta = state.get("report_meta") or {}
    comparison_pool = _build_pool(rows, "comparison")
    cell_by_key = _cell_lookup(cells)
    cat_only = _category_only_pool(_build_pool(rows, "corpus"))
    cmp_cat_only = _category_only_pool(comparison_pool)

    user = state.get("resolved_user") or {}
    username = user.get("username") or user.get("email") or "—"
    mode = state.get("run_mode") or "—"
    generated = state.get("generated_at") or "—"

    lines: list[str] = [
        "# CRTQA stats",
        "",
        f"- Mode: `{mode}`",
        f"- Generated: `{generated}`",
        f"- User: `{username}`",
        f"- Report profile: `{profile}`",
        f"- Counts: corpus `{meta.get('corpus_n', 0)}`, "
        f"comparison `{meta.get('comparison_n', 0)}`",
        f"- Representable cells: `{meta.get('representable_cells', 0)}` "
        f"(corpus n ≥ {REPRESENTABLE_MIN})",
        "",
        PROFILE_CLAIMS.get(profile, ""),
        "",
        "Corpus = manual baseline; comparison = AI-assisted (agentic epic helper). "
        "Association, not causation.",
        "",
    ]

    lines.extend(_render_task_table(rows))
    lines.extend(_render_draft_logged_chart(rows))
    lines.extend(_render_benchmark_chart(rows, profile))
    lines.extend(_render_longitudinal_chart(longitudinal_path))

    lines.extend(
        [
            "## Primary table (category × size)",
            "",
            "| Category | Size | Corpus n | Corpus median h | Comparison n | "
            "Comparison median h | Saved % | Evidence |",
            "|---|---|---:|---:|---:|---:|---:|---|",
        ]
    )

    primary_keys = sorted(
        set(comparison_pool.keys())
        | {_cell_key(c["category_id"], c["size_band_id"]) for c in cells}
    )
    for cat, band in primary_keys:
        corpus_vals = _build_pool(rows, "corpus").get((cat, band), [])
        cmp_vals = comparison_pool.get((cat, band), [])
        cell = cell_by_key.get((cat, band)) or _make_cell(cat, band, corpus_vals)
        c_n = cell.get("corpus_n") or len(corpus_vals)
        c_med = cell.get("median_hours_logged")
        if cell.get("borrowed_from") == "category_only":
            c_med = _median(cat_only.get(cat, []))
            c_n = len(cat_only.get(cat, []))
        m_n = len(cmp_vals)
        m_med = _median(cmp_vals)
        representable = bool(cell.get("representable")) or (
            cell.get("borrowed_from") == "category_only"
            and (c_n or 0) >= REPRESENTABLE_MIN
        )
        if representable and c_med is not None:
            saved = _saved_pct(c_med, m_med)
            ev = _evidence(cell, m_n)
        else:
            saved = _pending_note(int(c_n or 0))
            ev = _evidence(cell, m_n)
        cat_label = CATEGORY_LABELS.get(cat, cat)
        band_label = SIZE_LABELS.get(band, band)
        lines.append(
            f"| {cat_label} | {band_label} | {c_n} | {_fmt_hours(c_med)} | {m_n} | "
            f"{_fmt_hours(m_med)} | {saved} | {ev} |"
        )

    lines.extend(["", "## Category-only rollup", ""])
    lines.extend(
        [
            "| Category | Corpus n | Corpus median h | Comparison n | "
            "Comparison median h | Median vs draft (cmp) | Saved % | Evidence |",
            "|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for cat in sorted(set(cat_only) | set(cmp_cat_only)):
        c_vals = cat_only.get(cat, [])
        m_vals = cmp_cat_only.get(cat, [])
        c_n = len(c_vals)
        m_n = len(m_vals)
        c_med = _median(c_vals)
        m_med = _median(m_vals)
        cmp_rows = [
            r
            for r in rows
            if r.get("role") == "comparison" and r.get("category_id") == cat
        ]
        vs_drafts = [
            _float_or_none(r.get("hours_vs_draft"))
            for r in cmp_rows
            if _float_or_none(r.get("hours_vs_draft")) is not None
        ]
        med_vs_draft = _median(vs_drafts) if vs_drafts else None
        representable = c_n >= REPRESENTABLE_MIN
        if representable and c_med is not None:
            saved = _saved_pct(c_med, m_med)
            ev = "representable" if m_n >= 3 else "comparison_weak"
        else:
            saved = _pending_note(c_n)
            ev = "directional" if c_n > 0 else "pending"
        cat_label = CATEGORY_LABELS.get(cat, cat)
        lines.append(
            f"| {cat_label} | {c_n} | {_fmt_hours(c_med)} | {m_n} | "
            f"{_fmt_hours(m_med)} | {_fmt_hours(med_vs_draft)} | {saved} | {ev} |"
        )

    new_keys = state.get("new_keys_this_run") or []
    skipped = state.get("skipped_epics") or []
    comparison_epics = [
        k
        for k, v in (state.get("attestation_by_epic") or {}).items()
        if isinstance(v, dict) and v.get("role") == "comparison"
    ]

    lines.extend(["", "## Footer", ""])
    lines.append(
        "- Caveat: observed time differences are associative, not causal. "
        "`estimate_only` means under draft hours, not proven AI causation."
    )
    lines.append(
        "- Attribution: "
        + "; ".join(f"`{k}` = {v}" for k, v in ATTRIBUTION_LABELS.items())
    )
    if new_keys:
        lines.append(f"- New keys this run: `{', '.join(new_keys)}`.")
    if skipped:
        lines.append(f"- Skipped epics: `{', '.join(skipped)}`.")
    if comparison_epics:
        lines.append(
            f"- Epics marked comparison (AI-assisted on first run): "
            f"`{', '.join(sorted(comparison_epics))}`."
        )
    lines.append(
        "- After v4 upgrade: run `mode=full_refresh` once to reload draft estimates "
        "from Jira `customfield_11250`."
    )
    return "\n".join(lines) + "\n"


def migrate_v3_to_v4(state: dict[str, Any], *, repair_estimate: bool) -> None:
    state["schema_version"] = SCHEMA_V4
    jfm = state.setdefault("jira_field_map", {})
    if not jfm.get("draft_estimate_hours"):
        jfm["draft_estimate_hours"] = jfm.get("draft_estimate_hours") or "customfield_11250"
    for row in state.get("rows") or []:
        if not isinstance(row, dict):
            continue
        draft = _float_or_none(row.get("draft_estimate_hours"))
        if draft is None and repair_estimate:
            est = _float_or_none(row.get("estimate_hours"))
            if est is not None and est >= HOURS_PER_SP:
                row["draft_estimate_hours"] = est
        elif draft is None:
            est = _float_or_none(row.get("estimate_hours"))
            if est is not None and est >= HOURS_PER_SP:
                row["draft_estimate_hours"] = est


def verify_state(state: dict[str, Any], *, allow_v3: bool) -> list[str]:
    errors: list[str] = []
    ver = int(state.get("schema_version") or 0)
    if ver == 3 and allow_v3:
        return errors
    if ver != SCHEMA_V4:
        errors.append(
            f"schema_version must be {SCHEMA_V4} (got {ver}); "
            "use --allow-v3-migrate or full_refresh"
        )
    rows = state.get("rows")
    if not isinstance(rows, list):
        errors.append("rows must be an array")
        return errors
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"rows[{i}] must be an object")
            continue
        if row.get("role") not in ("corpus", "comparison"):
            errors.append(f"rows[{i}].role must be corpus or comparison")
        if not row.get("category_id"):
            errors.append(f"rows[{i}].category_id is required")
    return errors


def _longitudinal_entry(state: dict[str, Any], cells: list[dict[str, Any]]) -> dict[str, Any]:
    rows = state.get("rows") or []
    corpus_n = sum(1 for r in rows if r.get("role") == "corpus")
    comparison_n = sum(1 for r in rows if r.get("role") == "comparison")
    saved_by_cat: dict[str, float | None] = {}
    cat_only_c = _category_only_pool(_build_pool(rows, "corpus"))
    cat_only_m = _category_only_pool(_build_pool(rows, "comparison"))
    for cat in set(cat_only_c) | set(cat_only_m):
        c_med = _median(cat_only_c.get(cat, []))
        m_med = _median(cat_only_m.get(cat, []))
        if c_med is not None and m_med is not None and c_med != 0:
            saved_by_cat[cat] = round((c_med - m_med) / c_med * 100.0, 2)
        else:
            saved_by_cat[cat] = None

    vs_draft_sum = round(
        sum(
            _float_or_none(r.get("hours_vs_draft")) or 0.0
            for r in rows
            if r.get("role") == "comparison"
        ),
        2,
    )

    return {
        "run_id": state.get("snapshot_run_id"),
        "generated_at": state.get("generated_at"),
        "run_mode": state.get("run_mode"),
        "report_profile": state.get("report_profile"),
        "new_issues_this_run": state.get("new_keys_this_run") or [],
        "corpus_n": corpus_n,
        "comparison_n": comparison_n,
        "representable_cells": sum(1 for c in cells if c.get("representable")),
        "comparison_hours_sum": round(
            sum(_hours(r) or 0.0 for r in rows if r.get("role") == "comparison"), 2
        ),
        "total_hours_vs_draft_comparison": vs_draft_sum,
        "saved_pct_by_category": saved_by_cat,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="CRTQA stats rollup (schema v4)")
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--latest", type=Path, default=DEFAULT_LATEST)
    parser.add_argument(
        "--append-longitudinal",
        action="store_true",
        help="Append one run entry to state/longitudinal.json",
    )
    parser.add_argument("--longitudinal", type=Path, default=DEFAULT_LONGITUDINAL)
    parser.add_argument(
        "--allow-v3-migrate",
        action="store_true",
        help="Bump schema 3→4 and infer draft from estimate_hours when >= 8",
    )
    parser.add_argument(
        "--repair-draft-from-estimate",
        action="store_true",
        help="When migrating, set draft_estimate_hours from estimate_hours if >= 8",
    )
    args = parser.parse_args()

    if not args.state.is_file():
        print(f"ERROR: state file not found: {args.state}", file=sys.stderr)
        return 1

    try:
        with args.state.open(encoding="utf-8") as f:
            state = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: cannot read state: {e}", file=sys.stderr)
        return 1

    if not isinstance(state, dict):
        print("ERROR: state root must be an object", file=sys.stderr)
        return 1

    if int(state.get("schema_version") or 0) == 3:
        if not args.allow_v3_migrate:
            print(
                "ERROR: schema v3 detected; use --allow-v3-migrate or "
                "re-fetch with mode=full_refresh",
                file=sys.stderr,
            )
            return 1
        migrate_v3_to_v4(
            state, repair_estimate=args.repair_draft_from_estimate
        )

    errors = verify_state(state, allow_v3=args.allow_v3_migrate)
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1

    rows = state.get("rows") or []
    if not isinstance(rows, list):
        rows = []

    apply_draft_sizing(rows)
    cells = compute_corpus_cells(rows)
    enrich_rows(rows, cells)
    state["rows"] = rows
    state["corpus_cells"] = cells
    state["schema_version"] = SCHEMA_V4

    profile, meta = compute_report_profile(rows, cells)
    state["report_profile"] = profile
    state["report_meta"] = meta
    state["rollup_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    args.state.parent.mkdir(parents=True, exist_ok=True)
    with args.state.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")

    latest_md = render_latest(state, cells, longitudinal_path=args.longitudinal)
    args.latest.parent.mkdir(parents=True, exist_ok=True)
    args.latest.write_text(latest_md, encoding="utf-8")

    if args.append_longitudinal:
        entry = _longitudinal_entry(state, cells)
        hist: list[Any] = []
        if args.longitudinal.is_file():
            try:
                with args.longitudinal.open(encoding="utf-8") as f:
                    hist_obj = json.load(f)
                if isinstance(hist_obj, list):
                    hist = hist_obj
            except (OSError, json.JSONDecodeError):
                pass
        hist.append(entry)
        args.longitudinal.parent.mkdir(parents=True, exist_ok=True)
        with args.longitudinal.open("w", encoding="utf-8") as f:
            json.dump(hist, f, indent=2)
            f.write("\n")

    print(
        f"OK: profile={profile}, {len(cells)} corpus cells, latest -> {args.latest}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
