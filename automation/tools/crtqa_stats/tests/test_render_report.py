from crtqa_stats.render_report import (
    _display_tier_label,
    _fmt_saved_pct,
    _pack_epic_rows,
    render_latest_markdown,
)


def test_saved_pct() -> None:
    assert _fmt_saved_pct(10.0, 5.0) == "50.0%"
    assert _fmt_saved_pct(10.0, None) == "—"
    assert _fmt_saved_pct(None, 5.0) == "—"


def test_pack_epic_rows_corpus_vs_comparison() -> None:
    rows = [
        {"epic": "CRT-1", "role": "corpus", "estimate": 8.0, "logged": 10.0},
        {"epic": "CRT-1", "role": "corpus", "estimate": 16.0, "logged": 12.0},
        {"epic": "CRT-2", "role": "comparison", "estimate": 8.0, "logged": 4.0},
    ]
    p = _pack_epic_rows(rows, state={}, all_rows=rows, attested=set())
    assert p["n_epics"] == 1
    assert p["n_ai_epics"] == 1
    assert p["median_est"] == 12.0
    assert p["median_log"] == 11.0
    assert p["ai_avg_log"] == 4.0
    assert _fmt_saved_pct(p["median_log"], p["ai_avg_log"]) == "63.6%"


def test_attested_ai_epic_count_without_comparison_rows() -> None:
    from crtqa_stats.render_report import _attested_ai_epics, render_latest_markdown

    state = {
        "jira_user": "mshpak",
        "attestation_by_epic": {
            "CRT-594": {"ai_assisted": True, "reason": "operator_excluded_initial_assessment"}
        },
        "report_meta": {"tests_scanned": 100},
        "_inventory_rows": [
            {
                "issue": "CRTQA-1",
                "epic": "CRT-100",
                "role": "corpus",
                "category_id": "other",
                "size_id": "small_tcd",
                "estimate": 8.0,
                "logged": 10.0,
            },
        ],
    }
    assert _attested_ai_epics(state) == {"CRT-594"}
    md = render_latest_markdown(state)
    assert "1 AI-assisted epics" in md
    assert "AI epics | AI logged avg" in md
    assert "| 16.00 | 15.00 | 1 | — | — |" in md


def test_display_tier_collapsed() -> None:
    tiers = {"fe": "none", "be": "partial", "api": "none", "other": "partial"}
    assert _display_tier_label(tiers) == "collapsed"


def _corpus_row(epic: str, size_id: str, est: float = 8.0, log: float = 6.0) -> dict:
    return {
        "issue": f"CRTQA-{epic}",
        "epic": epic,
        "role": "corpus",
        "category_id": "fe",
        "size_id": size_id,
        "estimate": est,
        "logged": log,
    }


def test_collapsed_single_row_when_sparse_bands() -> None:
    rows = [
        _corpus_row("CRT-1", "small_tcd"),
        _corpus_row("CRT-2", "small_tcd"),
        _corpus_row("CRT-3", "big_tcd"),
    ]
    state = {"jira_user": "u", "report_meta": {"tests_scanned": 1}, "_inventory_rows": rows}
    md = render_latest_markdown(state)
    assert "## Collapsed rollup" in md
    assert "Subcategory" not in md.split("## Category rollup")[0]


def test_collapsed_split_when_both_bands_representable() -> None:
    rows = []
    for i in range(5):
        rows.append(_corpus_row(f"CRT-S{i}", "small_tcd"))
    for i in range(4):
        rows.append(_corpus_row(f"CRT-B{i}", "big_tcd", est=20.0))
    state = {"jira_user": "u", "report_meta": {"tests_scanned": 9}, "_inventory_rows": rows}
    md = render_latest_markdown(state)
    collapsed = md.split("## Category rollup")[0]
    assert "| Subcategory |" in collapsed
    assert "Small TCD (≤16h)" in collapsed
    assert "Big TCD (>16h)" in collapsed
    assert collapsed.count("| FE Epic |") == 0


def test_render_minimal_state() -> None:
    state = {
        "jira_user": "testuser",
        "report_meta": {"tests_scanned": 5},
        "_inventory_rows": [
            {
                "issue": "CRTQA-1",
                "epic": "CRT-100",
                "role": "corpus",
                "category_id": "fe",
                "size_id": "small_tcd",
                "estimate": 8.0,
                "logged": 6.0,
            },
        ],
    }
    md = render_latest_markdown(state)
    assert "CRTQA stats" in md
    assert "`testuser`" in md
    assert "## Collapsed rollup" in md
    assert "## Category rollup" not in md
    assert "`micro`" in md
    assert "| 16.00 | 15.00 |" in md


def test_render_micro_with_comparison_saved_pct() -> None:
    state = {
        "jira_user": "arodzevich",
        "attestation_by_epic": {
            "CRT-639": {"ai_assisted": True, "reason": "operator_excluded_initial_assessment"}
        },
        "report_meta": {"tests_scanned": 19},
        "_inventory_rows": [
            {
                "issue": "CRTQA-10034",
                "epic": "CRT-632",
                "role": "corpus",
                "category_id": "fe",
                "size_id": "small_tcd",
                "estimate": 16.0,
                "logged": 14.67,
            },
            {
                "issue": "CRTQA-10132",
                "epic": "CRT-639",
                "role": "comparison",
                "category_id": "be",
                "size_id": "small_tcd",
                "estimate": 16.0,
                "logged": 13.0,
            },
        ],
    }
    md = render_latest_markdown(state)
    assert "## Category rollup" not in md
    assert "| 16.00 | 15.00 | 1 | 13.00 | 13.3% |" in md
