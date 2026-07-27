#!/usr/bin/env bash
# Atlassian REST smoke (Jira + Confluence + Stash) — fail fast before agent steps.
# Data Center: each product needs its own PAT (do not reuse Jira PAT for Confluence/Stash).
set -eu

EPIC="${EPIC_KEY:-}"
JIRA_TOKEN="${JIRA_API_TOKEN:-}"
CONF_TOKEN="${CONFLUENCE_API_TOKEN:-}"
BB_TOKEN="${BITBUCKET_API_TOKEN:-}"
JIRA_BASE="${JIRA_BASE_URL:-https://jira.in.devexperts.com}"
JIRA_BASE="${JIRA_BASE%/}"
CONF_BASE="${ATLASSIAN_MCP_CONFLUENCE_URL:-https://confluence.in.devexperts.com}"
CONF_BASE="${CONF_BASE%/}"
BB_BASE="${ATLASSIAN_MCP_BITBUCKET_URL:-https://stash.in.devexperts.com}"
BB_BASE="${BB_BASE%/}"

if [ -z "$JIRA_TOKEN" ]; then
  echo "ERROR: JIRA_API_TOKEN empty for MCP/Jira smoke"
  exit 1
fi
if [ -z "$CONF_TOKEN" ]; then
  echo "ERROR: CONFLUENCE_API_TOKEN empty for Confluence smoke"
  exit 1
fi
if [ -z "$BB_TOKEN" ]; then
  echo "ERROR: BITBUCKET_API_TOKEN empty for Stash/Bitbucket smoke"
  exit 1
fi

if [ -z "$EPIC" ]; then
  echo "SKIP MCP smoke: EPIC_KEY empty (manual dispatch-only checkout)"
  exit 0
fi

python3 - "$EPIC" "$JIRA_BASE" "$JIRA_TOKEN" "$CONF_BASE" "$CONF_TOKEN" "$BB_BASE" "$BB_TOKEN" <<'PY'
import json
import sys
import urllib.error
import urllib.request

(
    epic,
    jira_base,
    jira_token,
    conf_base,
    conf_token,
    bb_base,
    bb_token,
) = sys.argv[1:8]


def get_json(url: str, token: str, label: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:400]
        print(f"ERROR: {label} smoke HTTP {exc.code}: {body}", file=sys.stderr)
        raise SystemExit(1) from exc
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {label} smoke failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


jira = get_json(
    f"{jira_base}/rest/api/2/issue/{epic}?fields=summary,status",
    jira_token,
    "Jira",
)
print(
    f"Jira smoke OK: {jira.get('key', '')} — "
    f"{((jira.get('fields') or {}).get('summary') or '')[:80]}"
)

# Confluence DC: authenticated current user
conf = get_json(f"{conf_base}/rest/api/user/current", conf_token, "Confluence")
conf_user = conf.get("username") or conf.get("displayName") or conf.get("userKey") or "?"
print(f"Confluence smoke OK: user={conf_user}")

# Stash DC: known Corner product repo used by EPIC-PREP browse
bb = get_json(
    f"{bb_base}/rest/api/1.0/projects/CAN/repos/corner",
    bb_token,
    "Stash",
)
slug = bb.get("slug") or bb.get("name") or "?"
print(f"Stash smoke OK: CAN/{slug}")
PY

echo "MCP bootstrap smoke OK (Jira + Confluence + Stash)"
