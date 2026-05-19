"""Skeleton generator for docs/webbroker-harness/locations/ctqa.json (Stage 3 bootstrap)."""
import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
base = _REPO / "docs" / "webbroker-harness"
cm = json.loads((base / "concept-map.json").read_text(encoding="utf-8"))
ia = json.loads((base / "ia-map.json").read_text(encoding="utf-8"))
path_by_id = {p["feature_id"]: p for p in ia["feature_paths"]}

wave_by_id = {
    "webbroker.session.authentication": "W1",
    "webbroker.session.account_portfolio_selector": "W1",
    "webbroker.embedded.dxtrade_widgets_context": "W1",
    "webbroker.requirements.hub_cornertrader": "W1",
    "webbroker.requirements.hub_dxbro": "W1",
    "webbroker.workspace.watchlist": "W2",
    "webbroker.chart.tradingview_advanced": "W2",
    "webbroker.market_depth": "W2",
    "webbroker.instrument.instrument_page": "W2",
    "webbroker.orders.order_entry": "W2",
    "webbroker.orders.orders_widget": "W3",
    "webbroker.orders.order_book": "W3",
    "webbroker.positions.position_book": "W3",
    "webbroker.account.portfolio_metrics": "W3",
    "webbroker.transactions.account_transactions": "W3",
    "webbroker.settings.order_defaults": "W4",
    "webbroker.market_data.subscriptions": "W4",
    "webbroker.notifications.platform_toasts": "W4",
    "webbroker.notifications.messages_feed": "W4",
    "webbroker.risk.flatten_all": "W4",
}


def drift_login(pp: str) -> list:
    return [
        "Not verified in this automation run: session stopped at public login (no credentials used).",
        f"IA primary_path (narrow search after login): {pp}",
    ]


locations: dict = {}

auth_id = "webbroker.session.authentication"
locations[auth_id] = {
    "feature_id": auth_id,
    "wave": "W1",
    "verified_at": "2026-05-15",
    "primary_path_ok": True,
    "steps": [
        "Navigate to https://ctqa.prosp.devexperts.com/webbroker/",
        "Observe login shell with Username, Password, Log In",
    ],
    "verify": {
        "page_title": "Cornèrtrader - your online trading platform.",
        "labels": ["Username", "Password", "Show password", "Log In"],
        "regions": ["main"],
    },
    "drift_notes": [
        "Post-login dealer shell not captured in this run; extend Wave W1 after operator authentication.",
        "Root WebBroker path /webbroker/ — not retail site root.",
    ],
    "selectors_may_change": {},
}

for f in cm["features"]:
    fid = f["id"]
    if fid == auth_id:
        continue
    p = path_by_id[fid]
    pp = p["primary_path"]
    row = {
        "feature_id": fid,
        "wave": wave_by_id.get(fid, "W?"),
        "verified_at": "2026-05-15",
        "primary_path_ok": False,
        "steps": [],
        "verify": {},
        "drift_notes": drift_login(pp) + ([p["shell_note"]] if p.get("shell_note") else []),
        "selectors_may_change": {},
    }
    if fid.startswith("webbroker.requirements.hub_"):
        row["drift_notes"] = [
            "External Confluence navigation; not applicable to CTQA web UI verification.",
            f"IA primary_path: {pp}",
        ]
    locations[fid] = row

out = {
    "schema_version": 1,
    "env": "ctqa",
    "base_url": "https://ctqa.prosp.devexperts.com/webbroker/",
    "verified_at": "2026-05-15",
    "session_note": (
        "Dealer WebBroker /webbroker/ path intended; operator must complete Log In for W2–W4 live verification. "
        "No secrets in this file."
    ),
    "phase0": {
        "chrome_devtools_mcp": (
            "navigate_page and take_snapshot should be run against base_url (login page)."
        ),
        "account_class_intended": "dealer_webbroker",
        "auth_handoff": (
            "See locations/PHASE0.md. Re-run waves after login to flip primary_path_ok for gated features."
        ),
        "exploration_note": (
            "Bootstrap ctqa.json records login-surface verification for authentication; "
            "other features carry IA-only drift until post-login passes."
        ),
    },
    "locations": locations,
}

dest = base / "locations" / "ctqa.json"
dest.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("wrote", dest, "keys", len(locations))
