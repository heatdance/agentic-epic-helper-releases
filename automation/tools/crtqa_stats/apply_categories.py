#!/usr/bin/env python3
"""Apply manual epic category registry to CRTQA stats v5 state."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from crtqa_stats.categories import TOP_CATEGORY_LABELS, classify_epic
from crtqa_stats.ingest import REPO_ROOT, load_contract

VALID_CATEGORIES = frozenset({"fe", "be", "api", "other"})


def epic_categories_path(contract: dict[str, Any] | None = None) -> Path:
    c = contract or load_contract()
    rel = (c.get("paths") or {}).get(
        "epic_categories", "stats/crtqa-stats/epic-categories.json"
    )
    return REPO_ROOT / rel


def load_epic_categories(contract: dict[str, Any] | None = None) -> dict[str, Any]:
    path = epic_categories_path(contract)
    if not path.is_file():
        return {"schema_version": 1, "reviews": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    reviews = data.get("reviews") or {}
    for key, rev in reviews.items():
        cid = str(rev.get("category_id") or "other").lower()
        if cid not in VALID_CATEGORIES:
            raise ValueError(f"Invalid category_id {cid!r} for epic {key}")
    return data


def save_epic_categories(data: dict[str, Any], contract: dict[str, Any] | None = None) -> Path:
    path = epic_categories_path(contract)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def jira_blob_from_meta(meta: dict[str, Any] | None) -> dict[str, Any] | None:
    if not meta:
        return None
    components: list[dict[str, str]] = []
    for c in meta.get("components") or []:
        if isinstance(c, dict):
            components.append({"name": str(c.get("name") or "")})
        else:
            components.append({"name": str(c)})
    return {
        "summary": meta.get("summary"),
        "labels": meta.get("labels") or [],
        "components": components,
        "description": meta.get("description") or "",
    }


def get_review(epic_key: str, contract: dict[str, Any] | None = None) -> dict[str, Any] | None:
    data = load_epic_categories(contract)
    return (data.get("reviews") or {}).get(epic_key.upper())


def resolve_classification(
    epic_key: str,
    state: dict[str, Any],
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Registry override, else classify from epic_meta in state."""
    ek = epic_key.upper()
    review = get_review(ek, contract)
    if review:
        cid = str(review.get("category_id") or "other").lower()
        return {
            "epic_key": ek,
            "category_id": cid,
            "category_label": TOP_CATEGORY_LABELS[cid],
            "category_confidence": "high",
            "hint_score": 0,
            "classification_source": "manual_review",
            "rationale": str(review.get("rationale") or ""),
            "evidence": review.get("evidence") or [],
        }
    meta = (state.get("epic_meta") or {}).get(ek) or (state.get("epic_meta") or {}).get(epic_key)
    return classify_epic(ek, jira_blob_from_meta(meta))


def apply_epic_categories_to_state(
    state: dict[str, Any],
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Patch epic_classifications and row category_id from registry + epic_meta."""
    c = contract or load_contract()
    keys: set[str] = set()
    for ek in state.get("corpus_epic_keys") or []:
        keys.add(str(ek).upper())
    for ek in (state.get("attestation_by_epic") or {}).keys():
        keys.add(str(ek).upper())
    for r in state.get("rows") or []:
        el = str(r.get("epic_link") or "")
        if el:
            keys.add(el.upper())

    classifications: dict[str, dict[str, Any]] = {}
    for ek in sorted(keys):
        classifications[ek] = resolve_classification(ek, state, c)

    for r in state.get("rows") or []:
        el = str(r.get("epic_link") or "").upper()
        if el in classifications:
            r["category_id"] = classifications[el]["category_id"]

    corpus_order = [str(ek).upper() for ek in (state.get("corpus_epic_keys") or [])]
    state["epic_classifications"] = [
        classifications[ek] for ek in corpus_order if ek in classifications
    ]
    extra = sorted(k for k in classifications if k not in corpus_order)
    for ek in extra:
        if not any(
            str(x.get("epic_key") or "").upper() == ek
            for x in state.get("epic_classifications") or []
        ):
            state.setdefault("epic_classifications", []).append(classifications[ek])

    return state


def set_epic_review(
    epic_key: str,
    category_id: str,
    rationale: str,
    *,
    evidence: list[str] | None = None,
    contract: dict[str, Any] | None = None,
) -> Path:
    cid = category_id.lower()
    if cid not in VALID_CATEGORIES:
        raise ValueError(f"category_id must be one of {sorted(VALID_CATEGORIES)}")
    data = load_epic_categories(contract)
    ek = epic_key.upper()
    data.setdefault("reviews", {})[ek] = {
        "category_id": cid,
        "rationale": rationale.strip(),
        "evidence": evidence or [],
        "reviewed_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    return save_epic_categories(data, contract)
