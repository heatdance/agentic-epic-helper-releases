#!/usr/bin/env bash
set -u

EPIC="${EPIC_KEY:-}"
QA="${QA_TASK_KEY:-}"
TOKEN="${JIRA_API_TOKEN:-}"
JIRA_URL="${JIRA_BASE_URL:-https://jira.in.devexperts.com}"
BUILD_URL="${TEAMCITY_BUILD_URL:-}"

if [ -z "$EPIC" ] || [ -z "$QA" ]; then
  echo "ERROR: EPIC_KEY or QA_TASK_KEY is empty"
  exit 1
fi
if [ -z "$TOKEN" ]; then
  echo "ERROR: JIRA_API_TOKEN is empty"
  exit 1
fi

MD="epics/${EPIC}/${EPIC}-coverage.md"
if [ ! -f "$MD" ]; then
  echo "ERROR: $MD not found"
  exit 1
fi

echo "Attach coverage.md to $QA (epic $EPIC)"

curl -sS -f -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "X-Atlassian-Token: no-check" \
  -F "file=@${MD}" \
  "${JIRA_URL}/rest/api/2/issue/${QA}/attachments"

COMMENT_BODY="Corner Epic QA: coverage for *${EPIC}* is ready."
if [ -n "$BUILD_URL" ]; then
  COMMENT_BODY="${COMMENT_BODY} Build: ${BUILD_URL}"
fi

python3 -c "
import json, os, urllib.request

url = os.environ['JIRA_URL'].rstrip('/') + '/rest/api/2/issue/' + os.environ['QA'] + '/comment'
body = json.dumps({'body': os.environ['COMMENT_BODY']}).encode('utf-8')
req = urllib.request.Request(
    url,
    data=body,
    headers={
        'Authorization': 'Bearer ' + os.environ['TOKEN'],
        'Content-Type': 'application/json',
    },
    method='POST',
)
with urllib.request.urlopen(req) as resp:
    print('comment status:', resp.status)
" \
  JIRA_URL="$JIRA_URL" \
  QA="$QA" \
  TOKEN="$TOKEN" \
  COMMENT_BODY="$COMMENT_BODY"

echo "Jira success OK"
