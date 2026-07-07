#!/usr/bin/env bash
set -eu

EPIC="${EPIC_KEY:?EPIC_KEY empty}"
if [ -z "${CURSOR_API_KEY:-}" ]; then
  echo "ERROR: CURSOR_API_KEY is empty"
  exit 1
fi

# GROUND probes dx console — same OpenSSH secrets as console gate (step 6).
# shellcheck source=automation/tools/teamcity/crtqa-openssh-env.sh
source automation/tools/teamcity/crtqa-openssh-env.sh

python3 -m pip install --user -q cursor-sdk

export EPIC_KEY="$EPIC"

python3 -c "
import os, sys
from cursor_sdk import Agent, AgentOptions, LocalAgentOptions

epic = os.environ['EPIC_KEY']
# Linux CI: openssh env already exported; playbook must use crtqa_console / openssh not desktop multiplex.
prompt = (
    f'GROUND: {epic} '
    'Use CRTQA_CONSOLE_TRANSPORT=openssh and existing CRTQA_SSH_* / CRTQA_SUDO_PASSWORD env. '
    'Run runtime probes for every console-tagged check; ground_verify --mode emit must pass.'
)
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
print('GROUND agent finished')
"
