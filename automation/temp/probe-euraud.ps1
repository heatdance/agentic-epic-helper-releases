$repo = Resolve-Path (Join-Path $PSScriptRoot '../..')
Set-Location $repo
. ./automation/tools/crtqa-console/Invoke-CrtqaDxConsole.ps1 -Commands @(
    'use 1251'
    'show metrics EURAUD.spot'
    'show instrument EURAUD.spot'
    'show positions instrument_filter=EURAUD show_activities'
    'exit'
)
