h2. CRT-594: FX_SPOT shell observation setup

h3. Configuration through console

# Log in to the dxCore console on CTQA and confirm FX_SPOT group keys via read-only show commands.
{code}
show account_group_hierarchy
{code}

# Run show prices for the target instrument and record first-tier bid/ask for cross-surface comparison.
{code}
show prices for <instrument_symbol>
{code}
