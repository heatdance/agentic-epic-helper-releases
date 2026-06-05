import json
from pathlib import Path

import pytest

from crtqa_stats.ingest import (
    apply_corpus_gate,
    epic_user_logged_hours,
    incremental_missing_state_message,
    load_contract,
    new_state_skeleton,
    rows_for_report,
    state_exists,
)


def test_corpus_gate() -> None:
    rows = [
        {"epic_link": "CRT-1", "lane": "tcd", "hours_logged": 0},
        {"epic_link": "CRT-2", "lane": "tcd", "hours_logged": 2.5},
    ]
    assert apply_corpus_gate(["CRT-1", "CRT-2"], rows) == ["CRT-2"]
    assert epic_user_logged_hours(rows, "CRT-2") == 2.5


def test_rows_for_report_size_band() -> None:
    state = {
        "rows": [
            {
                "issue": "CRTQA-9",
                "epic_link": "CRT-9",
                "lane": "tcd",
                "role": "corpus",
                "category_id": "be",
                "draft_estimate_hours": 20,
                "hours_logged": 15,
            }
        ]
    }
    inv = rows_for_report(state)
    assert inv[0]["size_id"] == "big_tcd"


def test_incremental_message() -> None:
    msg = incremental_missing_state_message("nobody")
    assert "initial_assessment" in msg
    assert "nobody" in msg


def test_state_exists_false(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    contract = load_contract()

    def fake_path(user: str, c=None):
        return tmp_path / f"last-sync-{user}.json"

    monkeypatch.setattr("crtqa_stats.ingest.state_path_for_user", fake_path)
    assert state_exists("x", contract) is False
