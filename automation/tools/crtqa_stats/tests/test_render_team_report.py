from crtqa_stats.render_team_report import aggregate_team_band, render_team_markdown


def _state(user: str, small_pack: dict, big_pack: dict | None = None) -> dict:
    """Build minimal state; bands supplied via monkeypatching pack_user_collapsed_bands in render."""
    return {"jira_user": user, "rows": [], "report_meta": {}}


def test_aggregate_team_band_sums_and_means() -> None:
    user_bands = [
        {
            "small_tcd": {
                "n_epics": 20,
                "n_ai_epics": 1,
                "median_est": 8.0,
                "median_log": 7.1,
                "ai_avg_log": None,
            },
            "big_tcd": {
                "n_epics": 14,
                "n_ai_epics": 0,
                "median_est": 22.5,
                "median_log": 21.15,
                "ai_avg_log": None,
            },
        },
        {
            "small_tcd": {
                "n_epics": 16,
                "n_ai_epics": 0,
                "median_est": 4.0,
                "median_log": 12.42,
                "ai_avg_log": None,
            },
            "big_tcd": {
                "n_epics": 11,
                "n_ai_epics": 0,
                "median_est": 36.0,
                "median_log": 36.08,
                "ai_avg_log": None,
            },
        },
    ]
    small = aggregate_team_band(user_bands, "small_tcd")
    assert small["n_epics"] == 36
    assert small["n_ai_epics"] == 1
    assert small["median_est"] == 6.0
    assert abs(small["median_log"] - 9.76) < 0.01


def test_aggregate_team_band_saved_pct_from_team_row() -> None:
    user_bands = [
        {
            "small_tcd": {
                "n_epics": 1,
                "n_ai_epics": 1,
                "median_est": 16.0,
                "median_log": 15.0,
                "ai_avg_log": 13.0,
            },
            "big_tcd": {"n_epics": 0, "n_ai_epics": 0, "median_est": None, "median_log": None, "ai_avg_log": None},
        },
        {
            "small_tcd": {
                "n_epics": 2,
                "n_ai_epics": 1,
                "median_est": 8.0,
                "median_log": 10.0,
                "ai_avg_log": 5.0,
            },
            "big_tcd": {"n_epics": 0, "n_ai_epics": 0, "median_est": None, "median_log": None, "ai_avg_log": None},
        },
    ]
    small = aggregate_team_band(user_bands, "small_tcd")
    assert small["ai_avg_log"] == 9.0
    assert abs(small["median_log"] - 12.5) < 0.01
    assert abs(small["saved_pct"] - 28.0) < 0.1


def test_render_team_markdown_header_and_table(monkeypatch) -> None:
    def fake_pack(state, contract=None):
        return {
            "small_tcd": {
                "n_epics": 1,
                "n_ai_epics": 1,
                "median_est": 16.0,
                "median_log": 15.0,
                "ai_avg_log": 13.0,
            },
            "big_tcd": {
                "n_epics": 0,
                "n_ai_epics": 0,
                "median_est": None,
                "median_log": None,
                "ai_avg_log": None,
            },
        }

    import crtqa_stats.render_team_report as tr

    monkeypatch.setattr(tr, "pack_user_collapsed_bands", fake_pack)
    md = render_team_markdown([{"jira_user": "u1"}], users=["u1"])
    assert "# CRTQA stats (team)" in md
    assert "**Users:** `u1`" in md
    assert "**Scope:**" in md
    assert "Display tier" not in md
    assert "Counts:" not in md
    assert "## Collapsed rollup" in md
    assert "## Per-user rollup" in md
    assert "Small TCD" in md
    assert "Big TCD" in md
    assert "13.3%" in md


def test_pack_user_collapsed_bands_micro() -> None:
    from crtqa_stats.render_report import pack_user_collapsed_bands

    state = {
        "jira_user": "micro",
        "attestation_by_epic": {"CRT-639": {"ai_assisted": True}},
        "rows": [
            {
                "issue": "CRTQA-1",
                "epic_link": "CRT-632",
                "lane": "tcd",
                "role": "corpus",
                "category_id": "fe",
                "size_id": "small_tcd",
                "draft_estimate_hours": 16.0,
                "hours_logged": 14.67,
            },
            {
                "issue": "CRTQA-2",
                "epic_link": "CRT-639",
                "lane": "tcd",
                "role": "comparison",
                "category_id": "be",
                "size_id": "small_tcd",
                "draft_estimate_hours": 16.0,
                "hours_logged": 13.0,
            },
        ],
    }
    bands = pack_user_collapsed_bands(state)
    assert bands["small_tcd"]["median_est"] == 16.0
    assert bands["small_tcd"]["median_log"] == 15.0
    assert bands["small_tcd"]["n_ai_epics"] == 1
    assert bands["small_tcd"]["ai_avg_log"] == 13.0
    assert bands["big_tcd"]["n_epics"] == 0
