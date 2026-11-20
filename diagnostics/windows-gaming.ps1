$ErrorActionPreference = 'Stop'
try {
    $t = [Windows.Gaming.Preview.GamesEnumeration.GameModeUserConfiguration,Windows.Gaming,ContentType=WindowsRuntime]
    $t.GetMethods() | Where-Object { $_.DeclaringType -eq $t } | Select-Object -ExpandProperty Name
    $current = $t::GetDefault()
    $current | Format-List *
} catch { Write-Output "Game Mode API: $($_.Exception.GetBaseException().Message)" }
try {
    $capture = [Windows.Media.Capture.AppCaptureManager,Windows.Media.Capture,ContentType=WindowsRuntime]::GetCurrentSettings()
    $capture | Select-Object IsAppCaptureEnabled, IsHistoricalCaptureEnabled | Format-List
} catch { Write-Output "Capture API: $($_.Exception.GetBaseException().Message)" }
