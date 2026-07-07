#!/usr/bin/env bash
set -u

EPIC="${EPIC_KEY:-}"
if [ -z "$EPIC" ]; then
  echo "ERROR: EPIC_KEY is empty"
  exit 1
fi

COV="epics/${EPIC}/${EPIC}-coverage.json"
REF="epics/${EPIC}/${EPIC}-ref.json"

if [ ! -f "$COV" ] || [ ! -f "$REF" ]; then
  echo "ERROR: missing $COV or $REF"
  exit 1
fi

python3 automation/tools/ground_verify.py --mode emit --coverage "$COV" --ref "$REF" || exit 1
echo "GROUND verify OK"
