#!/usr/bin/env bash
set -u

EPIC="${EPIC_KEY:-}"
if [ -z "$EPIC" ]; then
  echo "ERROR: EPIC_KEY is empty"
  exit 1
fi

ANALYSIS="epics/${EPIC}/${EPIC}-analysis.json"
COV="epics/${EPIC}/${EPIC}-coverage.json"
REF="epics/${EPIC}/${EPIC}-ref.json"

if [ ! -f "$ANALYSIS" ]; then
  echo "ERROR: $ANALYSIS not created"
  exit 1
fi
if [ ! -f "$COV" ] || [ ! -f "$REF" ]; then
  echo "ERROR: missing $COV or $REF"
  exit 1
fi

python3 automation/tools/analysis_verify.py \
  --mode draft_truth \
  --strict-topology \
  --strict-principal \
  --analysis "$ANALYSIS" \
  --coverage "$COV" \
  --ref "$REF"
echo "ANALYSE verify OK"
