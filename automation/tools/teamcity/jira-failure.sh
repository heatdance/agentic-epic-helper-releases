#!/usr/bin/env bash
set -u

EPIC="${EPIC_KEY:-}"
QA="${QA_TASK_KEY:-}"
TOKEN="${JIRA_API_TOKEN:-}"
JIRA_URL="${JIRA_BASE_URL:-https://jira.in.devexperts.com}"
BUILD_URL="${TEAMCITY_BUILD_URL:-unknown}"

if [ -z "$QA" ]; then
  echo "ERROR: QA_TASK_KEY is empty"
  exit 1
fi
if [ -z "$TOKEN" ]; then
  echo "ERROR: JIRA_API_TOKEN is empty"
  exit 1
fi

COMMENT_BODY="Corner Epic QA: pipeline failed for epic *${EPIC:-?}*. See build log: ${BUILD_URL}"

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

echo "Jira failure comment posted"
