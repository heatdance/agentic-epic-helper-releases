#Requires -Version 5.1
<#
.SYNOPSIS
  Run non-interactive host shell batches as the project sudo user (ctqa/ctuat)
  over multiplex PuTTY (-share) — WITHOUT `dx run console`.

.DESCRIPTION
  After /crtqa-console start, this hops: SSH → sudo su - <sudoUnixUser> → bash.
  Home of that user is the project root; component logs live under ./log/ (see
  docs/crtqa-console-contract.json host_logs).

.EXAMPLE
  . ./automation/tools/crtqa-console/Invoke-CrtqaHostShell.ps1 -Commands @('pwd','ls log','exit')
#>
[CmdletBinding()]
param(
    [string] $ConfigRoot,
    [string] $TranscriptLog,
    [Parameter(Mandatory)]
    [string[]] $Commands
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$extra = @($MyInvocation.UnboundArguments)
if ($extra.Count -gt 0) {
    $Commands = @($Commands) + $extra
}

. (Join-Path $PSScriptRoot 'CrtqaConsole.Common.ps1')

if ([string]::IsNullOrWhiteSpace($ConfigRoot) -or -not (Test-Path -LiteralPath (Join-Path $ConfigRoot 'crtqa-console.config.json'))) {
    $ConfigRoot = Get-CrtqaToolDirectory
}

$secureRoot = Get-CrtqaSecureRoot -ConfigRoot $ConfigRoot
$statePath = Join-Path $secureRoot 'session.active.json'
if (-not (Test-Path -LiteralPath $statePath)) {
    throw 'No multiplex session. Run /crtqa-console start or Start-CrtqaConsoleSession.ps1 first.'
}

$state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
$entropy = Get-CrtqaEntropy -ConfigRoot $ConfigRoot -Additional $state.sshTarget

$credPath = Join-Path $secureRoot $state.credentialDpapi
if (-not (Test-Path -LiteralPath $credPath)) { throw 'Missing session-credential.dpapi ; restart multiplex session.' }

$cipher = [IO.File]::ReadAllBytes($credPath)
$b64Pw = [Convert]::ToBase64String(
    (Unprotect-CrtqaSessionSecret -Cipher $cipher -Entropy $entropy))

$cmdsBlock = ($Commands | Where-Object { $_ -and $_.Trim().Length }) -join "`n"
# Host shell does not need `exit` the way dx console does; keep optional for parity.
$b64Cmds = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($cmdsBlock))

$tpl = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'crtqa-host-shell-remote.bash.template') -Raw

$bootstrap = $tpl.
    Replace('__PW_B64__', $b64Pw).
    Replace('__CMD_B64__', $b64Cmds).
    Replace('__SUDO__', [string]$state.sudoUnixUser).
    Replace('__TERM__', [string]$state.termForRemote)
$bootstrap = $bootstrap -replace "`r`n?", "`n"

$tmpBootstrap = Join-Path $secureRoot ("host-" + ([guid]::NewGuid().ToString('n')) + '.bash')

if ([string]::IsNullOrWhiteSpace($TranscriptLog)) {
    $TranscriptLog = Join-Path $secureRoot ('host-' + ([DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss')) + '.log')
}

Write-Utf8NoBom -LiteralPath $tmpBootstrap -Text $bootstrap
$tmpBootstrap = [IO.Path]::GetFullPath($tmpBootstrap)

$plink = [string]$state.plinkPath
$target = [string]$state.sshTarget
$stdoutTmp = Join-Path $Env:TEMP ("crtqa-host-o-" + [guid]::NewGuid().ToString('n'))
$stderrTmp = Join-Path $Env:TEMP ("crtqa-host-e-" + [guid]::NewGuid().ToString('n'))

try {
    "" | Out-File -FilePath $TranscriptLog -Encoding utf8
    "--- $(Get-Date -Format o) --- HOST COMMANDS ---`n$cmdsBlock`n--- OUTPUT ---`n" | Out-File -FilePath $TranscriptLog -Append -Encoding utf8

    $p = Start-Process -FilePath $plink `
        -ArgumentList @('-ssh', '-share', '-batch', $target, 'bash', '-s') `
        -RedirectStandardInput $tmpBootstrap `
        -RedirectStandardOutput $stdoutTmp `
        -RedirectStandardError $stderrTmp `
        -Wait -PassThru -NoNewWindow

    if (Test-Path $stdoutTmp) {
        $content = Get-Content -LiteralPath $stdoutTmp -Raw
        Write-Host $content
        $content | Out-File -FilePath $TranscriptLog -Append -Encoding utf8
        Remove-Item $stdoutTmp -Force -ea 0
    }
    if (Test-Path $stderrTmp) {
        $errContent = Get-Content -LiteralPath $stderrTmp -Raw -ea 0
        if (-not [string]::IsNullOrWhiteSpace($errContent)) {
            "--- STDERR ---`n$errContent" | Out-File -FilePath $TranscriptLog -Append -Encoding utf8
            Write-Host $errContent -ForegroundColor Yellow
        }
        Remove-Item $stderrTmp -Force -ea 0
    }

    Write-Host "Transcript: $TranscriptLog" -ForegroundColor Green

    if ($null -ne $p.ExitCode -and $p.ExitCode -ne 0) {
        Write-Warning ("Remote exit code: {0}" -f $p.ExitCode)
    }
}
finally {
    if (Test-Path $tmpBootstrap) { Remove-Item $tmpBootstrap -Force -ea 0 }
}
