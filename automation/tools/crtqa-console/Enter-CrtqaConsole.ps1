#Requires -Version 5.1
<#
.SYNOPSIS
  Opens an interactive dxCore console session on CRTQA over PuTTY plink.

.DESCRIPTION
  Opens a graphical password prompt (masked) and attaches an interactive tty to dx.
  Prefer Start-CrtqaConsoleSession.ps1 + Invoke-CrtqaDxConsole.ps1 for multiplex / agent pipelines.
  - Stores the password only in short-lived files under %TEMP% (plink -pwfile) with a best-effort
    ACL; files are scrubbed in a finally block.

  Limitation: OpenSSH cannot authenticate with a password hash. This script never writes the
  cleartext password to the repo; plink still needs a temporary plaintext -pwfile on disk for the
  SSH handshake.
#>
[CmdletBinding()]
param(
  [string] $ConfigRoot = $PSScriptRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-CrtqaMergedConfig {
  param([string] $Root)
  $path = Join-Path $Root 'crtqa-console.config.json'
  if (-not (Test-Path -LiteralPath $path)) {
    throw "Missing config: $path"
  }
  $cfg = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
  $local = Join-Path $Root 'crtqa-console.local.json'
  if (Test-Path -LiteralPath $local) {
    $overlay = Get-Content -LiteralPath $local -Raw | ConvertFrom-Json
    foreach ($p in $overlay.PSObject.Properties) {
      $cfg | Add-Member -NotePropertyName $p.Name -NotePropertyValue $p.Value -Force
    }
  }
  return $cfg
}

function Invoke-WindowsPasswordPrompt {
  [CmdletBinding()]
  param([string] $Title)

  Add-Type -AssemblyName System.Drawing
  Add-Type -AssemblyName System.Windows.Forms
  try { [System.Windows.Forms.Application]::EnableVisualStyles() } catch { }

  $sshLabel = '(ssh)'
  $sudoLabel = '(sudo)'
  $form = New-Object System.Windows.Forms.Form
  $form.Text = $Title
  $form.MinimizeBox = $false
  $form.MaximizeBox = $false
  $form.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::FixedDialog
  $form.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen
  $form.ClientSize = New-Object System.Drawing.Size 440, 160
  $form.TopMost = $true

  $lbl = New-Object System.Windows.Forms.Label
  $lbl.AutoSize = $false
  $lbl.Location = New-Object System.Drawing.Point 14, 12
  $lbl.Size = New-Object System.Drawing.Size 408, 60
  $lbl.Text = (
    "Enter the shared password used for SSH $sshLabel and sudo $sudoLabel (example: `"sudo su - ctqa`"). " +
    'Password is kept in memory plus short-lived files under %TEMP%, not checked into Git.'
  )
  $lbl.Font = New-Object System.Drawing.Font @('Segoe UI', 9.0)

  $pwdBox = New-Object System.Windows.Forms.TextBox
  $pwdBox.PasswordChar = [char]'*'
  $pwdBox.Location = New-Object System.Drawing.Point 16, 80
  $pwdBox.Width = 400

  $ok = New-Object System.Windows.Forms.Button
  $ok.Text = 'OK'
  $ok.DialogResult = [System.Windows.Forms.DialogResult]::OK
  $ok.Location = New-Object System.Drawing.Point 242, 118

  $cancel = New-Object System.Windows.Forms.Button
  $cancel.Text = 'Cancel'
  $cancel.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
  $cancel.Location = New-Object System.Drawing.Point 322, 118

  $form.AcceptButton = $ok
  $form.CancelButton = $cancel
  $form.Controls.AddRange(@($lbl, $pwdBox, $ok, $cancel))

  $dialogResult = $form.ShowDialog()
  if ($dialogResult -ne [System.Windows.Forms.DialogResult]::OK) {
    return $null
  }
  return $pwdBox.Text
}

function New-DirectoryForce {
  param([string] $Path)
  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Path $Path -Force | Out-Null
  }
}

function Write-Utf8NoBom {
  param([string] $LiteralPath,[string]$Text)
  $enc = New-Object System.Text.UTF8Encoding $false
  [System.IO.File]::WriteAllText($LiteralPath, $Text, $enc)
}

function New-RestrictedTempPasswordFile {
  param([string] $Password)
  $tmp = Join-Path ([IO.Path]::GetTempPath()) ('crtqa-plink-pw-' + [guid]::NewGuid().ToString('n'))
  $null = New-Item -ItemType File -Path $tmp -Force
  Set-Content -LiteralPath $tmp -Value $Password -Encoding ascii -NoNewline
  try {
    icacls $tmp /inheritance:r /grant:r "${Env:USERNAME}:(R,W)" *> $null
  } catch { }
  return $tmp
}

$cfg = Get-CrtqaMergedConfig -Root $ConfigRoot

$repoRoot = Resolve-Path (Join-Path $ConfigRoot '../../..') | Select-Object -ExpandProperty Path
$secureRoot = Join-Path $repoRoot 'temp/crtqa-console'
New-DirectoryForce -Path $secureRoot

Write-Host '[crtqa-console] Enter password in the modal dialog.' -ForegroundColor Cyan
$pwdPlain = Invoke-WindowsPasswordPrompt -Title 'crtqa-console: SSH/sudo password'
if ($null -eq $pwdPlain -or [string]::IsNullOrWhiteSpace($pwdPlain)) {
  Write-Host '[crtqa-console] Cancelled.'
  exit 1
}

$b64Pw = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($pwdPlain))
$bootstrap = @'
set -euo pipefail
PW="$(printf '%s' "__B64_PW__" | base64 -d)"
printf '%s\n' "$PW" | sudo -S su - "__SUDO_USER__" -c 'export TERM="__TERM__"; exec __REMOTE_DX_CMD__'
'@
$bootstrap = $bootstrap.Replace('__B64_PW__', $b64Pw)
$bootstrap = $bootstrap.Replace('__SUDO_USER__', $cfg.sudoUnixUser)
$bootstrap = $bootstrap.Replace('__TERM__', $cfg.termForRemote)
$bootstrap = $bootstrap.Replace('__REMOTE_DX_CMD__', $cfg.remoteDxCommand)

if ($bootstrap.Contains('__')) { throw 'Bootstrap template substitution failed.' }

$bootstrapPath = Join-Path $secureRoot ('bootstrap-' + [guid]::NewGuid().ToString('n') + '.bash')
Write-Utf8NoBom -LiteralPath $bootstrapPath -Text $bootstrap

$plinkExe = $cfg.plinkPath
if (-not (Test-Path -LiteralPath $plinkExe)) {
  throw "plink not found at $plinkExe — install PuTTY or set `"plinkPath`" in crtqa-console.local.json"
}

$plinkPwFile = $null
$exitCode = 0

try {
  # plink needs a short-lived plaintext `-pwfile`; keep it only in %TEMP% and overwrite in finally.
  $plinkPwFile = New-RestrictedTempPasswordFile -Password $pwdPlain
  $target = ('{0}@{1}' -f $cfg.sshUser, $cfg.sshHost)
  $plinkArgs = @(
    '-ssh',
    '-pwfile', $plinkPwFile,
    '-t',
    $target,
    'bash', '-s'
  )
  Write-Host "[crtqa-console] Connecting to ${target} ..." -ForegroundColor Green
  Get-Content -LiteralPath $bootstrapPath -Raw | & $plinkExe @plinkArgs
  $exitCode = $LASTEXITCODE
} finally {
  if ($plinkPwFile -and (Test-Path -LiteralPath $plinkPwFile)) {
    try {
      $len = (Get-Item -LiteralPath $plinkPwFile).Length
      [IO.File]::WriteAllBytes($plinkPwFile, (New-Object byte[] $len))
    }
    catch { }
    Remove-Item -LiteralPath $plinkPwFile -Force -ErrorAction SilentlyContinue
  }
  Remove-Item -LiteralPath $bootstrapPath -Force -ErrorAction SilentlyContinue
  if ($null -ne $pwdPlain) {
    $pwdPlain = $null
  }
}

exit $exitCode