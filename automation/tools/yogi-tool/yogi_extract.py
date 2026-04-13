"""Extract Yogi requirement text from Confluence storage HTML (requirement macro by key)."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field

# Snippets shorter than this are treated as low-confidence unless no better candidate exists.
MIN_SUBSTANTIVE_LEN = 40

# Higher = preferred when picking among macros with the same key (e.g. LINK in table vs DEFINITION in heading).
_TYPE_RANK = {
    "DEFINITION": 100,
    "": 30,
    "LINK": 5,
}

_TD_SEARCH_WINDOW = 25_000
_H2P_SEARCH_WINDOW = 12_000


@dataclass
class ExtractResult:
    requirement_key: str
    text: str
    mode: str  # inline_td | after_th_td | definition_h2_p | key_not_found | macro_end_not_found
    storage_html_chars: int = 0
    candidates_considered: int = 0
    selected_reason: str = ""  # e.g. best_of_n_macros | single_candidate | fallback_first


def _strip_storage_to_text(fragment: str) -> str:
    """Remove Confluence/storage tags; keep readable text."""
    s = fragment
    s = re.sub(r"<ac:structured-macro[^>]*>.*?</ac:structured-macro>", " ", s, flags=re.DOTALL | re.IGNORECASE)
    s = re.sub(r"<ac:emoticon[^>]*/>", " ", s, flags=re.IGNORECASE)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _fold_requirement_macros_to_keys(fragment: str) -> str:
    """Replace nested requirement macros with their key parameter (e.g. CRT-1741)."""

    def repl(mm: re.Match[str]) -> str:
        mk = re.search(
            r'ac:name="key">((?:CRT|SET|XT|[A-Z]{2,})-\d+)</ac:parameter>',
            mm.group(0),
            re.I,
        )
        if mk:
            return " " + mk.group(1).upper() + " "
        return " "

    return re.sub(
        r"<ac:structured-macro[^>]*>.*?</ac:structured-macro>",
        repl,
        fragment,
        flags=re.DOTALL | re.IGNORECASE,
    )


def _parse_macro_type(macro_xml: str) -> str:
    m = re.search(
        r'<ac:parameter ac:name="type">([^<]*)</ac:parameter>',
        macro_xml,
        re.IGNORECASE,
    )
    if not m:
        m = re.search(
            r"<ac:parameter ac:name='type'>([^<]*)</ac:parameter>",
            macro_xml,
            re.IGNORECASE,
        )
    return (m.group(1) or "").strip().upper() if m else ""


def _extract_td_after_macro(storage_html: str, macro_end_j: int) -> tuple[str, str]:
    """Text from end of requirement macro to first </td> within a bounded window."""
    rest = storage_html[macro_end_j : macro_end_j + _TD_SEARCH_WINDOW]
    close = rest.find("</td>")
    if close < 0:
        return "", "macro_end_not_found"
    fragment = rest[:close]
    text = _strip_storage_to_text(fragment)
    mode = "after_th_td" if "</th>" in fragment[:800] else "inline_td"
    return text, mode


def _extract_definition_h2_first_p(storage_html: str, macro_end_j: int) -> tuple[str, str] | None:
    """
    Pattern: ...</ac:structured-macro></h2><p>...</p> (macro closes immediately before </h2>).
    macro_end_j points to the first character after </ac:structured-macro>.
    """
    window = storage_html[macro_end_j : macro_end_j + _H2P_SEARCH_WINDOW]
    m = re.match(r"\s*</h2>\s*<p[^>]*>", window, re.IGNORECASE)
    if not m:
        return None
    start_p = macro_end_j + m.end()
    end_p = storage_html.find("</p>", start_p)
    if end_p < 0 or end_p - start_p > 50_000:
        return None
    inner = storage_html[start_p:end_p]
    inner = _fold_requirement_macros_to_keys(inner)
    text = _strip_storage_to_text(inner)
    if not text:
        return None
    return text, "definition_h2_p"


def _score_candidate(macro_type: str, text: str) -> tuple[int, int]:
    """
    Return a sortable key (higher is better).
    Tie-break: longer substantive text wins.
    """
    rank = _TYPE_RANK.get(macro_type, 15)
    ln = len(text.strip())
    if ln < MIN_SUBSTANTIVE_LEN:
        rank -= 80
    return (rank, ln)


def _find_requirement_macro_bounds(storage_html: str, key_idx: int, needle_len: int) -> tuple[int, int] | None:
    """Return (macro_open, index_after_closing_structured_macro) or None if invalid."""
    macro_open = storage_html.rfind("<ac:structured-macro", 0, key_idx)
    if macro_open < 0:
        return None
    macro_head = storage_html[macro_open : key_idx + needle_len]
    if 'ac:name="requirement"' not in macro_head and "ac:name='requirement'" not in macro_head:
        return None
    end_macro = storage_html.find("</ac:structured-macro>", key_idx)
    if end_macro < 0:
        return None
    j = end_macro + len("</ac:structured-macro>")
    return macro_open, j


def _iter_key_needle_positions(storage_html: str, key: str) -> list[int]:
    positions: list[int] = []
    needles = (
        f'<ac:parameter ac:name="key">{key}</ac:parameter>',
        f"<ac:parameter ac:name='key'>{key}</ac:parameter>",
    )
    for needle in needles:
        start = 0
        while True:
            idx = storage_html.find(needle, start)
            if idx < 0:
                break
            positions.append(idx)
            start = idx + 1
    return sorted(set(positions))


def _candidates_for_one_macro(storage_html: str, macro_open: int, macro_end_j: int) -> list[tuple[str, str, str]]:
    """Return list of (text, mode, macro_type) for this macro instance."""
    macro_xml = storage_html[macro_open:macro_end_j]
    mtype = _parse_macro_type(macro_xml)
    out: list[tuple[str, str, str]] = []

    h2p = _extract_definition_h2_first_p(storage_html, macro_end_j)
    if h2p:
        out.append((h2p[0], h2p[1], mtype))

    td_text, td_mode = _extract_td_after_macro(storage_html, macro_end_j)
    if td_mode != "macro_end_not_found":
        out.append((td_text, td_mode, mtype))

    return out


def _best_for_macro(storage_html: str, macro_open: int, macro_end_j: int) -> tuple[str, str, str, tuple[int, int]] | None:
    """Best (text, mode, macro_type, score) for a single macro occurrence."""
    macro_xml = storage_html[macro_open:macro_end_j]
    mtype = _parse_macro_type(macro_xml)
    candidates = _candidates_for_one_macro(storage_html, macro_open, macro_end_j)
    if not candidates:
        return None

    best: tuple[str, str, str, tuple[int, int]] | None = None
    for text, mode, mt in candidates:
        sc = _score_candidate(mt or mtype, text)
        cand = (text, mode, mt or mtype, sc)
        if best is None or sc > best[3]:
            best = cand
    return best


def extract_requirement_snippet(storage_html: str, requirement_key: str) -> ExtractResult:
    """
    Find ac:name="requirement" macros with the given key; pick the best snippet by macro type and length.

    Patterns seen in CT:
    - Inline: </ac:structured-macro> prose ... </td>   (e.g. CRT-1730 on Portfolio Metrics)
    - Adjacent: macro in </th> then next <td> ... </td> (e.g. CRT-1741 on Functional Configuration)
    - Definition in heading: </ac:structured-macro></h2><p>prose</p> (e.g. CRT-1738 vs duplicate LINK in table)
    """
    key = requirement_key.strip().upper()
    n = len(storage_html)

    key_indices = _iter_key_needle_positions(storage_html, key)
    if not key_indices:
        return ExtractResult(
            key,
            "",
            "key_not_found",
            n,
            0,
            "no_key_parameter_match",
        )

    macro_starts_seen: set[tuple[int, int]] = set()
    per_macro_best: list[tuple[str, str, str, tuple[int, int]]] = []

    needles = (
        f'<ac:parameter ac:name="key">{key}</ac:parameter>',
        f"<ac:parameter ac:name='key'>{key}</ac:parameter>",
    )

    for key_idx in key_indices:
        needle_len: int | None = None
        for needle in needles:
            end = key_idx + len(needle)
            if storage_html[key_idx:end] == needle:
                needle_len = len(needle)
                break
        if needle_len is None:
            continue
        bounds = _find_requirement_macro_bounds(storage_html, key_idx, needle_len)
        if bounds is None:
            continue
        mo, mj = bounds
        sig = (mo, mj)
        if sig in macro_starts_seen:
            continue
        macro_starts_seen.add(sig)
        one = _best_for_macro(storage_html, mo, mj)
        if one:
            per_macro_best.append(one)

    if not per_macro_best:
        return ExtractResult(
            key,
            "",
            "macro_end_not_found",
            n,
            len(key_indices),
            "key_found_but_not_in_requirement_macro",
        )

    overall = max(per_macro_best, key=lambda x: x[3])
    text, mode, _mtype, _sc = overall
    reason = "best_of_n_macros" if len(per_macro_best) > 1 else "single_candidate"

    if not text.strip():
        return ExtractResult(
            key,
            "",
            "macro_end_not_found",
            n,
            len(per_macro_best),
            "empty_after_extraction",
        )

    return ExtractResult(
        key,
        text,
        mode,
        n,
        len(per_macro_best),
        reason,
    )
