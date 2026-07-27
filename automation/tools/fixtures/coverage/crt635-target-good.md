# CRT-635 — Smart Checklist

## Prerequisites

- [CRT-635] Console — open at least one FX_SPOT position
> Prerequisite: console fill for FX_SPOT before Adaptive checks

## Adaptive — Transactions

### Transaction card

- [DXINV-025] Quantity from negative source displays without a minus sign
> Not signed — source-negative quantity displays without a minus sign
- [DXINV-025] Fill price shows account currency symbol
> Displayed with account currency symbol

### Transaction details card

- [DXINV-236] Cash effect displays without a minus sign
> Not signed

## Adaptive — Trade History

### Trade card

- [DXINV-CB-92] Quantity from negative source displays without a minus sign
> Not signed
- [DXINV-CB-92] Total cost shows account currency symbol
> Displayed with account currency symbol

### Trade details card

- [DXINV-CB-95] negative Realized PL shows minus sign and red
> Signed. Colored: red for negative, green for positive
- [DXINV-CB-95] positive Realized PL shows green
> Signed. Colored: red for negative, green for positive
- [DXINV-CB-95] Fees and Commission display without a minus sign
> Not signed
