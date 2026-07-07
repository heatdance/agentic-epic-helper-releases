#!/usr/bin/env bash
# Corner Epic QA Dispatch — poll CRTQA for "Agent: Coverage" and queue Pipeline via TeamCity REST.
# Reference copy for git; TeamCity build step may paste this or call it from VCS checkout.
# TeamCity parameters: JIRA_API_TOKEN, PIPELINE_BUILD_TYPE_ID, DISPATCH_LOOKBACK_MINUTES,
#   TRIGGER_PHRASE, TC_REST_TOKEN; optional TC_SERVER_URL (text, default dxcity).
set -euo pipefail

JIRA_URL="https://jira.in.devexperts.com"
TOKEN="%JIRA_API_TOKEN%"
PIPELINE_ID="%PIPELINE_BUILD_TYPE_ID%"
LOOKBACK="%DISPATCH_LOOKBACK_MINUTES%"
PHRASE="%TRIGGER_PHRASE%"
STATE_DIR="dispatch-state"
PROCESSED="${STATE_DIR}/processed_comment_ids.txt"
TC_SERVER_URL="${TC_SERVER_URL:-https://dxcity.in.devexperts.com}"
TC_REST_TOKEN="%TC_REST_TOKEN%"

mkdir -p "$STATE_DIR"
touch "$PROCESSED"

if [ -f "dispatch-state.in/processed_comment_ids.txt" ]; then
  sort -u "${PROCESSED}" dispatch-state.in/processed_comment_ids.txt -o "${PROCESSED}"
fi

export JIRA_URL TOKEN PIPELINE_ID LOOKBACK PHRASE PROCESSED TC_SERVER_URL TC_REST_TOKEN

python3 <<'PY'
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta

jira_url = os.environ["JIRA_URL"]
token = os.environ["TOKEN"]
pipeline_id = os.environ["PIPELINE_ID"]
lookback = int(os.environ["LOOKBACK"])
phrase = os.environ["PHRASE"]
processed_path = os.environ["PROCESSED"]
tc_server_url = os.environ["TC_SERVER_URL"]
tc_rest_token = os.environ["TC_REST_TOKEN"]

processed = set()
if os.path.exists(processed_path):
    with open(processed_path, encoding="utf-8") as f:
        processed = {line.strip() for line in f if line.strip()}


def jira_api(path):
    req = urllib.request.Request(
        jira_url + path,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def epic_from_summary(summary):
    m = re.search(r"\bCRT-\d+\b", summary or "")
    return m.group(0) if m else None


def parse_jira_ts(created):
    # No strftime / percent signs — TeamCity treats % as parameter references.
    s = (created or "")[:19]
    return datetime.fromisoformat(s).replace(tzinfo=timezone.utc)


def queue_pipeline(epic, qa_key, cid):
    xml = (
        f'<build><buildType id="{pipeline_id}"/>'
        f"<properties>"
        f'<property name="EPIC_KEY" value="{epic}"/>'
        f'<property name="QA_TASK_KEY" value="{qa_key}"/>'
        f'<property name="COMMENT_ID" value="{cid}"/>'
        f"</properties></build>"
    )
    req = urllib.request.Request(
        f"{tc_server_url}/app/rest/buildQueue",
        data=xml.encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/xml",
            "Authorization": f"Bearer {tc_rest_token}",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            print(f"TeamCity queued: HTTP {resp.status}")
            print(body[:800])
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        print(f"TeamCity queue FAILED: HTTP {e.code}", file=sys.stderr)
        print(err[:800], file=sys.stderr)
        raise


cutoff = datetime.now(timezone.utc) - timedelta(minutes=lookback)
jql = urllib.parse.quote(
    f"project = CRTQA AND updated >= -{lookback}m ORDER BY updated DESC"
)
search = jira_api(f"/rest/api/2/search?jql={jql}&maxResults=40&fields=summary")
queued = 0

for issue in search.get("issues", []):
    key = issue["key"]
    summary = issue["fields"].get("summary", "")
    epic = epic_from_summary(summary)
    if not epic:
        print(f"SKIP {key}: no CRT-* in summary ({summary!r})")
        continue

    comments = jira_api(f"/rest/api/2/issue/{key}/comment?maxResults=50")
    for c in comments.get("comments", []):
        cid = c["id"]
        body = c.get("body") or ""
        if phrase.lower() not in body.lower():
            continue

        created = c.get("created", "")
        try:
            ts = parse_jira_ts(created)
        except ValueError:
            print(f"SKIP {key}#{cid}: bad created timestamp {created!r}")
            continue

        if ts < cutoff:
            continue

        token_id = f"{key}#{cid}"
        if token_id in processed:
            print(f"SKIP already processed {token_id}")
            continue

        print(f"QUEUE pipeline {pipeline_id} for {token_id} epic={epic}")
        queue_pipeline(epic, key, cid)
        processed.add(token_id)
        queued += 1

with open(processed_path, "w", encoding="utf-8") as f:
    for x in sorted(processed):
        f.write(x + "\n")

print(f"Dispatch done, queued={queued}")
PY

echo "##teamcity[publishArtifacts '${STATE_DIR} => dispatch-state']"
