#!/usr/bin/env python3
"""Render stats/crtqa-stats/latest-<user>.md from v5 state."""

from __future__ import annotations

import statistics
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from crtqa_stats.apply_categories import resolve_classification
from crtqa_stats.categories import TOP_CATEGORY_LABELS, TOP_CATEGORY_ORDER
from crtqa_stats.epic_breakdown import render_epic_breakdown_sections
from crtqa_stats.ingest import load_contract

REPRESENTABLE_MIN = 4
SIZE_LABEL = {
    "small_tcd": "Small TCD (≤16h)",
    "big_tcd": "Big TCD (>16h)",
}
ATTESTED_ONLY_SIZE = "small_tcd"


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    return float(statistics.median(values))


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return float(sum(values) / len(values))


def _attested_ai_epics(state: dict[str, Any]) -> set[str]:
    att = state.get("attestation_by_epic") or {}
    return {str(k).upper() for k, v in att.items() if v.get("ai_assisted")}


def _ai_epic_keys_in_bucket(
    all_rows: list[dict[str, Any]],
    attested: set[str],
    state: dict[str, Any],
    *,
    category_id: str | None = None,
    size_id: str | None = None,
) -> set[str]:
    """Unique epics with AI assistance in a rollup bucket."""
    keys: set[str] = set()
    for r in all_rows:
        if r.get("role") != "comparison":
            continue
        if category_id is not None and r.get("category_id") != category_id:
            continue
        if size_id is not None and r.get("size_id") != size_id:
            continue
        epic = str(r.get("epic") or "")
        if epic:
            keys.add(epic)

    for ek in attested:
        if ek in keys:
            continue
        cls = resolve_classification(ek, state)
        if category_id is not None and cls["category_id"] != category_id:
            continue
        cmp_for_epic = [
            r
            for r in all_rows
            if r.get("role") == "comparison" and str(r.get("epic") or "") == ek
        ]
        if cmp_for_epic:
            epic_sz = str(cmp_for_epic[0].get("size_id") or ATTESTED_ONLY_SIZE)
        else:
            epic_sz = ATTESTED_ONLY_SIZE
        if size_id is not None and epic_sz != size_id:
            continue
        keys.add(ek)
    return keys


def _pack_epic_rows(
    rows: list[dict[str, Any]],
    *,
    state: dict[str, Any],
    all_rows: list[dict[str, Any]] | None = None,
    attested: set[str] | None = None,
    category_id: str | None = None,
    size_id: str | None = None,
) -> dict[str, Any]:
    if not rows and not attested:
        return {
            "n_epics": 0,
            "n_ai_epics": 0,
            "median_est": None,
            "median_log": None,
            "ai_avg_log": None,
        }
    corpus = [r for r in rows if r.get("role") == "corpus"]
    cmp_rows = [r for r in rows if r.get("role") == "comparison"]
    est = [float(r["estimate"]) for r in corpus]
    log = [float(r["logged"]) for r in corpus]
    cmp_logs = [float(r["logged"]) for r in cmp_rows]
    epic_set = {r["epic"] for r in corpus if r.get("epic")}
    pool = all_rows if all_rows is not None else rows
    ai_keys = _ai_epic_keys_in_bucket(
        pool,
        attested or set(),
        state,
        category_id=category_id,
        size_id=size_id,
    )
    return {
        "n_epics": len(epic_set),
        "n_ai_epics": len(ai_keys),
        "median_est": _median(est),
        "median_log": _median(log),
        "ai_avg_log": _rollup_ai_avg_log(cmp_logs),
    }


def _fmt_hours(v: float | None) -> str:
    if v is None:
        return "—"
    return f"{v:.2f}"


def _rollup_ai_avg_log(comparison_logged_hours: list[float]) -> float | None:
    """Mean logged hours on comparison rows (same formula for collapsed and category scope)."""
    return _mean(comparison_logged_hours) if comparison_logged_hours else None


def _fmt_saved_pct(corpus_med: float | None, ai_avg: float | None) -> str:
    if ai_avg is None:
        return "—"
    if corpus_med is None or corpus_med == 0:
        return "—"
    return f"{(corpus_med - ai_avg) / corpus_med * 100:.1f}%"


def _category_tier(small_epics: int, big_epics: int) -> str:
    if small_epics >= REPRESENTABLE_MIN and big_epics >= REPRESENTABLE_MIN:
        return "full"
    if small_epics + big_epics > 0:
        return "partial"
    return "none"


def _display_tier_label(cat_tiers: dict[str, str]) -> str:
    sparse = sum(1 for t in cat_tiers.values() if t != "full")
    if sparse >= 2:
        return "collapsed"
    if any(t == "full" for t in cat_tiers.values()):
        return "partial" if sparse else "full"
    return "collapsed"


def _corpus_epic_counts_by_size(rows: list[dict[str, Any]]) -> tuple[int, int]:
    small: set[str] = set()
    big: set[str] = set()
    for r in rows:
        if r.get("role") != "corpus":
            continue
        epic = str(r.get("epic") or "")
        if not epic:
            continue
        sz = r.get("size_id") or "small_tcd"
        if sz == "big_tcd":
            big.add(epic)
        else:
            small.add(epic)
    return len(small), len(big)


def _collapsed_rollup_rows(
    rows: list[dict[str, Any]],
    state: dict[str, Any],
    attested: set[str],
) -> list[tuple[str | None, dict[str, Any]]]:
    """(subcategory label or None, pack) — two rows when both size bands have ≥4 corpus epics."""
    small_n, big_n = _corpus_epic_counts_by_size(rows)
    if small_n >= REPRESENTABLE_MIN and big_n >= REPRESENTABLE_MIN:
        out: list[tuple[str | None, dict[str, Any]]] = []
        for sz, label in (("small_tcd", SIZE_LABEL["small_tcd"]), ("big_tcd", SIZE_LABEL["big_tcd"])):
            if sz == "big_tcd":
                band = [r for r in rows if r.get("size_id") == "big_tcd"]
            else:
                band = [r for r in rows if r.get("size_id") != "big_tcd"]
            out.append(
                (
                    label,
                    _pack_epic_rows(
                        band,
                        state=state,
                        all_rows=rows,
                        attested=attested,
                        size_id=sz,
                    ),
                )
            )
        return out
    return [
        (
            None,
            _pack_epic_rows(rows, state=state, all_rows=rows, attested=attested),
        )
    ]


def _is_micro_corpus(corpus_epic_count: int, contract: dict[str, Any] | None = None) -> bool:
    c = contract or load_contract()
    min_epics = int(c.get("representable_min_epics_per_subcategory", REPRESENTABLE_MIN))
    return corpus_epic_count < min_epics


def pack_user_collapsed_bands(
    state: dict[str, Any],
    contract: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    """Per-user Small/Big band packs for team rollup (always two bands)."""
    c = contract or load_contract()
    from crtqa_stats.ingest import rows_for_report

    rows = rows_for_report(state)
    attested = _attested_ai_epics(state)
    corpus_epics = len({r["epic"] for r in rows if r.get("role") == "corpus" and r.get("epic")})
    empty: dict[str, Any] = {
        "n_epics": 0,
        "n_ai_epics": 0,
        "median_est": None,
        "median_log": None,
        "ai_avg_log": None,
    }

    if _is_micro_corpus(corpus_epics, c):
        micro = _pack_micro_corpus_row(rows, state, attested, c)
        return {
            "small_tcd": {
                "n_epics": corpus_epics,
                "n_ai_epics": micro["n_ai_epics"],
                "median_est": micro["median_est"],
                "median_log": micro["median_log"],
                "ai_avg_log": micro["ai_avg_log"],
            },
            "big_tcd": dict(empty),
        }

    bands: dict[str, dict[str, Any]] = {}
    for sz in ("small_tcd", "big_tcd"):
        if sz == "big_tcd":
            band_rows = [r for r in rows if r.get("size_id") == "big_tcd"]
        else:
            band_rows = [r for r in rows if r.get("size_id") != "big_tcd"]
        bands[sz] = _pack_epic_rows(
            band_rows,
            state=state,
            all_rows=rows,
            attested=attested,
            size_id=sz,
        )
    return bands


def _micro_corpus_baselines(contract: dict[str, Any] | None = None) -> tuple[float, float]:
    c = contract or load_contract()
    draft = float(c.get("corpus_tcd_small_max_hours", 16))
    logged = float(c.get("micro_corpus_baseline_logged_hours", 15))
    return draft, logged


def _pack_micro_corpus_row(
    rows: list[dict[str, Any]],
    state: dict[str, Any],
    attested: set[str],
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Small corpus: fixed small-TCD baselines; AI metrics from actual comparison rows."""
    draft, logged = _micro_corpus_baselines(contract)
    cmp_rows = [r for r in rows if r.get("role") == "comparison"]
    cmp_logs = [float(r["logged"]) for r in cmp_rows]
    ai_keys = _ai_epic_keys_in_bucket(rows, attested, state)
    return {
        "median_est": draft,
        "median_log": logged,
        "n_ai_epics": len(ai_keys),
        "ai_avg_log": _rollup_ai_avg_log(cmp_logs),
    }


def _render_micro_collapsed_rollup_section(pack: dict[str, Any]) -> list[str]:
    lines = [
        "## Collapsed rollup",
        "",
        "Small corpus: corpus medians use the small-TCD draft ceiling and baseline logged hours; "
        "AI metrics use actual comparison TCD worklogs.",
        "",
        "| Median draft (h) | Median logged (h) | AI epics | AI logged avg (h) | Saved % |",
        "|-----------------:|------------------:|---------:|------------------:|--------:|",
        f"| {_fmt_hours(pack['median_est'])} | {_fmt_hours(pack['median_log'])} | "
        f"{pack['n_ai_epics']} | {_fmt_hours(pack['ai_avg_log'])} | "
        f"{_fmt_saved_pct(pack['median_log'], pack['ai_avg_log'])} |",
        "",
    ]
    return lines


def _render_collapsed_rollup_section(
    collapsed_rows: list[tuple[str | None, dict[str, Any]]],
) -> list[str]:
    split = collapsed_rows[0][0] is not None
    lines = ["## Collapsed rollup", ""]
    if split:
        lines.extend(
            [
                "| Subcategory | Epics | Median draft (h) | Median logged (h) | "
                "AI epics | AI logged avg (h) | Saved % |",
                "|-------------|------:|-----------------:|------------------:|"
                "---------:|------------------:|--------:|",
            ]
        )
        for label, p in collapsed_rows:
            lines.append(
                f"| {label} | {p['n_epics']} | {_fmt_hours(p['median_est'])} | "
                f"{_fmt_hours(p['median_log'])} | {p['n_ai_epics']} | "
                f"{_fmt_hours(p['ai_avg_log'])} | "
                f"{_fmt_saved_pct(p['median_log'], p['ai_avg_log'])} |"
            )
    else:
        p = collapsed_rows[0][1]
        lines.extend(
            [
                "| Epics | Median draft (h) | Median logged (h) | AI epics | AI logged avg (h) | Saved % |",
                "|------:|-----------------:|------------------:|---------:|------------------:|--------:|",
                f"| {p['n_epics']} | {_fmt_hours(p['median_est'])} | "
                f"{_fmt_hours(p['median_log'])} | {p['n_ai_epics']} | "
                f"{_fmt_hours(p['ai_avg_log'])} | "
                f"{_fmt_saved_pct(p['median_log'], p['ai_avg_log'])} |",
            ]
        )
    lines.append("")
    return lines


def render_latest_markdown(state: dict[str, Any]) -> str:
    user = str(state.get("jira_user") or "")
    contract = load_contract()
    rows = state.get("_inventory_rows")
    if rows is None:
        from crtqa_stats.ingest import rows_for_report

        rows = rows_for_report(state)

    attested = _attested_ai_epics(state)

    cells: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        cat = r.get("category_id") or "other"
        sz = r.get("size_id") or "small_tcd"
        cells[(cat, sz)].append(r)

    cat_tiers: dict[str, str] = {}
    for cat in TOP_CATEGORY_ORDER:
        small_epics = len({x["epic"] for x in cells.get((cat, "small_tcd"), []) if x.get("role") == "corpus"})
        big_epics = len({x["epic"] for x in cells.get((cat, "big_tcd"), []) if x.get("role") == "corpus"})
        cat_tiers[cat] = _category_tier(small_epics, big_epics)

    meta = state.get("report_meta") or {}
    tests_n = int(meta.get("tests_scanned") or 0)
    corpus_rows = [r for r in rows if r.get("role") == "corpus"]
    cmp_rows = [r for r in rows if r.get("role") == "comparison"]
    corpus_epics = len({r["epic"] for r in corpus_rows if r.get("epic")})
    ai_epics_total = len(_ai_epic_keys_in_bucket(rows, attested, state))
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    micro = _is_micro_corpus(corpus_epics, contract)
    tier = "micro" if micro else _display_tier_label(cat_tiers)

    lines = [
        "# CRTQA stats",
        "",
        f"- **Generated:** {generated}",
        f"- **User:** `{user}`",
        f"- **Counts:** {corpus_epics} epics in corpus · {len(corpus_rows)} corpus rows · "
        f"{len(cmp_rows)} comparison rows · {ai_epics_total} AI-assisted epics · {tests_n} tests scanned",
        f"- **Display tier:** `{tier}`",
        "",
    ]

    if micro:
        lines.extend(
            [
                "**Micro corpus** — fewer than 4 corpus epics: **collapsed rollup only** "
                "(no category or epic tables). Corpus medians use small-TCD reference hours; "
                "AI epics, logged avg, and Saved % use actual comparison TCD data.",
                "",
            ]
        )
        pack = _pack_micro_corpus_row(rows, state, attested, contract)
        lines.extend(_render_micro_collapsed_rollup_section(pack))
        return "\n".join(lines) + "\n"

    collapsed_entries = _collapsed_rollup_rows(rows, state, attested)

    lines.extend(
        [
            "**Display tiers:** **full** — both Small and Big subcategories have ≥4 epics; "
            "show category×subcategory detail. **partial** — some subcategories are sparse; "
            "prefer category rollup. **collapsed** — two or more categories are not full; "
            "lead with collapsed rollup, then category×subcategory. "
            "**Collapsed rollup** splits into Small/Big TCD rows when **both** bands have ≥4 corpus epics; "
            "otherwise one all-corpus row.",
            "",
            "**AI-assisted epics** — operator-attested at initial assessment (`attestation_by_epic`) "
            "and/or epics with **comparison** Done TCD rows after incremental update. "
            "**AI logged avg** and **Saved %** use comparison rows only (Done TCD with user worklogs); "
            "attested-only epics count toward **AI epics** but not avg/Saved until logged.",
            "",
        ]
    )
    lines.extend(_render_collapsed_rollup_section(collapsed_entries))
    lines.extend(
        [
            "## Category rollup",
            "",
            "| Category | Subcategory | Epics | Median draft (h) | Median logged (h) | "
            "AI epics | AI logged avg (h) | Saved % |",
            "|----------|-------------|------:|-----------------:|------------------:|"
            "---------:|------------------:|--------:|",
        ]
    )

    for cat in TOP_CATEGORY_ORDER:
        for sz in ("small_tcd", "big_tcd"):
            rs = cells.get((cat, sz), [])
            p = _pack_epic_rows(
                rs,
                state=state,
                all_rows=rows,
                attested=attested,
                category_id=cat,
                size_id=sz,
            )
            lines.append(
                f"| {TOP_CATEGORY_LABELS[cat]} | {SIZE_LABEL[sz]} | {p['n_epics']} | "
                f"{_fmt_hours(p['median_est'])} | {_fmt_hours(p['median_log'])} | "
                f"{p['n_ai_epics']} | {_fmt_hours(p['ai_avg_log'])} | "
                f"{_fmt_saved_pct(p['median_log'], p['ai_avg_log'])} |"
            )

    lines.extend(render_epic_breakdown_sections(state))
    return "\n".join(lines) + "\n"
