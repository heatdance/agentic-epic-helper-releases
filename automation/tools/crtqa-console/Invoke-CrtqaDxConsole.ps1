#Requires -Version 5.1
<#
.SYNOPSIS
  Run non-interactive dx console batches over multiplex PuTTY (-share).

.EXAMPLE
  .\Invoke-CrtqaDxConsole.ps1 -Commands @('show profiles','exit')
#>
[CmdletBinding(DefaultParameterSetName = 'Commands')]
param(
    [string] $ConfigRoot,
    [string] $TranscriptLog,
    [Parameter(Mandatory, ParameterSetName = 'Commands')]
    [string[]] $Commands,
    [Parameter(Mandatory, ParameterSetName = 'Probe')]
    [switch] $Probe
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($Probe) {
    $Commands = @('show console_guide', 'exit')
}
elseif ($PSCmdlet.ParameterSetName -eq 'Commands') {
    # Nested `pwsh -File … -Commands @('help','exit')` splats so trailing tokens miss -Commands.
    $extra = @($MyInvocation.UnboundArguments)
    if ($extra.Count -gt 0) {
        $Commands = @($Commands) + $extra
    }
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
if ($cmdsBlock -notmatch '(?ms)(\A|\n)\s*exit\s*(\n|\z)') { $cmdsBlock += "`nexit" }

$b64Cmds = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($cmdsBlock))

$tpl = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'crtqa-invoke-remote.bash.template') -Raw
$dxFrag = [string]$state.remoteDxCommand
if ($dxFrag -match "[`"'\\]") { throw 'remoteDxCommand in config contains shell metacharacters; simplify (e.g. dx run console).' }

$bootstrap = $tpl.
    Replace('__PW_B64__', $b64Pw).
    Replace('__CMD_B64__', $b64Cmds).
    Replace('__SUDO__', [string]$state.sudoUnixUser).
    Replace('__TERM__', [string]$state.termForRemote).
    Replace('__DX__', $dxFrag)
# CRLF-on-Windows checkout breaks remote bash (e.g. "pipefail\r: invalid option name").
$bootstrap = $bootstrap -replace "`r`n?", "`n"

$tmpBootstrap = Join-Path $secureRoot ("invoke-" + ([guid]::NewGuid().ToString('n')) + '.bash')

if ([string]::IsNullOrWhiteSpace($TranscriptLog)) {
    $TranscriptLog = Join-Path $secureRoot ('invoke-' + ([DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss')) + '.log')
}

Write-Utf8NoBom -LiteralPath $tmpBootstrap -Text $bootstrap
$tmpBootstrap = [IO.Path]::GetFullPath($tmpBootstrap)

$plink = [string]$state.plinkPath
$target = [string]$state.sshTarget
$stdoutTmp = Join-Path $Env:TEMP ("crtqa-invoke-o-" + [guid]::NewGuid().ToString('n'))
$stderrTmp = Join-Path $Env:TEMP ("crtqa-invoke-e-" + [guid]::NewGuid().ToString('n'))

try {
    "" | Out-File -FilePath $TranscriptLog -Encoding utf8
    "--- $(Get-Date -Format o) --- COMMANDS ---`n$cmdsBlock`n--- OUTPUT ---`n" | Out-File -FilePath $TranscriptLog -Append -Encoding utf8

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

