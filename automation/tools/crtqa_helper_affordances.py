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
    return {
        "epic_key": discover.get("epic_key"),
        "schema_version": discover.get("schema_version"),
        "verification_affordances": discover.get("verification_affordances"),
        "obligation_ledger": discover.get("obligation_ledger"),
        "fixture_needs": discover.get("fixture_needs"),
        "client_shell_impact": discover.get("client_shell_impact"),
        "discovery_status": discover.get("discovery_status"),
        "source": str(discover.get("epic_key", "")) + "-discover.json",
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Export affordances slice for crtqa-helper reinforce")
    p.add_argument("--discover", required=True, type=Path, help="Path to <KEY>-discover.json")
    p.add_argument("--out", required=True, type=Path, help="Output affordances-slice.json path")
    args = p.parse_args()

    discover_path = args.discover if args.discover.is_absolute() else REPO_ROOT / args.discover
    out_path = args.out if args.out.is_absolute() else REPO_ROOT / args.out

    doc = _load(discover_path)
    if not doc:
        print(f"FAIL: cannot read discover JSON: {discover_path}", file=sys.stderr)
        return 1

    slice_doc = build_slice(doc)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(slice_doc, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"OK affordances_slice rows={len(slice_doc.get('verification_affordances') or [])} -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
