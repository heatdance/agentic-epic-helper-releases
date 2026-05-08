#!/usr/bin/env python3
"""
Compare benchmark snapshots for one epic.

Discovery modes:
- Legacy dirs: <benchmark-root>/run-*/ (meta.json + epic-ref / coverage snapshots).
- Coverage-bench suite: <benchmark-root>/runs/run-<suite_id>/attempts/<EPIC>/run-*.json
  (--suite-id + default benchmark-root).

Hub suite (shadow + optional _machine wrappers):
  --suite-run-dir <path/to/.cursor/benchmark/runs/<suite_id>>
  Per attempt-<nn>/, prefers **_machine**/attempts/<EPIC>/run-*.json** with matching **phase**.
  If none exist for that attempt, falls back to **shadow** snapshots:
    - prep: shadow/<EPIC>/<EPIC>-ref.json**
    - coverage: shadow/<EPIC>/<EPIC>-coverage.json** (+ sibling **-coverage.md** for bullets)
    - test: shadow/<EPIC>/<EPIC>-tests.json**
  Metrics payload records **discovery_source**: **hub_machine** | **hub_shadow_fallback** | **mixed**.
  Writes under:
    <suite-run-dir>/_aggregate/crossref/
  Append-only KPI history defaults to **global**:
    <suite-run-dir>/../../history/  (= .cursor/benchmark/history/)
  unless using legacy benchmark-root-only mode (history under benchmark-root/history/).

Gold JSON is resolved from (first hit): explicit --gold-root, then canonical
.cursor/benchmark/data/, then legacy coverage-bench/data/.

Malformed JSON files are still listed so load errors surface.
Stdlib only.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import re
from pathlib import Path
from typing import Any


METRICS_SCHEMA_VERSION = 4
SCRIPT_VERSION = "p2-sanitization-softfail-v1"
TREND_WINDOW = 5
SANITIZATION_DEFAULTS = {
    "enabled": True,
    "forbidden_regex": [
        r"(?i)\b(api[_-]?key|token|secret|password)\s*[:=]\s*\S+",
        r"(?i)\bbearer\s+[a-z0-9._-]{8,}",
    ],
    "forbidden_substrings": [
        "jira.in.devexperts.com",
        "confluence.in.devexperts.com",
        "stash.in.devexperts.com",
        "devexperts.slack.com",
    ],
    "allowed_exceptions": [],
    "scan_targets": {
        "prep": ["client_shell_impact"],
        "coverage": ["checklist_markdown"],
    },
}


def _norm_ws(s: str) -> str:
    return " ".join(s.split())


def _sha256_norm(s: str) -> str:
    return hashlib.sha256(_norm_ws(s).encode("utf-8")).hexdigest()


def _load_json(p: Path) -> Any:
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sanitize_excerpt(text: str, start: int, end: int, window: int = 24) -> str:
    lo = max(0, start - window)
    hi = min(len(text), end + window)
    snippet = text[lo:hi]
    snippet = _norm_ws(snippet)
    # Keep context but avoid leaking long token-like sequences.
    snippet = re.sub(r"[A-Za-z0-9._%+-]{12,}", "***", snippet)
    return snippet


def _discover_legacy(benchmark_root: Path, epic_key: str) -> list[tuple[str, Path]]:
    """Legacy: run-* dirs with meta.json + epic_key."""
    out: list[tuple[str, Path]] = []
    for d in sorted(benchmark_root.glob("run-*")):
        if not d.is_dir():
            continue
        if (d / "queue.json").is_file():
            continue
        meta = d / "meta.json"
        if not meta.is_file():
            continue
        try:
            m = _load_json(meta)
        except (json.JSONDecodeError, OSError):
            continue
        mk = m.get("epic_key")
        if not isinstance(mk, str) or mk.strip().upper() != epic_key:
            continue
        out.append((d.name, d))
    return out


def _hub_machine_runs_for_phase(
    attempt_dir: Path,
    epic_key: str,
    phase: str,
) -> list[tuple[str, Path]]:
    """Valid run-*.json under attempt/_machine/attempts/<EPIC>/ filtered by wrap.phase."""
    machine = attempt_dir / "_machine" / "attempts" / epic_key
    if not machine.is_dir():
        return []
    out: list[tuple[str, Path]] = []
    for p in sorted(machine.glob("run-*.json")):
        if not p.is_file():
            continue
        label = f"{attempt_dir.name}__{p.stem}"
        try:
            wrap = _load_json(p)
        except (json.JSONDecodeError, OSError):
            out.append((label, p))
            continue
        if wrap.get("phase") != phase:
            continue
        out.append((label, p))
    return out


def _hub_shadow_snapshot_path(
    attempt_dir: Path,
    epic_key: str,
    phase: str,
) -> tuple[str, Path] | None:
    """Single shadow JSON per attempt when _machine wrappers are absent."""
    shadow_epic = attempt_dir / "shadow" / epic_key
    if phase == "prep":
        p = shadow_epic / f"{epic_key}-ref.json"
        if p.is_file():
            return (f"{attempt_dir.name}__shadow-prep", p)
    elif phase == "coverage":
        p = shadow_epic / f"{epic_key}-coverage.json"
        if p.is_file():
            return (f"{attempt_dir.name}__shadow-coverage", p)
    elif phase == "test":
        p = shadow_epic / f"{epic_key}-tests.json"
        if p.is_file():
            return (f"{attempt_dir.name}__shadow-test", p)
    return None


def _discover_suite_hub(
    suite_run_dir: Path,
    epic_key: str,
    phase: str,
) -> tuple[list[tuple[str, Path]], str]:
    """Hub: prefer _machine run-*.json per attempt; else shadow snapshot for that phase.

    Returns ``(run_dirs, discovery_source)`` where discovery_source is
    ``hub_machine``, ``hub_shadow_fallback``, ``mixed``, or ``none`` (caller
    treats empty list + none as failure).
    """
    out: list[tuple[str, Path]] = []
    per_attempt_sources: list[str] = []
    for attempt_dir in sorted(suite_run_dir.glob("attempt-*")):
        if not attempt_dir.is_dir():
            continue
        machine_runs = _hub_machine_runs_for_phase(attempt_dir, epic_key, phase)
        if machine_runs:
            out.extend(machine_runs)
            per_attempt_sources.append("machine")
        else:
            sh = _hub_shadow_snapshot_path(attempt_dir, epic_key, phase)
            if sh:
                out.append(sh)
                per_attempt_sources.append("shadow")
    if not out:
        return [], "none"
    if all(s == "machine" for s in per_attempt_sources):
        return out, "hub_machine"
    if all(s == "shadow" for s in per_attempt_sources):
        return out, "hub_shadow_fallback"
    return out, "mixed"


def _discover_suite(
    benchmark_root: Path,
    epic_key: str,
    suite_id: str,
    phase: str,
) -> list[tuple[str, Path]]:
    """Suite: runs/run-<suite_id>/attempts/<EPIC>/run-*.json.

    Includes:
      - files with matching `phase`
      - malformed files (to surface parse errors)

    Excludes:
      - valid files with non-matching phase (prevents phase-noise metrics)
    """
    attempts = benchmark_root / "runs" / f"run-{suite_id}" / "attempts" / epic_key
    if not attempts.is_dir():
        return []
    out: list[tuple[str, Path]] = []
    for p in sorted(attempts.glob("run-*.json")):
        if not p.is_file():
            continue
        try:
            wrap = _load_json(p)
        except (json.JSONDecodeError, OSError):
            out.append((p.stem, p))
            continue
        if wrap.get("phase") != phase:
            continue
        out.append((p.stem, p))
    return out


def _extract_bullets_from_md(text: str) -> list[str]:
    lines = text.splitlines()
    bullets: list[str] = []
    for line in lines:
        m = re.match(r"^\s*-\s+(.+)$", line)
        if m:
            bullets.append(_norm_ws(m.group(1).lower()))
    return bullets


def _is_diagnostic_bullet(normalized_bullet: str) -> bool:
    signal_patterns = (
        "snippet_text missing",
        "mcp_export_failed",
        "yogi_extract_empty",
        "no_cookie",
        "bitbucket_search_unavailable",
        "search unavailable",
        "http 404",
    )
    if normalized_bullet.startswith("! reason:"):
        return True
    return any(p in normalized_bullet for p in signal_patterns)


def _split_core_and_diagnostic_bullets(
    normalized_bullets: list[str],
) -> tuple[set[str], set[str]]:
    core: set[str] = set()
    diagnostic: set[str] = set()
    for b in normalized_bullets:
        if _is_diagnostic_bullet(b):
            diagnostic.add(b)
        else:
            core.add(b)
    return core, diagnostic


def _pairwise_jaccard(sets_by_name: dict[str, set[str]]) -> dict[str, dict[str, float]]:
    names = sorted(sets_by_name.keys())
    pairwise: dict[str, dict[str, float]] = {}
    for i, a in enumerate(names):
        pairwise[a] = {}
        sa = sets_by_name.get(a, set())
        for b in names[i + 1 :]:
            sb = sets_by_name.get(b, set())
            inter = sa & sb
            union = sa | sb
            j = len(inter) / len(union) if union else 1.0
            pairwise[a][b] = round(j, 4)
            if b not in pairwise:
                pairwise[b] = {}
            pairwise[b][a] = round(j, 4)
    return pairwise


def _jaccard_average(pairwise: dict[str, dict[str, float]]) -> float | None:
    vals: list[float] = []
    for _, peers in pairwise.items():
        for _, v in peers.items():
            vals.append(v)
    if not vals:
        return None
    return round(sum(vals) / len(vals), 4)


def _primary_focus_verbatim_pass(data: dict[str, Any]) -> bool | None:
    focus = data.get("epic_verification_focus") or {}
    statement = focus.get("statement")
    md = data.get("smart_checklist_markdown")
    if not isinstance(statement, str) or not statement.strip():
        return None
    if not isinstance(md, str) or not md.strip():
        return None

    lines = md.splitlines()
    normalized_statement = _norm_ws(statement).lower()

    first_substantive_h2: str | None = None
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s.startswith("## "):
            first_substantive_h2 = _norm_ws(s[3:])
            break
    if first_substantive_h2 is None:
        return False

    if first_substantive_h2.lower() == normalized_statement:
        return True

    if first_substantive_h2.lower() != "primary focus":
        return False

    # Expect the first bullet under "## Primary focus" to copy statement verbatim.
    in_primary_focus = False
    for line in lines:
        s = line.strip()
        if s.startswith("## "):
            in_primary_focus = _norm_ws(s[3:]).lower() == "primary focus"
            continue
        if not in_primary_focus:
            continue
        m = re.match(r"^\s*-\s+(.+)$", line)
        if m:
            return _norm_ws(m.group(1)).lower() == normalized_statement
    return False


def _prep_metrics(run_dirs: list[tuple[str, Path]]) -> dict[str, Any]:
    per_run: dict[str, Any] = {}
    included_runs: list[str] = []

    for name, d in run_dirs:
        if d.is_file() and d.suffix == ".json":
            try:
                wrap = _load_json(d)
            except (json.JSONDecodeError, OSError) as e:
                per_run[name] = {"error": str(e)}
                included_runs.append(name)
                continue

            # Guard against phase-noise if mixed input slipped through.
            if isinstance(wrap, dict) and wrap.get("phase") not in (None, "prep"):
                continue

            data = wrap.get("artifact") if isinstance(wrap, dict) else None
            if not isinstance(data, dict) and isinstance(wrap, dict):
                if isinstance(wrap.get("requirements"), list):
                    data = wrap
            if not isinstance(data, dict):
                per_run[name] = {"error": "missing artifact"}
                included_runs.append(name)
                continue
        else:
            snap = d / "epic-ref.snapshot.json"
            if not snap.is_file():
                per_run[name] = {"error": "missing epic-ref.snapshot.json"}
                included_runs.append(name)
                continue
            try:
                data = _load_json(snap)
            except (json.JSONDecodeError, OSError) as e:
                per_run[name] = {"error": str(e)}
                included_runs.append(name)
                continue

        reqs = data.get("requirements") or []
        keys_snippets: dict[str, str | None] = {}
        for r in reqs:
            if not isinstance(r, dict):
                continue
            k = r.get("key")
            if not isinstance(k, str) or not k.strip():
                continue
            st = r.get("snippet_text")
            keys_snippets[k] = st if isinstance(st, str) and st.strip() else None

        requirement_keys = sorted(keys_snippets.keys())
        missing_keys = sorted([k for k, v in keys_snippets.items() if v is None])
        total = len(requirement_keys)
        present = total - len(missing_keys)
        completion_rate = round(present / total, 4) if total else None

        per_run[name] = {
            "requirement_keys": requirement_keys,
            "requirement_count": total,
            "snippet_present_count": present,
            "snippet_missing_count": len(missing_keys),
            "snippet_missing_keys": missing_keys,
            "snippet_completion_rate": completion_rate,
            "snippet_sha256": {
                k: _sha256_norm(v) if v else None for k, v in keys_snippets.items()
            },
            "client_shell_impact": data.get("client_shell_impact"),
        }
        included_runs.append(name)

    successful = [n for n in included_runs if "error" not in per_run.get(n, {})]
    if successful:
        inter: set[str] | None = None
        for n in successful:
            ks = set(per_run[n].get("snippet_sha256", {}).keys())
            inter = ks if inter is None else inter & ks
        key_intersection = sorted(inter) if inter is not None else []
    else:
        key_intersection = []

    snippet_hash_agreement: dict[str, str] = {}
    unstable_keys: list[str] = []
    if successful:
        for k in sorted(key_intersection):
            hashes: list[str] = []
            for n in successful:
                hmap = per_run[n].get("snippet_sha256") or {}
                h = hmap.get(k)
                if h is None:
                    hashes = []
                    break
                hashes.append(h)
            if not hashes:
                continue
            if len(set(hashes)) == 1:
                snippet_hash_agreement[k] = hashes[0]

        all_keys: set[str] = set()
        for n in successful:
            all_keys |= set((per_run[n].get("snippet_sha256") or {}).keys())
        for k in sorted(all_keys):
            row_hashes = []
            for n in successful:
                h = (per_run[n].get("snippet_sha256") or {}).get(k)
                if h is not None:
                    row_hashes.append(h)
            if len(row_hashes) >= 2 and len(set(row_hashes)) > 1:
                unstable_keys.append(k)

    impacts = [
        json.dumps(per_run[n]["client_shell_impact"], sort_keys=True)
        for n in successful
        if "client_shell_impact" in per_run[n]
    ]
    client_shell_impact_drift = len(set(impacts)) > 1 if impacts else False

    completion_rates = {
        n: per_run[n].get("snippet_completion_rate")
        for n in successful
        if per_run[n].get("snippet_completion_rate") is not None
    }
    avg_completion_rate = (
        round(sum(completion_rates.values()) / len(completion_rates), 4)
        if completion_rates
        else None
    )
    missing_keys_by_run = {
        n: per_run[n].get("snippet_missing_keys", []) for n in successful
    }

    return {
        "schema_version": METRICS_SCHEMA_VERSION,
        "runs": included_runs,
        "per_run": per_run,
        "key_intersection_all_runs": key_intersection,
        "snippet_hash_stable_across_all_runs": snippet_hash_agreement,
        "unstable_keys": unstable_keys,
        "client_shell_impact_drift": client_shell_impact_drift,
        "kpis": {
            "snippet_completion_rate_by_run": completion_rates,
            "snippet_completion_rate_avg": avg_completion_rate,
            "snippet_missing_keys_by_run": missing_keys_by_run,
            "client_shell_impact_drift": client_shell_impact_drift,
        },
    }


def _coverage_metrics(run_dirs: list[tuple[str, Path]]) -> dict[str, Any]:
    per_run: dict[str, Any] = {}
    included_runs: list[str] = []
    all_bullets: dict[str, set[str]] = {}
    core_bullets: dict[str, set[str]] = {}
    diagnostic_bullets: dict[str, set[str]] = {}
    checklist_text_by_run: dict[str, str] = {}

    for name, d in run_dirs:
        if d.is_file() and d.suffix == ".json":
            try:
                wrap = _load_json(d)
            except (json.JSONDecodeError, OSError) as e:
                per_run[name] = {"error": str(e)}
                included_runs.append(name)
                continue

            # Guard against phase-noise if mixed input slipped through.
            if isinstance(wrap, dict) and wrap.get("phase") not in (None, "coverage"):
                continue

            data = wrap.get("artifact") if isinstance(wrap, dict) else None
            if not isinstance(data, dict) and isinstance(wrap, dict):
                if isinstance(wrap.get("coverage_matrix"), list):
                    data = wrap
            if not isinstance(data, dict):
                per_run[name] = {"error": "missing artifact"}
                included_runs.append(name)
                continue

            md = data.get("smart_checklist_markdown")
            if not (isinstance(md, str) and md.strip()):
                cm = wrap.get("checklist_markdown") if isinstance(wrap, dict) else None
                md = cm if isinstance(cm, str) and cm.strip() else ""
            if not (isinstance(md, str) and md.strip()) and d.is_file() and d.name.endswith(
                "-coverage.json"
            ):
                md_side = d.with_name(d.name.replace("-coverage.json", "-coverage.md"))
                if md_side.is_file():
                    try:
                        md = md_side.read_text(encoding="utf-8")
                    except OSError:
                        md = ""
        else:
            js = d / "coverage.snapshot.json"
            md_path = d / "coverage.snapshot.md"
            if not js.is_file():
                per_run[name] = {"error": "missing coverage.snapshot.json"}
                included_runs.append(name)
                continue
            try:
                data = _load_json(js)
            except (json.JSONDecodeError, OSError) as e:
                per_run[name] = {"error": str(e)}
                included_runs.append(name)
                continue

            md = data.get("smart_checklist_markdown")
            if not (isinstance(md, str) and md.strip()) and md_path.is_file():
                try:
                    md = md_path.read_text(encoding="utf-8")
                except OSError:
                    md = ""

        md_text = md if isinstance(md, str) else ""
        checklist_text_by_run[name] = md_text
        bullets = _extract_bullets_from_md(md_text)
        all_set = set(bullets)
        core_set, diagnostic_set = _split_core_and_diagnostic_bullets(bullets)

        primary_focus_pass = _primary_focus_verbatim_pass(data)

        per_run[name] = {
            "bullet_count": len(all_set),
            "core_bullet_count": len(core_set),
            "diagnostic_bullet_count": len(diagnostic_set),
            "matrix_rows": [
                {"id": row.get("id"), "verification_role": row.get("verification_role")}
                for row in (data.get("coverage_matrix") or [])
                if isinstance(row, dict)
            ],
            "primary_focus_verbatim_pass": primary_focus_pass,
        }
        all_bullets[name] = all_set
        core_bullets[name] = core_set
        diagnostic_bullets[name] = diagnostic_set
        included_runs.append(name)

    names = [n for n in included_runs if "error" not in per_run.get(n, {})]

    pairwise_jaccard = _pairwise_jaccard({n: all_bullets.get(n, set()) for n in names})
    core_pairwise_jaccard = _pairwise_jaccard(
        {n: core_bullets.get(n, set()) for n in names}
    )

    freq: dict[str, int] = {}
    core_freq: dict[str, int] = {}
    diagnostic_freq: dict[str, int] = {}
    n_success = len(names)
    for n in names:
        for b in all_bullets.get(n, set()):
            freq[b] = freq.get(b, 0) + 1
        for b in core_bullets.get(n, set()):
            core_freq[b] = core_freq.get(b, 0) + 1
        for b in diagnostic_bullets.get(n, set()):
            diagnostic_freq[b] = diagnostic_freq.get(b, 0) + 1

    strong = sorted([b for b, c in freq.items() if n_success and c == n_success])
    weak = sorted([b for b, c in freq.items() if 0 < c < n_success])
    core_strong = sorted([b for b, c in core_freq.items() if n_success and c == n_success])
    core_weak = sorted([b for b, c in core_freq.items() if 0 < c < n_success])

    pair_sets: list[set[tuple[Any, Any]]] = []
    matrix_roles_by_id: dict[str, set[str]] = {}
    for n in names:
        rows = per_run[n].get("matrix_rows") or []
        pair_set = {(r.get("id"), r.get("verification_role")) for r in rows}
        pair_sets.append(pair_set)
        for r in rows:
            rid = r.get("id")
            role = r.get("verification_role")
            if isinstance(rid, str):
                role_set = matrix_roles_by_id.setdefault(rid, set())
                if isinstance(role, str):
                    role_set.add(role)

    matrix_intersection: list[list[Any]] = []
    if pair_sets:
        mi = set.intersection(*pair_sets)
        matrix_intersection = [
            list(x) for x in sorted(mi, key=lambda x: (str(x[0]), str(x[1])))
        ]

    matrix_role_flip_count = sum(1 for _, roles in matrix_roles_by_id.items() if len(roles) > 1)

    diagnostic_bullet_count_by_run = {
        n: per_run[n].get("diagnostic_bullet_count", 0) for n in names
    }
    primary_focus_flags = {
        n: per_run[n].get("primary_focus_verbatim_pass")
        for n in names
        if per_run[n].get("primary_focus_verbatim_pass") is not None
    }
    primary_focus_verbatim_pass_rate = (
        round(
            sum(1 for _, ok in primary_focus_flags.items() if ok)
            / len(primary_focus_flags),
            4,
        )
        if primary_focus_flags
        else None
    )

    return {
        "schema_version": METRICS_SCHEMA_VERSION,
        "runs": included_runs,
        "per_run": per_run,
        "pairwise_jaccard": pairwise_jaccard,
        "core_pairwise_jaccard": core_pairwise_jaccard,
        "bullet_frequency": freq,
        "core_bullet_frequency": core_freq,
        "diagnostic_bullet_frequency": diagnostic_freq,
        "strong_bullets_all_runs": strong,
        "weak_bullets": weak,
        "core_strong_bullets_all_runs": core_strong,
        "core_weak_bullets": core_weak,
        "matrix_intersection": matrix_intersection,
        "kpis": {
            "core_bullet_jaccard_avg": _jaccard_average(core_pairwise_jaccard),
            "diagnostic_bullet_count_by_run": diagnostic_bullet_count_by_run,
            "matrix_role_flip_count": matrix_role_flip_count,
            "primary_focus_verbatim_pass_rate": primary_focus_verbatim_pass_rate,
        },
        "_checklist_text_by_run": checklist_text_by_run,
    }


def _test_metrics(run_dirs: list[tuple[str, Path]]) -> dict[str, Any]:
    """Structural metrics over TEST-PREP shadow/mirror `-tests.json` artifacts."""
    per_run: dict[str, Any] = {}
    included_runs: list[str] = []

    for name, d in run_dirs:
        if not d.is_file() or d.suffix != ".json":
            per_run[name] = {"error": "expected JSON file"}
            included_runs.append(name)
            continue
        try:
            wrap = _load_json(d)
        except (json.JSONDecodeError, OSError) as e:
            per_run[name] = {"error": str(e)}
            included_runs.append(name)
            continue
        if isinstance(wrap, dict) and wrap.get("phase") not in (None, "test"):
            continue

        data = wrap.get("artifact") if isinstance(wrap, dict) else None
        if not isinstance(data, dict) and isinstance(wrap, dict):
            if isinstance(wrap.get("test_bundles"), list) or (
                isinstance(wrap.get("sources"), dict)
                and isinstance(wrap.get("epic_key"), str)
                and isinstance(wrap.get("schema_version"), (int, float))
            ):
                data = wrap
        if not isinstance(data, dict):
            per_run[name] = {"error": "missing test artifact shape"}
            included_runs.append(name)
            continue

        sources = data.get("sources") if isinstance(data.get("sources"), dict) else {}
        bundles = data.get("test_bundles") or []
        if not isinstance(bundles, list):
            bundles = []
        subprocess_total = sum(
            1
            for b in bundles
            if isinstance(b, dict)
            and isinstance((b.get("authoring") or {}), dict)
            and isinstance((b.get("authoring") or {}).get("subprocess"), bool)
            and (b.get("authoring") or {}).get("subprocess") is True
        )
        subprocess_completed = sum(
            1
            for b in bundles
            if isinstance(b, dict)
            and isinstance((b.get("authoring") or {}), dict)
            and (b.get("authoring") or {}).get("subprocess_completed") is True
        )
        rate = (
            round(subprocess_completed / subprocess_total, 4)
            if subprocess_total
            else None
        )

        dumped = ""
        temp_fragment = False
        try:
            dumped = json.dumps(data, ensure_ascii=False)
            temp_fragment = "/temp/" in dumped
        except (TypeError, ValueError):
            temp_fragment = True

        tests_md: Path | None = None
        if d.name.endswith("-tests.json"):
            tests_md = d.with_name(d.name.replace("-tests.json", "-tests.md"))
        tests_md_present = bool(tests_md and tests_md.is_file())

        per_run[name] = {
            "bundle_count": len(bundles),
            "subprocess_bundle_count": subprocess_total,
            "subprocess_completed_count": subprocess_completed,
            "subprocess_completed_rate": rate,
            "sources_map_only": sources.get("map_only"),
            "sources_coverage_loaded": sources.get("coverage_loaded"),
            "temp_path_fragment_in_json": temp_fragment,
            "tests_md_present": tests_md_present,
            "tests_md_path": str(tests_md.as_posix()) if tests_md else None,
        }
        included_runs.append(name)

    successful = [n for n in included_runs if "error" not in per_run.get(n, {})]
    temp_violations = sum(
        1 for n in successful if per_run.get(n, {}).get("temp_path_fragment_in_json")
    )
    md_missing = sum(1 for n in successful if not per_run.get(n, {}).get("tests_md_present"))

    rates = {
        n: per_run[n].get("subprocess_completed_rate")
        for n in successful
        if per_run[n].get("subprocess_completed_rate") is not None
    }
    avg_rate = round(sum(rates.values()) / len(rates), 4) if rates else None

    return {
        "schema_version": METRICS_SCHEMA_VERSION,
        "runs": included_runs,
        "per_run": per_run,
        "kpis": {
            "test_bundle_count_by_run": {
                n: per_run[n].get("bundle_count") for n in successful
            },
            "subprocess_completed_rate_by_run": rates,
            "subprocess_completed_rate_avg": avg_rate,
            "temp_path_fragment_violation_run_count": temp_violations,
            "tests_md_missing_run_count": md_missing,
        },
    }


def _gold_data_search_dirs(
    gold_root: Path | None,
    suite_run_dir: Path | None,
    benchmark_root: Path,
) -> list[Path]:
    """Directories that may contain ``<EPIC>-gold.json`` (search in order)."""
    seen: set[str] = set()
    ordered: list[Path] = []

    def push(p: Path) -> None:
        try:
            key = str(p.resolve())
        except OSError:
            key = str(p)
        if key not in seen:
            seen.add(key)
            ordered.append(p)

    if gold_root is not None:
        push(gold_root)
    if suite_run_dir is not None:
        push(suite_run_dir.parent.parent / "data")
    push(benchmark_root.parent / "data")
    push(benchmark_root / "data")
    return ordered


def _find_gold(epic_key: str, search_data_dirs: list[Path]) -> tuple[dict[str, Any] | None, Path | None]:
    for d in search_data_dirs:
        p = d / f"{epic_key}-gold.json"
        if not p.is_file():
            continue
        try:
            obj = _load_json(p)
        except (json.JSONDecodeError, OSError):
            continue
        if isinstance(obj, dict):
            return obj, p
    return None, None


def _gold_pipeline_applies(gold: dict[str, Any], kind: str) -> bool:
    """Whether gold file targets this metric kind."""
    p = gold.get("pipeline")
    if kind == "test":
        return p == "test"
    if p == "both":
        return kind in ("prep", "coverage")
    return p == kind


def _legacy_gold_checks_prep(
    gold: dict[str, Any], payload: dict[str, Any]
) -> dict[str, Any]:
    required_keys = gold.get("required_requirement_keys_in_snippets") or []
    required_keys = [k for k in required_keys if isinstance(k, str) and k.strip()]
    failures: list[dict[str, Any]] = []
    if required_keys:
        for run_name, row in payload.get("per_run", {}).items():
            if "error" in row:
                continue
            sha = row.get("snippet_sha256") or {}
            missing = [k for k in required_keys if sha.get(k) is None]
            if missing:
                failures.append({"run": run_name, "missing_keys": missing})

    return {
        "required_requirement_keys_in_snippets": {
            "configured_keys": required_keys,
            "pass": len(failures) == 0,
            "failures": failures,
        }
    }


def _legacy_gold_checks_coverage(
    gold: dict[str, Any], payload: dict[str, Any]
) -> dict[str, Any]:
    required_substrings = gold.get("required_smart_checklist_substrings") or []
    required_substrings = [
        s for s in required_substrings if isinstance(s, str) and s.strip()
    ]
    forbidden_regex = gold.get("forbidden_checklist_regex") or []
    forbidden_regex = [r for r in forbidden_regex if isinstance(r, str) and r.strip()]

    text_by_run = payload.get("_checklist_text_by_run", {})
    missing_substrings: list[dict[str, Any]] = []
    forbidden_hits: list[dict[str, Any]] = []

    for run_name, text in text_by_run.items():
        low = (text or "").lower()
        missing = [s for s in required_substrings if s.lower() not in low]
        if missing:
            missing_substrings.append({"run": run_name, "missing_substrings": missing})
        for pattern in forbidden_regex:
            try:
                if re.search(pattern, text or ""):
                    forbidden_hits.append({"run": run_name, "regex": pattern})
            except re.error:
                forbidden_hits.append(
                    {"run": run_name, "regex": pattern, "error": "invalid_regex"}
                )

    return {
        "required_smart_checklist_substrings": {
            "configured_substrings": required_substrings,
            "pass": len(missing_substrings) == 0,
            "failures": missing_substrings,
        },
        "forbidden_checklist_regex": {
            "configured_patterns": forbidden_regex,
            "pass": len(forbidden_hits) == 0,
            "failures": forbidden_hits,
        },
    }


def _structured_gold_checks_prep(
    gold: dict[str, Any], payload: dict[str, Any]
) -> dict[str, Any]:
    structured = (gold.get("structured_assertions") or {}).get("prep") or {}
    if not isinstance(structured, dict) or not structured:
        return {"status": "not_configured"}

    checks: dict[str, Any] = {}

    req_keys = structured.get("required_snippet_keys") or []
    req_keys = [k for k in req_keys if isinstance(k, str) and k.strip()]
    if req_keys:
        failures = []
        for run_name, row in payload.get("per_run", {}).items():
            if "error" in row:
                continue
            sha = row.get("snippet_sha256") or {}
            missing = [k for k in req_keys if sha.get(k) is None]
            if missing:
                failures.append({"run": run_name, "missing_keys": missing})
        checks["required_snippet_keys"] = {
            "configured_keys": req_keys,
            "pass": len(failures) == 0,
            "failures": failures,
        }

    min_completion = structured.get("min_snippet_completion_rate")
    if isinstance(min_completion, (int, float)):
        failures = []
        for run_name, row in payload.get("per_run", {}).items():
            if "error" in row:
                continue
            rate = row.get("snippet_completion_rate")
            if rate is None or rate < float(min_completion):
                failures.append({"run": run_name, "value": rate})
        checks["min_snippet_completion_rate"] = {
            "threshold": float(min_completion),
            "pass": len(failures) == 0,
            "failures": failures,
        }

    allowed_sources = structured.get("client_shell_source_in") or []
    allowed_sources = [
        s for s in allowed_sources if isinstance(s, str) and s.strip()
    ]
    if allowed_sources:
        failures = []
        for run_name, row in payload.get("per_run", {}).items():
            if "error" in row:
                continue
            impact = row.get("client_shell_impact") or {}
            src = impact.get("source") if isinstance(impact, dict) else None
            if src not in allowed_sources:
                failures.append({"run": run_name, "value": src})
        checks["client_shell_source_in"] = {
            "allowed_values": allowed_sources,
            "pass": len(failures) == 0,
            "failures": failures,
        }

    return checks if checks else {"status": "configured_but_empty"}


def _structured_gold_checks_coverage(
    gold: dict[str, Any], payload: dict[str, Any]
) -> dict[str, Any]:
    structured = (gold.get("structured_assertions") or {}).get("coverage") or {}
    if not isinstance(structured, dict) or not structured:
        return {"status": "not_configured"}

    checks: dict[str, Any] = {}

    matrix_roles = structured.get("required_matrix_roles") or []
    if isinstance(matrix_roles, list) and matrix_roles:
        expected_pairs = []
        for row in matrix_roles:
            if (
                isinstance(row, dict)
                and isinstance(row.get("id"), str)
                and isinstance(row.get("verification_role"), str)
            ):
                expected_pairs.append((row["id"], row["verification_role"]))
        failures = []
        for run_name, row in payload.get("per_run", {}).items():
            if "error" in row:
                continue
            pairs = {
                (x.get("id"), x.get("verification_role"))
                for x in (row.get("matrix_rows") or [])
                if isinstance(x, dict)
            }
            missing = [
                {"id": rid, "verification_role": vrole}
                for rid, vrole in expected_pairs
                if (rid, vrole) not in pairs
            ]
            if missing:
                failures.append({"run": run_name, "missing_matrix_roles": missing})
        checks["required_matrix_roles"] = {
            "configured": [
                {"id": rid, "verification_role": vrole}
                for rid, vrole in expected_pairs
            ],
            "pass": len(failures) == 0,
            "failures": failures,
        }

    min_core = structured.get("min_core_bullet_count")
    if isinstance(min_core, int) and min_core >= 0:
        failures = []
        for run_name, row in payload.get("per_run", {}).items():
            if "error" in row:
                continue
            count = row.get("core_bullet_count")
            if not isinstance(count, int) or count < min_core:
                failures.append({"run": run_name, "value": count})
        checks["min_core_bullet_count"] = {
            "threshold": min_core,
            "pass": len(failures) == 0,
            "failures": failures,
        }

    req_oos = structured.get("required_out_of_scope_substrings") or []
    req_oos = [s for s in req_oos if isinstance(s, str) and s.strip()]
    if req_oos:
        text_by_run = payload.get("_checklist_text_by_run", {})
        failures = []
        for run_name, text in text_by_run.items():
            low = (text or "").lower()
            missing = [s for s in req_oos if s.lower() not in low]
            if missing:
                failures.append({"run": run_name, "missing_substrings": missing})
        checks["required_out_of_scope_substrings"] = {
            "configured_substrings": req_oos,
            "pass": len(failures) == 0,
            "failures": failures,
        }

    focus_required = structured.get("primary_focus_verbatim_required")
    if isinstance(focus_required, bool) and focus_required:
        failures = []
        for run_name, row in payload.get("per_run", {}).items():
            if "error" in row:
                continue
            ok = row.get("primary_focus_verbatim_pass")
            if ok is not True:
                failures.append({"run": run_name, "value": ok})
        checks["primary_focus_verbatim_required"] = {
            "required": True,
            "pass": len(failures) == 0,
            "failures": failures,
        }

    return checks if checks else {"status": "configured_but_empty"}


def _threshold_config(gold: dict[str, Any] | None, kind: str) -> dict[str, Any]:
    if not isinstance(gold, dict):
        return {}
    cfg = ((gold.get("structured_assertions") or {}).get("thresholds") or {}).get(kind) or {}
    return cfg if isinstance(cfg, dict) else {}


def _evaluate_thresholds(
    kind: str,
    payload: dict[str, Any],
    gold: dict[str, Any] | None,
) -> dict[str, Any]:
    cfg = _threshold_config(gold, kind)
    if not cfg:
        return {
            "evaluated": False,
            "reason": "not_configured",
            "checks": [],
            "summary": {"pass_count": 0, "fail_count": 0, "status": "not_configured"},
        }

    checks: list[dict[str, Any]] = []
    kpis = payload.get("kpis") or {}

    if kind == "prep":
        min_completion = cfg.get("min_snippet_completion_rate")
        if isinstance(min_completion, (int, float)):
            actual = kpis.get("snippet_completion_rate_avg")
            passed = isinstance(actual, (int, float)) and actual >= float(min_completion)
            checks.append(
                {
                    "name": "min_snippet_completion_rate",
                    "actual": actual,
                    "expected": {"op": ">=", "value": float(min_completion)},
                    "pass": bool(passed),
                }
            )

        max_missing = cfg.get("max_missing_snippet_keys")
        if isinstance(max_missing, int) and max_missing >= 0:
            by_run = kpis.get("snippet_missing_keys_by_run") or {}
            counts = {
                run_name: len(v) if isinstance(v, list) else 0 for run_name, v in by_run.items()
            }
            actual = max(counts.values()) if counts else 0
            checks.append(
                {
                    "name": "max_missing_snippet_keys",
                    "actual": actual,
                    "expected": {"op": "<=", "value": max_missing},
                    "pass": actual <= max_missing,
                    "details": {"by_run": counts},
                }
            )

        require_stable = cfg.get("require_client_shell_impact_stable")
        if isinstance(require_stable, bool):
            actual = not bool(kpis.get("client_shell_impact_drift"))
            checks.append(
                {
                    "name": "require_client_shell_impact_stable",
                    "actual": actual,
                    "expected": {"op": "==", "value": require_stable},
                    "pass": actual == require_stable,
                }
            )

    elif kind == "coverage":
        min_core_jaccard = cfg.get("min_core_bullet_jaccard_avg")
        if isinstance(min_core_jaccard, (int, float)):
            actual = kpis.get("core_bullet_jaccard_avg")
            passed = isinstance(actual, (int, float)) and actual >= float(min_core_jaccard)
            checks.append(
                {
                    "name": "min_core_bullet_jaccard_avg",
                    "actual": actual,
                    "expected": {"op": ">=", "value": float(min_core_jaccard)},
                    "pass": bool(passed),
                }
            )

        max_flips = cfg.get("max_matrix_role_flip_count")
        if isinstance(max_flips, int) and max_flips >= 0:
            actual = kpis.get("matrix_role_flip_count")
            passed = isinstance(actual, int) and actual <= max_flips
            checks.append(
                {
                    "name": "max_matrix_role_flip_count",
                    "actual": actual,
                    "expected": {"op": "<=", "value": max_flips},
                    "pass": bool(passed),
                }
            )

        min_focus_rate = cfg.get("min_primary_focus_verbatim_pass_rate")
        if isinstance(min_focus_rate, (int, float)):
            actual = kpis.get("primary_focus_verbatim_pass_rate")
            passed = isinstance(actual, (int, float)) and actual >= float(min_focus_rate)
            checks.append(
                {
                    "name": "min_primary_focus_verbatim_pass_rate",
                    "actual": actual,
                    "expected": {"op": ">=", "value": float(min_focus_rate)},
                    "pass": bool(passed),
                }
            )

        max_diag_per_run = cfg.get("max_diagnostic_bullets_per_run")
        if isinstance(max_diag_per_run, int) and max_diag_per_run >= 0:
            by_run = kpis.get("diagnostic_bullet_count_by_run") or {}
            values = {
                run_name: int(v) if isinstance(v, int) else 0 for run_name, v in by_run.items()
            }
            actual = max(values.values()) if values else 0
            checks.append(
                {
                    "name": "max_diagnostic_bullets_per_run",
                    "actual": actual,
                    "expected": {"op": "<=", "value": max_diag_per_run},
                    "pass": actual <= max_diag_per_run,
                    "details": {"by_run": values},
                }
            )

    elif kind == "test":
        max_temp_runs = cfg.get("max_temp_path_fragment_run_count")
        if isinstance(max_temp_runs, int) and max_temp_runs >= 0:
            actual = int(kpis.get("temp_path_fragment_violation_run_count") or 0)
            checks.append(
                {
                    "name": "max_temp_path_fragment_run_count",
                    "actual": actual,
                    "expected": {"op": "<=", "value": max_temp_runs},
                    "pass": actual <= max_temp_runs,
                }
            )
        max_md_missing = cfg.get("max_tests_md_missing_run_count")
        if isinstance(max_md_missing, int) and max_md_missing >= 0:
            actual = int(kpis.get("tests_md_missing_run_count") or 0)
            checks.append(
                {
                    "name": "max_tests_md_missing_run_count",
                    "actual": actual,
                    "expected": {"op": "<=", "value": max_md_missing},
                    "pass": actual <= max_md_missing,
                }
            )
        min_subproc_rate = cfg.get("min_subprocess_completed_rate_avg")
        if isinstance(min_subproc_rate, (int, float)):
            actual = kpis.get("subprocess_completed_rate_avg")
            passed = isinstance(actual, (int, float)) and actual >= float(min_subproc_rate)
            checks.append(
                {
                    "name": "min_subprocess_completed_rate_avg",
                    "actual": actual,
                    "expected": {"op": ">=", "value": float(min_subproc_rate)},
                    "pass": bool(passed),
                }
            )
    else:
        return {
            "evaluated": False,
            "reason": "unknown_kind",
            "checks": [],
            "summary": {"pass_count": 0, "fail_count": 0, "status": "not_configured"},
        }

    pass_count = sum(1 for c in checks if c.get("pass") is True)
    fail_count = sum(1 for c in checks if c.get("pass") is False)
    status = "pass" if fail_count == 0 else "fail"

    return {
        "evaluated": True,
        "checks": checks,
        "summary": {
            "pass_count": pass_count,
            "fail_count": fail_count,
            "status": status,
        },
    }


def _sanitization_policy(gold: dict[str, Any] | None, kind: str) -> dict[str, Any]:
    policy = {
        "enabled": SANITIZATION_DEFAULTS["enabled"],
        "forbidden_regex": list(SANITIZATION_DEFAULTS["forbidden_regex"]),
        "forbidden_substrings": list(SANITIZATION_DEFAULTS["forbidden_substrings"]),
        "allowed_exceptions": list(SANITIZATION_DEFAULTS["allowed_exceptions"]),
        "scan_targets": list((SANITIZATION_DEFAULTS["scan_targets"] or {}).get(kind, [])),
    }
    if not isinstance(gold, dict):
        return policy

    cfg = ((gold.get("structured_assertions") or {}).get("sanitization")) or {}
    if not isinstance(cfg, dict):
        return policy

    kind_cfg = cfg.get(kind) if isinstance(cfg.get(kind), dict) else {}
    merged = {}
    merged.update(cfg)
    merged.update(kind_cfg)

    enabled = merged.get("enabled")
    if isinstance(enabled, bool):
        policy["enabled"] = enabled

    for key in ("forbidden_regex", "forbidden_substrings", "allowed_exceptions"):
        v = merged.get(key)
        if isinstance(v, list):
            policy[key] = [x for x in v if isinstance(x, str) and x.strip()]

    scan_targets = merged.get("scan_targets")
    if isinstance(scan_targets, list):
        policy["scan_targets"] = [x for x in scan_targets if isinstance(x, str) and x.strip()]

    return policy


def _collect_scan_records(
    kind: str,
    payload: dict[str, Any],
    scan_targets: list[str],
) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []

    if kind == "prep":
        if "client_shell_impact" in scan_targets:
            for run_name, row in (payload.get("per_run") or {}).items():
                if not isinstance(row, dict) or "error" in row:
                    continue
                impact = row.get("client_shell_impact") or {}
                if isinstance(impact, dict):
                    for shell in ("corner_trader", "adaptive"):
                        info = impact.get(shell) or {}
                        if isinstance(info, dict):
                            for field in ("note", "evidence"):
                                val = info.get(field)
                                if isinstance(val, str) and val.strip():
                                    records.append(
                                        {
                                            "run": run_name,
                                            "path": f"per_run.{run_name}.client_shell_impact.{shell}.{field}",
                                            "text": val,
                                        }
                                    )
                    src = impact.get("source")
                    if isinstance(src, str) and src.strip():
                        records.append(
                            {
                                "run": run_name,
                                "path": f"per_run.{run_name}.client_shell_impact.source",
                                "text": src,
                            }
                        )

    elif kind == "coverage":
        if "checklist_markdown" in scan_targets:
            text_by_run = payload.get("_checklist_text_by_run") or {}
            if isinstance(text_by_run, dict):
                for run_name, text in text_by_run.items():
                    if isinstance(text, str) and text.strip():
                        records.append(
                            {
                                "run": run_name,
                                "path": f"_checklist_text_by_run.{run_name}",
                                "text": text,
                            }
                        )

    return records


def _evaluate_sanitization(
    kind: str,
    payload: dict[str, Any],
    gold: dict[str, Any] | None,
) -> dict[str, Any]:
    policy = _sanitization_policy(gold, kind)
    if not policy.get("enabled", True):
        return {
            "evaluated": False,
            "reason": "disabled",
            "policy": policy,
            "checks": [],
            "violations": [],
            "summary": {
                "pass_count": 0,
                "fail_count": 0,
                "status": "disabled",
                "violation_count": 0,
            },
        }

    records = _collect_scan_records(kind, payload, policy.get("scan_targets") or [])
    exceptions = [x.lower() for x in (policy.get("allowed_exceptions") or []) if isinstance(x, str)]
    violations: list[dict[str, Any]] = []

    regex_rules = [
        r for r in (policy.get("forbidden_regex") or []) if isinstance(r, str) and r.strip()
    ]
    for rule in regex_rules:
        try:
            compiled = re.compile(rule)
        except re.error:
            violations.append(
                {
                    "run": None,
                    "path": "policy.forbidden_regex",
                    "rule_id": "invalid_regex",
                    "rule": rule,
                    "match_type": "policy_error",
                    "excerpt": "invalid_regex",
                }
            )
            continue
        for rec in records:
            text = rec.get("text", "")
            for m in compiled.finditer(text):
                excerpt = _sanitize_excerpt(text, m.start(), m.end())
                if any(ex in excerpt.lower() for ex in exceptions):
                    continue
                violations.append(
                    {
                        "run": rec.get("run"),
                        "path": rec.get("path"),
                        "rule_id": "forbidden_regex",
                        "rule": rule,
                        "match_type": "regex",
                        "excerpt": excerpt,
                    }
                )

    substring_rules = [
        s
        for s in (policy.get("forbidden_substrings") or [])
        if isinstance(s, str) and s.strip()
    ]
    for needle in substring_rules:
        low = needle.lower()
        for rec in records:
            text = rec.get("text", "")
            text_low = text.lower()
            idx = text_low.find(low)
            if idx < 0:
                continue
            excerpt = _sanitize_excerpt(text, idx, idx + len(needle))
            if any(ex in excerpt.lower() for ex in exceptions):
                continue
            violations.append(
                {
                    "run": rec.get("run"),
                    "path": rec.get("path"),
                    "rule_id": "forbidden_substrings",
                    "rule": needle,
                    "match_type": "substring",
                    "excerpt": excerpt,
                }
            )

    checks = [
        {
            "name": "forbidden_regex",
            "configured_count": len(regex_rules),
            "violation_count": sum(1 for v in violations if v.get("rule_id") == "forbidden_regex"),
            "pass": sum(1 for v in violations if v.get("rule_id") == "forbidden_regex") == 0,
        },
        {
            "name": "forbidden_substrings",
            "configured_count": len(substring_rules),
            "violation_count": sum(
                1 for v in violations if v.get("rule_id") == "forbidden_substrings"
            ),
            "pass": sum(1 for v in violations if v.get("rule_id") == "forbidden_substrings") == 0,
        },
    ]
    pass_count = sum(1 for c in checks if c.get("pass") is True)
    fail_count = sum(1 for c in checks if c.get("pass") is False)
    status = "pass" if fail_count == 0 and not violations else "fail"

    return {
        "evaluated": True,
        "policy": policy,
        "checks": checks,
        "violations": violations,
        "summary": {
            "pass_count": pass_count,
            "fail_count": fail_count,
            "status": status,
            "violation_count": len(violations),
        },
    }


def _apply_soft_fail_to_thresholds(
    thresholds: dict[str, Any],
    sanitization: dict[str, Any],
) -> dict[str, Any]:
    t = thresholds if isinstance(thresholds, dict) else {}
    summary = t.get("summary")
    if not isinstance(summary, dict):
        summary = {"pass_count": 0, "fail_count": 0, "status": "not_configured"}
        t["summary"] = summary

    s_summary = sanitization.get("summary") if isinstance(sanitization, dict) else None
    s_status = s_summary.get("status") if isinstance(s_summary, dict) else None
    if s_status == "fail":
        summary["status"] = "fail"
        summary["fail_count"] = int(summary.get("fail_count", 0)) + 1
        summary["soft_fail_triggered"] = True
        sources = summary.get("soft_fail_sources")
        if not isinstance(sources, list):
            sources = []
        if "sanitization" not in sources:
            sources.append("sanitization")
        summary["soft_fail_sources"] = sources
    return t


def _history_file(history_root: Path, epic_key: str, kind: str) -> Path:
    return history_root / f"{epic_key}-{kind}-history.jsonl"


def _resolve_history_root(
    suite_run_dir: Path | None,
    benchmark_root: Path,
) -> Path:
    """Global history under ``.cursor/benchmark/history/`` for hub runs; else under benchmark root."""
    if suite_run_dir is not None:
        return suite_run_dir.parent.parent / "history"
    return benchmark_root / "history"


def _append_history_entry(
    history_root: Path,
    epic_key: str,
    kind: str,
    payload: dict[str, Any],
) -> list[dict[str, Any]]:
    history_path = _history_file(history_root, epic_key, kind)
    history_path.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "at_utc": _utc_now_iso(),
        "epic_key": epic_key,
        "kind": kind,
        "suite_id": payload.get("suite_id"),
        "runs": payload.get("runs", []),
        "metrics_schema_version": payload.get("schema_version"),
        "script_version": SCRIPT_VERSION,
        "kpis": payload.get("kpis", {}),
        "thresholds_summary": (payload.get("thresholds") or {}).get("summary"),
        "thresholds_evaluated": (payload.get("thresholds") or {}).get("evaluated"),
        "sanitization_summary": (payload.get("sanitization") or {}).get("summary"),
        "sanitization_evaluated": (payload.get("sanitization") or {}).get("evaluated"),
    }

    with history_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    entries: list[dict[str, Any]] = []
    with history_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                entries.append(obj)
    return entries


def _status_rank(status: str | None) -> int:
    mapping = {"fail": 0, "not_configured": 1, "pass": 2}
    if status is None:
        return -1
    return mapping.get(status, -1)


def _trend_snapshot(
    kind: str,
    entries: list[dict[str, Any]],
    history_path: Path,
) -> dict[str, Any]:
    if len(entries) < 1:
        return {
            "status": "insufficient_history",
            "history_file": str(history_path.as_posix()),
            "latest_n": [],
        }

    latest = entries[-TREND_WINDOW:]
    compact_latest = []
    for e in latest:
        compact_latest.append(
            {
                "at_utc": e.get("at_utc"),
                "suite_id": e.get("suite_id"),
                "runs_count": len(e.get("runs") or []),
                "kpis": e.get("kpis", {}),
                "thresholds_summary": e.get("thresholds_summary"),
                "sanitization_summary": e.get("sanitization_summary"),
            }
        )

    if len(entries) < 2:
        return {
            "status": "insufficient_history",
            "history_file": str(history_path.as_posix()),
            "latest_n": compact_latest,
        }

    prev = entries[-2]
    curr = entries[-1]
    prev_kpis = prev.get("kpis") or {}
    curr_kpis = curr.get("kpis") or {}

    numeric_keys_by_kind = {
        "prep": ["snippet_completion_rate_avg"],
        "coverage": [
            "core_bullet_jaccard_avg",
            "matrix_role_flip_count",
            "primary_focus_verbatim_pass_rate",
        ],
        "test": ["subprocess_completed_rate_avg", "temp_path_fragment_violation_run_count"],
    }
    delta_vs_prev: dict[str, float] = {}
    for key in numeric_keys_by_kind.get(kind, []):
        a = prev_kpis.get(key)
        b = curr_kpis.get(key)
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            delta_vs_prev[key] = round(float(b) - float(a), 4)

    regression_flags: list[dict[str, Any]] = []
    prev_status = ((prev.get("thresholds_summary") or {}).get("status")) if isinstance(prev.get("thresholds_summary"), dict) else None
    curr_status = ((curr.get("thresholds_summary") or {}).get("status")) if isinstance(curr.get("thresholds_summary"), dict) else None
    if _status_rank(curr_status) < _status_rank(prev_status):
        regression_flags.append(
            {
                "type": "threshold_status_worsened",
                "from": prev_status,
                "to": curr_status,
            }
        )

    prev_s = prev.get("sanitization_summary") if isinstance(prev.get("sanitization_summary"), dict) else {}
    curr_s = curr.get("sanitization_summary") if isinstance(curr.get("sanitization_summary"), dict) else {}
    prev_v = prev_s.get("violation_count")
    curr_v = curr_s.get("violation_count")
    if isinstance(prev_v, int) and isinstance(curr_v, int):
        delta_vs_prev["sanitization_violation_count"] = round(float(curr_v - prev_v), 4)
        if curr_v > prev_v:
            regression_flags.append(
                {
                    "type": "sanitization_violations_increased",
                    "from": prev_v,
                    "to": curr_v,
                }
            )

    return {
        "status": "ok",
        "history_file": str(history_path.as_posix()),
        "latest_n": compact_latest,
        "delta_vs_prev": delta_vs_prev,
        "regression_flags": regression_flags,
    }


def _attach_gold_checks(
    kind: str,
    payload: dict[str, Any],
    gold: dict[str, Any] | None,
    gold_path: Path | None,
) -> dict[str, Any]:
    gold_path_str = str(gold_path.as_posix()) if gold_path is not None else None
    if not gold:
        return {
            "gold_file": None,
            "applied": False,
            "reason": "gold_not_found",
        }
    if not _gold_pipeline_applies(gold, kind):
        return {
            "gold_file": gold_path_str,
            "applied": False,
            "reason": "pipeline_not_applicable",
            "pipeline": gold.get("pipeline"),
        }

    if kind == "prep":
        legacy = _legacy_gold_checks_prep(gold, payload)
        structured = _structured_gold_checks_prep(gold, payload)
    elif kind == "coverage":
        legacy = _legacy_gold_checks_coverage(gold, payload)
        structured = _structured_gold_checks_coverage(gold, payload)
    else:
        return {
            "gold_file": gold_path_str,
            "applied": False,
            "reason": "gold_checks_not_defined_for_kind",
            "pipeline": gold.get("pipeline"),
        }

    return {
        "gold_file": gold_path_str,
        "applied": True,
        "pipeline": gold.get("pipeline"),
        "legacy_checks": legacy,
        "structured_checks": structured,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Compare benchmark snapshots for one epic.")
    ap.add_argument(
        "--benchmark-root",
        type=Path,
        default=Path(".cursor/benchmark/coverage-bench"),
        help="Coverage benchmark root (usually .cursor/benchmark/coverage-bench)",
    )
    ap.add_argument("--epic", required=True, help="Epic key, e.g. CRT-639")
    ap.add_argument(
        "--kind",
        choices=("prep", "coverage", "test"),
        required=True,
        help="prep | coverage | test (TEST-PREP -tests.json)",
    )
    ap.add_argument(
        "--suite-id",
        type=str,
        default="",
        help=(
            "Suite id (metadata + legacy discovery): coverage-bench "
            "runs/run-<id>/attempts/<EPIC>/run-*.json; optional if --suite-run-dir "
            "is set (defaults to suite folder name)"
        ),
    )
    ap.add_argument(
        "--suite-run-dir",
        type=Path,
        default=None,
        help=(
            "Hub suite folder (.cursor/benchmark/runs/<suite_id>): discovers "
            "attempt-*/_machine/attempts/<EPIC>/run-*.json, else shadow/<EPIC>/ "
            "snapshots; writes _aggregate/crossref/ here; uses global "
            ".cursor/benchmark/history/"
        ),
    )
    ap.add_argument(
        "--gold-root",
        type=Path,
        default=None,
        help=(
            "Directory containing <EPIC>-gold.json (normally .cursor/benchmark/data). "
            "Tried before other gold search paths."
        ),
    )
    args = ap.parse_args()

    root: Path = args.benchmark_root.resolve()
    epic = (args.epic or "").strip().upper()
    suite_id = (args.suite_id or "").strip()
    suite_run_dir: Path | None = (
        args.suite_run_dir.resolve() if args.suite_run_dir is not None else None
    )
    gold_root_arg: Path | None = (
        args.gold_root.resolve() if args.gold_root is not None else None
    )

    if not root.is_dir():
        print(f"benchmark root not found: {root}")
        return 2
    if suite_run_dir is not None and not suite_run_dir.is_dir():
        print(f"suite-run-dir not found: {suite_run_dir}")
        return 2

    hub_mode = suite_run_dir is not None
    hub_discovery_source = ""
    if hub_mode:
        if not suite_id:
            suite_id = suite_run_dir.name
        run_dirs, hub_discovery_source = _discover_suite_hub(
            suite_run_dir, epic, phase=args.kind
        )
        if not run_dirs:
            print(
                "No hub snapshots for "
                f"epic={epic!r} phase={args.kind!r} under {suite_run_dir}: "
                "expected attempt-*/_machine/attempts/*/run-*.json with matching phase, "
                "or shadow fallbacks "
                "(ref.json / coverage.json / tests.json per kind)."
            )
            return 1
        crossref = suite_run_dir / "_aggregate" / "crossref"
    elif suite_id:
        run_dirs = _discover_suite(root, epic, suite_id, phase=args.kind)
        if not run_dirs:
            print(
                f"No suite files under runs/run-{suite_id}/attempts/{epic}/ (run-*.json)"
            )
            return 1
        crossref = root / "crossref"
    else:
        run_dirs = _discover_legacy(root, epic)
        if not run_dirs:
            print(f"No legacy run-*/meta.json with epic_key={epic!r} under {root}")
            return 1
        crossref = root / "crossref"

    crossref.mkdir(parents=True, exist_ok=True)
    gold_search = _gold_data_search_dirs(gold_root_arg, suite_run_dir, root)
    gold, gold_path = _find_gold(epic, gold_search)

    history_root = _resolve_history_root(suite_run_dir, root)
    hist_path_prep = _history_file(history_root, epic, "prep")
    hist_path_cov = _history_file(history_root, epic, "coverage")
    hist_path_test = _history_file(history_root, epic, "test")

    kind = args.kind
    if kind == "prep":
        payload = _prep_metrics(run_dirs)
        payload["epic_key"] = epic
        if suite_id:
            payload["suite_id"] = suite_id
        if hub_mode:
            payload["discovery"] = "hub_suite_run_dir"
            payload["discovery_source"] = hub_discovery_source
            payload["suite_run_dir"] = str(suite_run_dir.as_posix())
        payload["gold_checks"] = _attach_gold_checks("prep", payload, gold, gold_path)
        payload["thresholds"] = _evaluate_thresholds("prep", payload, gold)
        payload["sanitization"] = _evaluate_sanitization("prep", payload, gold)
        payload["thresholds"] = _apply_soft_fail_to_thresholds(
            payload.get("thresholds", {}), payload.get("sanitization", {})
        )
        history_entries = _append_history_entry(history_root, epic, "prep", payload)
        payload["trend"] = _trend_snapshot("prep", history_entries, hist_path_prep)
        out = crossref / f"{epic}-prep-metrics.json"
    elif kind == "coverage":
        payload = _coverage_metrics(run_dirs)
        payload["epic_key"] = epic
        if suite_id:
            payload["suite_id"] = suite_id
        if hub_mode:
            payload["discovery"] = "hub_suite_run_dir"
            payload["discovery_source"] = hub_discovery_source
            payload["suite_run_dir"] = str(suite_run_dir.as_posix())
        payload["gold_checks"] = _attach_gold_checks("coverage", payload, gold, gold_path)
        payload["thresholds"] = _evaluate_thresholds("coverage", payload, gold)
        payload["sanitization"] = _evaluate_sanitization("coverage", payload, gold)
        payload["thresholds"] = _apply_soft_fail_to_thresholds(
            payload.get("thresholds", {}), payload.get("sanitization", {})
        )
        history_entries = _append_history_entry(history_root, epic, "coverage", payload)
        payload["trend"] = _trend_snapshot(
            "coverage", history_entries, hist_path_cov
        )
        payload.pop("_checklist_text_by_run", None)
        out = crossref / f"{epic}-coverage-metrics.json"
    else:
        payload = _test_metrics(run_dirs)
        payload["epic_key"] = epic
        if suite_id:
            payload["suite_id"] = suite_id
        if hub_mode:
            payload["discovery"] = "hub_suite_run_dir"
            payload["discovery_source"] = hub_discovery_source
            payload["suite_run_dir"] = str(suite_run_dir.as_posix())
        payload["gold_checks"] = _attach_gold_checks("test", payload, gold, gold_path)
        payload["thresholds"] = _evaluate_thresholds("test", payload, gold)
        payload["sanitization"] = _evaluate_sanitization("test", payload, gold)
        payload["thresholds"] = _apply_soft_fail_to_thresholds(
            payload.get("thresholds", {}), payload.get("sanitization", {})
        )
        history_entries = _append_history_entry(history_root, epic, "test", payload)
        payload["trend"] = _trend_snapshot("test", history_entries, hist_path_test)
        out = crossref / f"{epic}-test-metrics.json"

    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
