# Shared helpers for crtqa-console tooling (dot-source).
try { Add-Type -AssemblyName System.Security } catch {}

function Get-CrtqaMergedConfig {
    param([string] $Root)
    $path = Join-Path $Root 'crtqa-console.config.json'
    if (-not (Test-Path -LiteralPath $path)) { throw "Missing config: $path" }
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

function Get-CrtqaToolDirectory {
    if ($script:CrtqaConsoleToolDir) {
        return $script:CrtqaConsoleToolDir
    }
    throw 'CrtqaConsole.Common.ps1 was not dot-sourced; cannot resolve tool directory.'
}

function Get-CrtqaRepoRootFromTool {
    param([string] $ConfigRoot)
    $toolDir = $ConfigRoot
    if (-not (Test-Path -LiteralPath (Join-Path $toolDir 'crtqa-console.config.json'))) {
        $toolDir = Get-CrtqaToolDirectory
    }
    return (Resolve-Path (Join-Path $toolDir '../../..') | Select-Object -ExpandProperty Path)
}

function Get-CrtqaSecureRoot {
    param([string] $ConfigRoot)
    $repo = Get-CrtqaRepoRootFromTool -ConfigRoot $ConfigRoot
    return (Join-Path $repo 'temp/crtqa-console')
}

# Anchor paths to this file (works when dot-sourced from Start/Invoke/Stop).
$script:CrtqaConsoleToolDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function New-DirectoryForce {
    param([string] $Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Write-Utf8NoBom {
    param([string] $LiteralPath, [string] $Text)
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
    } catch {}
    return $tmp
}

function Invoke-CrtqaCredentialForm {
    <#
    Returns hashtable @{ Username = '...'; Password = '...' } or $null if cancelled.
    Shows a Windows Forms dialog (masked password). Same UI style as crtqa-console,
    suitable when the agent invokes PowerShell—the dialog is desktop-native (not Cursor's built-in input box API).
    #>
    param(
        [string] $DefaultUsername,
        [string] $Title = 'crtqa-console – sign in')
    Add-Type -AssemblyName System.Drawing
    Add-Type -AssemblyName System.Windows.Forms
    try { [System.Windows.Forms.Application]::EnableVisualStyles() } catch {}

    $form = New-Object System.Windows.Forms.Form
    $form.Text = $Title
    $form.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::FixedDialog
    $form.MinimizeBox = $false
    $form.MaximizeBox = $false
    $form.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen
    $form.TopMost = $true
    $form.ClientSize = New-Object System.Drawing.Size 460, 200

    $lblUser = New-Object System.Windows.Forms.Label
    $lblUser.Location = New-Object System.Drawing.Point 14, 14
    $lblUser.Size = New-Object System.Drawing.Size 430, 20
    $lblUser.Text = 'SSH / AD username (Linux login on CRTQA)'
    $txtUser = New-Object System.Windows.Forms.TextBox
    $txtUser.Location = New-Object System.Drawing.Point 16, 36
    $txtUser.Width = 428
    if ($DefaultUsername) { $txtUser.Text = $DefaultUsername }

    $lblPwd = New-Object System.Windows.Forms.Label
    $lblPwd.Location = New-Object System.Drawing.Point 14, 74
    $lblPwd.Size = New-Object System.Drawing.Size 430, 42
    $lblPwd.Text = ('Password — used once for SSH (plink) and sudo (`sudo su - …`). Stored for this workstation session only (DPAPI encrypt + multiplex).')
    $txtPwd = New-Object System.Windows.Forms.TextBox
    $txtPwd.PasswordChar = '*'
    $txtPwd.Location = New-Object System.Drawing.Point 16, 114
    $txtPwd.Width = 428

    $ok = New-Object System.Windows.Forms.Button
    $ok.Text = 'OK'
    $ok.DialogResult = [System.Windows.Forms.DialogResult]::OK
    $ok.Location = New-Object System.Drawing.Point 262, 154
    $cancel = New-Object System.Windows.Forms.Button
    $cancel.Text = 'Cancel'
    $cancel.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
    $cancel.Location = New-Object System.Drawing.Point 348, 154

    $form.AcceptButton = $ok
    $form.CancelButton = $cancel
    $form.Controls.AddRange(@($lblUser, $txtUser, $lblPwd, $txtPwd, $ok, $cancel))

    $dr = $form.ShowDialog()
    if ($dr -ne [System.Windows.Forms.DialogResult]::OK) { return $null }
    return @{
        Username = $txtUser.Text.Trim()
        Password = $txtPwd.Text
    }
}

function Protect-CrtqaSessionSecret {
    param([byte[]] $PlainBytes, [byte[]] $Entropy)
    return [Security.Cryptography.ProtectedData]::Protect($PlainBytes, $Entropy, 'CurrentUser')
}

function Unprotect-CrtqaSessionSecret {
    param([byte[]] $Cipher, [byte[]] $Entropy)
    return [Security.Cryptography.ProtectedData]::Unprotect($Cipher, $Entropy, 'CurrentUser')
}

function Get-CrtqaEntropy {
    param([string] $ConfigRoot, [string] $Additional)
    return [Text.Encoding]::UTF8.GetBytes(('crtqa-console-v2|{0}|{1}' -f $(Resolve-Path $ConfigRoot).Path, $Additional))
}
