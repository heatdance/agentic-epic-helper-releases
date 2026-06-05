import json
from pathlib import Path

from crtqa_stats.apply_categories import (
    apply_epic_categories_to_state,
    resolve_classification,
    set_epic_review,
)
from crtqa_stats.render_report import _fmt_saved_pct, _pack_epic_rows


def test_manual_review_overrides_hint(tmp_path, monkeypatch) -> None:
    registry = tmp_path / "epic-categories.json"
    registry.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "reviews": {
                    "CRT-290": {
                        "category_id": "fe",
                        "rationale": "DXTF chart UI work.",
                        "evidence": ["CRT-983"],
                        "reviewed_utc": "2026-01-01T00:00:00Z",
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    import crtqa_stats.apply_categories as ac

    monkeypatch.setattr(ac, "epic_categories_path", lambda _c=None: registry)

    state = {
        "corpus_epic_keys": ["CRT-290"],
        "epic_meta": {
            "CRT-290": {"summary": "Mapping algorithm", "description": "console job"}
        },
        "rows": [
            {
                "issue": "CRTQA-1",
                "epic_link": "CRT-290",
                "role": "corpus",
                "category_id": "other",
                "lane": "tcd",
                "draft_estimate_hours": 8,
                "hours_logged": 5,
            }
        ],
    }
    apply_epic_categories_to_state(state)
    cls = resolve_classification("CRT-290", state)
    assert cls["category_id"] == "fe"
    assert cls["classification_source"] == "manual_review"
    assert state["rows"][0]["category_id"] == "fe"


def test_ai_metrics_per_category_scope() -> None:
    """Collapsed uses all comparison rows; FE bucket uses FE comparison only."""
    rows = [
        {"epic": "CRT-A", "role": "corpus", "category_id": "fe", "size_id": "small_tcd", "estimate": 8.0, "logged": 10.0},
        {"epic": "CRT-B", "role": "corpus", "category_id": "be", "size_id": "small_tcd", "estimate": 8.0, "logged": 20.0},
        {"epic": "CRT-A", "role": "comparison", "category_id": "fe", "size_id": "small_tcd", "estimate": 8.0, "logged": 2.0},
        {"epic": "CRT-B", "role": "comparison", "category_id": "be", "size_id": "small_tcd", "estimate": 8.0, "logged": 8.0},
    ]
    state = {"jira_user": "u", "epic_classifications": []}
    collapsed = _pack_epic_rows(rows, state=state, all_rows=rows, attested=set())
    fe_only = [r for r in rows if r["category_id"] == "fe" and r["size_id"] == "small_tcd"]
    fe_pack = _pack_epic_rows(
        fe_only, state=state, all_rows=rows, attested=set(), category_id="fe", size_id="small_tcd"
    )
    assert collapsed["ai_avg_log"] == 5.0
    assert fe_pack["ai_avg_log"] == 2.0
    assert _fmt_saved_pct(collapsed["median_log"], collapsed["ai_avg_log"]) == "66.7%"
    assert _fmt_saved_pct(fe_pack["median_log"], fe_pack["ai_avg_log"]) == "80.0%"
