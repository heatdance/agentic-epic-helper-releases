#!/usr/bin/env python3
"""
Resolve Devexperts Confluence "Yogi" requirement links to structured parts.

Without authentication, /requirements/{space}/{KEY} usually redirects to login; this
tool still normalizes inputs and can follow redirects when you pass a session
cookie (see --cookie / CONFLUENCE_SESSION_COOKIE).

Usage:
  python yogi_resolve.py CRT-1741 --space CT
  python yogi_resolve.py "https://confluence.in.devexperts.com/requirements/CT/CRT-1741"
  python yogi_resolve.py "https://.../pages/345721535/Title#req-CRT-1741"
  python yogi_resolve.py "https://.../requirements/CT/CRT-1741" --follow --cookie "JSESSIONID=..."
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, urlunparse

_TOOLS = Path(__file__).resolve().parent

# Short link: https://confluence.../requirements/CT/CRT-1741
_RE_SHORT = re.compile(
    r"^https?://[^/]+/requirements/([^/]+)/((?:CRT|SET|XT|[A-Z]{2,})-\d+)/?\s*$",
    re.IGNORECASE,
)
# Bare requirement key
_RE_KEY = re.compile(r"^((?:CRT|SET|XT|[A-Z]{2,})-\d+)$", re.IGNORECASE)
# pageId= in query
_RE_PAGE_ID_QUERY = re.compile(r"(?:^|[?&])pageId=(\d+)", re.IGNORECASE)
# /spaces/KEY/pages/12345/...
_RE_PAGES_PATH = re.compile(r"/spaces/([^/]+)/pages/(\d+)(?:/|$)", re.IGNORECASE)
# Fragment #req-CRT-1741
_RE_ANCHOR = re.compile(r"#(req-(?:CRT|SET|XT|[A-Z]{2,}-\d+))$", re.IGNORECASE)

DEFAULT_HOST = "https://confluence.in.devexperts.com"


@dataclass
class YogiResolution:
    requirement_key: str
    space_key: str
    short_url: str
    anchor: str
    page_id: Optional[str] = None
    final_url: Optional[str] = None
    canonical_url_with_anchor: Optional[str] = None
    login_redirect: bool = False
    notes: list[str] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)


def parse_short_url(url: str) -> tuple[str, str]:
    m = _RE_SHORT.match(url.strip())
    if not m:
        raise ValueError(f"Not a /requirements/{{space}}/{{KEY}} URL: {url!r}")
    space, key = m.group(1), m.group(2)
    return space.upper(), key.upper()


def parse_canonical_url(url: str) -> tuple[Optional[str], Optional[str], Optional[str], str]:
    """
    Returns (space_key, page_id, anchor_without_hash, requirement_key or "").
    requirement_key from anchor if present.
    """
    parsed = urlparse(url.strip())
    space_key: Optional[str] = None
    page_id: Optional[str] = None
    anchor_fragment: Optional[str] = None
    req_from_anchor = ""

    m_path = _RE_PAGES_PATH.search(parsed.path or "")
    if m_path:
        space_key = m_path.group(1).upper()
        page_id = m_path.group(2)

    mq = _RE_PAGE_ID_QUERY.search(parsed.query or "")
    if mq:
        page_id = mq.group(1)

    if parsed.fragment:
        ma = _RE_ANCHOR.match("#" + parsed.fragment)
        if ma:
            anchor_fragment = ma.group(1)
            mkey = re.match(r"^req-((?:CRT|SET|XT|[A-Z]{2,}-\d+))$", anchor_fragment, re.I)
            if mkey:
                req_from_anchor = mkey.group(1).upper()

    return space_key, page_id, anchor_fragment, req_from_anchor


def build_short_url(host: str, space_key: str, requirement_key: str) -> str:
    base = host.rstrip("/")
    return f"{base}/requirements/{space_key}/{requirement_key}"


def follow_redirects(
    url: str,
    cookie: Optional[str],
    timeout: float,
) -> tuple[str, bool]:
    """
    GET url, follow redirects, return (final_url, looks_like_login).
    """
    headers = {
        "User-Agent": "cursor.corner-yogi-resolve/1.0 (+QA workspace)",
        "Accept": "text/html,*/*",
    }
    if cookie:
        headers["Cookie"] = cookie.strip()

    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        final = resp.geturl()

    parsed = urlparse(final)
    login = "login.action" in (parsed.path or "").lower()
    return final, login


def extract_page_id_from_url(url: str) -> Optional[str]:
    sk, pid, _, _ = parse_canonical_url(url)
    if pid:
        return pid
    mq = _RE_PAGE_ID_QUERY.search(url)
    return mq.group(1) if mq else None


def resolve(
    input_value: str,
    *,
    space_default: Optional[str],
    host: str,
    follow: bool,
    cookie: Optional[str],
    timeout: float,
) -> YogiResolution:
    notes: list[str] = []
    s = input_value.strip()
    requirement_key: str
    space_key: str

    # 1) Full canonical URL with optional fragment
    if s.startswith("http://") or s.startswith("https://"):
        if "/requirements/" in s:
            space_key, requirement_key = parse_short_url(s)
            short_url = s.split("?", 1)[0].rstrip("/")
            if not short_url.endswith(requirement_key):
                short_url = build_short_url(host, space_key, requirement_key)
            anchor = f"req-{requirement_key}"
            res = YogiResolution(
                requirement_key=requirement_key,
                space_key=space_key,
                short_url=short_url,
                anchor=anchor,
                notes=list(notes),
            )
            if follow:
                return _apply_follow(res, cookie, timeout, host)
            notes.append(
                "Without --follow, only normalized URLs are returned. Unauthenticated HTTP often redirects to login."
            )
            res.notes = notes
            return res
        else:
            sk, pid, anchor_frag, req_a = parse_canonical_url(s)
            if not req_a and not pid:
                raise ValueError(
                    "URL is not a /requirements/ short link nor a Confluence page URL with pageId/pages/ path."
                )
            requirement_key = req_a
            space_key = (sk or space_default or "").strip().upper()
            if not requirement_key and pid:
                notes.append(
                    "Page URL has no #req-... anchor; pass requirement key as input or use short /requirements/ URL."
                )
                requirement_key = "UNKNOWN"
            if not space_key:
                space_key = (space_default or "").strip().upper()
            if not space_key:
                raise ValueError(
                    "Could not infer space key from URL; pass --space CT (or your space)."
                )
            short_url = build_short_url(host, space_key, requirement_key if requirement_key != "UNKNOWN" else "CRT-0")
            if requirement_key == "UNKNOWN":
                short_url = s  # don't invent
            anchor = f"req-{requirement_key}" if requirement_key != "UNKNOWN" else ""
            res = YogiResolution(
                requirement_key=requirement_key,
                space_key=space_key,
                short_url=short_url if requirement_key != "UNKNOWN" else s,
                anchor=anchor,
                page_id=pid,
                notes=notes,
            )
            if pid and anchor:
                p = urlparse(s)
                rebuilt = urlunparse(
                    (p.scheme, p.netloc, p.path, p.params, p.query, anchor)
                )
                res.canonical_url_with_anchor = rebuilt
            if follow and requirement_key != "UNKNOWN":
                return _apply_follow(res, cookie, timeout, host)
            if not follow:
                notes.append(
                    "Use confluence_get_page(page_id=...) via MCP for body text, or --follow with a session cookie to resolve redirects."
                )
            res.notes = notes
            return res

    # 2) Bare KEY
    m = _RE_KEY.match(s)
    if m:
        requirement_key = m.group(1).upper()
        if not space_default:
            raise ValueError("Pass --space CT (or the Confluence space key) for a bare requirement key.")
        space_key = space_default.strip().upper()
        short_url = build_short_url(host, space_key, requirement_key)
    else:
        raise ValueError(f"Unrecognized input: {input_value!r}")

    anchor = f"req-{requirement_key}"
    res = YogiResolution(
        requirement_key=requirement_key,
        space_key=space_key,
        short_url=short_url,
        anchor=anchor,
        notes=notes,
    )
    if follow:
        res = _apply_follow(res, cookie, timeout, host)
    else:
        notes.append(
            "Without --follow, only normalized URLs are returned. Unauthenticated HTTP often redirects to login."
        )
        res.notes = notes
    return res


def _apply_follow(
    res: YogiResolution,
    cookie: Optional[str],
    timeout: float,
    host: str,
) -> YogiResolution:
    notes = list(res.notes)
    try:
        final, login = follow_redirects(res.short_url, cookie, timeout)
    except urllib.error.HTTPError as e:
        notes.append(f"HTTP error following short URL: {e.code} {e.reason}")
        res.notes = notes
        return res
    except OSError as e:
        notes.append(f"Network error: {e}")
        res.notes = notes
        return res

    res.final_url = final
    res.login_redirect = login
    if login:
        notes.append(
            "Redirect ended on login.action; pass --cookie with a valid Confluence session or use MCP inside Cursor."
        )
    else:
        pid = extract_page_id_from_url(final)
        if pid:
            res.page_id = pid
        parsed = urlparse(final)
        frag = res.anchor
        rebuilt = urlunparse(
            (parsed.scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, frag)
        )
        res.canonical_url_with_anchor = rebuilt
        notes.append("Follow completed; use page_id with Atlassian MCP confluence_get_page.")
    res.notes = notes
    return res


def main() -> int:
    p = argparse.ArgumentParser(description="Resolve Yogi requirement URLs to page id + anchor hints.")
    p.add_argument("input", help="CRT-… key, short /requirements/… URL, or full page URL with #req-…")
    p.add_argument(
        "--space",
        default=os.environ.get("CONFLUENCE_SPACE_KEY"),
        help="Space key when input is a bare requirement key (or env CONFLUENCE_SPACE_KEY)",
    )
    p.add_argument(
        "--host",
        default=os.environ.get("CONFLUENCE_BASE_URL", DEFAULT_HOST).rstrip("/"),
        help="Confluence base URL (default: Devexperts)",
    )
    p.add_argument(
        "--follow",
        action="store_true",
        help="GET short URL and follow redirects (needs session cookie for private instances)",
    )
    p.add_argument(
        "--cookie",
        default=os.environ.get("CONFLUENCE_SESSION_COOKIE"),
        help="Cookie header value, e.g. JSESSIONID=... (or env CONFLUENCE_SESSION_COOKIE)",
    )
    p.add_argument("--timeout", type=float, default=30.0)
    p.add_argument(
        "--snippet",
        action="store_true",
        help="After resolve, fetch body.storage via REST and extract only this requirement's text (needs page_id + --cookie)",
    )
    args = p.parse_args()

    try:
        out = resolve(
            args.input,
            space_default=args.space,
            host=args.host,
            follow=args.follow,
            cookie=args.cookie,
            timeout=args.timeout,
        )
    except ValueError as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        return 2

    payload: dict = asdict(out)
    exit_code = 0
    if args.snippet:
        if str(_TOOLS) not in sys.path:
            sys.path.insert(0, str(_TOOLS))
        from yogi_confluence import fetch_body_storage
        from yogi_extract import extract_requirement_snippet

        sn: dict = {"enabled": True}
        er = None
        if not out.page_id:
            sn["error"] = (
                "page_id missing; use a canonical URL with pageId/pages/ path, or --follow with --cookie"
            )
        elif not (args.cookie and args.cookie.strip()):
            sn["error"] = "REST fetch needs --cookie (or CONFLUENCE_SESSION_COOKIE)"
        else:
            try:
                storage, meta = fetch_body_storage(
                    out.page_id,
                    base_url=args.host,
                    cookie=args.cookie,
                    timeout=max(args.timeout, 60.0),
                )
                er = extract_requirement_snippet(storage, out.requirement_key)
                sn["snippet_text"] = er.text
                sn["snippet_chars"] = len(er.text)
                sn["extract_mode"] = er.mode
                sn["candidates_considered"] = er.candidates_considered
                sn["selected_reason"] = er.selected_reason
                sn["storage_html_chars"] = len(storage)
                sn["rest_json_bytes"] = meta.get("rest_response_bytes")
                if er.text and storage:
                    sn["storage_to_snippet_ratio_percent"] = round(
                        len(er.text) / len(storage) * 100, 4
                    )
            except (OSError, RuntimeError, ValueError) as e:
                sn["error"] = str(e)
                exit_code = 1
        if (
            er is not None
            and exit_code == 0
            and (
                er.mode in ("key_not_found", "macro_end_not_found")
                or not (er.text or "").strip()
            )
        ):
            exit_code = 3
        payload["snippet_fetch"] = sn

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
