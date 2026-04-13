#!/usr/bin/env python3
"""
Fetch Confluence body.storage (REST) and extract only the Yogi requirement row text.

Designed to stay token-light: default output is a small JSON with snippet text + size stats.

Usage:
  python yogi_snippet.py --page-id 345703196 --req CRT-1730 --cookie "JSESSIONID=..."
  python yogi_snippet.py --page-id 345703196 --req CRT-1730 --storage-file export.json
  python yogi_snippet.py --page-id 345703196 --req CRT-1730 --cookie "..." --compare

Exit codes: 0 = snippet ok; 1 = fetch/parse error; 2 = missing --page-id and --storage-file; 3 = key not found or empty snippet in storage.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from yogi_confluence import fetch_body_storage
from yogi_extract import extract_requirement_snippet

DEFAULT_HOST = "https://confluence.in.devexperts.com"


def load_storage_from_export(data: object) -> str:
    """
    Unwrap Confluence storage HTML from common export shapes:
    - REST: {"body": {"storage": {"value": "..."}}}
    - Wrapped: {"content": {"value": "..."}}
    - MCP confluence_get_page: {"metadata": {"content": {"value": "..."}}}
    - Raw: a string (storage HTML)
    """
    if isinstance(data, str):
        return data
    if not isinstance(data, dict):
        raise ValueError("Export must be a JSON object or a string (storage HTML)")

    c = data.get("content")
    if isinstance(c, dict) and "value" in c:
        return str(c["value"])

    body = data.get("body")
    if isinstance(body, dict):
        stor = body.get("storage")
        if isinstance(stor, dict) and "value" in stor:
            return str(stor["value"])

    md = data.get("metadata")
    if isinstance(md, dict):
        c2 = md.get("content")
        if isinstance(c2, dict) and "value" in c2:
            return str(c2["value"])

    raise ValueError(
        "JSON must include content.value, body.storage.value, or metadata.content.value (Confluence storage HTML)"
    )


def _load_storage_from_file(path: str) -> str:
    raw = open(path, encoding="utf-8").read()
    data = json.loads(raw)
    return load_storage_from_export(data)


def main() -> int:
    p = argparse.ArgumentParser(description="Lightweight Yogi requirement text from Confluence storage.")
    p.add_argument("--page-id", help="Confluence numeric page id")
    p.add_argument("--req", required=True, help="Requirement key, e.g. CRT-1730")
    p.add_argument(
        "--storage-file",
        help="Offline: JSON with storage HTML (MCP get_page raw or REST response)",
    )
    p.add_argument(
        "--cookie",
        default=os.environ.get("CONFLUENCE_SESSION_COOKIE"),
        help="Session cookie for REST (or env CONFLUENCE_SESSION_COOKIE)",
    )
    p.add_argument(
        "--base-url",
        default=os.environ.get("CONFLUENCE_BASE_URL", DEFAULT_HOST).rstrip("/"),
    )
    p.add_argument(
        "--compare",
        action="store_true",
        help="Include full storage size vs snippet length in output",
    )
    p.add_argument("--timeout", type=float, default=60.0)
    args = p.parse_args()

    meta: dict = {}
    try:
        if args.storage_file:
            storage = _load_storage_from_file(args.storage_file)
            meta["source"] = "storage_file"
        else:
            if not args.page_id:
                print(
                    json.dumps({"error": "Provide --page-id or --storage-file"}),
                    file=sys.stderr,
                )
                return 2
            storage, meta = fetch_body_storage(
                args.page_id,
                base_url=args.base_url,
                cookie=args.cookie,
                timeout=args.timeout,
            )
            meta["source"] = "rest_storage"
    except (OSError, ValueError, RuntimeError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False), file=sys.stderr)
        return 1

    er = extract_requirement_snippet(storage, args.req)
    out: dict = {
        "requirement_key": er.requirement_key,
        "mode": er.mode,
        "snippet_text": er.text,
        "snippet_chars": len(er.text),
        "candidates_considered": er.candidates_considered,
        "selected_reason": er.selected_reason,
    }
    if args.compare or meta.get("source") == "rest_storage":
        out["storage_html_chars"] = len(storage)
        if meta.get("rest_response_bytes") is not None:
            out["rest_json_bytes"] = meta["rest_response_bytes"]
        if er.text and len(storage) > 0:
            out["storage_to_snippet_ratio"] = round(len(er.text) / len(storage) * 100, 4)

    if meta.get("page_id"):
        out["page_id"] = meta["page_id"]

    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0 if er.mode not in ("key_not_found", "macro_end_not_found") else 3


if __name__ == "__main__":
    raise SystemExit(main())
