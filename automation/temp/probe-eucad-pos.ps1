$repo = Resolve-Path (Join-Path $PSScriptRoot '../..')
Set-Location $repo
. ./automation/tools/crtqa-console/Invoke-CrtqaDxConsole.ps1 -Commands @(
    'use 1251'
    'show metrics EURCAD.spot'
    'show positions instrument_filter=EURCAD show_activities'
    'exit'
)
