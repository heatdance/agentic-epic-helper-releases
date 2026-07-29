#!/usr/bin/env python3
"""Render stats/epic-stats/latest-team.md from multiple user states."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from epic_stats.ingest import load_contract
from epic_stats.render_report import (
    SIZE_LABEL,
    _fmt_hours,
    _fmt_saved_pct,
    _mean,
    pack_user_collapsed_bands,
)


def _team_saved_pct_from_row(
    team_median_log: float | None,
    team_ai_avg_log: float | None,
) -> float | None:
    """Saved % for team row — from team median logged and team AI logged avg."""
    if team_ai_avg_log is None or team_median_log is None or team_median_log == 0:
        return None
    return (team_median_log - team_ai_avg_log) / team_median_log * 100.0


def _format_saved_pct(saved: float | None) -> str:
    if saved is None:
        return "—"
    return f"{saved:.1f}%"


def aggregate_team_band(
    user_bands: list[dict[str, dict[str, Any]]],
    band_key: str,
) -> dict[str, Any]:
    packs = [bands[band_key] for bands in user_bands if band_key in bands]
    epics = sum(int(p.get("n_epics") or 0) for p in packs)
    ai_epics = sum(int(p.get("n_ai_epics") or 0) for p in packs)

    med_est = [float(p["median_est"]) for p in packs if p.get("median_est") is not None]
    med_log = [float(p["median_log"]) for p in packs if p.get("median_log") is not None]
    ai_logs = [float(p["ai_avg_log"]) for p in packs if p.get("ai_avg_log") is not None]

    avg_est = _mean(med_est)
    avg_log = _mean(med_log)
    avg_ai = _mean(ai_logs)

    return {
        "n_epics": epics,
        "n_ai_epics": ai_epics,
        "median_est": avg_est,
        "median_log": avg_log,
        "ai_avg_log": avg_ai,
        "saved_pct": _team_saved_pct_from_row(avg_log, avg_ai),
    }


def render_team_markdown(
    states: list[dict[str, Any]],
    *,
    users: list[str] | None = None,
) -> str:
    contract = load_contract()
    names = users or [str(s.get("jira_user") or "") for s in states]
    names = [n for n in names if n]
    user_bands = [pack_user_collapsed_bands(s, contract) for s in states]
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    user_list = ", ".join(f"`{u}`" for u in names)

    lines = [
        "# CRTQA stats (team)",
        "",
        f"- **Generated:** {generated}",
        f"- **Users:** {user_list}",
        "- **Scope:** Team collapsed rollup after incremental AI comparison update; "
        "per-user corpus baselines from state.",
        "",
        "**Team Saved %** — `(team median logged − team AI logged avg) / team median logged` "
        "using the team row values. **Per-user Saved %** — same formula on each engineer's "
        "Small/Big band medians and AI logged avg.",
        "",
        "## Collapsed rollup",
        "",
        "| Subcategory | Epics | Median draft (h) | Median logged (h) | "
        "AI epics | AI logged avg (h) | Saved % |",
        "|-------------|------:|-----------------:|------------------:|"
        "---------:|------------------:|--------:|",
    ]

    for band_key in ("small_tcd", "big_tcd"):
        agg = aggregate_team_band(user_bands, band_key)
        lines.append(
            f"| {SIZE_LABEL[band_key]} | {agg['n_epics']} | "
            f"{_fmt_hours(agg['median_est'])} | {_fmt_hours(agg['median_log'])} | "
            f"{agg['n_ai_epics']} | {_fmt_hours(agg['ai_avg_log'])} | "
            f"{_format_saved_pct(agg['saved_pct'])} |"
        )

    lines.extend(
        [
            "",
            "## Per-user rollup",
            "",
            "| User | Subcategory | Epics | Median draft (h) | Median logged (h) | "
            "AI epics | AI logged avg (h) | Saved % |",
            "|------|-------------|------:|-----------------:|------------------:|"
            "---------:|------------------:|--------:|",
        ]
    )

    for user, bands in zip(names, user_bands):
        for band_key in ("small_tcd", "big_tcd"):
            pack = bands[band_key]
            lines.append(
                f"| `{user}` | {SIZE_LABEL[band_key]} | {pack['n_epics']} | "
                f"{_fmt_hours(pack['median_est'])} | {_fmt_hours(pack['median_log'])} | "
                f"{pack['n_ai_epics']} | {_fmt_hours(pack['ai_avg_log'])} | "
                f"{_fmt_saved_pct(pack['median_log'], pack['ai_avg_log'])} |"
            )

    lines.append("")
    return "\n".join(lines) + "\n"
