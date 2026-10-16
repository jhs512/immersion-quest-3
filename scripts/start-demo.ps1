$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$demoRoot = Join-Path $projectRoot 'target/demo'
$demoBin = Join-Path $demoRoot 'bin'
New-Item -ItemType Directory -Force -Path $demoBin | Out-Null
$binary = Join-Path $demoBin 'molip-quest.exe'
$runningApp = Get-Process -Name 'molip-quest' -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq $binary }
if ($runningApp) { throw 'Close the demo window before starting a new build.' }
Copy-Item -LiteralPath (Join-Path $projectRoot 'target/debug/molip-quest.exe') -Destination $binary -Force
$app = Start-Process -FilePath $binary -WorkingDirectory $projectRoot -RedirectStandardOutput (Join-Path $demoRoot 'app.log') -RedirectStandardError (Join-Path $demoRoot 'app-error.log') -PassThru
$app.Id | Set-Content (Join-Path $demoRoot 'app.pid')
Write-Output 'Standalone learning app launched.'
