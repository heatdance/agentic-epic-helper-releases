#!/usr/bin/env bash
set -e
echo "PWD=$PWD"
test -f AGENTS.md
test -d automation/tools
test -d epics
python3 --version
ls automation/tools/epic_prep_verify.py automation/tools/coverage_verify.py
echo "Harness checkout OK"
