# AF formulas / Est. AF Effect — delivery (plan implementation)

Ephemeral research output for the closed plan **AF formulas Confluence trace**. Sources: MCP Atlassian (`confluence_get_page`, `confluence_search`), `yogi_snippet.py` on exported storage.

---

## 1. CRT-030 (Available / Prospective AF) — Portfolio Metrics

**Page:** [Portfolio Metrics](https://confluence.in.devexperts.com/pages/viewpage.action?pageId=345703196) (storage export: `automation/temp/confluence-portfolio-metrics-345703196.json`).

**Yogi snippet** (`yogi_snippet --req CRT-030`):

> Ph1: Prospective Equity - Prospective Initial Margin Ph2: Portfolio Balance + Sum (underlying.AFEffectWithOrders * CR) + Orders Prospective Commissions + SUM (Open PL for Non-equity cash flow positions * CR) Where underlying. AFEffectWithOrders is according to CR is conversion from underlying instrument currency to portfolio currency. Orders Prospective Commissions converted to portfolio currency from commission currency for each order included in the calculation of underlying.AFEffectWithOrders, negative. Open PL is according to . Open PL is not considered in AFEffectWithOrders as is not impacted by opening/closing orders: PL from opening orders is considered as 0, PL from closing order is the same as Open PL of non-closed position.

**Expanded context** (same page, first table row for Available Funds; links preserved as text): **Ph1:** Prospective Equity − Prospective Initial Margin (**CRT-580**). **Ph2:** Portfolio Balance + SUM(underlying.AFEffectWithOrders × CR) + Orders Prospective Commissions (**CRT-787**) + SUM(Open PL for Non-equity cash flow positions × CR), where `underlying.AFEffectWithOrders` is per **CRT-572**, CR to portfolio currency, prospective commissions negative, Open PL per **CRT-008** with the PL rules stated in the snippet.

---

## 2. CRT-707 (Est. AF Effect) — Order Confirmation

**Page:** [Order Confirmation](https://confluence.in.devexperts.com/pages/viewpage.action?pageId=396603896), section **3** / **CRT-1140**.

**Definition (markdown from MCP):**

- **Est. AF Effect** (**CRT-707**): *Prospective Available Funds − Available Funds*, where  
  - *Prospective Available Funds* — metric per **CRT-030** on portfolio of positions and orders **including** the order under validation;  
  - *Available Funds* — same per **CRT-030** on portfolio **NOT** including the order under validation.

---

## 3. CRT-1730 (FX_SPOT `mark_price` for order_mark_price) — Portfolio Metrics

**Yogi snippet** (`yogi_snippet --req CRT-1730`):

> For FX_SPOT mark_price is taken from the reference price on the order (link TBD)

**Interpretation vs “average market price” / cash settlement:**  
The explicit **CRT-1730** text ties FX_SPOT `mark_price` (within the **order price / order_mark_price** table, **CRT-017**) to **reference price on the order**, not to a generic session mark alone. The **“link TBD”** in Yogi was not resolved to a separate page via Confluence title search.

**Related product context (estimation / elaboration):** [FX Rolling Spot Estimations](https://confluence.in.devexperts.com/pages/viewpage.action?pageId=490569747) describes **reference price** on market flow from watchlist and includes **“Cash Settlement based on Average Price”** (PL, settlement). Use that page together with **CRT-1730** when aligning “average market price” behaviour with order-stored reference fields.

**Order placement pointer:** [Order Confirmation §4](https://confluence.in.devexperts.com/pages/viewpage.action?pageId=396603896) — **CRT-1836** *FX Spot exception*: for **Market** orders on FX Spot, save additional parameters per **CRT-1910** (Yogi LINK macro only in export; treat as separate requirement key **CRT-1910** under CT requirements tree).

---

## 4. BE parity checklist (`be-parity` todo)

No live BE/API call from this workspace; use as QA handoff:

| Step | Action |
|------|--------|
| 1 | Record instrument (FX_SPOT), side, qty, order type (Market vs Limit), limit/stop if any, **reference price** fields on order if exposed. |
| 2 | Capture **Est. AF Effect** from API/UI for the same moment as **Prospective AF** and **AF** (if separate metrics exposed) or two full metric payloads with/without order. |
| 3 | Verify identity **CRT-707**: `EstAFEffect = ProspectiveAF(with order) − AF(without order)` per **CRT-030** definition used in env. |
| 4 | If decomposing: IM leg for CFD/FX positions uses **mark/mid** per [CFD and FX_SPOT Margin](https://confluence.in.devexperts.com/pages/viewpage.action?pageId=342174999) (**CRT-569**); order-side pricing follows **CRT-017** + **CRT-1730** for FX_SPOT. Mismatch only after (3) is a spec/impl gap, not heuristic MV×Haircut vs IM alone. |

---

## 5. Files created during this run

| File | Note |
|------|------|
| `automation/temp/confluence-portfolio-metrics-345703196.json` | Full storage HTML for page 345703196 (~185 KB); for Yogi re-runs. |
| `automation/temp/af-effect-plan-delivery.md` | This summary. |

Remove scratch script: `automation/temp/_extract_crt030.py` (optional delete after read).
