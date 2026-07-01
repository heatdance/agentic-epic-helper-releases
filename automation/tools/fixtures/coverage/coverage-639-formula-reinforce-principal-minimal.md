# CRT-639 — fixture formula_first + principal (pass 2 reinforce)

## Primary focus

- Verify weighted-average cash settlement formulas and ladders for FX Spot per CRT-1738–1743 configuration and metric parity.

## Primary focus

- [CRT-1738] Weighted-average ladder: open two lots, partial close — average fill unchanged on remainder.
  > Discover: console_ladder_session WeightedAvg FX_SPOT at command_family (fix-001).

## Deferred obligations

- ! reason: Scenarios that reconfigure valuation method for already-existing instrument types may be skipped in regression scope.
  > Discovery: deferral_obligation_keyed; no reinforce executable lines.
- ! reason: Authoritative cent-level numeric outputs for the full CRT-1738 worked ladder table remain deferred pending upstream XT-7911 alignment.
  > Discovery: deferral_obligation_keyed; no reinforce executable lines.
