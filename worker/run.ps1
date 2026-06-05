$ErrorActionPreference = "Stop"

Set-Location -Path $PSScriptRoot

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Environnement virtuel introuvable. Installation en cours..."
    & powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "install.ps1")
}

& $venvPython -m app.main @args
exit $LASTEXITCODE
