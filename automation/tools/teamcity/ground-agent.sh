#!/usr/bin/env bash
set -euo pipefail

# shellcheck source=automation/tools/teamcity/agent-env.sh
source automation/tools/teamcity/agent-env.sh

# GROUND probes dx console — same OpenSSH secrets as console gate (step 6).
# shellcheck source=automation/tools/teamcity/crtqa-openssh-env.sh
source automation/tools/teamcity/crtqa-openssh-env.sh

EPIC="$EPIC_KEY"
PROMPT=$(cat <<EOF
GROUND: ${EPIC}

CI addendum: CRTQA console Phase 0 is already done (Pipeline step 6 console gate passed).
Do not use Invoke-CrtqaDxConsole.ps1 or desktop multiplex — use OpenSSH transport with exported CRTQA_SSH_* / CRTQA_SUDO_PASSWORD env and crtqa_console_probe.py per playbook.
Follow .cursor/pipelines/ground.md end-to-end for epic ${EPIC}.
Mutate runtime_probes on console-tagged checks in epics/${EPIC}/${EPIC}-coverage.json; ground_verify.py --mode emit must pass.
Delete epics/${EPIC}/temp/ when done.
EOF
)

python3 automation/tools/teamcity/run_pipeline_agent.py \
  --prompt "$PROMPT" \
  --require "epics/%EPIC_KEY%/%EPIC_KEY%-coverage.json"

echo "GROUND agent finished"
