<#
  Intune Win32 app: uninstall Air Business XSLT Polyfill.

  Removes this extension's entry from Edge's force-install policy list. Edge
  then removes the extension. Other entries in the list are left alone.
  Runs as SYSTEM.
#>

$ErrorActionPreference = 'Stop'

$ExtensionId = 'mmnheljcggbgjibghjangafmlajjnnag'
$PolicyPath  = 'SOFTWARE\Policies\Microsoft\Edge\ExtensionInstallForcelist'
$LogFile     = Join-Path $env:ProgramData 'Microsoft\IntuneManagementExtension\Logs\AirBusinessXsltPolyfill.log'

function Write-Log([string]$Message) {
    $line = '{0:u} [Uninstall] {1}' -f (Get-Date), $Message
    try { Add-Content -Path $LogFile -Value $line } catch { }
    Write-Output $line
}

if ($ExtensionId -notmatch '^[a-p]{32}$') {
    Write-Log 'Extension ID has not been set in Uninstall.ps1. Nothing changed.'
    exit 1
}

$hklm = [Microsoft.Win32.RegistryKey]::OpenBaseKey('LocalMachine', 'Registry64')
$key = $null
try {
    $key = $hklm.OpenSubKey($PolicyPath, $true)
    if (-not $key) {
        Write-Log 'Policy key not present; nothing to remove.'
        exit 0
    }
    $removed = 0
    foreach ($name in @($key.GetValueNames())) {
        if ([string]$key.GetValue($name) -like "$ExtensionId;*") {
            $key.DeleteValue($name)
            $removed++
            Write-Log "Removed entry $name."
        }
    }
    if (-not $removed) { Write-Log 'No entry for this extension; nothing to remove.' }
    exit 0
}
catch {
    Write-Log "Failed: $($_.Exception.Message)"
    exit 1
}
finally {
    if ($key) { $key.Close() }
    $hklm.Close()
}
