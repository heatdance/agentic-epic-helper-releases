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
            if ($p.Name -eq 'environments' -and $cfg.PSObject.Properties.Name -contains 'environments') {
                foreach ($envProp in $p.Value.PSObject.Properties) {
                    $envId = $envProp.Name
                    if ($cfg.environments.PSObject.Properties.Name -contains $envId) {
                        foreach ($field in $envProp.Value.PSObject.Properties) {
                            $cfg.environments.$envId | Add-Member -NotePropertyName $field.Name -NotePropertyValue $field.Value -Force
                        }
                    }
                    else {
                        $cfg.environments | Add-Member -NotePropertyName $envId -NotePropertyValue $envProp.Value -Force
                    }
                }
            }
            else {
                $cfg | Add-Member -NotePropertyName $p.Name -NotePropertyValue $p.Value -Force
            }
        }
    }
    return $cfg
}

function Resolve-CrtqaEnvironment {
    <#
    Returns hashtable: EnvironmentId, Label, SshHost, SudoUnixUser, PlatformMapId
    Prefer $EnvironmentId; else cfg.defaultEnvironment; else first environments key; else legacy cfg.sshHost.
    #>
    param(
        $Config,
        [string] $EnvironmentId
    )
    $id = if (-not [string]::IsNullOrWhiteSpace($EnvironmentId)) {
        $EnvironmentId.Trim().ToLowerInvariant()
    }
    elseif ($Config.PSObject.Properties.Name -contains 'defaultEnvironment' -and $Config.defaultEnvironment) {
        [string]$Config.defaultEnvironment
    }
    else {
        'qa'
    }

    if ($Config.PSObject.Properties.Name -contains 'environments' -and $null -ne $Config.environments) {
        $names = @($Config.environments.PSObject.Properties.Name)
        if ($names -notcontains $id) {
            throw ("Unknown environment '{0}'. Known: {1}" -f $id, ($names -join ', '))
        }
        $env = $Config.environments.$id
        return @{
            EnvironmentId = $id
            Label         = if ($env.PSObject.Properties.Name -contains 'label' -and $env.label) { [string]$env.label } else { $id }
            SshHost       = [string]$env.sshHost
            SudoUnixUser  = [string]$env.sudoUnixUser
            PlatformMapId = if ($env.PSObject.Properties.Name -contains 'platformMapId') { [string]$env.platformMapId } else { '' }
        }
    }

    # Legacy single-host config (pre qa/uat split)
    if (-not $Config.sshHost) { throw 'Config missing environments.* and legacy sshHost.' }
    return @{
        EnvironmentId = $id
        Label         = $id
        SshHost       = [string]$Config.sshHost
        SudoUnixUser  = [string]$Config.sudoUnixUser
        PlatformMapId = ''
    }
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
    Returns hashtable @{ Username; Password; EnvironmentId } or $null if cancelled.
    Shows a Windows Forms dialog (masked password + qa/uat environment). Desktop-native UI.
    #>
    param(
        [string] $DefaultUsername,
        [string] $Title = 'crtqa-console – sign in',
        [string[]] $EnvironmentIds = @('qa', 'uat'),
        [hashtable] $EnvironmentLabels = @{},
        [string] $DefaultEnvironment = 'qa')
    Add-Type -AssemblyName System.Drawing
    Add-Type -AssemblyName System.Windows.Forms
    try { [System.Windows.Forms.Application]::EnableVisualStyles() } catch {}

    if (-not $EnvironmentIds -or $EnvironmentIds.Count -eq 0) {
        $EnvironmentIds = @('qa', 'uat')
    }
    if ([string]::IsNullOrWhiteSpace($DefaultEnvironment)) { $DefaultEnvironment = $EnvironmentIds[0] }
    if ($EnvironmentIds -notcontains $DefaultEnvironment) { $DefaultEnvironment = $EnvironmentIds[0] }

    $form = New-Object System.Windows.Forms.Form
    $form.Text = $Title
    $form.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::FixedDialog
    $form.MinimizeBox = $false
    $form.MaximizeBox = $false
    $form.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen
    $form.TopMost = $true
    $form.ClientSize = New-Object System.Drawing.Size 460, 250

    $lblEnv = New-Object System.Windows.Forms.Label
    $lblEnv.Location = New-Object System.Drawing.Point 14, 12
    $lblEnv.Size = New-Object System.Drawing.Size 430, 18
    $lblEnv.Text = 'Environment (SSH host / sudo user)'
    $cmbEnv = New-Object System.Windows.Forms.ComboBox
    $cmbEnv.DropDownStyle = [System.Windows.Forms.ComboBoxStyle]::DropDownList
    $cmbEnv.Location = New-Object System.Drawing.Point 16, 32
    $cmbEnv.Width = 428
    foreach ($eid in $EnvironmentIds) {
        $label = if ($EnvironmentLabels.ContainsKey($eid) -and $EnvironmentLabels[$eid]) {
            '{0} — {1}' -f $eid, $EnvironmentLabels[$eid]
        }
        else { $eid }
        [void]$cmbEnv.Items.Add($label)
    }
    $cmbEnv.SelectedIndex = [Math]::Max(0, [Array]::IndexOf(@($EnvironmentIds), $DefaultEnvironment))

    $lblUser = New-Object System.Windows.Forms.Label
    $lblUser.Location = New-Object System.Drawing.Point 14, 64
    $lblUser.Size = New-Object System.Drawing.Size 430, 18
    $lblUser.Text = 'SSH / AD username (Linux login)'
    $txtUser = New-Object System.Windows.Forms.TextBox
    $txtUser.Location = New-Object System.Drawing.Point 16, 84
    $txtUser.Width = 428
    if ($DefaultUsername) { $txtUser.Text = $DefaultUsername }

    $lblPwd = New-Object System.Windows.Forms.Label
    $lblPwd.Location = New-Object System.Drawing.Point 14, 116
    $lblPwd.Size = New-Object System.Drawing.Size 430, 36
    $lblPwd.Text = 'Password — SSH (plink) + sudo. Session-only (DPAPI + multiplex).'
    $txtPwd = New-Object System.Windows.Forms.TextBox
    $txtPwd.PasswordChar = '*'
    $txtPwd.Location = New-Object System.Drawing.Point 16, 154
    $txtPwd.Width = 428

    $ok = New-Object System.Windows.Forms.Button
    $ok.Text = 'OK'
    $ok.DialogResult = [System.Windows.Forms.DialogResult]::OK
    $ok.Location = New-Object System.Drawing.Point 262, 198
    $cancel = New-Object System.Windows.Forms.Button
    $cancel.Text = 'Cancel'
    $cancel.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
    $cancel.Location = New-Object System.Drawing.Point 348, 198

    $form.AcceptButton = $ok
    $form.CancelButton = $cancel
    $form.Controls.AddRange(@($lblEnv, $cmbEnv, $lblUser, $txtUser, $lblPwd, $txtPwd, $ok, $cancel))

    $dr = $form.ShowDialog()
    if ($dr -ne [System.Windows.Forms.DialogResult]::OK) { return $null }
    $selIdx = $cmbEnv.SelectedIndex
    if ($selIdx -lt 0) { $selIdx = 0 }
    return @{
        Username      = $txtUser.Text.Trim()
        Password      = $txtPwd.Text
        EnvironmentId = [string]$EnvironmentIds[$selIdx]
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
