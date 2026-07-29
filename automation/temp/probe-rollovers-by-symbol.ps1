$repo = Resolve-Path (Join-Path $PSScriptRoot '../..')
Set-Location $repo
. ./automation/tools/crtqa-console/Invoke-CrtqaDxConsole.ps1 -Commands @(
    'use 1251'
    'show effective_transactions from=2026-07-29T00:00:00Z types=FX_SPOT_ROLLOVER accounts=antonfx:antonfx symbols=EURAUD.spot'
    'show effective_transactions from=2026-07-29T00:00:00Z types=FX_SPOT_ROLLOVER accounts=antonfx:antonfx symbols=EURCAD.spot'
    'exit'
)
