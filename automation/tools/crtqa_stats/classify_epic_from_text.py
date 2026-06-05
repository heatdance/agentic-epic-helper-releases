#!/usr/bin/env python3
"""Suggest FE/BE/API/Other from epic summary + description (manual review input)."""

from __future__ import annotations

import re
from typing import Any

FE_SIGNALS = (
    "dxtrade",
    "dxtf",
    "webbroker",
    "adaptive",
    "chart",
    "widget",
    "instrument page",
    "order entry",
    " oe ",
    "oe form",
    "ui ",
    " ui",
    "panel",
    "display",
    "trading panel",
    "confirmation page",
    "client area",
    "frontend",
    "dealer",
    "chrome",
    "midpoint",
    "price type in settings",
    "horn-",
    "dxinv-cb",
)

BE_SIGNALS = (
    "dxcore",
    "console",
    "algorithm",
    "mapping algorithm",
    "margin",
    "settlement",
    "metrics",
    "mark price",
    "portfolio",
    "position",
    "allowedjobs",
    "job",
    "expiration",
    "expire day",
    "eod report",
    "risk management",
    "pricing",
    "fixture",
    "postgres",
    "server",
    "backend",
    "instrument exposure",
    "maintenance margin",
    "initial margin",
    "undefined margin",
    "cfd margin",
    "autoexpiration",
    "non-trading day",
)

API_SIGNALS = (
    "integration",
    "connectivity",
    "openapi",
    " rest ",
    "external",
    "dxfeed",
    "third-party",
    "api ",
    " protocol",
    "connect to",
)


def suggest_category(summary: str, description: str) -> tuple[str, str]:
    text = f"{summary} {description}".lower()
    text = re.sub(r"\s+", " ", text)

    fe = sum(1 for s in FE_SIGNALS if s in text)
    be = sum(1 for s in BE_SIGNALS if s in text)
    api = sum(1 for s in API_SIGNALS if s in text)

    if "chart" in text and ("oe" in text or "order entry" in text):
        fe += 2
    if "metrics" in text and "instrument" in text:
        be += 2
    if "port chart" in text or "chart trading panel" in text:
        fe += 3
    if "order expiration" in text or "day orders" in text:
        be += 2
    if "fx_spot pricing" in text or "groups and mapping to dxfeed" in text:
        api += 2
    if " ca api" in text or "to ca api" in text or " rest api" in text:
        api += 3
    if "transactions widget" in text and "api includes" in text:
        api += 2
        fe += 1

    scores = {"fe": fe, "be": be, "api": api, "other": 0}
    best = max(scores, key=lambda k: scores[k])
    if scores[best] == 0:
        best = "other"
    elif best != "other":
        ordered = sorted(scores.items(), key=lambda x: -x[1])
        if len(ordered) > 1 and ordered[0][1] == ordered[1][1] and ordered[1][1] > 0:
            if ordered[0][0] == "fe" and ordered[1][0] == "be":
                best = "fe"
            elif ordered[0][0] == "be" and ordered[1][0] == "fe":
                best = "be"
            else:
                best = ordered[0][0]

    rationale = _rationale(best, summary, scores)
    return best, rationale


def _rationale(cat: str, summary: str, scores: dict[str, int]) -> str:
    s = summary.strip()[:80]
    if cat == "fe":
        return f"Major work is client-facing UI (dxTrade5/WebBroker/charts/OE): {s}."
    if cat == "be":
        return f"Major work is server-side logic, metrics, jobs, or risk/settlement: {s}."
    if cat == "api":
        return f"Major work is external integration or connectivity: {s}."
    return f"No dominant FE/BE/API signal in epic scope; classified Other: {s}."
