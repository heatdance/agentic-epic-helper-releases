#!/usr/bin/env bash
set -u

EPIC="${EPIC_KEY:-}"
if [ -z "$EPIC" ]; then
  echo "ERROR: EPIC_KEY is empty"
  exit 1
fi

REF="epics/${EPIC}/${EPIC}-ref.json"
if [ ! -f "$REF" ]; then
  echo "ERROR: $REF not created by EPIC-PREP agent"
  exit 1
fi

python3 automation/tools/epic_prep_verify.py \
  --mode ref \
  --strict-topology \
  --strict-principal \
  --ref "$REF"
echo "EPIC-PREP verify OK"
