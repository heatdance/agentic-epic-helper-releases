from pathlib import Path

import pytest

from crtqa_stats.process_incremental import apply_incremental


def test_apply_incremental_subset(tmp_path: Path) -> None:
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    state = {
        "schema_version": 5,
        "jira_user": "tester",
        "included_issue_keys": ["CRTQA-1"],
        "corpus_epic_keys": ["CRT-100"],
        "rows": [
            {
                "issue": "CRTQA-1",
                "epic_link": "CRT-100",
                "lane": "tcd",
                "role": "corpus",
                "category_id": "fe",
                "size_id": "small_tcd",
                "draft_estimate_hours": 8.0,
                "hours_logged": 10.0,
                "summary": "corpus",
            }
        ],
        "epic_classifications": [],
        "attestation_by_epic": {},
        "report_meta": {"tests_scanned": 1},
    }
    state_path = state_dir / "last-sync-tester.json"
    state_path.write_text(__import__("json").dumps(state), encoding="utf-8")

    candidates = {
        "candidates": [
            {
                "key": "CRTQA-2",
                "epic": "CRT-100",
                "summary": "AI TCD",
                "logged_hours": 4.0,
                "estimate_hours": 8.0,
            },
            {
                "key": "CRTQA-3",
                "epic": "CRT-200",
                "summary": "other epic",
                "logged_hours": 5.0,
                "estimate_hours": 8.0,
            },
        ]
    }
    cand_path = tmp_path / "candidates.json"
    cand_path.write_text(__import__("json").dumps(candidates), encoding="utf-8")

    contract_path = tmp_path / "contract.json"
    contract_path.write_text(
        __import__("json").dumps(
            {
                "schema_version": 5,
                "paths": {
                    "state_template": str(state_dir / "last-sync-{jira_user}.json"),
                },
            }
        ),
        encoding="utf-8",
    )

    from crtqa_stats import ingest

    orig = ingest.CONTRACT_PATH
    ingest.CONTRACT_PATH = contract_path
    try:
        report = apply_incremental("tester", cand_path, include_keys={"CRTQA-2"})
    finally:
        ingest.CONTRACT_PATH = orig

    assert report["added_count"] == 1
    saved = __import__("json").loads(state_path.read_text(encoding="utf-8"))
    cmp_rows = [r for r in saved["rows"] if r.get("role") == "comparison"]
    assert len(cmp_rows) == 1
    assert cmp_rows[0]["issue"] == "CRTQA-2"
    assert "CRTQA-2" in saved["included_issue_keys"]
