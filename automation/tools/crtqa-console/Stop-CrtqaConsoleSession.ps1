#Requires -Version 5.1
[CmdletBinding()]
param([string]$ConfigRoot = $PSScriptRoot)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'CrtqaConsole.Common.ps1')

if ([string]::IsNullOrWhiteSpace($ConfigRoot) -or -not (Test-Path -LiteralPath (Join-Path $ConfigRoot 'crtqa-console.config.json'))) {
    $ConfigRoot = Get-CrtqaToolDirectory
}

$secureRoot = Get-CrtqaSecureRoot -ConfigRoot $ConfigRoot
$statePath = Join-Path $secureRoot 'session.active.json'
if (-not (Test-Path -LiteralPath $statePath)) {
    Write-Host '[Stop-CrtqaConsoleSession] No session.active.json — nothing to stop.'
    return
}

$s = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
if ($s.masterProcessId) {
    try { Stop-Process -Id ([int]$s.masterProcessId) -Force -ErrorAction SilentlyContinue } catch {}
}
Remove-Item (Join-Path $secureRoot ([string]$s.credentialDpapi)) -Force -ErrorAction SilentlyContinue
Remove-Item $statePath -Force
Write-Host '[Stop-CrtqaConsoleSession] Multiplex upstream stop requested; credential blob removed.' -ForegroundColor Green

