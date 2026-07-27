# CRT-635 — Smart Checklist

## Prerequisites

- [CRT-635] Console — open at least one FX_SPOT position

- [CRT-635] Adaptive — Transactions and Trade History show the FX_SPOT position

## Adaptive — Transactions

### Transaction card

- [DXINV-025] Side shows Buy or Sell, green for Buy and red for Sell

- [DXINV-025] Quantity is unsigned

- [DXINV-025] Fill price shows account currency symbol, native format

- [DXINV-025] Transaction date, Symbol, Account name are present

### Transaction details card

- [DXINV-236] renders collapsed by default

- [DXINV-236] Cash effect unsigned, 2 decimals, account currency

## Adaptive — Trade History

### Trade card

- [DXINV-CB-92] Side coloring, Quantity unsigned, Total cost signed

- [DXINV-CB-92] Quantity is unsigned

- [DXINV-CB-92] Total cost is signed

### Trade details card

- [DXINV-CB-95] Realized PL signed, red negative, green positive

- [DXINV-CB-95] Fees and Commission unsigned
