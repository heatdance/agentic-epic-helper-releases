# 1. Connect to dxCore console on CTQA (for example dx run console as the CTQA operator). Confirm the session responds to help.

# 2. Create a dedicated test user and account for this epic run, or select an existing client account already configured for FX Spot visibility. Run create broker_client for broker CH or BS when creating new credentials (name=<username> and a newly generated secret per help create); do not reuse the operator login account.

{code}help create broker_client

{code}

{code}create broker_client name=<username> broker=CH currency=USD

{code}

{info}Use broker BS instead of CH when validating the BS routing line.{info}

# 3. Allow FX_SPOT instruments for the test account: corner_subtype set_allowed account=<clearing_code>:<account_code> allowedsubtypes=FX_SPOT. Run help corner_subtype on CTQA to confirm syntax for your build.

{code}help corner_subtype set_allowed

{code}

{code}corner_subtype set_allowed account=<clearing_code>:<account_code> allowedsubtypes=FX_SPOT

{code}

# 4. Add the account to the broker CAG group and a CornerTraderFxConfiguration group (for example Opportunity): run show account_group_hierarchy, locate CAG-CH (or CAG-BS) under the broker RAG node, then update account_group_members key=<cag_group_key> add_accounts=<account_id>. Add the CornerTraderFxConfiguration group key=<fx_config_group_key> (grep Opportunity in hierarchy output).

{code}show account_group_hierarchy

{code}

{code}update account_group_members key=<cag_group_key> add_accounts=<account_id>

{code}

{code}update account_group_members key=<fx_config_group_key> add_accounts=<account_id>

{code}

{info}Hierarchy shows Opportunity and CAG-CH under RAG-CH on CTQA; resolve keys from live hierarchy, not from a prior session.{info}

# 5. Configure ExternalExecution routing for FX_SPOT at account level. Run show profiles domains=ExternalExecution to inspect FIX_AUTO vs ET routing. Assign the profile matching your test policy (FIX auto-fill or ET FIX path for FX Spot).

{code}show profiles domains=ExternalExecution

{code}

{code}assign profile account=<clearing_code>:<account_code> profile=<profile_name>

{code}

{info}Sample profiles on CTQA include FIX_AUTO and IG_DMA execution destinations under ExternalExecution domain.{info}

# 6. Publish a realtime quote for the FX spot instrument planned for tests (EURUSD.spot for your CornerTraderFxConfiguration group). Run help pub_to_realtime on CTQA for the exact instrument string and publisher arguments.

{code}help pub_to_realtime

{code}

{code}pub_to_realtime <instrument> <arguments per help>

{code}

# 7. On the configured account, place or locate FX Spot market, limit, and stop orders on EURUSD.spot using console commands. For limit and stop orders use prices significantly off the current market so the order can route and fill when manually completed. For market orders use the market command family per help buy; note the retail UI market path may be defect-sensitive while console-issued orders still drive visibility checks.

{code}use <account_code>

{code}

{code}buy <qty> EURUSD.spot mkt fok

{code}

{code}buy <qty> EURUSD.spot at <off_market_price> gtc

{code}

{code}stp_order buy <qty> EURUSD.spot stop=<stop_price> limit=<limit_price> gtc

{code}

{code}show order last

{code}

{code}execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now

{code}

{info}Run help buy and help stp_order on CTQA to confirm exact parameter names for market, limit, and stop families.{info}

# 8. Log in to the CTQA WebBroker dealer UI at https://ctqa.prosp.devexperts.com/webbroker/ with a dealer principal that has user-management and client-area view rights.

# 9. Open Client Area for the test account and confirm Orders, Account Transactions, and Positions widgets are available from the header flyout. Open Trading workspace and confirm Order Book and Position Book widgets are available for dealer-side verification.

{info}Client Area flyout lists Positions, Orders, and Account Transactions; Trading menu lists Order Book and Position Book.{info}

# 10. When creating a new client account, use User Management: open New User and confirm field labels (Login, Domain, Full name, Email). Create the client account with Allowed Instruments FX_SPOT, initial balance, CornerTraderFxConfiguration group aligned with console setup, and CAG membership matching console configuration.

{info}Skip user creation when reusing an existing FX Spot-configured client account.{info}

# 11. Log in to CTQA dxTrade5 at https://ctqa.prosp.devexperts.com/ with the client credentials for the test account. Confirm Orders, Account Transactions, Positions, and Order History widgets are on the default layout or add them from the widget gallery.

# 12. Open CTQA Adaptive at https://ctqa.prosp.devexperts.com/adaptive/ with the client principal for the test account. Confirm Portfolio, Working Orders, Trade History, and Positions views list EURUSD.spot rows when the account has FX Spot activity.

{info}When switching Adaptive user context in CTQA, set the application token per environment policy (do not store credentials in test artefacts).{info}
