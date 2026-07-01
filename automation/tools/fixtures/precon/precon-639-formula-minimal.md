h2. CRT-639: Account and system configuration

h3. Configuration through console

# Log in to the dxCore console on CTQA using the shared QA principal.
{code}
use <account_code>
{code}

# Verify WeightedAvg FX_SPOT configuration posture via read-only show commands.
{code}
show console_guide output=MARKDOWN
{code}
