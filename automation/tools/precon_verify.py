#!/usr/bin/env python3
"""
Verify TEST-PRECON artefact before TEST-PREP consumption.

Examples:
  python automation/tools/precon_verify.py \\
    --coverage epics/CRT-639/CRT-639-coverage.json \\
    --precon epics/CRT-639/CRT-639-precon.json \\
    --md epics/CRT-639/CRT-639-precon.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

TEMP_PATH_RE = re.compile(r"(?:^|[/\\])temp(?:[/\\]|$)|/temp/", re.I)
PASSWORDISH_RE = re.compile(
    r"(password\s*[:=]|postgresql://[^@\s]+:[^@\s]+@|Bearer\s+[A-Za-z0-9._-]{20,})",
    re.I,
)

# Jira-facing hygiene (body, code_examples, branch_notes, optional .md)
HARNESS_TOKEN_RE = re.compile(
    r"\b(discover(?:y)?|probe(?:d|s)?|multiplex|parity|fixture(?:_need)?s?|"
    r"obligation(?:_closure)?|crtqa_index|validation_log|ladder_in_test|"
    r"TEST-PREP|TEST-DISCOVER|precon-ledger|console_guide family|ladder parity)\b",
    re.I,
)
PROBE_ACCOUNT_RE = re.compile(r"\bantonfx\b", re.I)
TB_REF_RE = re.compile(r"\btb-\d{3}\b", re.I)
ACCOUNT_ID_LITERAL_RE = re.compile(r"account_id\s*=\s*\d+", re.I)
LONG_NUMERIC_ID_RE = re.compile(r"\b\d{8,}\b")
MD_PREAMBLE_RE = re.compile(
    r"(paste into jira|CRT-639-precon\.json|epics/.+-precon\.json|"
    r"full structured artefact)",
    re.I,
)
MD_FOOTER_RE = re.compile(
    r"(ladder_in_test|regression test bundles tb-)",
    re.I,
)

FE_CHROME_SURFACES = frozenset({"chrome", "dxtrade5", "webbroker"})
FE_UI_AUTHENTICATED_OK = frozenset({"authenticated", "waived"})
FE_UI_SHALLOW = frozenset({"shell_only", "waived"})
POST_LOGIN_WB_BODY_RE = re.compile(
    r"(create\s+(dealer\s+)?user|assign\s+account|assign\s+to\s+group|position\s+book)",
    re.I,
)
POST_LOGIN_DX_BODY_RE = re.compile(
    r"(positions\s+widget|retail\s+login|metric\s+column)",
    re.I,
)
SMOKE_ACTION_RE = re.compile(r"post-login\s+smoke", re.I)
INSTRUMENT_ID_RE = re.compile(r"instrument_id|account_group_id", re.I)
SHOW_IN_ACTION_RE = re.compile(r"\bshow\b", re.I)

REPO_ROOT = Path(__file__).resolve().parents[2]
LADDER_PATH = REPO_ROOT / "docs" / "exploration-depth-ladder.json"
DEPTH_ORDER = ["smoke", "discover_probe", "precon_drill", "prep_verify_view"]


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        with path.open(encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _primary_check_ids(coverage: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for chk in coverage.get("checks") or []:
        if not isinstance(chk, dict):
            continue
        cid = chk.get("id")
        if not cid:
            continue
        if chk.get("verification_role") == "primary":
            ids.append(str(cid))
    return sorted(set(ids))


def _walk_strings(obj: Any, path: str = "$") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(obj, str):
        found.append((path, obj))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k.startswith("_"):
                continue
            if k in (
                "exploration_grounding",
                "exploration_log",
                "validation_log",
                "anti_pattern_findings",
                "optional_jira_audit",
            ):
                continue
            found.extend(_walk_strings(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            found.extend(_walk_strings(v, f"{path}[{i}]"))
    return found


def _jira_facing_texts(precon: dict[str, Any]) -> list[tuple[str, str]]:
    texts: list[tuple[str, str]] = []
    for cluster in precon.get("precon_clusters") or []:
        if not isinstance(cluster, dict):
            continue
        cid = cluster.get("id", "?")
        for step in cluster.get("steps") or []:
            if not isinstance(step, dict):
                continue
            order = step.get("order", "?")
            prefix = f"precon_clusters[{cid}].steps[{order}]"
            body = step.get("body")
            if body:
                texts.append((f"{prefix}.body", str(body)))
            for i, ex in enumerate(step.get("code_examples") or []):
                texts.append((f"{prefix}.code_examples[{i}]", str(ex)))
            for i, note in enumerate(step.get("branch_notes") or []):
                texts.append((f"{prefix}.branch_notes[{i}]", str(note)))
    return texts


def _load_ladder() -> dict[str, Any]:
    reg = _load_json(LADDER_PATH)
    return reg if reg else {}


def _depth_rank(level: str | None) -> int:
    if not level:
        return -1
    try:
        return DEPTH_ORDER.index(str(level))
    except ValueError:
        return -1


def _discover_fixtures_by_id(discover: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    if not discover:
        return out
    for row in discover.get("fixture_needs") or []:
        if isinstance(row, dict) and row.get("id"):
            out[str(row["id"])] = row
    return out


def _gap_covers(
    gaps: list[Any],
    *,
    cluster_id: str,
    fixture_id: str | None = None,
    view_id: str | None = None,
    surface: str | None = None,
) -> bool:
    for g in gaps:
        if not isinstance(g, dict):
            continue
        if str(g.get("cluster_id")) != cluster_id:
            continue
        if fixture_id and str(g.get("fixture_id")) != fixture_id:
            continue
        if view_id and str(g.get("view_id")) != view_id:
            continue
        if surface and str(g.get("surface")) != surface:
            continue
        if g.get("reason") in ("tooling_blocked", "chrome_unavailable", "waived"):
            return True
    return False


def _verify_cluster_exploration_depth(
    cluster: dict[str, Any],
    *,
    discover: dict[str, Any] | None,
    fe_waived: bool,
    fe_sessions: dict[str, Any],
    ladder: dict[str, Any],
    precon: dict[str, Any],
    errors: list[str],
) -> None:
    cid = str(cluster.get("id") or "?")
    logs = [x for x in (cluster.get("exploration_log") or []) if isinstance(x, dict)]
    gaps = precon.get("exploration_gaps") or []
    fixtures_by_id = _discover_fixtures_by_id(discover)
    precon_req = (ladder.get("precon_requires") or {}).get("by_fixture_kind") or {}
    shallow_deny = set(
        (ladder.get("precon_requires") or {}).get("shallow_nav_denylist") or []
    )
    drill_nav = set(
        (ladder.get("precon_requires") or {}).get("shallow_nav_requires_drill") or []
    )

    if len(logs) >= 2:
        at_values = [str(x.get("at") or "") for x in logs if x.get("at")]
        if at_values and len(set(at_values)) == 1:
            errors.append(
                f"precon_clusters {cid}: all exploration_log rows share identical at "
                "(batch fabricate — use distinct timestamps per navigation)"
            )

    for i, log in enumerate(logs):
        action = str(log.get("action") or "")
        outcome = str(log.get("outcome") or "").lower()
        depth = log.get("depth_level")
        view_id = log.get("view_id")
        if outcome == "pass" and SMOKE_ACTION_RE.search(action):
            if depth != "smoke":
                errors.append(
                    f"precon_clusters {cid} exploration_log[{i}]: post-login smoke pass "
                    f"requires depth_level smoke (got {depth!r})"
                )
        surface = str(log.get("surface") or "").lower()
        if surface in FE_CHROME_SURFACES and outcome == "pass":
            if _depth_rank(str(depth)) < _depth_rank("precon_drill") and not fe_waived:
                if not _gap_covers(gaps, cluster_id=cid, surface=surface):
                    errors.append(
                        f"precon_clusters {cid} exploration_log[{i}]: FE pass requires "
                        f"depth_level precon_drill with view_id (got depth={depth!r})"
                    )
            if _depth_rank(str(depth)) >= _depth_rank("precon_drill") and not view_id:
                if not _gap_covers(gaps, cluster_id=cid, surface=surface):
                    errors.append(
                        f"precon_clusters {cid} exploration_log[{i}]: precon_drill "
                        "requires view_id"
                    )

    fe_drill_logs = [
        x
        for x in logs
        if _depth_rank(str(x.get("depth_level"))) >= _depth_rank("precon_drill")
        and str(x.get("surface") or "").lower() in FE_CHROME_SURFACES | {"webbroker", "dxtrade5", "adaptive"}
    ]
    if fe_drill_logs and not fe_waived:
        all_widgets: set[str] = set()
        for x in fe_drill_logs:
            for w in x.get("widgets_seen") or []:
                all_widgets.add(str(w))
        if all_widgets and all_widgets <= shallow_deny:
            if not _gap_covers(gaps, cluster_id=cid):
                errors.append(
                    f"precon_clusters {cid}: widgets_seen only shallow nav labels "
                    f"{sorted(all_widgets)} — drill into {sorted(drill_nav)} views"
                )

    for fid in cluster.get("satisfies_fixture_ids") or []:
        fid = str(fid)
        fix = fixtures_by_id.get(fid)
        if not fix:
            continue
        if str(fix.get("setup_depth")) != "probe_executed":
            continue
        kind = str(fix.get("kind") or "")
        req = precon_req.get(kind) if isinstance(precon_req.get(kind), dict) else None
        if not req:
            continue
        min_depth = str(req.get("min_depth") or "precon_drill")
        has_drill = any(
            str(x.get("discover_fixture_id")) == fid
            and _depth_rank(str(x.get("depth_level"))) >= _depth_rank(min_depth)
            for x in logs
        )
        if not has_drill and not _gap_covers(gaps, cluster_id=cid, fixture_id=fid):
            errors.append(
                f"precon_clusters {cid}: fixture {fid} ({kind}) needs "
                f"exploration_log depth>={min_depth} (discover probe_executed)"
            )
        for view in req.get("required_views") or []:
            if not isinstance(view, dict):
                continue
            vid = view.get("view_id")
            vsurf = str(view.get("surface") or "").lower()
            if not vid:
                continue
            if fe_waived and vsurf in ("dxtrade5", "webbroker"):
                continue
            if fe_sessions.get(vsurf) in FE_UI_SHALLOW and vsurf in ("dxtrade5", "webbroker"):
                continue
            has_view = any(
                str(x.get("view_id")) == str(vid)
                and str(x.get("surface") or "").lower() == vsurf
                and _depth_rank(str(x.get("depth_level"))) >= _depth_rank("precon_drill")
                for x in logs
            )
            if not has_view and not _gap_covers(
                gaps, cluster_id=cid, fixture_id=fid, view_id=str(vid), surface=vsurf
            ):
                errors.append(
                    f"precon_clusters {cid}: missing precon_drill view_id={vid!r} "
                    f"surface={vsurf} for fixture {fid}"
                )

    if discover and not fe_waived:
        needs_show = False
        cluster_fids = {str(x) for x in (cluster.get("satisfies_fixture_ids") or [])}
        for fix in fixtures_by_id.values():
            fid_str = str(fix.get("id") or "")
            if fid_str not in cluster_fids:
                continue
            notes = str(fix.get("notes") or "")
            if INSTRUMENT_ID_RE.search(notes):
                needs_show = True
                break
        if needs_show:
            console_logs = [
                x for x in logs if str(x.get("surface") or "").lower() == "console"
            ]
            has_show = any(
                SHOW_IN_ACTION_RE.search(str(x.get("action") or ""))
                or any(
                    SHOW_IN_ACTION_RE.search(str(c))
                    for c in (x.get("commands_seen") or [])
                )
                for x in console_logs
            )
            if not has_show and not _gap_covers(gaps, cluster_id=cid, surface="console"):
                errors.append(
                    f"precon_clusters {cid}: discover notes have account/instrument ids "
                    "but no console exploration_log with show commands"
                )


def _check_jira_hygiene(label: str, text: str) -> list[str]:
    errors: list[str] = []
    if HARNESS_TOKEN_RE.search(text):
        errors.append(f"jira hygiene ({label}): harness/pipeline vocabulary")
    if PROBE_ACCOUNT_RE.search(text):
        errors.append(f"jira hygiene ({label}): probe account name (antonfx)")
    if TB_REF_RE.search(text):
        errors.append(f"jira hygiene ({label}): test bundle id reference (tb-NNN)")
    if ACCOUNT_ID_LITERAL_RE.search(text):
        errors.append(f"jira hygiene ({label}): literal account_id=<digits>")
    if LONG_NUMERIC_ID_RE.search(text):
        errors.append(f"jira hygiene ({label}): long numeric id (8+ digits)")
    return errors


def verify(
    coverage: dict[str, Any],
    precon: dict[str, Any],
    *,
    discover: dict[str, Any] | None = None,
    md_path: Path | None = None,
) -> list[str]:
    errors: list[str] = []
    warnings: list[str] = []

    primary_ids = _primary_check_ids(coverage)
    if not primary_ids:
        errors.append("coverage: no primary checks[] rows found")

    excluded: set[str] = set()
    for row in precon.get("excluded_checks_with_reason") or []:
        if isinstance(row, dict) and row.get("check_id"):
            excluded.add(str(row["check_id"]))

    skeleton = precon.get("test_skeleton") or []
    if not isinstance(skeleton, list):
        errors.append("test_skeleton must be an array")
        skeleton = []

    covered: set[str] = set()
    for row in skeleton:
        if not isinstance(row, dict):
            continue
        for cid in row.get("covers_check_ids") or []:
            covered.add(str(cid))

    for cid in primary_ids:
        if cid in excluded:
            continue
        if cid not in covered:
            errors.append(
                f"traceability: primary check {cid} not in test_skeleton "
                "or excluded_checks_with_reason"
            )

    schema_v = int(precon.get("schema_version") or 4)
    if schema_v >= 5 and str(precon.get("precon_status")) == "complete":
        ph = precon.get("session_placeholders")
        if not isinstance(ph, dict) or not ph:
            errors.append("schema v5: session_placeholders must be non-empty object")
        cp = precon.get("command_patterns")
        if not isinstance(cp, dict) or not cp.get("ladder_step"):
            errors.append("schema v5: command_patterns.ladder_step required")
        outline_by_chk: dict[str, int] = {}
        for row in skeleton:
            if not isinstance(row, dict):
                continue
            bid = row.get("bundle_id") or "?"
            covers = [str(c) for c in (row.get("covers_check_ids") or [])]
            outlines = row.get("case_outline") or []
            if not isinstance(outlines, list):
                errors.append(f"test_skeleton {bid}: case_outline must be array")
                continue
            for item in outlines:
                if not isinstance(item, dict):
                    continue
                chk = str(item.get("check_id") or "")
                if chk and chk not in covers:
                    errors.append(
                        f"test_skeleton {bid}: case_outline check_id {chk!r} "
                        f"not in covers_check_ids"
                    )
                for field in ("case_id", "title", "intent"):
                    if not item.get(field):
                        errors.append(
                            f"test_skeleton {bid}: case_outline missing {field}"
                        )
                if chk:
                    outline_by_chk[chk] = outline_by_chk.get(chk, 0) + 1
            for chk in covers:
                if chk in excluded:
                    continue
                if outline_by_chk.get(chk, 0) < 1:
                    errors.append(
                        f"test_skeleton {bid}: no case_outline row for check {chk}"
                    )

    clusters = precon.get("precon_clusters") or []
    if not isinstance(clusters, list) or not clusters:
        errors.append("precon_clusters must be a non-empty array")

    fe_sessions = precon.get("fe_ui_sessions") or {}
    if not isinstance(fe_sessions, dict):
        fe_sessions = {}
    fe_waived = bool((precon.get("sources") or {}).get("fe_exploration_waived"))
    ladder = _load_ladder()
    precon_status = str(precon.get("precon_status") or "complete")

    cluster_ids = set()
    for cluster in clusters:
        if not isinstance(cluster, dict):
            continue
        cid = cluster.get("id")
        if not cid:
            errors.append("precon_clusters row missing id")
            continue
        cluster_ids.add(str(cid))
        steps = cluster.get("steps") or []
        if not isinstance(steps, list) or not steps:
            errors.append(f"precon_clusters {cid}: steps[] must be non-empty")
            continue
        orders: list[int] = []
        for step in steps:
            if not isinstance(step, dict):
                continue
            order = step.get("order")
            body = step.get("body")
            if order is None:
                errors.append(f"precon_clusters {cid}: step missing order")
            else:
                orders.append(int(order))
            if not body or not str(body).strip():
                errors.append(f"precon_clusters {cid}: step order {order} missing body")
            else:
                errors.extend(_check_jira_hygiene(f"{cid} step {order} body", str(body)))
            for field in ("code_examples", "branch_notes"):
                for i, item in enumerate(step.get(field) or []):
                    errors.extend(
                        _check_jira_hygiene(
                            f"{cid} step {order} {field}[{i}]", str(item)
                        )
                    )
        if orders:
            expected = list(range(1, len(orders) + 1))
            if sorted(orders) != expected:
                errors.append(
                    f"precon_clusters {cid}: step order must be 1..N contiguous "
                    f"(got {sorted(orders)})"
                )

        for i, log in enumerate(cluster.get("exploration_log") or []):
            if not isinstance(log, dict):
                continue
            surface = str(log.get("surface") or "").lower()
            outcome = str(log.get("outcome") or "").lower()
            login_state = log.get("login_state")
            if surface in FE_CHROME_SURFACES and outcome == "pass":
                if fe_waived:
                    if login_state not in ("shell_only", "authenticated", None):
                        errors.append(
                            f"precon_clusters {cid} exploration_log[{i}]: "
                            "fe_exploration_waived but unexpected login_state"
                        )
                elif login_state != "authenticated":
                    errors.append(
                        f"precon_clusters {cid} exploration_log[{i}]: "
                        f"outcome pass on {surface!r} requires login_state authenticated "
                        f"(got {login_state!r})"
                    )

        if discover is not None or ladder:
            _verify_cluster_exploration_depth(
                cluster,
                discover=discover,
                fe_waived=fe_waived,
                fe_sessions=fe_sessions,
                ladder=ladder,
                precon=precon,
                errors=errors,
            )

        wb_session = fe_sessions.get("webbroker")
        if wb_session in FE_UI_SHALLOW:
            for step in steps:
                if not isinstance(step, dict):
                    continue
                body = str(step.get("body") or "")
                if step.get("surface") == "webbroker" and POST_LOGIN_WB_BODY_RE.search(body):
                    if "[TBD]" not in body.upper():
                        errors.append(
                            f"precon_clusters {cid}: webbroker step describes post-login UI "
                            f"but fe_ui_sessions.webbroker={wb_session!r} (use [TBD])"
                        )

        dx_session = fe_sessions.get("dxtrade5")
        if dx_session in FE_UI_SHALLOW:
            for step in steps:
                if not isinstance(step, dict):
                    continue
                body = str(step.get("body") or "")
                if step.get("surface") == "dxtrade5" and POST_LOGIN_DX_BODY_RE.search(body):
                    if "[TBD]" not in body.upper():
                        errors.append(
                            f"precon_clusters {cid}: dxtrade5 step describes post-login UI "
                            f"but fe_ui_sessions.dxtrade5={dx_session!r} (use [TBD])"
                        )

    skeleton_surfaces: set[str] = set()
    for row in skeleton:
        if isinstance(row, dict):
            for s in row.get("surfaces") or []:
                skeleton_surfaces.add(str(s).lower())

    if "dxtrade5" in skeleton_surfaces and not fe_waived:
        has_dx_log = False
        for cluster in clusters:
            if not isinstance(cluster, dict):
                continue
            for log in cluster.get("exploration_log") or []:
                if not isinstance(log, dict):
                    continue
                if str(log.get("surface")).lower() in ("dxtrade5", "chrome"):
                    has_dx_log = True
        if not has_dx_log and fe_sessions.get("dxtrade5") not in FE_UI_AUTHENTICATED_OK:
            warnings.append(
                "test_skeleton includes dxtrade5 but no chrome/dxtrade5 exploration_log "
                "(and fe_ui_sessions.dxtrade5 not authenticated)"
            )

    for row in skeleton:
        if not isinstance(row, dict):
            continue
        pcid = row.get("precon_cluster_id")
        if pcid and str(pcid) not in cluster_ids:
            errors.append(
                f"test_skeleton {row.get('bundle_id')}: precon_cluster_id {pcid!r} "
                "not found in precon_clusters"
            )

    if discover:
        fixture_ids = {
            str(r["id"])
            for r in (discover.get("fixture_needs") or [])
            if isinstance(r, dict) and r.get("id")
        }
        for cluster in clusters:
            if not isinstance(cluster, dict):
                continue
            for fid in cluster.get("satisfies_fixture_ids") or []:
                if str(fid) not in fixture_ids:
                    warnings.append(
                        f"precon_clusters {cluster.get('id')}: satisfies_fixture_ids "
                        f"{fid} not in discover fixture_needs"
                    )

    ladder_only = all(
        isinstance(r, dict) and r.get("ladder_in_test") is True for r in skeleton
    )
    if skeleton and ladder_only and clusters:
        errors.append(
            "test_skeleton: all bundles have ladder_in_test true but precon_clusters "
            "exist — need at least one env/config bundle"
        )

    for path, s in _walk_strings(precon):
        if TEMP_PATH_RE.search(s):
            errors.append(f"schema hygiene: /temp/ path in {path}")
        if PASSWORDISH_RE.search(s):
            errors.append(f"schema hygiene: possible secret in {path}")

    if precon_status == "complete" and precon.get("precon_verify_passed") is True:
        gaps = precon.get("exploration_gaps") or []
        if isinstance(gaps, list) and len(gaps) > 0:
            errors.append(
                "precon_status complete but exploration_gaps non-empty — "
                "set precon_status incomplete or resolve gaps"
            )

    if md_path and md_path.is_file():
        md_text = md_path.read_text(encoding="utf-8")
        errors.extend(_check_jira_hygiene("precon.md", md_text))
        if MD_PREAMBLE_RE.search(md_text):
            errors.append("jira hygiene (precon.md): operator/preamble text")
        if MD_FOOTER_RE.search(md_text):
            errors.append("jira hygiene (precon.md): bundle/ladder footer")

    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)

    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify TEST-PRECON artefact.")
    ap.add_argument("--coverage", type=Path, required=True)
    ap.add_argument("--precon", type=Path, required=True)
    ap.add_argument("--discover", type=Path, default=None)
    ap.add_argument("--md", type=Path, default=None, help="Optional -precon.md Jira paste file")
    args = ap.parse_args()

    coverage = _load_json(args.coverage.resolve())
    precon = _load_json(args.precon.resolve())
    discover = _load_json(args.discover.resolve()) if args.discover else None
    md_path = args.md.resolve() if args.md else None

    if coverage is None:
        print(f"cannot read coverage: {args.coverage}", file=sys.stderr)
        return 2
    if precon is None:
        print(f"cannot read precon: {args.precon}", file=sys.stderr)
        return 2

    errors = verify(coverage, precon, discover=discover, md_path=md_path)
    if errors:
        print("precon_verify failures:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    n_chk = len(_primary_check_ids(coverage))
    n_bundles = len(precon.get("test_skeleton") or [])
    print(f"OK precon ({n_bundles} skeleton bundles, {n_chk} primary checks) — {args.precon}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
