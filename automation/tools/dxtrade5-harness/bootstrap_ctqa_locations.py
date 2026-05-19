"""One-off generator for docs/dxtrade5-harness/locations/ctqa.json (Stage 3 bootstrap)."""
import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
base = _REPO / "docs" / "dxtrade5-harness"
cm = json.loads((base / "concept-map.json").read_text(encoding="utf-8"))
ia = json.loads((base / "ia-map.json").read_text(encoding="utf-8"))
path_by_id = {p["feature_id"]: p for p in ia["feature_paths"]}

wave_by_id = {
    "dxtrade5.session.authentication": "W1",
    "dxtrade5.session.account_portfolio_selector": "W1",
    "dxtrade5.embedded.dxtrade_widgets_in_webbroker": "W1",
    "dxtrade5.requirements.hub_cornertrader": "W1",
    "dxtrade5.requirements.hub_dxbro": "W1",
    "dxtrade5.workspace.watchlist": "W2",
    "dxtrade5.chart.tradingview_advanced": "W2",
    "dxtrade5.market_depth": "W2",
    "dxtrade5.instrument.instrument_page": "W2",
    "dxtrade5.orders.order_entry": "W2",
    "dxtrade5.orders.orders_widget": "W3",
    "dxtrade5.orders.order_book": "W3",
    "dxtrade5.positions.position_book": "W3",
    "dxtrade5.account.portfolio_metrics": "W3",
    "dxtrade5.transactions.account_transactions": "W3",
    "dxtrade5.settings.order_defaults": "W4",
    "dxtrade5.market_data.subscriptions": "W4",
    "dxtrade5.notifications.platform_toasts": "W4",
    "dxtrade5.notifications.messages_feed": "W4",
    "dxtrade5.risk.flatten_all": "W4",
}


def drift_login(pp: str) -> list:
    return [
        "Not verified in this automation run: session stopped at public login (no credentials used).",
        f"IA primary_path (narrow search after login): {pp}",
    ]


locations: dict = {}

auth_id = "dxtrade5.session.authentication"
locations[auth_id] = {
    "feature_id": auth_id,
    "wave": "W1",
    "verified_at": "2026-05-15",
    "primary_path_ok": True,
    "steps": [
        "Navigate to https://ctqa.prosp.devexperts.com/",
        "Observe login shell with Username, Password, Log In",
    ],
    "verify": {
        "page_title": "Cornèrtrader - your online trading platform.",
        "labels": ["Username", "Password", "Show password", "Log In"],
        "regions": ["main"],
    },
    "drift_notes": [
        "Post-login shell not captured in this run; extend Wave W1 after operator authentication.",
        "RootWebArea title and form labels taken from Chrome DevTools MCP accessibility snapshot.",
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
    if fid.startswith("dxtrade5.requirements.hub_"):
        row["drift_notes"] = [
            "External Confluence navigation; not applicable to CTQA web UI verification.",
            f"IA primary_path: {pp}",
        ]
    locations[fid] = row

out = {
    "schema_version": 1,
    "env": "ctqa",
    "base_url": "https://ctqa.prosp.devexperts.com/",
    "verified_at": "2026-05-15",
    "session_note": (
        "Retail Cornèrtrader CTQA shell intended; operator must complete Log In for W2–W4 live verification. "
        "No secrets in this file."
    ),
    "phase0": {
        "chrome_devtools_mcp": (
            "navigate_page and take_snapshot executed successfully against base_url (login page)."
        ),
        "account_class_intended": "retail_dxtrade5",
        "auth_handoff": (
            "See locations/PHASE0.md. Re-run waves after login to flip primary_path_ok for gated features."
        ),
        "exploration_note": (
            "Initial ctqa.json records login-surface verification for authentication; "
            "other features carry IA-only drift until post-login passes."
        ),
    },
    "locations": locations,
}

dest = base / "locations" / "ctqa.json"
dest.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("wrote", dest, "keys", len(locations))
