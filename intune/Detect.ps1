<#
  Intune Win32 app: detection rule for Air Business XSLT Polyfill.

  Upload this as a custom detection script. Reports "installed" (output and
  exit 0) only when Edge's force-install list contains this exact entry.
#>

$ExtensionId = 'mmnheljcggbgjibghjangafmlajjnnag'
$UpdateUrl   = 'https://github.com/airbusiness-csec/Air-Business-Extension/releases/latest/download/updates.xml'
$PolicyPath  = 'SOFTWARE\Policies\Microsoft\Edge\ExtensionInstallForcelist'
$Entry       = "$ExtensionId;$UpdateUrl"

$hklm = [Microsoft.Win32.RegistryKey]::OpenBaseKey('LocalMachine', 'Registry64')
try {
    $key = $hklm.OpenSubKey($PolicyPath)
    if ($key) {
        try {
            foreach ($name in $key.GetValueNames()) {
                if ([string]$key.GetValue($name) -eq $Entry) {
                    Write-Output 'Air Business XSLT Polyfill force-install policy present.'
                    exit 0
                }
            }
        } finally { $key.Close() }
    }
} finally { $hklm.Close() }

exit 1
