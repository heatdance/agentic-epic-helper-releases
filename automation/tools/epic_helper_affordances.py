#!/usr/bin/env python3
"""Export jq-shaped affordance slice from -discover.json for COVERAGE-REINFORCE."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load(path: Path) -> dict[str, Any] | None:
    try:
        with path.open(encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def build_slice(discover: dict[str, Any]) -> dict[str, Any]:
    sources = discover.get("sources") or {}
    env = discover.get("environment") or {}
    topology_loaded = sources.get("topology_loaded") if isinstance(sources, dict) else None
    client_shell = env.get("client_shell_impact") if isinstance(env, dict) else None
    return {
        "epic_key": discover.get("epic_key"),
        "schema_version": discover.get("schema_version"),
        "verification_affordances": discover.get("verification_affordances"),
        "obligation_ledger": discover.get("obligation_ledger"),
        "fixture_needs": discover.get("fixture_needs"),
        "environment": {"client_shell_impact": client_shell} if client_shell else {},
        "topology_loaded": topology_loaded,
        "discovery_status": discover.get("discovery_status"),
        "source": str(discover.get("epic_key", "")) + "-discover.json",
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Export affordances slice for epic-helper reinforce")
    p.add_argument("--discover", required=True, type=Path, help="Path to <KEY>-discover.json")
    p.add_argument("--out", required=True, type=Path, help="Output affordances-slice.json path")
    p.add_argument(
        "--strict-topology",
        action="store_true",
        help="Echo when discover.sources.topology_loaded is true",
    )
    p.add_argument(
        "--strict-principal",
        action="store_true",
        help="Echo when discover.sources.principal_loaded is true",
    )
    args = p.parse_args()

    discover_path = args.discover if args.discover.is_absolute() else REPO_ROOT / args.discover
    out_path = args.out if args.out.is_absolute() else REPO_ROOT / args.out

    doc = _load(discover_path)
    if not doc:
        print(f"FAIL: cannot read discover JSON: {discover_path}", file=sys.stderr)
        return 1

    slice_doc = build_slice(doc)
    principal_loaded = (doc.get("sources") or {}).get("principal_loaded")
    slice_doc["principal_loaded"] = principal_loaded
    if args.strict_topology and not slice_doc.get("topology_loaded"):
        print("warning: --strict-topology but discover.sources.topology_loaded is not true", file=sys.stderr)

    if args.strict_principal and not slice_doc.get("principal_loaded"):
        print(
            "warning: --strict-principal but discover.sources.principal_loaded is not true",
            file=sys.stderr,
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(slice_doc, f, indent=2, ensure_ascii=False)
        f.write("\n")

    oracle_count = sum(
        1
        for aff in slice_doc.get("verification_affordances") or []
        if isinstance(aff, dict) and aff.get("oracle_binding")
    )
    provision_count = sum(
        1
        for fix in slice_doc.get("fixture_needs") or []
        if isinstance(fix, dict)
        and (
            fix.get("derivation") == "ref_principal_provision"
            or (fix.get("linked_obligation_ids") or [])
        )
    )
    print(
        f"OK affordances_slice rows={len(slice_doc.get('verification_affordances') or [])} "
        f"oracle_bindings={oracle_count} topology_loaded={slice_doc.get('topology_loaded')} "
        f"principal_loaded={slice_doc.get('principal_loaded')} provision_fixtures={provision_count} "
        f"-> {out_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
