# Intune detection script. Counts as installed if our entry is in Edge's
# force-install list.

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
