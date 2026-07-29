$repo = Resolve-Path (Join-Path $PSScriptRoot '../..')
Set-Location $repo
. ./automation/tools/crtqa-console/Invoke-CrtqaHostShell.ps1 -Commands @(
    'grep -nE ''POSITION_NOT_EXIST|test-rollover-antonfx-002|rolling-transactions|expected rollover'' log/dxweb.default.ctuat.log | tail -80'
)
