# Adds the extension to Edge's force-install list and Edge does the rest.
# Leaves other extensions' entries alone. Fine to run more than once.

$ErrorActionPreference = 'Stop'

$ExtensionId = 'mmnheljcggbgjibghjangafmlajjnnag'
$UpdateUrl   = 'https://github.com/airbusiness-csec/Air-Business-Extension/releases/latest/download/updates.xml'
$PolicyPath  = 'SOFTWARE\Policies\Microsoft\Edge\ExtensionInstallForcelist'
$Entry       = "$ExtensionId;$UpdateUrl"
$LogFile     = Join-Path $env:ProgramData 'Microsoft\IntuneManagementExtension\Logs\AirBusinessXsltPolyfill.log'

function Write-Log([string]$Message) {
    $line = '{0:u} [Install] {1}' -f (Get-Date), $Message
    try { Add-Content -Path $LogFile -Value $line } catch { }
    Write-Output $line
}

if ($ExtensionId -notmatch '^[a-p]{32}$') {
    Write-Log 'Extension ID has not been set in Install.ps1. Nothing changed.'
    exit 1
}

# 64-bit view, in case Intune runs this as 32-bit PowerShell.
$hklm = [Microsoft.Win32.RegistryKey]::OpenBaseKey('LocalMachine', 'Registry64')
$key = $null
try {
    $key = $hklm.CreateSubKey($PolicyPath, $true)
    $names = @($key.GetValueNames())

    foreach ($name in $names) {
        $value = [string]$key.GetValue($name)
        if ($value -like "$ExtensionId;*") {
            if ($value -eq $Entry) {
                Write-Log "Already present as entry $name."
            } else {
                $key.SetValue($name, $Entry, [Microsoft.Win32.RegistryValueKind]::String)
                Write-Log "Updated entry $name to $Entry."
            }
            exit 0
        }
    }

    $index = 1
    while ($names -contains "$index") { $index++ }
    $key.SetValue("$index", $Entry, [Microsoft.Win32.RegistryValueKind]::String)
    Write-Log "Added entry $index : $Entry"
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
