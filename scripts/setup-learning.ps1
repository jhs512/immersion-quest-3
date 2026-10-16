$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
Push-Location $taskRoot
try {
    if (!(Get-Command uv -ErrorAction SilentlyContinue)) { throw 'Install uv first, then run this script again.' }
    uv venv target/ml-env --python 3.13
    if ($LASTEXITCODE -ne 0) { throw 'Python environment setup failed.' }
    uv pip install --python target/ml-env/Scripts/python.exe -r requirements-learning.txt
    if ($LASTEXITCODE -ne 0) { throw 'Learning package installation failed.' }
    Write-Output 'Learning Python is ready. Restart the development app and run Environment Doctor.'
} finally { Pop-Location }
