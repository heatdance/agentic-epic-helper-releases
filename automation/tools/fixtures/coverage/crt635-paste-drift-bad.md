# CRT-635 — Smart Checklist

## Prerequisites

- [CRT-635] Console — open at least one FX_SPOT position
> Prerequisite: console fill for FX_SPOT before Adaptive checks

## Adaptive — Transactions

### Transaction card

- [DXINV-025] Quantity from negative source displays without a minus sign
> Not signed — source-negative quantity displays without a minus sign
- [DXINV-025] Fill price shows account currency symbol
> Fill price — Displayed with account currency symbol (account currency, not instrument currency)

- [DXINV-236] Cash effect displays without a minus sign
> Cash effect — Not signed: a source-negative cash effect renders without a minus sign

## Adaptive — Trade History

### Trade card

- [DXINV-CB-92] Quantity from negative source displays without a minus sign
> Quantity — Not signed: a source-negative quantity renders without a minus sign
- [DXINV-CB-92] Total cost shows account currency symbol
> Total cost — Displayed with account currency symbol

### Trade details card

- [DXINV-CB-95] negative Realized PL shows minus sign and red
> Realized PL — Signed. Colored: red for negative — expect a minus sign and red text
- [DXINV-CB-95] positive Realized PL shows green
> Realized PL — Signed. Colored: green for positive — expect no minus sign and green text
