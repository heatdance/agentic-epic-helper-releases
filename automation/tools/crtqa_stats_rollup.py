#!/usr/bin/env python3
"""
Recompute corpus_cells and render stats/crtqa-stats/latest.md from last-sync.json (schema v3).

Examples:
  python automation/tools/crtqa_stats_rollup.py
  python automation/tools/crtqa_stats_rollup.py --state stats/crtqa-stats/state/last-sync.json
  python automation/tools/crtqa_stats_rollup.py --append-longitudinal
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
REPRESENTABLE_MIN = 4

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


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    return float(statistics.median(values))


def _hours(row: dict[str, Any]) -> float | None:
    h = row.get("hours_logged")
    if h is None:
        return None
    try:
        return float(h)
    except (TypeError, ValueError):
        return None


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
    med = _median(corpus_vals)
    cell: dict[str, Any] = {
        "category_id": category_id,
        "size_band_id": size_band_id,
        "corpus_n": n,
        "median_hours_logged": med,
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
        key = (cat, "sp_unknown")
        if key in seen:
            continue
        cells.append(_make_cell(cat, "sp_unknown", vals))

    return cells


def _comparison_pool(rows: list[dict[str, Any]]) -> dict[tuple[str, str], list[float]]:
    return _build_pool(rows, "comparison")


def _cell_lookup(cells: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        _cell_key(str(c["category_id"]), str(c["size_band_id"])): c for c in cells
    }


def _saved_pct(corpus_median: float | None, comparison_median: float | None) -> str:
    if corpus_median is None or comparison_median is None or corpus_median == 0:
        return "—"
    pct = (corpus_median - comparison_median) / corpus_median * 100.0
    return f"{pct:.1f}%"


def _evidence(
    corpus_cell: dict[str, Any],
    comparison_n: int,
) -> str:
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


def render_latest(state: dict[str, Any], cells: list[dict[str, Any]]) -> str:
    rows = state.get("rows") or []
    if not isinstance(rows, list):
        rows = []
    comparison_pool = _comparison_pool(rows)
    cell_by_key = _cell_lookup(cells)

    corpus_n = sum(1 for r in rows if r.get("role") == "corpus")
    comparison_n = sum(1 for r in rows if r.get("role") == "comparison")
    representable_count = sum(1 for c in cells if c.get("representable"))

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
        f"- Counts: corpus `{corpus_n}`, comparison `{comparison_n}`",
        f"- Representable cells: `{representable_count}` (corpus n ≥ {REPRESENTABLE_MIN})",
        "",
        "Corpus = manual baseline; comparison = AI-assisted (agentic epic helper). "
        "Association, not causation.",
        "",
    ]

    chart_cats: list[str] = []
    corpus_bars: list[float] = []
    comparison_bars: list[float] = []
    cat_only = _category_only_pool(_build_pool(rows, "corpus"))
    cmp_cat_only = _category_only_pool(comparison_pool)

    for cat in sorted(set(cat_only) | set(cmp_cat_only)):
        c_vals = cat_only.get(cat, [])
        m_vals = cmp_cat_only.get(cat, [])
        if len(c_vals) < REPRESENTABLE_MIN:
            continue
        c_med = _median(c_vals)
        m_med = _median(m_vals) if m_vals else None
        if c_med is None:
            continue
        chart_cats.append(cat)
        corpus_bars.append(round(c_med, 2))
        comparison_bars.append(round(m_med, 2) if m_med is not None else 0.0)

    if chart_cats:
        ymax = max(max(corpus_bars or [0]), max(comparison_bars or [0]), 1.0)
        ymax = int(ymax * 1.2) + 1
        x_labels = json.dumps(chart_cats)
        lines.extend(
            [
                "```mermaid",
                "xychart-beta",
                '  title "Median logged hours by category (corpus n≥4)"',
                f"  x-axis {x_labels}",
                f'  y-axis "Hours" 0 --> {ymax}',
                f'  bar "Corpus" {json.dumps(corpus_bars)}',
                f'  bar "Comparison" {json.dumps(comparison_bars)}',
                "```",
                "",
            ]
        )

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
        set(comparison_pool.keys()) | {_cell_key(c["category_id"], c["size_band_id"]) for c in cells}
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
            "Comparison median h | Saved % | Evidence |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for cat in sorted(set(cat_only) | set(cmp_cat_only)):
        c_vals = cat_only.get(cat, [])
        m_vals = cmp_cat_only.get(cat, [])
        c_n = len(c_vals)
        m_n = len(m_vals)
        c_med = _median(c_vals)
        m_med = _median(m_vals)
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
            f"{_fmt_hours(m_med)} | {saved} | {ev} |"
        )

    new_keys = state.get("new_keys_this_run") or []
    skipped = state.get("skipped_epics") or []
    comparison_epics = [
        k
        for k, v in (state.get("attestation_by_epic") or {}).items()
        if isinstance(v, dict) and v.get("role") == "comparison"
    ]

    lines.extend(
        [
            "",
            "## Footer",
            "",
            "- Caveat: observed time differences are associative, not causal.",
        ]
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
    return "\n".join(lines) + "\n"


def verify_state(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if int(state.get("schema_version") or 0) != 3:
        errors.append("schema_version must be 3")
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
    return {
        "run_id": state.get("snapshot_run_id"),
        "generated_at": state.get("generated_at"),
        "run_mode": state.get("run_mode"),
        "new_issues_this_run": state.get("new_keys_this_run") or [],
        "corpus_n": corpus_n,
        "comparison_n": comparison_n,
        "representable_cells": sum(1 for c in cells if c.get("representable")),
        "comparison_hours_sum": round(
            sum(_hours(r) or 0.0 for r in rows if r.get("role") == "comparison"), 2
        ),
        "saved_pct_by_category": saved_by_cat,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="CRTQA stats rollup (schema v3)")
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--latest", type=Path, default=DEFAULT_LATEST)
    parser.add_argument(
        "--append-longitudinal",
        action="store_true",
        help="Append one run entry to state/longitudinal.json",
    )
    parser.add_argument(
        "--longitudinal",
        type=Path,
        default=DEFAULT_LONGITUDINAL,
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

    errors = verify_state(state)
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1

    rows = state.get("rows") or []
    cells = compute_corpus_cells(rows)
    state["corpus_cells"] = cells
    state["rollup_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    args.state.parent.mkdir(parents=True, exist_ok=True)
    with args.state.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")

    latest_md = render_latest(state, cells)
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

    print(f"OK: {len(cells)} corpus cells, latest -> {args.latest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
