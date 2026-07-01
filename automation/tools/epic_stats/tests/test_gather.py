from epic_stats.gather import (
    classify_task_summary,
    estimate_from_fields,
    extract_epics_from_issue,
    is_excluded_qa_task,
    logged_from_worklogs,
    logged_hours_for_lane,
)


def test_extract_epics_tests_link() -> None:
    issue = {
        "key": "CRTQA-156",
        "fields": {
            "summary": "Mapping algorithm",
            "issuelinks": [
                {
                    "type": {"name": "Tests"},
                    "outward_issue": {
                        "key": "CRT-290",
                        "fields": {"issuetype": {"name": "Epic"}},
                    },
                }
            ],
        },
    }
    epics, method, _ = extract_epics_from_issue(issue)
    assert epics == ["CRT-290"]
    assert method == "tests_link"


def test_estimate_and_worklogs() -> None:
    fields = {
        "customfield_11250": {"value": 8.0},
        "timetracking": {"original_estimate": "1d"},
        "worklog": {
            "total": 1,
            "worklogs": [{"author": {"name": "mshpak"}, "timeSpentSeconds": 16080}],
        },
    }
    est, src, _ = estimate_from_fields(fields)
    logged, others, _ = logged_from_worklogs(fields["worklog"], "mshpak")
    assert est == 8.0 and src == "draft"
    assert logged == 4.47
    assert others == 0.0


def test_lanes_and_exclude() -> None:
    assert (
        classify_task_summary("[Release notes] [CRT-79] dxCore", "Test Execution")
        == "release_notes"
    )
    assert (
        classify_task_summary("Update tests according to margin", "QA Task")
        == "update_test"
    )
    assert is_excluded_qa_task(
        "[CRT-100] Requirements Analysis",
        "QA Task",
        [{"issuetype": "QA Task", "summary_needles": ["requirements analysis"]}],
    )


def test_logged_hours_for_lane_user_worklog() -> None:
    fields = {
        "worklog": {
            "total": 1,
            "worklogs": [{"author": {"name": "mshpak"}, "timeSpentSeconds": 16080}],
        },
    }
    logged, others, scope, _ = logged_hours_for_lane(
        "release_notes",
        [{"lane": "release_notes", "logged_scope": "user_worklog"}],
        fields["worklog"],
        {"timeSpent": "6h"},
        "mshpak",
    )
    assert scope == "user_worklog" and logged == 4.47 and others == 0.0
