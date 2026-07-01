from epic_stats.categories import (
    category_justification,
    category_size_label,
    epic_size_from_rows,
)
from epic_stats.epic_breakdown import (
    build_ai_breakdown_rows,
    build_corpus_breakdown_rows,
    jira_browse_url,
    render_epic_breakdown_sections,
)
from epic_stats.render_report import render_latest_markdown


def test_category_size_label() -> None:
    assert category_size_label("fe", "small_tcd") == "FE+S"
    assert category_size_label("other", "big_tcd") == "Other+B"


def test_epic_size_from_max_draft() -> None:
    rows = [{"estimate": 8.0}, {"estimate": 20.0}]
    assert epic_size_from_rows(rows) == "big_tcd"
    assert epic_size_from_rows([{"estimate": 8.0}]) == "small_tcd"


def test_category_justification_epic_ref() -> None:
    text = category_justification(
        {"classification_source": "epic_ref", "category_confidence": "high", "hint_score": 3}
    )
    assert "epic ref" in text
    assert "high" in text


def test_corpus_breakdown_aggregates_multi_row_epic() -> None:
    state = {
        "corpus_epic_keys": ["CRT-572"],
        "epic_meta": {"CRT-572": {"summary": "Option trading UX dxtrade5 widget"}},
        "epic_classifications": [
            {
                "epic_key": "CRT-572",
                "category_id": "fe",
                "category_confidence": "medium",
                "hint_score": 1,
                "classification_source": "jira",
            }
        ],
        "rows": [
            {
                "issue": "CRTQA-1",
                "epic_link": "CRT-572",
                "lane": "tcd",
                "role": "corpus",
                "category_id": "fe",
                "draft_estimate_hours": 16.0,
                "hours_logged": 10.0,
            },
            {
                "issue": "CRTQA-2",
                "epic_link": "CRT-572",
                "lane": "epic_validation",
                "role": "corpus",
                "category_id": "fe",
                "draft_estimate_hours": 8.0,
                "hours_logged": 6.0,
            },
        ],
    }
    rows = build_corpus_breakdown_rows(state)
    assert len(rows) == 1
    assert rows[0]["draft"] == 24.0
    assert rows[0]["logged"] == 16.0
    assert rows[0]["category_label"] == "FE+S"


def test_ai_breakdown_attested_only() -> None:
    state = {
        "corpus_epic_keys": ["CRT-100"],
        "attestation_by_epic": {
            "CRT-594": {"ai_assisted": True, "reason": "operator_excluded_initial_assessment"}
        },
        "epic_meta": {
            "CRT-594": {"summary": "Some AI epic"},
            "CRT-100": {"summary": "Corpus epic"},
        },
        "rows": [
            {
                "issue": "CRTQA-1",
                "epic_link": "CRT-100",
                "lane": "tcd",
                "role": "corpus",
                "category_id": "other",
                "draft_estimate_hours": 8.0,
                "hours_logged": 5.0,
            },
        ],
    }
    ai = build_ai_breakdown_rows(state)
    assert len(ai) == 1
    assert ai[0]["epic_key"] == "CRT-594"
    assert ai[0]["draft"] is None
    assert ai[0]["logged"] is None
    assert "AI-assisted" in ai[0]["note"]


def test_jira_browse_url() -> None:
    url = jira_browse_url("CRT-290")
    assert url.endswith("/browse/CRT-290")


def test_render_includes_breakdown_sections() -> None:
    state = {
        "jira_user": "tester",
        "corpus_epic_keys": ["CRT-100"],
        "epic_meta": {"CRT-100": {"summary": "Test epic summary"}},
        "epic_classifications": [
            {
                "epic_key": "CRT-100",
                "category_id": "other",
                "category_confidence": "low",
                "hint_score": 0,
                "classification_source": "fallback",
            }
        ],
        "report_meta": {"tests_scanned": 1},
        "_inventory_rows": [
            {
                "issue": f"CRTQA-{i}",
                "epic": f"CRT-{100 + i}",
                "role": "corpus",
                "category_id": "other",
                "size_id": "small_tcd",
                "estimate": 8.0,
                "logged": 6.0,
            }
            for i in range(4)
        ],
        "rows": [
            {
                "issue": f"CRTQA-{i}",
                "epic_link": f"CRT-{100 + i}",
                "lane": "tcd",
                "role": "corpus",
                "category_id": "other",
                "draft_estimate_hours": 8.0,
                "hours_logged": 6.0,
            }
            for i in range(4)
        ],
    }
    md = render_latest_markdown(state)
    assert "## Epic breakdown" in md
    assert "## AI Epic breakdown" in md
    assert "[CRT-100]" in md
