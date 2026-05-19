h1. CRT-639: Account & system configuration

h3. Configuration through console

# Connect to dxCore console on CTQA (for example dx run console as the CTQA operator). Confirm the session responds to help.

# Create a dedicated test user and account: run create broker_client for broker CH or BS (.com test platforms), domain default, currency USD. Use new credentials for this test run (name=<username> and a newly generated secret per help create); do not reuse the operator login account.
{code}help create broker_client{code}
{code}create broker_client name=<username> broker=CH currency=USD{code}
* Use broker BS instead of CH when validating the BS routing line.

# Allow FX_SPOT instruments for the account: corner_subtype set_allowed account=<clearing_code>:<account_code> allowedsubtypes=FX_SPOT. Run help corner_subtype on CTQA to confirm syntax for your build.
{code}help corner_subtype set_allowed{code}
{code}corner_subtype set_allowed account=<clearing_code>:<account_code> allowedsubtypes=FX_SPOT{code}

# Add the account to the broker CAG group and a CornerTraderFxConfiguration group (for example Opportunity): run show account_group_hierarchy, locate CAG-CH (or CAG-BS) under the broker RAG node, then update account_group_members key=<cag_group_key> add_accounts=<account_id>. Add the CornerTraderFxConfiguration group key=<fx_config_group_key> (grep Opportunity in hierarchy output).
{code}show account_group_hierarchy{code}
{code}update account_group_members key=<cag_group_key> add_accounts=<account_id>{code}
{code}update account_group_members key=<fx_config_group_key> add_accounts=<account_id>{code}
* Hierarchy shows Opportunity and CAG-CH under RAG-CH on CTQA; resolve keys from live hierarchy, not from a prior session.

# Configure ExternalExecution routing for FX_SPOT at account level. Run show profiles domains=ExternalExecution to inspect FIX_AUTO vs ET routing. If ET executor is active for FX_SPOT, unassign FIX_AUTO profile and assign ET per environment policy (FIX_AUTO takes precedence when both apply).
{code}show profiles domains=ExternalExecution{code}
{code}assign profile account=<clearing_code>:<account_code> profile=<profile_name>{code}
* Sample profiles on CTQA include FIX_AUTO and IG_OTC execution destinations under ExternalExecution domain.

# Publish a realtime quote for the FX spot instrument planned for tests (for example EURUSD.spot for your CornerTraderFxConfiguration group). Run help pub_to_realtime on CTQA for the exact instrument string and publisher arguments.
{code}help pub_to_realtime{code}
{code}pub_to_realtime <instrument> <arguments per help>{code}

h3. WebBroker

# Log in to the CTQA WebBroker dealer UI at https://ctqa.prosp.devexperts.com/webbroker/ with a dealer principal that has user-management rights.

# In WebBroker User Management, create a client user: set Broker code CH or BS, Client Type POA, and add the user to the broker CPG used for client accounts. Open the New User action from the User Management toolbar on CTQA and confirm field labels (Login, Domain, Full name, Email) match your build.
* User Management workspace shows New User, Login, Domain, Full name, and Email on authenticated dealer shell.

# Create a client account linked to the console user: Allowed Instruments FX_SPOT, initial balance, CornerTraderFxConfiguration group aligned with console setup (for example Opportunity), and assign the account to the same CAG membership used in console configuration.
* Position Book shows Avg Price column header on authenticated dealer shell; align account picker with the console-created client account.
