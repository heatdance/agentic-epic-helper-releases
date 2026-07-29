$repo = Resolve-Path (Join-Path $PSScriptRoot '../..')
Set-Location $repo
. ./automation/tools/crtqa-console/Invoke-CrtqaDxConsole.ps1 -Commands @(
    'use 1251'
    'show metrics EURAUD.spot'
    'show effective_transactions from=2026-07-29 types=FX_SPOT_ROLLOVER accounts=antonfx:antonfx'
    'show instrument EURAUD.spot'
    'exit'
)
