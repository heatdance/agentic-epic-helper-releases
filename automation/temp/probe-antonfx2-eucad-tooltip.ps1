$repo = Resolve-Path (Join-Path $PSScriptRoot '../..')
Set-Location $repo
. ./automation/tools/crtqa-console/Invoke-CrtqaDxConsole.ps1 -Commands @(
    'use 1401'
    'show account this'
    'show metrics EURCAD.spot'
    'show instrument EURCAD.spot'
    'show positions instrument_filter=EURCAD show_activities'
    'show effective_transactions from=2026-07-29T00:00:00Z types=FX_SPOT_ROLLOVER accounts=antonfx2:antonfx2 symbols=EURCAD.spot'
    'exit'
)
