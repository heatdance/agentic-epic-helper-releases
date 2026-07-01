# CRT-639 — fixture formula_first + principal focus

## Primary focus

- Verify weighted-average cash settlement formulas and ladders for FX Spot per CRT-1738–1743 configuration and metric parity.

- [CRT-1738] Weighted-average ladder: open two lots, partial close — average fill unchanged on remainder.

## Deferred obligations

- ! reason: Scenarios that reconfigure valuation method for already-existing instrument types may be skipped in regression scope.
- ! reason: Authoritative cent-level numeric outputs for the full CRT-1738 worked ladder table remain deferred pending upstream XT-7911 alignment.
