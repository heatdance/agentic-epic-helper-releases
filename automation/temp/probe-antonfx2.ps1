$repo = Resolve-Path (Join-Path $PSScriptRoot '../..')
Set-Location $repo
. ./automation/tools/crtqa-console/Invoke-CrtqaDxConsole.ps1 -Commands @(
    'show account antonfx2:antonfx2'
    'show instrument EURUSD.spot'
    'exit'
)
