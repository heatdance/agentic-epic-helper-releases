# Teach skill — examples

## Good: first move after manual step

**Operator:** `/teach` then pastes manual step “Login as dealer, open Orders, verify default filter is Active.”

**Agent (good):** Teach mode ON. For Playwright smoke, login and navigation are usually shared fixtures or a `beforeEach` — not duplicated per test. **Where would you put the dealer login so this smoke and the next one reuse it?** (No full test file.)

## Bad: unprompted full test

**Agent (bad):** Here is the complete `test_orders_default_filter.py` with page objects, locators, and assertions …

Unless the operator asked for the full solution.

## Good: after operator asks for solution

**Operator:** “I’m stuck — show me the full Playwright test for this step.”

**Agent (good):** Provides complete test with brief comments on choices.

## `/teach stop`

**Operator:** `/teach stop`

**Agent:** Teach mode OFF; session `active: false`. Normal Corner rules apply for your next message.
