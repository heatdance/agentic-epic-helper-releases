#!/usr/bin/env bash
set -u

EPIC="${EPIC_KEY:-}"
if [ -z "$EPIC" ]; then
  echo "ERROR: EPIC_KEY is empty"
  exit 1
fi
if [ -z "${CURSOR_API_KEY:-}" ]; then
  echo "ERROR: CURSOR_API_KEY is empty"
  exit 1
fi

python3 -m pip install --user -q cursor-sdk

python3 -c "
import os, sys
from cursor_sdk import Agent, AgentOptions, LocalAgentOptions

epic = os.environ['EPIC_KEY']
prompt = f'EPIC-PREP: {epic} strict_topology=yes strict_principal=yes'
result = Agent.prompt(
    prompt,
    AgentOptions(
        api_key=os.environ['CURSOR_API_KEY'],
        model='composer-2.5',
        local=LocalAgentOptions(cwd=os.getcwd()),
    ),
)
print('status:', result.status)
if result.status != 'finished':
    sys.exit(2)
print('EPIC-PREP agent finished')
"
