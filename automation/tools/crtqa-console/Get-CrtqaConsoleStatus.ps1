#Requires -Version 5.1
<#
.SYNOPSIS
  Read-only crtqa console multiplex health (no modal, no dx batch).

.DESCRIPTION
  Checks session.active.json, master plink PID, and plink -share echo.
  Writes temp/crtqa-console/gate-status.json for agents and crtqa_env_probe.py.
  Exit 0 when all checks pass; 1 otherwise.
#>
[CmdletBinding()]
param(
    [string] $ConfigRoot,
    [switch] $Quiet
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'CrtqaConsole.Common.ps1')

if ([string]::IsNullOrWhiteSpace($ConfigRoot) -or -not (Test-Path -LiteralPath (Join-Path $ConfigRoot 'crtqa-console.config.json'))) {
    $ConfigRoot = Get-CrtqaToolDirectory
}

$secureRoot = Get-CrtqaSecureRoot -ConfigRoot $ConfigRoot
$statePath = Join-Path $secureRoot 'session.active.json'
$gatePath = Join-Path $secureRoot 'gate-status.json'

$sessionPresent = Test-Path -LiteralPath $statePath
$masterPidAlive = $false
$multiplexEchoOk = $false
$plinkPath = $null
$sshTarget = $null
$masterProcessId = $null
$detail = @()

if ($sessionPresent) {
    $state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
    $plinkPath = [string]$state.plinkPath
    $sshTarget = [string]$state.sshTarget
    $masterProcessId = $state.masterProcessId
    if ($null -ne $masterProcessId) {
        try {
            $proc = Get-Process -Id ([int]$masterProcessId) -ErrorAction Stop
            $masterPidAlive = -not $proc.HasExited
        }
        catch {
            $masterPidAlive = $false
        }
    }
    if ($plinkPath -and $sshTarget -and (Test-Path -LiteralPath $plinkPath)) {
        $echoOut = & $plinkPath @('-ssh', '-share', '-batch', $sshTarget, 'echo', 'crtqa_multiplex_ok') 2>&1
        $multiplexEchoOk = ($LASTEXITCODE -eq 0) -and ($echoOut -match 'crtqa_multiplex_ok')
        if (-not $multiplexEchoOk) {
            $detail += "multiplex echo failed (exit $LASTEXITCODE)"
        }
    }
    else {
        $detail += 'plink path or sshTarget missing in session state'
    }
}
else {
    $detail += 'session.active.json not found'
}

$overallOk = $sessionPresent -and $masterPidAlive -and $multiplexEchoOk

$gate = @{
    schema_version    = 1
    checked_at        = [DateTime]::UtcNow.ToString('o')
    overall           = if ($overallOk) { 'pass' } else { 'fail' }
    session_present   = $sessionPresent
    master_pid_alive  = $masterPidAlive
    multiplex_echo_ok = $multiplexEchoOk
    master_process_id = $masterProcessId
    detail            = ($detail -join '; ')
}
Write-Utf8NoBom -LiteralPath $gatePath -Text ($gate | ConvertTo-Json -Depth 6)

if (-not $Quiet) {
    Write-Host "[Get-CrtqaConsoleStatus] overall=$($gate.overall) session=$sessionPresent pid=$masterPidAlive echo=$multiplexEchoOk" -ForegroundColor $(if ($overallOk) { 'Green' } else { 'Yellow' })
    if ($detail.Count -gt 0) { Write-Host $gate.detail }
    Write-Host "Wrote: $gatePath"
}

if (-not $overallOk) { exit 1 }
exit 0
