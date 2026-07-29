#!/usr/bin/env python3
"""One-shot restore of CRTQA stats baselines after CLEAN wiped gitignored state."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOLS = REPO / "automation" / "tools"
sys.path.insert(0, str(TOOLS))

from crtqa_stats.apply_categories import apply_epic_categories_to_state  # noqa: E402
from crtqa_stats.ingest import load_contract, save_state, new_state_skeleton  # noqa: E402

DOWNLOADS = Path.home() / "Downloads"
MSHPAK_PATCHES = {
    "CRT-308": {"draft_estimate_hours": 7.0},
    "CRT-530": {"draft_estimate_hours": 40.0, "hours_logged": 82.85},
    "CRT-544": {"draft_estimate_hours": 5.0, "hours_logged": 3.47},
}
CAT_MAP = {
    "FE": "fe",
    "BE": "be",
    "API": "api",
    "Other": "other",
}


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=REPO, check=True)


def _strip_attested_only_comparisons(user: str, epics: list[str]) -> None:
    """Peer-reviewed baselines may attest AI epics without comparison TCD rows."""
    path = REPO / f"stats/crtqa-stats/state/last-sync-{user}.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    drop_epics = set(epics)
    drop_keys = {
        str(r.get("issue"))
        for r in state.get("rows") or []
        if r.get("role") == "comparison" and str(r.get("epic_link")) in drop_epics
    }
    state["rows"] = [
        r
        for r in state.get("rows") or []
        if not (
            r.get("role") == "comparison"
            and str(r.get("epic_link")) in drop_epics
        )
    ]
    state["included_issue_keys"] = sorted(
        k for k in state.get("included_issue_keys") or [] if k not in drop_keys
    )
    apply_epic_categories_to_state(state)
    save_state(state)


def _patch_mshpak_state() -> None:
    path = REPO / "stats/crtqa-stats/state/last-sync-mshpak.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    for row in state.get("rows") or []:
        ek = str(row.get("epic_link") or "")
        if ek not in MSHPAK_PATCHES:
            continue
        if row.get("lane") != "tcd" and row.get("role") != "comparison":
            continue
        row.update(MSHPAK_PATCHES[ek])
    apply_epic_categories_to_state(state)
    save_state(state)


def _import_amukanova_from_peer_md() -> None:
    src = DOWNLOADS / "latest-amukanova_2.md"
    text = src.read_text(encoding="utf-8")
    row_re = re.compile(
        r"\|\s*\[?(CRT-\d+)\]?\([^)]+\)\s*\|\s*([A-Za-z/+]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|"
    )
    contract = load_contract()
    small_max = float(contract.get("corpus_tcd_small_max_hours", 16))
    state = new_state_skeleton("amukanova", contract)
    rows = []
    included: set[str] = set()
    corpus_epics: list[str] = []
    for epic, cat_label, draft_s, logged_s in row_re.findall(text):
        top, band = cat_label.split("+", 1)
        cat_id = CAT_MAP.get(top.strip(), "other")
        size_id = "small_tcd" if band.strip().upper() == "S" else "big_tcd"
        draft = float(draft_s)
        logged = float(logged_s)
        issue = f"SYNTH-{epic}"
        rows.append(
            {
                "issue": issue,
                "epic_link": epic,
                "lane": "tcd",
                "role": "corpus",
                "category_id": cat_id,
                "size_id": size_id,
                "draft_estimate_hours": draft,
                "estimate_source": "peer_review",
                "hours_logged": logged,
                "others_logged_hours": 0.0,
                "summary": f"Peer-reviewed epic total for {epic}",
                "anomalies": ["peer_review_import"],
            }
        )
        included.add(issue)
        corpus_epics.append(epic)
    state["rows"] = rows
    state["included_issue_keys"] = sorted(included)
    state["corpus_epic_keys"] = sorted(set(corpus_epics))
    state["report_meta"] = {
        "tests_scanned": 390,
        "last_mode": "initial_assessment",
        "last_sync_utc": "2026-06-04T12:00:00Z",
        "epics_discovered": len(corpus_epics),
        "epics_gated": len(corpus_epics),
        "epics_dropped_zero_logged": 0,
        "epics_excluded_operator": [],
        "qa_tasks_in_scope": len(rows),
        "peer_review_import": True,
    }
    apply_epic_categories_to_state(state, contract)
    save_state(state)


def main() -> int:
    stats = REPO / "stats/crtqa-stats"
    (stats / "state").mkdir(parents=True, exist_ok=True)

    _run(
        [
            sys.executable,
            str(TOOLS / "crtqa_stats/process_initial_assessment.py"),
            "--jira-user",
            "arodzevich",
            "--tests-count",
            "19",
            "--qa-list",
            "stats/crtqa-stats/temp/initial-arodzevich/qa-tasks-search.json",
            "--issues-dir",
            "stats/crtqa-stats/temp/initial-arodzevich/issues",
            "--epic-meta",
            "stats/crtqa-stats/temp/initial-arodzevich/epic-meta.json",
            "--exclude-epics",
            "CRT-639",
        ]
    )

    _run(
        [
            sys.executable,
            str(TOOLS / "crtqa_stats/process_initial_assessment.py"),
            "--jira-user",
            "mshpak",
            "--tests-count",
            "1059",
            "--qa-list",
            "stats/crtqa-stats/temp/initial-mshpak/qa-tasks-search.json",
            "--issues-dir",
            "stats/crtqa-stats/temp/initial-mshpak/issues",
            "--epic-meta",
            "stats/crtqa-stats/temp/initial-mshpak/epic-meta.json",
            "--exclude-epics",
            "CRT-594",
        ]
    )
    _patch_mshpak_state()
    _strip_attested_only_comparisons("mshpak", ["CRT-594"])

    for user, tests in (("mshram", "34"), ("mtavadze", "312")):
        _run(
            [
                sys.executable,
                str(TOOLS / "crtqa_stats/process_initial_assessment.py"),
                "--jira-user",
                user,
                "--tests-count",
                tests,
                "--qa-list",
                f"stats/crtqa-stats/temp/initial-{user}/qa-tasks-search.json",
                "--issues-dir",
                f"stats/crtqa-stats/temp/initial-{user}/issues",
                "--epic-meta",
                f"stats/crtqa-stats/temp/initial-{user}/epic-meta.json",
            ]
        )

    _import_amukanova_from_peer_md()

    shutil.copy2(DOWNLOADS / "latest-mshpak.md", stats / "latest-mshpak.md")
    shutil.copy2(DOWNLOADS / "latest-amukanova_2.md", stats / "latest-amukanova.md")

    for user in ("arodzevich", "mshram", "mtavadze"):
        _run(
            [
                sys.executable,
                str(TOOLS / "crtqa_stats_rollup.py"),
                "--jira-user",
                user,
            ]
        )

    _run(
        [
            sys.executable,
            str(TOOLS / "crtqa_stats_team_rollup.py"),
            "--users",
            "mshpak,amukanova,mtavadze,arodzevich,mshram",
        ]
    )

    print("Restore complete at", datetime.now(timezone.utc).isoformat())
    return 0


if __name__ == "__main__":
    sys.exit(main())
