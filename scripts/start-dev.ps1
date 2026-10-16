$ErrorActionPreference = 'Stop'
$taskProjectRoot = Split-Path -Parent $PSScriptRoot
$taskDx = Join-Path $taskProjectRoot 'target/dev-tools/dx.exe'
if (!(Test-Path -LiteralPath $taskDx)) {
    throw 'Install Dioxus CLI 0.7 into target/dev-tools/dx.exe, or use dx serve --desktop --bin molip-quest.'
}
$taskPreviousLive = $env:MOLIP_DEV_LIVE
try {
    $env:MOLIP_DEV_LIVE = '1'
    Push-Location $taskProjectRoot
    try {
        & $taskDx serve --desktop --bin molip-quest --interactive false --always-on-top false
        if ($LASTEXITCODE -ne 0) { throw "Development server exited with code $LASTEXITCODE" }
    } finally { Pop-Location }
} finally { $env:MOLIP_DEV_LIVE = $taskPreviousLive }
