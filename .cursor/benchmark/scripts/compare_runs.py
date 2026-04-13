#!/usr/bin/env python3
"""
Compare benchmark snapshots for one epic:
- Legacy: .cursor/benchmark/run-*/ (meta.json + epic-ref / coverage snapshots)
- Suite: .cursor/benchmark/runs/run-<suite_id>/attempts/<EPIC>/run-*.json
  When using --suite-id, only files whose JSON "phase" matches --kind (prep/coverage)
  are included; malformed JSON files are still listed so load errors surface.

Writes crossref/<KEY>-prep-metrics.json or <KEY>-coverage-metrics.json.
Stdlib only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


def _norm_ws(s: str) -> str:
    return " ".join(s.split())


def _sha256_norm(s: str) -> str:
    return hashlib.sha256(_norm_ws(s).encode("utf-8")).hexdigest()


def _load_json(p: Path) -> Any:
    with p.open(encoding="utf-8") as f:
        return json.load(f)


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


def _discover_suite(
    benchmark_root: Path,
    epic_key: str,
    suite_id: str,
    phase: str | None = None,
) -> list[tuple[str, Path]]:
    """Suite: runs/run-<suite_id>/attempts/<EPIC>/run-*.json.

    If ``phase`` is ``prep`` or ``coverage``, include only files whose wrapper JSON
    has matching ``phase``; skip others. Malformed JSON is still included so metrics
    can report parse errors.
    """
    attempts = benchmark_root / "runs" / f"run-{suite_id}" / "attempts" / epic_key
    if not attempts.is_dir():
        return []
    out: list[tuple[str, Path]] = []
    for p in sorted(attempts.glob("run-*.json")):
        if not p.is_file():
            continue
        if phase:
            try:
                wrap = _load_json(p)
            except (json.JSONDecodeError, OSError):
                pass
            else:
                if wrap.get("phase") != phase:
                    continue
        out.append((p.stem, p))
    return out


def _prep_metrics(run_dirs: list[tuple[str, Path]]) -> dict[str, Any]:
    per_run: dict[str, Any] = {}

    for name, d in run_dirs:
        if d.is_file() and d.suffix == ".json":
            try:
                wrap = _load_json(d)
            except (json.JSONDecodeError, OSError) as e:
                per_run[name] = {"error": str(e)}
                continue
            if wrap.get("phase") != "prep":
                per_run[name] = {"error": "not a prep phase record"}
                continue
            data = wrap.get("artifact")
            if not isinstance(data, dict):
                per_run[name] = {"error": "missing artifact"}
                continue
        else:
            snap = d / "epic-ref.snapshot.json"
            if not snap.is_file():
                per_run[name] = {"error": "missing epic-ref.snapshot.json"}
                continue
            try:
                data = _load_json(snap)
            except (json.JSONDecodeError, OSError) as e:
                per_run[name] = {"error": str(e)}
                continue

        reqs = data.get("requirements") or []
        keys_snippets: dict[str, str | None] = {}
        for r in reqs:
            k = r.get("key")
            if not k:
                continue
            st = r.get("snippet_text")
            keys_snippets[k] = st if isinstance(st, str) else None

        per_run[name] = {
            "requirement_keys": sorted(keys_snippets.keys()),
            "snippet_sha256": {
                k: _sha256_norm(v) if v else None for k, v in keys_snippets.items()
            },
            "client_shell_impact": data.get("client_shell_impact"),
        }

    successful = [n for n, _ in run_dirs if "error" not in per_run.get(n, {})]
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

    return {
        "runs": [n for n, _ in run_dirs],
        "per_run": per_run,
        "key_intersection_all_runs": key_intersection,
        "snippet_hash_stable_across_all_runs": snippet_hash_agreement,
        "unstable_keys": unstable_keys,
        "client_shell_impact_drift": client_shell_impact_drift,
    }


def _extract_bullets_from_md(text: str) -> list[str]:
    lines = text.splitlines()
    bullets: list[str] = []
    for line in lines:
        m = re.match(r"^\s*-\s+(.+)$", line)
        if m:
            bullets.append(_norm_ws(m.group(1).lower()))
    return bullets


def _bullets_from_coverage_data(data: dict[str, Any]) -> list[str]:
    md = data.get("smart_checklist_markdown")
    if isinstance(md, str) and md.strip():
        return _extract_bullets_from_md(md)
    return []


def _coverage_metrics(run_dirs: list[tuple[str, Path]]) -> dict[str, Any]:
    per_run: dict[str, Any] = {}
    all_normalized_bullets: dict[str, set[str]] = {}

    for name, d in run_dirs:
        if d.is_file() and d.suffix == ".json":
            try:
                wrap = _load_json(d)
            except (json.JSONDecodeError, OSError) as e:
                per_run[name] = {"error": str(e)}
                continue
            if wrap.get("phase") != "coverage":
                per_run[name] = {"error": "not a coverage phase record"}
                continue
            data = wrap.get("artifact")
            if not isinstance(data, dict):
                per_run[name] = {"error": "missing artifact"}
                continue
            bullets = _bullets_from_coverage_data(data)
            cm = wrap.get("checklist_markdown")
            if not bullets and isinstance(cm, str) and cm.strip():
                bullets = _extract_bullets_from_md(cm)
        else:
            js = d / "coverage.snapshot.json"
            md_path = d / "coverage.snapshot.md"
            if not js.is_file():
                per_run[name] = {"error": "missing coverage.snapshot.json"}
                continue
            try:
                data = _load_json(js)
            except (json.JSONDecodeError, OSError) as e:
                per_run[name] = {"error": str(e)}
                continue
            bullets = _bullets_from_coverage_data(data)
            if not bullets and md_path.is_file():
                try:
                    bullets = _extract_bullets_from_md(md_path.read_text(encoding="utf-8"))
                except OSError:
                    pass

        per_run[name] = {
            "bullet_count": len(bullets),
            "matrix_rows": [
                {"id": row.get("id"), "verification_role": row.get("verification_role")}
                for row in (data.get("coverage_matrix") or [])
                if isinstance(row, dict)
            ],
        }
        all_normalized_bullets[name] = set(bullets)

    names = [n for n, _ in run_dirs if "error" not in per_run.get(n, {})]
    pairwise_jaccard: dict[str, dict[str, float]] = {}
    for i, a in enumerate(names):
        pairwise_jaccard[a] = {}
        sa = all_normalized_bullets.get(a, set())
        for b in names[i + 1 :]:
            sb = all_normalized_bullets.get(b, set())
            inter = sa & sb
            union = sa | sb
            j = len(inter) / len(union) if union else 1.0
            pairwise_jaccard[a][b] = round(j, 4)
            if b not in pairwise_jaccard:
                pairwise_jaccard[b] = {}
            pairwise_jaccard[b][a] = round(j, 4)

    freq: dict[str, int] = {}
    n_success = len(names)
    for n in names:
        for b in all_normalized_bullets.get(n, set()):
            freq[b] = freq.get(b, 0) + 1

    strong = sorted([b for b, c in freq.items() if n_success and c == n_success])
    weak = sorted([b for b, c in freq.items() if 0 < c < n_success])

    pair_sets: list[set[tuple[Any, Any]]] = []
    for n in names:
        rows = per_run[n].get("matrix_rows") or []
        pair_sets.append({(r.get("id"), r.get("verification_role")) for r in rows})
    matrix_intersection: list[list[Any]] = []
    if pair_sets:
        mi = set.intersection(*pair_sets)
        matrix_intersection = [list(x) for x in sorted(mi, key=lambda x: (str(x[0]), str(x[1])))]

    return {
        "runs": [n for n, _ in run_dirs],
        "per_run": per_run,
        "pairwise_jaccard": pairwise_jaccard,
        "bullet_frequency": freq,
        "strong_bullets_all_runs": strong,
        "weak_bullets": weak,
        "matrix_intersection": matrix_intersection,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Compare benchmark snapshots for one epic.")
    ap.add_argument(
        "--benchmark-root",
        type=Path,
        default=Path(".cursor/benchmark"),
        help="Path to .cursor/benchmark",
    )
    ap.add_argument("--epic", required=True, help="Epic key, e.g. CRT-639")
    ap.add_argument("--kind", choices=("prep", "coverage"), required=True)
    ap.add_argument(
        "--suite-id",
        type=str,
        default="",
        help="Suite id: use runs/run-<id>/attempts/<EPIC>/run-*.json (phase must match --kind)",
    )
    args = ap.parse_args()

    root: Path = args.benchmark_root.resolve()
    epic = (args.epic or "").strip().upper()
    suite_id = (args.suite_id or "").strip()
    if not root.is_dir():
        print(f"benchmark root not found: {root}")
        return 2

    if suite_id:
        run_dirs = _discover_suite(root, epic, suite_id, phase=args.kind)
        if not run_dirs:
            print(
                f"No suite files under runs/run-{suite_id}/attempts/{epic}/ (run-*.json)"
            )
            return 1
    else:
        run_dirs = _discover_legacy(root, epic)
        if not run_dirs:
            print(f"No legacy run-*/meta.json with epic_key={epic!r} under {root}")
            return 1

    crossref = root / "crossref"
    crossref.mkdir(parents=True, exist_ok=True)

    if args.kind == "prep":
        payload = _prep_metrics(run_dirs)
        payload["epic_key"] = epic
        if suite_id:
            payload["suite_id"] = suite_id
        out = crossref / f"{epic}-prep-metrics.json"
    else:
        payload = _coverage_metrics(run_dirs)
        payload["epic_key"] = epic
        if suite_id:
            payload["suite_id"] = suite_id
        out = crossref / f"{epic}-coverage-metrics.json"

    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
