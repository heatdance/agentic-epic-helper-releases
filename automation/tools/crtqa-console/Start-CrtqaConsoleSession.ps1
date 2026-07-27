#Requires -Version 5.1
<#
.SYNOPSIS
  Start PuTTY connection-sharing upstream (-share -N) for CT QA/UAT SSH; store sudo credential (DPAPI) for dx batches.

.DESCRIPTION
  1. Windows Forms dialog: Environment (qa|uat), SSH Linux login + password (masked).
  2. Starts hidden `plink … -ssh -pwfile FILE -share -batch -N user@host` as upstream.
  3. Writes DPAPI ciphertext of the password onto temp/crtqa-console for sudo batches (reuse until Stop).

  Subsequent `Invoke-CrtqaDxConsole.ps1` reuses multiplex SSH (`-share`); sudo password decrypted per batch unless host uses NOPASSWD.

.PARAMETER Environment
  Optional pre-select: qa | uat (skips changing default in dialog if passed; dialog still shows picker).
#>
[CmdletBinding()]
param(
    [string] $ConfigRoot = $PSScriptRoot,
    [string] $Environment
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'CrtqaConsole.Common.ps1')

if ([string]::IsNullOrWhiteSpace($ConfigRoot) -or -not (Test-Path -LiteralPath (Join-Path $ConfigRoot 'crtqa-console.config.json'))) {
    $ConfigRoot = Get-CrtqaToolDirectory
}

$cfg = Get-CrtqaMergedConfig -Root $ConfigRoot
$secureRoot = Get-CrtqaSecureRoot -ConfigRoot $ConfigRoot
New-DirectoryForce -Path $secureRoot

if (-not (Test-Path -LiteralPath $cfg.plinkPath)) { throw "plink not found at $($cfg.plinkPath)" }

$envIds = @()
$envLabels = @{}
if ($cfg.PSObject.Properties.Name -contains 'environments' -and $null -ne $cfg.environments) {
    foreach ($p in $cfg.environments.PSObject.Properties) {
        $envIds += $p.Name
        $lab = if ($p.Value.PSObject.Properties.Name -contains 'label') { [string]$p.Value.label } else { '' }
        $envLabels[$p.Name] = $lab
    }
}
else {
    $envIds = @('qa', 'uat')
}

$defaultEnv = if (-not [string]::IsNullOrWhiteSpace($Environment)) {
    $Environment
}
elseif ($cfg.PSObject.Properties.Name -contains 'defaultEnvironment' -and $cfg.defaultEnvironment) {
    [string]$cfg.defaultEnvironment
}
else {
    'qa'
}

$cred = Invoke-CrtqaCredentialForm `
    -DefaultUsername $cfg.sshUser `
    -Title 'CT console — environment, SSH login & password' `
    -EnvironmentIds $envIds `
    -EnvironmentLabels $envLabels `
    -DefaultEnvironment $defaultEnv
if ($null -eq $cred -or [string]::IsNullOrWhiteSpace($cred.Username) -or [string]::IsNullOrWhiteSpace($cred.Password)) {
    Write-Host '[Start-CrtqaConsoleSession] Cancelled.'
    exit 1
}

$resolved = Resolve-CrtqaEnvironment -Config $cfg -EnvironmentId $cred.EnvironmentId
$sshTarget = '{0}@{1}' -f $cred.Username, $resolved.SshHost
$entropy = Get-CrtqaEntropy -ConfigRoot $ConfigRoot -Additional $sshTarget

$statePath = Join-Path $secureRoot 'session.active.json'
if (Test-Path -LiteralPath $statePath) {
    try { & (Join-Path $PSScriptRoot 'Stop-CrtqaConsoleSession.ps1') -ConfigRoot $ConfigRoot } catch { Write-Warning $_.Exception.Message }
}

$credCipherPath = Join-Path $secureRoot 'session-credential.dpapi'
$credPwd = [string]::Copy($cred.Password)
$cred['Password'] = ''

[IO.File]::WriteAllBytes(
    $credCipherPath,
    (Protect-CrtqaSessionSecret -PlainBytes ([Text.Encoding]::UTF8.GetBytes($credPwd)) -Entropy $entropy))

$pwFile = $null
$masterProc = $null

try {
    $pwFile = New-RestrictedTempPasswordFile -Password $credPwd
    $credPwd = ''

    Write-Host ("[Start-CrtqaConsoleSession] Environment={0} ({1}) host={2} sudo={3}" -f `
            $resolved.EnvironmentId, $resolved.Label, $resolved.SshHost, $resolved.SudoUnixUser) -ForegroundColor Cyan
    Write-Host '[Start-CrtqaConsoleSession] Bringing up plink multiplex upstream (-share -N)…' -ForegroundColor Green
    try {
        $null = Start-Process -FilePath $cfg.plinkPath -ArgumentList @('-ssh', '-shareexists', $sshTarget) -PassThru -Wait `
            -WindowStyle Hidden -RedirectStandardError (Join-Path $Env:TEMP 'crtqa-share-probe.err')
    } catch {}

    $masterProc = Start-Process -FilePath $cfg.plinkPath -ArgumentList @(
            '-ssh', '-pwfile', $pwFile, '-share', '-batch', '-N', $sshTarget) -PassThru -WindowStyle Hidden
    Start-Sleep -Milliseconds 900

    & $cfg.plinkPath @('-ssh', '-share', '-batch', $sshTarget, 'echo', 'crtqa_multiplex_ok') | Out-Host
    if ($LASTEXITCODE -ne 0) {
        Stop-Process -Id $masterProc.Id -Force -ErrorAction SilentlyContinue
        throw "Upstream multiplex check failed (exit $($LASTEXITCODE)). Verify PuTTY ≥0.78 and network."
    }
}
catch {
    if (Test-Path -LiteralPath $credCipherPath) { Remove-Item $credCipherPath -Force -ErrorAction SilentlyContinue }
    if ($masterProc -and -not $masterProc.HasExited) { Stop-Process -Id $masterProc.Id -Force -ea 0 }
    throw $_
}
finally {
    if ($pwFile -and (Test-Path -LiteralPath $pwFile)) {
        try {
            $len = (Get-Item $pwFile).Length
            [IO.File]::WriteAllBytes($pwFile, (New-Object byte[] $len))
        }
        catch {}
        Remove-Item $pwFile -Force -ErrorAction SilentlyContinue
    }
}

$sshUserOnly = ($sshTarget -split '@')[0]
$state = @{
    version         = 3
    transport       = 'plink-share'
    environment     = $resolved.EnvironmentId
    environmentLabel = $resolved.Label
    platformMapId   = $resolved.PlatformMapId
    sshTarget       = $sshTarget
    sshHost         = $resolved.SshHost
    sshUser         = $sshUserOnly
    sudoUnixUser    = $resolved.SudoUnixUser
    remoteDxCommand = $cfg.remoteDxCommand
    termForRemote   = $cfg.termForRemote
    plinkPath       = $cfg.plinkPath
    masterProcessId = $masterProc.Id
    credentialDpapi = 'session-credential.dpapi'
    startedUtc      = [DateTime]::UtcNow.ToString('o')
    entropyTag      = 'Get-CrtqaEntropy(ConfigRoot,$sshTarget)'
}
Write-Utf8NoBom -LiteralPath $statePath -Text ($state | ConvertTo-Json -Depth 8)

Write-Host "[Start-CrtqaConsoleSession] Ready. env=$($resolved.EnvironmentId) session.active.json + multiplex PID $($masterProc.Id)." -ForegroundColor Green
Write-Host 'Invoke: .\Invoke-CrtqaDxConsole.ps1 -Commands @("help","exit")' -ForegroundColor Cyan
