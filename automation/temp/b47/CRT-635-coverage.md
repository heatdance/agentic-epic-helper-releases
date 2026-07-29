# CRT-635 — Smart Checklist

## Data setup

- [CRT-635] Console — open at least one FX_SPOT position
> Prerequisite: execute console fill for FX_SPOT before Adaptive card checks

## Prerequisites

- [CRT-635] Adaptive Transactions widget renders FX_SPOT transaction card and details card after console fill

- [CRT-635] Adaptive Trade History widget renders FX_SPOT trade card and details card after console fill

## Adaptive — Transactions

### Transaction card (FX_SPOT Trade — Transaction Info)

- [DXINV-025] Description displays per linked requirement
> Description — Instrument description
- [DXINV-025] Instrument's icon displays per linked requirement
> Instrument's icon — Displayed if symbol is available
- [DXINV-025] Transaction type icon reflects quantity sign (green outward / red inward)
> Transaction type icon — Displayed if symbol is not available; green with arrow outside when quantity >= 0, red with arrow inside when quantity < 0
- [DXINV-025] Account name displays per linked requirement
> Account name — The name of the account where transaction was settled
- [DXINV-025] Transaction type displays per linked requirement
> Transaction type — Transaction type name (label field; not the green/red quantity-direction icon when symbol unavailable)
- [DXINV-025] Transaction date displays per linked requirement
> Transaction date — Transaction date on Transactions widget transaction card
- [DXINV-025] Quantity from negative source displays without a minus sign
> Quantity — Not signed on Transactions transaction card: source-negative quantity renders without a minus sign
- [DXINV-025] Fill price shows account currency symbol
> Fill price — Displayed with account currency symbol (account currency, not instrument currency)
- [DXINV-025] Buy side label shows green coloring on Side
> Side — Buy/Sell. Colored: green for Buy on Transactions transaction card
- [DXINV-025] Sell side label shows red coloring on Side
> Side — Buy/Sell. Colored: red for Sell on Transactions transaction card

### Transaction details card

- [DXINV-236] Quantity displays per linked requirement
> Quantity — Can be negative. Format: Number "as is"
- [DXINV-236] Cash effect and Commission and Fees and Taxes from negative source displays without a minus sign
> Cash effect — Not signed: source-negative values render without a minus sign
- [DXINV-236] Trade price shows account currency symbol
> Trade price — Displayed with account currency symbol
- [DXINV-236] Transaction description row visible when value is present
> Transaction description — Text. Displayed only if not empty (visible when populated)
- [DXINV-236] Transaction description row hidden when value is empty
> Transaction description — Text. Displayed only if not empty (hidden when empty)
- [DXINV-236] Collapsed default view on first open
> Collapsed default — Each transaction details card displays in collapsed (default) view on first open
- [DXINV-236] Toggle expands collapsed view to full parameter list
> Collapsed default toggle — Each transaction details card can expand from collapsed (default) to expanded view

## Adaptive — Trade History

### Trade card (FX_SPOT Trade — Trade History)

- [DXINV-CB-92] Description displays per linked requirement
> Description — Instrument's description
- [DXINV-CB-92] Symbol displays per linked requirement
> Symbol — Symbol
- [DXINV-CB-92] Transaction date displays per linked requirement
> Transaction date — Transaction date on Trade History trade card
- [DXINV-CB-92] Account name displays per linked requirement
> Account name — Account name where transaction was settled
- [DXINV-CB-92] Quantity from negative source displays without a minus sign
> Quantity — Not signed on Trade History trade card: source-negative quantity renders without a minus sign
- [DXINV-CB-92] Buy side label shows green coloring on Side
> Side — Colored: Green for Buy on Trade History trade card
- [DXINV-CB-92] Sell side label shows red coloring on Side
> Side — Colored: Red for Sell on Trade History trade card
- [DXINV-CB-92] Fill price shows averaged fill price
> Fill price — Average fill price
- [DXINV-CB-92] negative Total cost shows minus sign and red
> Total cost — Signed. Colored: red for negative — expect minus sign and red text
- [DXINV-CB-92] positive Total cost shows green without minus sign
> Total cost — Signed. Colored: green for positive — expect green text without minus sign

### Trade details card

- [DXINV-CB-95] Fees and Commission from negative source displays without a minus sign
> Fees — Not signed: source-negative values render without a minus sign
- [DXINV-CB-95] negative Realized PL shows minus sign and red
> Realized PL — Signed. Colored: red for negative — expect minus sign and red text
- [DXINV-CB-95] positive Realized PL shows green without minus sign
> Realized PL — Signed. Colored: green for positive — expect green text without minus sign

## Invariants under configuration change

- [CRT-635] FX_SPOT card availability gates are verified under Prerequisites (no configuration-change invariant in this epic scope).

## Not attempted

- Corner Trader dxTrade5 / WebBroker surfaces — out of epic — Jira AC targets Adaptive Transactions and Trade History only; corner_trader not_applicable per ref client_shell_impact
- Non-FX_SPOT instrument card parameter matrices — out of epic — epic_verification_focus names FX_SPOT transaction/trade cards only
