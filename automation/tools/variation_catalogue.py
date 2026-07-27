"""Variation catalogue + structural parameter inventory helpers (D18).

Epic-agnostic: inventory from snippet structure; mandates from docs/variation-catalogue.json.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOGUE_PATH = REPO_ROOT / "docs" / "variation-catalogue.json"

# Name — Spec / Name: Spec (not markdown table)
PAIR_RE = re.compile(
    r"^\s*([A-Za-z][A-Za-z0-9 /_+%-]{1,40}?)\s*[—–\-:]\s+(.+?)\s*$"
)
# Markdown table data row: | Name | Spec |
TABLE_ROW_RE = re.compile(
    r"^\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|"
)
# Semicolon / period-separated "Name … signed; Name …"
INLINE_PARAM_RE = re.compile(
    r"\b([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)\s*[:—–-]?\s*"
    r"((?:(?![.;]?\s*[A-Z][a-z]+(?:\s+[A-Z])?).)+)",
)

_catalogue_cache: dict[str, Any] | None = None


def load_catalogue(path: Path | None = None) -> dict[str, Any]:
    global _catalogue_cache
    p = path or CATALOGUE_PATH
    if _catalogue_cache is not None and path is None:
        return _catalogue_cache
    with p.open(encoding="utf-8") as f:
        data = json.load(f)
    if path is None:
        _catalogue_cache = data
    return data


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def extract_parameter_inventory(snippet: str) -> list[dict[str, str]]:
    """Structural extract: markdown table rows or Name—Spec lines; no field whitelist."""
    if not snippet or not str(snippet).strip():
        return []
    seen: set[str] = set()
    out: list[dict[str, str]] = []

    def add(name: str, spec: str, source: str) -> None:
        n = name.strip()
        sp = spec.strip()
        if len(n) < 2 or len(sp) < 2:
            return
        if n.lower() in ("parameter", "name", "field", "value", "description"):
            # skip header-ish cells when they look like column titles with empty meaning
            if sp.lower() in ("description", "spec", "format", "value", "notes"):
                return
        key = _norm(n)
        if key in seen:
            return
        seen.add(key)
        out.append({"name": n, "spec_text": sp, "source_line": source.strip()[:240]})

    lines = str(snippet).splitlines()
    for line in lines:
        raw = line.strip()
        if not raw or set(raw) <= set("|-: "):
            continue
        tm = TABLE_ROW_RE.match(raw)
        if tm:
            add(tm.group(1), tm.group(2), raw)
            continue
        pm = PAIR_RE.match(raw)
        if pm:
            add(pm.group(1), pm.group(2), raw)
            continue

    # Fallback: prose with semicolon/comma-separated "Name … rule" clauses
    if len(out) < 2:
        blob = re.sub(r"\s+", " ", str(snippet))
        # Split on ; or . that look like clause breaks
        for clause in re.split(r"[;]|\\. (?=[A-Z])", blob):
            clause = clause.strip()
            if len(clause) < 8:
                continue
            m = re.match(
                r"^([A-Za-z][A-Za-z0-9 ]{1,40}?)\s+"
                r"((?:shows|is|displays|colored|signed|unsigned|with|Buy|Sell|collapsed|renders).+)$",
                clause,
                re.I,
            )
            if m:
                add(m.group(1), m.group(2), clause)

    return out


def _rule_matches(rule: dict[str, Any], spec_norm: str) -> bool:
    match_any = [_norm(x) for x in (rule.get("match_any") or []) if x]
    if not match_any:
        return False
    if not any(tok in spec_norm for tok in match_any):
        return False
    groups = rule.get("require_all_groups")
    if not groups:
        return True
    for group in groups:
        toks = [_norm(t) for t in group]
        if not any(t in spec_norm for t in toks):
            return False
    return True


def match_rule(spec_text: str, catalogue: dict[str, Any] | None = None) -> dict[str, Any] | None:
    cat = catalogue or load_catalogue()
    spec_norm = _norm(spec_text)
    for rule in cat.get("rules") or []:
        if isinstance(rule, dict) and _rule_matches(rule, spec_norm):
            return rule
    return None


def mandated_variations_for_inventory(
    inventory: list[dict[str, Any]],
    catalogue: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Return (mandated variation descriptors, unmatched inventory rows)."""
    cat = catalogue or load_catalogue()
    fallback = cat.get("fallback") or {}
    mandated: list[dict[str, Any]] = []
    unmatched: list[dict[str, str]] = []

    # Collapse: group by (rule_id, normalized identical spec) when rule.collapse
    collapse_buckets: dict[str, list[dict[str, Any]]] = {}
    non_collapse: list[tuple[dict[str, Any], dict[str, Any]]] = []

    for row in inventory:
        if not isinstance(row, dict):
            continue
        name = str(row.get("name") or "").strip()
        spec = str(row.get("spec_text") or "").strip()
        if not name or not spec:
            continue
        rule = match_rule(spec, cat)
        if rule is None:
            unmatched.append({"name": name, "spec_text": spec})
            if fallback.get("record_unmatched"):
                for m in fallback.get("mandates") or []:
                    mandated.append(
                        {
                            "rule_id": str(fallback.get("id") or "plain_presence"),
                            "kind": str(m.get("kind") or "positive"),
                            "parameter": name,
                            "assertion_hint": str(m.get("assertion_hint") or ""),
                            "needs_setup": False,
                            "collapsed_parameters": [name],
                        }
                    )
            continue
        if rule.get("collapse"):
            key = f"{rule.get('id')}::{_norm(spec)}"
            collapse_buckets.setdefault(key, []).append({"row": row, "rule": rule})
        else:
            non_collapse.append((row, rule))

    for _key, items in collapse_buckets.items():
        rule = items[0]["rule"]
        names = [str(i["row"].get("name") or "") for i in items]
        param_label = " and ".join(names)
        for m in rule.get("mandates") or []:
            mandated.append(
                {
                    "rule_id": str(rule.get("id")),
                    "kind": str(m.get("kind") or "positive"),
                    "parameter": param_label,
                    "assertion_hint": str(m.get("assertion_hint") or ""),
                    "needs_setup": bool(rule.get("needs_setup")),
                    "collapsed_parameters": names,
                }
            )

    for row, rule in non_collapse:
        name = str(row.get("name") or "")
        for m in rule.get("mandates") or []:
            suffix = m.get("parameter_suffix")
            param = f"{name}:{suffix}" if suffix else name
            mandated.append(
                {
                    "rule_id": str(rule.get("id")),
                    "kind": str(m.get("kind") or "positive"),
                    "parameter": param,
                    "assertion_hint": str(m.get("assertion_hint") or ""),
                    "needs_setup": bool(rule.get("needs_setup")),
                    "collapsed_parameters": [name],
                }
            )

    return mandated, unmatched


def variation_key(v: dict[str, Any]) -> str:
    return f"{v.get('rule_id')}|{v.get('kind')}|{_norm(str(v.get('parameter') or ''))}"


def obligation_variation_key(obl: dict[str, Any]) -> str | None:
    var = obl.get("variation")
    if not isinstance(var, dict):
        return None
    rule_id = var.get("rule_id")
    kind = var.get("kind")
    param = var.get("parameter")
    if not rule_id or not kind or not param:
        return None
    return f"{rule_id}|{kind}|{_norm(str(param))}"
