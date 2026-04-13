#!/usr/bin/env python3
"""Run: python test_yogi_extract.py (from automation/tools/yogi-tool/)"""

import json
import sys
from pathlib import Path

from yogi_extract import extract_requirement_snippet
from yogi_snippet import load_storage_from_export

_FIX = Path(__file__).resolve().parent / "fixtures"


def _load(name: str) -> str:
    p = _FIX / name
    return json.loads(p.read_text(encoding="utf-8"))["content"]["value"]


def main() -> int:
    h = _load("sample_inline_req.json")
    r = extract_requirement_snippet(h, "CRT-1730")
    assert r.mode == "inline_td", r.mode
    assert "FX_SPOT" in r.text and "mark_price" in r.text, r.text
    assert r.candidates_considered == 1, r.candidates_considered

    h2 = _load("sample_adjacent_req.json")
    r2 = extract_requirement_snippet(h2, "CRT-1741")
    assert r2.mode == "after_th_td", r2.mode
    assert "FIFO" in r2.text and "Weighted Average" in r2.text, r2.text
    assert r2.candidates_considered == 1, r2.candidates_considered

    h3 = _load("sample_duplicate_key_req.json")
    r3 = extract_requirement_snippet(h3, "CRT-1999")
    assert r3.mode == "definition_h2_p", r3.mode
    assert "weighted average" in r3.text.lower(), r3.text
    assert ")" not in r3.text, r3.text
    assert r3.candidates_considered == 2, r3.candidates_considered
    assert r3.selected_reason == "best_of_n_macros", r3.selected_reason

    # MCP-style export: storage under metadata.content.value
    mcp_like = {
        "metadata": {
            "id": "123",
            "content": {"value": "<p>stub</p>", "format": "storage"},
        }
    }
    assert "stub" in load_storage_from_export(mcp_like)
    assert "<table>" in load_storage_from_export(json.loads((_FIX / "sample_duplicate_key_req.json").read_text(encoding="utf-8")))

    print("ok:", r.text[:80], "|", r2.text[:80], "|", r3.text[:80])
    return 0


if __name__ == "__main__":
    sys.exit(main())
