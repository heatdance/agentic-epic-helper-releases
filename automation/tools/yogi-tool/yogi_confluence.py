"""Fetch Confluence page body.storage via REST (compact vs full page export)."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Optional


def fetch_body_storage(
    page_id: str,
    *,
    base_url: str,
    cookie: Optional[str],
    timeout: float = 60.0,
) -> tuple[str, dict]:
    """
    GET /rest/api/content/{id}?expand=body.storage
    Returns (storage_html, raw_meta_dict with size and status).
    """
    base = base_url.rstrip("/")
    url = f"{base}/rest/api/content/{page_id}?expand=body.storage"
    headers = {
        "User-Agent": "cursor.corner-yogi-snippet/1.0 (+QA workspace)",
        "Accept": "application/json",
    }
    if cookie and cookie.strip():
        headers["Cookie"] = cookie.strip()

    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise RuntimeError(f"Confluence REST HTTP {e.code}: {body[:500]}") from e

    data = json.loads(raw)
    storage = (
        data.get("body", {})
        .get("storage", {})
        .get("value", "")
    )
    meta = {
        "rest_response_bytes": len(raw.encode("utf-8")),
        "storage_html_chars": len(storage),
        "page_id": page_id,
    }
    return storage, meta
