#!/usr/bin/env python3
"""Epic category + TCD size bucketing for CRTQA stats v5."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CATEGORIES = REPO_ROOT / "stats" / "epic-stats" / "temp" / "categories.json"
EPICS_ROOT = REPO_ROOT / "epics"

TOP_CATEGORY_ORDER = ("fe", "be", "api", "other")
TOP_CATEGORY_LABELS = {
    "fe": "FE Epic",
    "be": "BE Epic",
    "api": "API / Integration",
    "other": "Other",
}
SIZE_LABELS = {
    "small_tcd": "Small TCD (≤16h)",
    "big_tcd": "Big TCD (>16h)",
}


def load_categories(path: Path | None = None) -> dict[str, Any]:
    p = path or DEFAULT_CATEGORIES
    return json.loads(p.read_text(encoding="utf-8"))


def _epic_ref_path(epic_key: str) -> Path | None:
    d = EPICS_ROOT / epic_key
    if not d.is_dir():
        return None
    p = d / f"{epic_key}-ref.json"
    if p.is_file():
        return p
    ctx = d / "context" / f"{epic_key}-ref.json"
    return ctx if ctx.is_file() else None


def _append_text_parts(parts: list[str], values: Any) -> None:
    if not values:
        return
    if isinstance(values, str):
        parts.append(values)
        return
    if not isinstance(values, list):
        parts.append(str(values))
        return
    for item in values:
        if isinstance(item, str):
            parts.append(item)
        elif isinstance(item, dict):
            parts.append(str(item.get("text") or item.get("name") or item.get("label") or ""))
        else:
            parts.append(str(item))


def _text_blob_from_ref(ref: dict[str, Any]) -> str:
    parts: list[str] = []
    epic = ref.get("epic") or {}
    parts.append(str(epic.get("summary") or ""))
    _append_text_parts(parts, epic.get("labels") or [])
    syn = ref.get("synthesis") or {}
    parts.append(str(syn.get("problem_gist") or ""))
    _append_text_parts(parts, syn.get("keywords") or [])
    _append_text_parts(parts, syn.get("impact_areas") or [])
    csi = ref.get("client_shell_impact") or {}
    for shell in ("corner_trader", "adaptive", "dxtrade5", "webbroker"):
        block = csi.get(shell) or {}
        if isinstance(block, dict):
            parts.append(str(block.get("note") or ""))
            parts.append(str(block.get("evidence") or ""))
            if str(block.get("status") or "").lower() == "affected":
                parts.append(shell)
    return " ".join(parts).lower()


def _text_blob_from_jira(issue: dict[str, Any]) -> str:
    parts: list[str] = []
    parts.append(str(issue.get("summary") or ""))
    parts.append(str(issue.get("description") or "")[:2000])
    parts.extend(issue.get("labels") or [])
    for comp in issue.get("components") or []:
        if isinstance(comp, dict):
            parts.append(str(comp.get("name") or ""))
        else:
            parts.append(str(comp))
    return " ".join(parts).lower()


def _score_categories(text: str, categories_cfg: dict[str, Any]) -> tuple[str, str, int]:
    scores: dict[str, int] = {}
    for cat in categories_cfg.get("categories") or []:
        cid = str(cat.get("id") or "")
        if cid == "other":
            continue
        hints = cat.get("mapping_hints") or []
        scores[cid] = sum(1 for h in hints if h.lower() in text)
    best_id = "other"
    best_score = 0
    for cid in TOP_CATEGORY_ORDER:
        if scores.get(cid, 0) > best_score:
            best_score = scores[cid]
            best_id = cid
    if best_id == "cross_cutting":
        best_id = "other"
    conf = "high" if best_score >= 2 else ("medium" if best_score == 1 else "low")
    return best_id, conf, best_score


def classify_epic(
    epic_key: str,
    jira_issue: dict[str, Any] | None = None,
    categories_cfg: dict[str, Any] | None = None,
) -> dict[str, Any]:
    cfg = categories_cfg or load_categories()
    ref_path = _epic_ref_path(epic_key)
    source = "jira"
    text = ""
    if ref_path:
        ref = json.loads(ref_path.read_text(encoding="utf-8"))
        text = _text_blob_from_ref(ref)
        source = "epic_ref"
    if jira_issue:
        jira_text = _text_blob_from_jira(jira_issue)
        text = f"{text} {jira_text}".strip()
        source = "epic_ref+jira" if source == "epic_ref" else "jira"
    if not text.strip():
        text = epic_key.lower()
        source = "fallback"
    cat_id, confidence, score = _score_categories(text, cfg)
    return {
        "epic_key": epic_key,
        "category_id": cat_id,
        "category_label": TOP_CATEGORY_LABELS[cat_id],
        "category_confidence": confidence,
        "hint_score": score,
        "classification_source": source,
    }


def tcd_size_band(estimate_hours: float, small_max: float = 16.0) -> str:
    if estimate_hours <= small_max:
        return "small_tcd"
    return "big_tcd"


CATEGORY_SHORT = {
    "fe": "FE",
    "be": "BE",
    "api": "API",
    "other": "Other",
}


def category_size_label(category_id: str, size_id: str) -> str:
    cat = CATEGORY_SHORT.get(category_id or "other", "Other")
    suffix = "S" if size_id == "small_tcd" else "B"
    return f"{cat}+{suffix}"


def epic_size_from_rows(rows: list[dict], *, small_max: float = 16.0) -> str:
    if not rows:
        return "small_tcd"
    max_draft = max(float(r.get("estimate") or r.get("draft_estimate_hours") or 0) for r in rows)
    return tcd_size_band(max_draft, small_max)


def category_justification(classification: dict) -> str:
    src = str(classification.get("classification_source") or "fallback")
    rationale = str(classification.get("rationale") or "").strip()
    if src == "manual_review" and rationale:
        return rationale
    conf = str(classification.get("category_confidence") or "low")
    score = int(classification.get("hint_score") or 0)
    if src == "epic_ref":
        return f"Classified from epic ref ({conf} confidence, hint score {score})."
    if src == "epic_ref+jira":
        return f"Classified from epic ref and Jira ({conf} confidence, hint score {score})."
    if src == "jira":
        return f"Classified from Jira epic summary/labels ({conf} confidence, hint score {score})."
    return (
        f"Low signal ({conf}); default Other — run EPIC-PREP for a ref to improve hints."
    )
