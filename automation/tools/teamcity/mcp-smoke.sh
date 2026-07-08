#!/usr/bin/env bash
# Jira REST smoke (same PAT as MCP) — fail fast before agent steps.
set -eu

EPIC="${EPIC_KEY:-}"
TOKEN="${JIRA_API_TOKEN:-}"
BASE="${JIRA_BASE_URL:-https://jira.in.devexperts.com}"
BASE="${BASE%/}"

if [ -z "$TOKEN" ]; then
  echo "ERROR: JIRA_API_TOKEN empty for MCP/Jira smoke"
  exit 1
fi

if [ -z "$EPIC" ]; then
  echo "SKIP MCP smoke: EPIC_KEY empty (manual dispatch-only checkout)"
  exit 0
fi

python3 - "$EPIC" "$BASE" "$TOKEN" <<'PY'
import json
import sys
import urllib.error
import urllib.request

epic, base, token = sys.argv[1:4]
url = f"{base}/rest/api/2/issue/{epic}?fields=summary,status"
req = urllib.request.Request(
    url,
    headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
)
try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
except urllib.error.HTTPError as exc:
    body = exc.read().decode("utf-8", errors="replace")[:400]
    print(f"ERROR: Jira smoke HTTP {exc.code}: {body}", file=sys.stderr)
    sys.exit(1)

key = data.get("key", "")
summary = (data.get("fields") or {}).get("summary", "")
print(f"Jira smoke OK: {key} — {summary[:80]}")
PY

echo "MCP bootstrap smoke OK"
