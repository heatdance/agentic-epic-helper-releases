h2. CRT-594: Account groups and quote publication

h3. Configuration through console

# Log in to the dxCore console on CTQA and confirm account group hierarchy includes <group_key_enrg> and <group_key_oppt> via read-only show commands.
{code}
show account_group_hierarchy
{code}

# Verify FxConfiguration posture and quote publication streams for the target instrument are aligned for dual-account observation.
{code}
show prices for <instrument_symbol>
{code}

h3. WebBroker

# Confirm dealer surfaces expose account group mapping labels consistent with console hierarchy for ENRG and OPPT contrast accounts.

h2. CRT-594: FX_SPOT shell observation setup

h3. Configuration through console

# After pc-setup completes, run show prices for the target instrument and record first-tier bid/ask for cross-surface comparison.
{code}
show prices for <instrument_symbol>
{code}
